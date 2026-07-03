import os
import asyncpg
import json
from typing import List, Dict, Any, Optional

from config import NEON_DATABASE_URL


async def init_db():
    """Initializes the database by creating tables if they don't exist."""
    conn = None
    try:
        conn = await asyncpg.connect(NEON_DATABASE_URL)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS datasets (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) NOT NULL,
                file_path VARCHAR(255) NOT NULL,
                columns JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id SERIAL PRIMARY KEY,
                dataset_id INTEGER REFERENCES datasets(id),
                template VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'completed',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            await conn.close()


async def save_dataset(filename: str, file_path: str, columns: List[str]):
    conn = None

    try:
        conn = await asyncpg.connect(NEON_DATABASE_URL)
        dataset_id = await conn.fetchval(
            """
            INSERT INTO datasets (filename, file_path, columns)
            VALUES ($1,$2,$3)
            RETURNING id;
            """, filename, file_path, json.dumps(columns)
        )

        return dataset_id
    except Exception as e:
        raise e
    finally:
        if conn:
            await conn.close()


async def get_dataset(id: str):
    conn = None

    try:
        conn = await asyncpg.connect(NEON_DATABASE_URL)
        dataset = await conn.fetchrow(
            """
            SELECT * FROM datasets WHERE id = $1
            """, id
        )

        if dataset:
            return dict(dataset)
        return None
    except Exception as e:
        raise e
    finally:
        if conn:
            await conn.close()


async def save_report(dataset_id: int, template: str, title: str, content: str) -> Optional[int]:
    """Saves a generated report to the database."""
    conn = None
    try:
        conn = await asyncpg.connect(NEON_DATABASE_URL)
        report_id = await conn.fetchval("""
            INSERT INTO reports (dataset_id, template, title, content)
            VALUES ($1, $2, $3, $4)
            RETURNING id;
        """, dataset_id, template, title, content)
        return report_id
    except Exception as e:
        print(f"Error saving report: {e}")
        return None
    finally:
        if conn:
            await conn.close()

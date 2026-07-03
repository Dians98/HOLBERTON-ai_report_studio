# backend/init_db.py
import asyncio
import neon_client


async def main():
    print("Initializing database...")
    await neon_client.init_db()
    print("Database initialization process finished.")

if __name__ == "__main__":
    asyncio.run(main())

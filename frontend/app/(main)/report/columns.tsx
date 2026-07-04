"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Timestamp } from "next/dist/server/lib/cache-handlers/types"


export type Reports = {
    id: number;
    title: string;
    template: string;
    created_at: string; // Or Date, depending on how you handle timestamps
}

export const columns: ColumnDef<Reports>[] = [
    {
        accessorKey: "title",
        header: "Title",
    },
    {
        accessorKey: "template",
        header: "Type",
    },
    {
        accessorKey: "created_at",
        header: "Created at",
    }

]
"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Timestamp } from "next/dist/server/lib/cache-handlers/types"
import { Eye, Trash2 } from "lucide-react"

import { Button } from "@/components/ui/button"


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
    },
    {
        id: "actions",
        cell: ({ row }) => {
            const report = row.original

            return (
                <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                        <Eye className="h-4 w-4" />
                        <span className="sr-only">View report</span>
                    </Button>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive hover:text-destructive">
                        <Trash2 className="h-4 w-4" />
                        <span className="sr-only">Delete report</span>
                    </Button>
                </div>
            )
        },
    },

]
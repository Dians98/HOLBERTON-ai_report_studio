// frontend/components/data-table-skeleton.tsx
import { Skeleton } from "@/components/ui/skeleton"

export function DataTableSkeleton() {
    return (
        <div className="rounded-md border">
            {/* Header row */}
            <div className="border-b bg-muted/50 p-4">
                <div className="flex gap-4">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-4 w-20" />
                    <Skeleton className="h-4 w-16" />
                </div>
            </div>
            {/* Data rows */}
            {[...Array(5)].map((_, i) => (
                <div key={i} className="border-b p-4">
                    <div className="flex gap-4">
                        <Skeleton className="h-4 w-36" />
                        <Skeleton className="h-4 w-28" />
                        <Skeleton className="h-4 w-24" />
                        <div className="flex gap-2">
                            <Skeleton className="h-8 w-8 rounded-md" />
                            <Skeleton className="h-8 w-8 rounded-md" />
                        </div>
                    </div>
                </div>
            ))}
        </div>
    )
}
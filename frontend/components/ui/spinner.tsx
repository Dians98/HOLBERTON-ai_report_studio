import { cn } from "@/lib/utils"
import { Loader2Icon } from "lucide-react"

function Spinner({ className, ...props }: React.ComponentProps<"svg">) {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <Loader2Icon data-slot="spinner" role="status" aria-label="Loading" className={cn("size-4 animate-spin", className)} {...props} />
        </div>

    )
}

export { Spinner }

"use client"

import { useEffect, useState } from "react"
import { FileText, BarChart3, AlertTriangle, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const TEMPLATES = [
  {
    id: "executive_summary",
    name: "Executive Summary",
    description: "Concise overview of key insights and high-level trends in your data.",
    icon: BarChart3,
  },
  {
    id: "weekly_digest",
    name: "Weekly Digest",
    description: "Periodic summary highlighting changes, patterns, and notable events.",
    icon: FileText,
  },
  {
    id: "incident_report",
    name: "Incident Report",
    description: "Detailed analysis of specific events, root causes, and recommendations.",
    icon: AlertTriangle,
  },
]

export default function TemplateSelector({
  datasetId,
  onSuccess,
}: {
  datasetId: string
  onSuccess?: (reportId: string) => void
}) {
  const [selected, setSelected] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)



  const handleGenerate = async () => {
    if (!selected) return

    setGenerating(true)
    setError(null)

    try {

      const res = await fetch("/api/reports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          dataset_id: datasetId,
          template: selected,
        }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => null)
        throw new Error(data?.detail || `Generation failed (${res.status})`)
      }

      const data = await res.json()
      onSuccess?.(data.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate report")
    } finally {
      setGenerating(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <div className="grid gap-4">
        {TEMPLATES.map((t) => {
          const Icon = t.icon
          const isActive = selected === t.id
          return (
            <button
              key={t.id}
              type="button"
              onClick={() => setSelected(t.id)}
              className={cn(
                "flex items-start gap-4 rounded-3xl border p-5 text-left transition-all",
                isActive
                  ? "border-primary bg-primary/5 ring-1 ring-primary"
                  : "border-muted-foreground/25 hover:border-muted-foreground/50"
              )}
            >
              <div
                className={cn(
                  "flex size-12 shrink-0 items-center justify-center rounded-full",
                  isActive ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                )}
              >
                <Icon className="size-5" />
              </div>
              <div className="min-w-0">
                <p className="font-medium text-foreground">{t.name}</p>
                <p className="mt-1 text-sm text-muted-foreground">{t.description}</p>
              </div>
            </button>
          )
        })}
      </div>

      {error && (
        <div className="mt-3 rounded-3xl bg-destructive/10 px-4 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <Button
        type="button"
        size="lg"
        className="mt-6 w-full"
        disabled={!selected || generating}
        onClick={handleGenerate}
      >
        {generating && <Loader2 className="size-4 animate-spin" />}
        {generating ? "Generating..." : "Generate Report"}
      </Button>
    </div>
  )
}

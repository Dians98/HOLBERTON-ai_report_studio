"use client"

import { useEffect, useState } from "react"
import { Loader2, Download, FileText, FileDown } from "lucide-react"
import { Button } from "@/components/ui/button"

type Report = {
  id: string
  title: string
  content: string
  template: string
  created_at: string
}

export default function ReportViewer({ reportId, onReset }: { reportId: string; onReset?: () => void }) {
  const [report, setReport] = useState<Report | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)

    fetch(`/api/reports/${reportId}`)
      .then(async (res) => {
        if (!res.ok) throw new Error(`Failed to load report (${res.status})`)
        return res.json()
      })
      .then((data) => setReport(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [reportId])

  const handleExport = async (format: "markdown" | "html" | "pdf") => {
    try {
      const res = await fetch(`/api/reports/${reportId}/export?format=${format}`)
      if (!res.ok) throw new Error(`Export failed (${res.status})`)

      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `report.${format === "markdown" ? "md" : format === "html" ? "html" : "pdf"}`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed")
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="size-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="rounded-3xl bg-destructive/10 px-4 py-2 text-sm text-destructive">
        {error}
      </div>
    )
  }

  if (!report) return null

  return (
    <div className="mx-auto max-w-2xl">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">{report.title}</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            {new Date(report.created_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => handleExport("markdown")}>
            <FileText className="size-4" />
            MD
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport("html")}>
            <FileDown className="size-4" />
            HTML
          </Button>
          <Button variant="outline" size="sm" onClick={() => handleExport("pdf")}>
            <Download className="size-4" />
            PDF
          </Button>
        </div>
      </div>

      <div className="prose prose-gray max-w-none rounded-3xl border bg-card p-8 dark:prose-invert">
        {report.content.split("\n").map((line, i) => (
          <p key={i}>{line}</p>
        ))}
      </div>

      <div className="mt-8 text-center">
        <Button
          type="button"
          size="lg"
          className="mt-6 w-full"

          onClick={onReset}
        >
          Generate new report
        </Button>
      </div>
    </div>
  )
}

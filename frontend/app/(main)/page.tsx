"use client"

import { useState } from "react"
import { cn } from "@/lib/utils"
import UploadForm from "@/components/UploadForm"
import TemplateSelector from "@/components/TemplateSelector"
import ReportViewer from "@/components/ReportViewer"

const STEPS = [
  { id: 1, label: "Upload your file" },
  { id: 2, label: "Choose your template" },
  { id: 3, label: "Your summary is ready" },
]

export default function HomePage() {
  const [step, setStep] = useState(1)
  const [datasetId, setDatasetId] = useState<string | null>(null)
  const [reportId, setReportId] = useState<string | null>(null)

  const handleReset = () => {
    setStep(1)
    setDatasetId(null)
    setReportId(null)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-12 text-center">
        <h1 className="mb-4 text-5xl font-bold text-foreground">AI Report Studio</h1>
        <p className="text-xl text-muted-foreground">
          Transform your data into insightful narrative reports with the power of AI.
        </p>
      </header>

      {/* Step indicator */}
      <nav className="mx-auto mb-12 flex max-w-xl items-center justify-center gap-0">
        {STEPS.map((s, i) => (
          <div key={s.id} className="flex items-center">
            <div
              className={cn(
                "flex size-10 items-center justify-center rounded text-sm font-medium transition-colors",
                step === s.id
                  ? "bg-primary text-primary-foreground"
                  : step > s.id
                    ? "bg-primary/20 text-primary"
                    : "bg-muted text-muted-foreground"
              )}
            >
              {step > s.id ? "✓" : s.id}
            </div>
            <span
              className={cn(
                "ml-2 text-sm",
                step === s.id
                  ? "font-medium text-foreground"
                  : "text-muted-foreground"
              )}
            >
              {s.label}
            </span>
            {i < STEPS.length - 1 && (
              <div
                className={cn(
                  "mx-4 h-px w-16",
                  step > s.id ? "bg-primary" : "bg-muted"
                )}
              />
            )}
          </div>
        ))}
      </nav>

      {/* Step content */}
      <section>
        {step === 1 && (
          <UploadForm
            onSuccess={(id) => {
              setDatasetId(id)
              setStep(2)
            }}
          />
        )}

        {step === 2 && datasetId && (
          <TemplateSelector
            datasetId={datasetId}
            onSuccess={(id) => {
              setReportId(id)
              setStep(3)
            }}
          />
        )}

        {step === 3 && reportId && <ReportViewer reportId={reportId} onReset={handleReset} />}
      </section>
    </div>
  )
}

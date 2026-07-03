"use client"

import { Suspense } from "react"
import { useSearchParams } from "next/navigation"

function ReportContent() {
  const searchParams = useSearchParams()
  const id = searchParams?.get("id")
  return <div>Report {id ?? "(no id)"}</div>
}

export default function ReportPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ReportContent />
    </Suspense>
  )
}

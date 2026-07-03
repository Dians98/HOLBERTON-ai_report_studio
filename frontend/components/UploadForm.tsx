"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, File, X, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

export default function UploadForm({ onSuccess }: { onSuccess?: (datasetId: string) => void }) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const ALLOWED_EXTENSIONS = [".csv", ".json"]

  const onDrop = useCallback((accepted: File[], rejected: import("react-dropzone").FileRejection[]) => {
    setError(null)
    setSuccess(false)

    const allRejected = [
      ...rejected,
      ...accepted.filter((f) => {
        const ext = f.name.substring(f.name.lastIndexOf(".")).toLowerCase()
        return !ALLOWED_EXTENSIONS.includes(ext)
      }),
    ]

    if (allRejected.length > 0) {
      setError("Only CSV and JSON files are allowed")
      return
    }

    if (accepted.length > 0) {
      setFile(accepted[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  const removeFile = () => {
    setFile(null)
    setError(null)
    setSuccess(false)
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append("file", file)

      const res = await fetch("/api/datasets", {
        method: "POST",
        body: formData,
      })

      if (!res.ok) {
        const data = await res.json().catch(() => null)
        throw new Error(data?.detail || `Upload failed (${res.status})`)
      }

      const data = await res.json()
      setSuccess(true)
      setFile(null)
      onSuccess?.(data.id)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      {error && (
        <div className=" rounded-3xl bg-destructive/10 px-4 py-2 text-sm text-destructive text-center">
          {error}
        </div>
      )}

      <div
        {...getRootProps()}
        className={cn(
          "relative flex cursor-pointer flex-col items-center gap-4 rounded-3xl border-2 border-dashed p-12 text-center transition-colors mt-10",
          isDragActive
            ? "border-primary bg-primary/5"
            : "border-muted-foreground/25 hover:border-muted-foreground/50",
          file && "pointer-events-none opacity-50"
        )}
      >

        <input {...getInputProps()} />
        <div className="flex size-14 items-center justify-center rounded-full bg-muted">
          <Upload className="size-6 text-muted-foreground" />
        </div>
        {isDragActive ? (
          <p className="text-lg font-medium text-primary">Drop your file here</p>
        ) : (
          <div>
            <p className="text-lg font-medium">
              <span className="text-primary">Click to upload</span> or drag and drop
            </p>
            <p className="mt-1 text-sm text-muted-foreground">CSV or JSON (max 10 MB)</p>
          </div>
        )}
      </div>

      {file && (
        <div className="mt-4 flex items-center gap-3 rounded-3xl border bg-muted/30 px-4 py-3">
          <File className="size-5 shrink-0 text-primary" />
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
          <button
            type="button"
            onClick={removeFile}
            className="flex size-7 items-center justify-center rounded-full hover:bg-muted"
          >
            <X className="size-4" />
          </button>
        </div>
      )}



      <Button
        type="button"
        size="lg"
        className="mt-6 w-full"
        disabled={!file || uploading}
        onClick={handleUpload}
      >
        {uploading && <Loader2 className="size-4 animate-spin" />}
        {uploading ? "Uploading..." : "Upload File"}
      </Button>
    </div>
  )
}

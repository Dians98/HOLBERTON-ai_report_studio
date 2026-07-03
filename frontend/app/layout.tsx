import type { Metadata } from "next"
import "@/styles/globals.css"

export const metadata: Metadata = {
  title: "AI Report Studio",
  description: "Transform your data into insightful narrative reports with AI",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

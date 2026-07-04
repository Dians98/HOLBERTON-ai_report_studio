"use client"

import { Suspense, useEffect, useState } from "react"
import { useSearchParams } from "next/navigation"
import { Reports, columns } from "./columns"
import { DataTable } from "./data-table"

import { DataTableSkeleton } from "./skeleton"
import { Skeleton } from "@/components/ui/skeleton"



function ReportContent() {
  const searchParams = useSearchParams()
  const id = searchParams?.get("id")
  return <div>Report {id ?? "(no id)"}</div>
}

async function fetchData(): Promise<Reports[]> {
  try {
    const res = await fetch("/api/reports")

    if (!res.ok) {
      // Handle non-2xx responses
      const errorText = await res.text();
      throw new Error(`Failed to fetch reports: ${res.status} ${res.statusText} - ${errorText}`);
    }

    const data: Reports[] = await res.json();
    console.log("Fetched data:", data);
    return data;
  } catch (error) {
    console.error("Error fetching reports:", error);
    // You might want to re-throw or return an empty array/handle in the calling component
    throw error; // Re-throw to propagate the error for the calling component to handle
  }
}

export default function ReportPage() {
  const [data, setData] = useState<Reports[]>([]); // Type the state
  const [loading, setLoading] = useState(true)
  const getData = async () => {
    try {

      const result = await fetchData();
      setData(result);
    } catch (error) {
      console.error("Error fetching reports:", error);
      // Handle error, e.g., setData([]) or show an error message
    } finally {
      setLoading(false)
    }
  };

  useEffect(() => {
    getData();
  }, []);



  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <header className="mb-12 text-center">
          <h1 className="mb-4 text-5xl font-bold text-foreground">Reports</h1>
          <p className="text-lg text-muted-foreground">Your generated AI reports</p>
        </header>

        <section>
          {loading ? (
            <DataTableSkeleton />
          ) : (
            <DataTable columns={columns} data={data} />
          )}
        </section>
      </div>
    )

  }
  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-12 text-center">
        <h1 className="mb-4 text-5xl font-bold text-foreground">Reports</h1>
        <p className="text-lg text-muted-foreground">Your generated AI reports</p>
      </header>

      <section>
        <DataTable columns={columns} data={data} />
      </section>
    </div>
  )
}

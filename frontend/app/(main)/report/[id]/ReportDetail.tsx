'use client'

import { useEffect, useState } from "react"



export default function ReportDetail({ reportId }: { reportId: string }) {
    const [report, setReport] = useState<any>(null)

    const fetchReport = async (reportId: string) => {


        try {
            const res = await fetch(`/api/reports/${reportId}`)

            if (!res.ok) {
                // Handle non-2xx responses
                const errorText = await res.text();
                throw new Error(`Failed to fetch reports: ${res.status} ${res.statusText} - ${errorText}`);
            }

            const data = await res.json()

            setReport(data)
        } catch (error) {
            console.error("Error fetching reports:", error);
            // You might want to re-throw or return an empty array/handle in the calling component
            throw error;
        }
    }

    useEffect(() => {
        fetchReport(reportId)

    }, [reportId])

    if (!report) {
        return <div>Loading...</div>
    }
    return (
        <div className="space-y-6">
            <h2 className="text-3xl font-bold">{report.title}</h2>
            <div className="text-sm text-muted-foreground">
                <p>Template: {report.template}</p>
                <p>Created: {new Date(report.created_at).toLocaleDateString()}</p>
                <p>Status: {report.status}</p>
            </div>
            <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap bg-muted p-4 rounded-lg">
                    {report.content}
                </pre>
            </div>
        </div>
    )

}


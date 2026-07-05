import ReportDetail from "../ReportDetail"

export default async function Report({ params }: { params: { id: string } }) {
    const { id } = await params

    return (
        <div className="container mx-auto px-4 py-8">
            <header className="mb-12 text-center">
                <h1 className="mb-4 text-5xl font-bold text-foreground">Report details</h1>
                <p className="text-lg text-muted-foreground">Your generated AI reports</p>
            </header>

            <ReportDetail reportId={id} />
        </div>
    )
}
from pydantic import BaseModel


class GenerateReportRequest(BaseModel):
    dataset_id: str
    template: str

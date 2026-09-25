from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

ImportStatus = "previewed", "imported", "completed_with_errors"


class ImportErrorRow(BaseModel):
    row_number: int
    errors: list[str]


class ImportPreviewResponse(BaseModel):
    id: UUID
    entity_type: str
    status: str
    filename: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    imported_rows: int
    skipped_rows: int
    errors: list[ImportErrorRow]


class ImportResponse(ImportPreviewResponse):
    completed_at: datetime | None

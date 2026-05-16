from pydantic import BaseModel, Field

from app.services.query_builder import DriveSearchParams
from app.services.search_engine import safe_search_drive
from langchain.tools import tool


class DriveSearchToolInput(BaseModel):
    name: str | None = Field(default=None, description="File name value to search.")
    name_match: str = Field(default="contains", description="Either 'contains' or 'exact'.")
    full_text: str | None = Field(default=None, description="Drive fullText query value.")
    mime_type: str | None = Field(default=None, description="MIME type or alias like pdf, image, spreadsheet.")
    modified_after: str | None = Field(default=None, description="ISO datetime or date string.")
    modified_before: str | None = Field(default=None, description="ISO datetime or date string.")
    folder_id: str | None = Field(default=None, description="Folder scope override.")
    include_trashed: bool = Field(default=False, description="Set true only when user asks for trashed files.")
    page_size: int = Field(default=10, ge=1, le=100)


@tool(args_schema=DriveSearchToolInput)
def drive_search_tool(
    name: str | None = None,
    name_match: str = "contains",
    full_text: str | None = None,
    mime_type: str | None = None,
    modified_after: str | None = None,
    modified_before: str | None = None,
    folder_id: str | None = None,
    include_trashed: bool = False,
    page_size: int = 10,
):
    """Search Google Drive with structured arguments."""
    params = DriveSearchParams(
        name=name,
        name_match="exact" if name_match == "exact" else "contains",
        full_text=full_text,
        mime_type=mime_type,
        modified_after=modified_after,
        modified_before=modified_before,
        folder_id=folder_id,
        include_trashed=include_trashed,
        page_size=page_size,
    )
    return safe_search_drive(params)

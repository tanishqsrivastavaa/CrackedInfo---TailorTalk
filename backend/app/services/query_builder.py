from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Literal

from pydantic import BaseModel, Field, field_validator

GOOGLE_DOC = "application/vnd.google-apps.document"
GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
GOOGLE_SLIDE = "application/vnd.google-apps.presentation"
GOOGLE_FOLDER = "application/vnd.google-apps.folder"
PDF = "application/pdf"

MIME_TYPE_ALIASES = {
    "pdf": PDF,
    "document": GOOGLE_DOC,
    "doc": GOOGLE_DOC,
    "docs": GOOGLE_DOC,
    "google doc": GOOGLE_DOC,
    "sheet": GOOGLE_SHEET,
    "sheets": GOOGLE_SHEET,
    "spreadsheet": GOOGLE_SHEET,
    "spreadsheets": GOOGLE_SHEET,
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "slide": GOOGLE_SLIDE,
    "slides": GOOGLE_SLIDE,
    "presentation": GOOGLE_SLIDE,
    "folder": GOOGLE_FOLDER,
    "folders": GOOGLE_FOLDER,
    "image": "image/",
    "images": "image/",
    "photo": "image/",
    "photos": "image/",
    "png": "image/png",
    "video": "video/",
    "videos": "video/",
    "mp4": "video/mp4",
    "script": "text/x-sh",
    "shell script": "text/x-sh",
    "sh": "text/x-sh",
}


class DriveSearchParams(BaseModel):
    name: str | None = None
    name_match: Literal["contains", "exact"] = "contains"
    full_text: str | None = None
    mime_type: str | None = None
    modified_after: datetime | None = None
    modified_before: datetime | None = None
    folder_id: str | None = None
    include_trashed: bool = False
    page_size: int = Field(default=10, ge=1, le=100)

    @field_validator("name", "full_text", "mime_type", "folder_id", mode="before")
    @classmethod
    def clean_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("mime_type", mode="before")
    @classmethod
    def resolve_mime_alias(cls, value: str | None) -> str | None:
        if value is None:
            return None
        lowered = value.strip().lower()
        return MIME_TYPE_ALIASES.get(lowered, value.strip())

    @field_validator("modified_after", "modified_before", mode="before")
    @classmethod
    def parse_relative_datetime(cls, value: str | datetime | None) -> datetime | None:
        if value is None or isinstance(value, datetime):
            return value
        text = value.strip().lower()
        now = datetime.now(UTC)
        if text == "now":
            return now
        if text == "today":
            return datetime(now.year, now.month, now.day, tzinfo=UTC)
        if text == "yesterday":
            return datetime(now.year, now.month, now.day, tzinfo=UTC) - timedelta(days=1)
        if text in {"1 week ago", "last week"}:
            return now - timedelta(days=7)
        return value


def escape_drive_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _to_drive_time(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    utc_value = value.astimezone(UTC)
    return utc_value.isoformat().replace("+00:00", "Z")


def build_drive_query(params: DriveSearchParams) -> str:
    conditions: list[str] = []

    if params.folder_id:
        conditions.append(f"'{escape_drive_literal(params.folder_id)}' in parents")

    if not params.include_trashed:
        conditions.append("trashed = false")

    if params.name:
        escaped_name = escape_drive_literal(params.name)
        if params.name_match == "exact":
            conditions.append(f"name = '{escaped_name}'")
        else:
            conditions.append(f"name contains '{escaped_name}'")

    if params.full_text:
        conditions.append(f"fullText contains '{escape_drive_literal(params.full_text)}'")

    if params.mime_type:
        if params.mime_type.endswith("/"):
            conditions.append(f"mimeType contains '{escape_drive_literal(params.mime_type)}'")
        else:
            conditions.append(f"mimeType = '{escape_drive_literal(params.mime_type)}'")

    if params.modified_after:
        conditions.append(f"modifiedTime > '{_to_drive_time(params.modified_after)}'")

    if params.modified_before:
        conditions.append(f"modifiedTime < '{_to_drive_time(params.modified_before)}'")

    return " and ".join(conditions)

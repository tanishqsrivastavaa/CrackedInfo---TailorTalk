from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.services.google_drive import DriveSearchError, search_files
from app.services.query_builder import DriveSearchParams, build_drive_query


def _parse_date_hint(raw: str, now: datetime) -> tuple[datetime | None, datetime | None]:
    text = raw.lower()
    before_match = re.search(r"\bbefore\s+([a-zA-Z]+\s+\d{1,2}(?:,\s*\d{4})?)", text)
    before_date = None
    if before_match:
        before_date = _try_parse_month_date(before_match.group(1), now.year)

    after_match = re.search(r"\bafter\s+([a-zA-Z]+\s+\d{1,2}(?:,\s*\d{4})?)", text)
    after_date = None
    if after_match:
        after_date = _try_parse_month_date(after_match.group(1), now.year)

    if "today" in text:
        after_date = datetime(now.year, now.month, now.day, tzinfo=UTC)
    elif "yesterday" in text:
        after_date = datetime(now.year, now.month, now.day, tzinfo=UTC) - timedelta(days=1)
        before_date = datetime(now.year, now.month, now.day, tzinfo=UTC)
    elif "last week" in text or "recent" in text:
        after_date = now - timedelta(days=7)

    return after_date, before_date


def _try_parse_month_date(value: str, fallback_year: int) -> datetime | None:
    clean = " ".join(value.split()).replace(",", "")
    with_year = f"{clean} {fallback_year}"
    for fmt in ("%B %d %Y", "%b %d %Y"):
        for candidate in (clean, with_year):
            try:
                parsed = datetime.strptime(candidate, fmt)
                return parsed.replace(tzinfo=UTC)
            except ValueError:
                continue
    return None


def params_from_message(message: str, now: datetime | None = None) -> DriveSearchParams:
    now = now or datetime.now(UTC)
    text = message.lower()

    name_match = "exact" if ("exact" in text or "named exactly" in text) else "contains"
    name = None

    exact_name_match = re.search(r"(?:exact file|named|file)\s+['\"]?([^'\"]+\.[a-z0-9]{2,8}|[^'\"]+)['\"]?$", message, re.IGNORECASE)
    if exact_name_match and ("exact" in text or "named" in text):
        name = exact_name_match.group(1).strip()

    full_text = None
    full_text_match = re.search(r"(?:containing|contains|full\s*text)\s+['\"]?([^'\"]+)['\"]?", message, re.IGNORECASE)
    if full_text_match and "file" not in full_text_match.group(1).lower():
        full_text = full_text_match.group(1).strip()

    mime_type = None
    for candidate in ["pdf", "spreadsheet", "excel", "image", "photo", "png", "video", "mp4", "folder", "document", "sheet", "script"]:
        if candidate in text:
            mime_type = candidate
            break

    if not name:
        cleaned = re.sub(
            r"\b(find|show|search|for|the|files?|file|containing|contains|with|named|exact|recently|modified|before|after|today|yesterday|last week|recent|or)\b",
            " ",
            text,
        )
        cleaned = " ".join(cleaned.split())
        if cleaned:
            name = cleaned

    modified_after, modified_before = _parse_date_hint(message, now)

    return DriveSearchParams(
        name=name or None,
        name_match=name_match,
        full_text=full_text,
        mime_type=mime_type,
        modified_after=modified_after,
        modified_before=modified_before,
        folder_id=settings.DRIVE_FOLDER_ID or None,
        include_trashed=False,
    )


def search_drive(params: DriveSearchParams):
    query = build_drive_query(params)
    files = search_files(query=query, page_size=params.page_size)
    return {"query": query, "count": len(files), "files": files}


def safe_search_drive(params: DriveSearchParams):
    try:
        result = search_drive(params)
        return result | {"error": None}
    except DriveSearchError as exc:
        return {"query": build_drive_query(params), "count": 0, "files": [], "error": str(exc)}

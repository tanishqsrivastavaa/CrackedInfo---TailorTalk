from datetime import UTC, datetime

import pytest

from app.services.google_drive import DriveSearchError
from app.services.query_builder import DriveSearchParams, build_drive_query
from app.services.search_engine import params_from_message, safe_search_drive, search_drive


def test_exact_name_query():
    params = DriveSearchParams(name="Daily Report.pdf", name_match="exact", folder_id="folder123")
    query = build_drive_query(params)
    assert "name = 'Daily Report.pdf'" in query
    assert "'folder123' in parents" in query
    assert "trashed = false" in query


def test_partial_name_query():
    params = DriveSearchParams(name="report", name_match="contains", folder_id="folder123")
    query = build_drive_query(params)
    assert "name contains 'report'" in query


def test_mime_type_query():
    params = DriveSearchParams(mime_type="spreadsheet", folder_id="folder123")
    query = build_drive_query(params)
    assert "mimeType = 'application/vnd.google-apps.spreadsheet'" in query


def test_full_text_query():
    params = DriveSearchParams(full_text="TailorTalk", folder_id="folder123")
    query = build_drive_query(params)
    assert "fullText contains 'TailorTalk'" in query


def test_date_range_query():
    params = DriveSearchParams(
        modified_after=datetime(2026, 3, 1, tzinfo=UTC),
        modified_before=datetime(2026, 3, 8, tzinfo=UTC),
        folder_id="folder123",
    )
    query = build_drive_query(params)
    assert "modifiedTime > '2026-03-01T00:00:00Z'" in query
    assert "modifiedTime < '2026-03-08T00:00:00Z'" in query


def test_folder_scoping_and_not_trashed():
    params = DriveSearchParams(name="report", folder_id="abc-folder", include_trashed=False)
    query = build_drive_query(params)
    assert "'abc-folder' in parents" in query
    assert "trashed = false" in query


def test_quote_escaping():
    params = DriveSearchParams(name="O'Brien", full_text="manager's notes", folder_id="x")
    query = build_drive_query(params)
    assert "name contains 'O\\'Brien'" in query
    assert "fullText contains 'manager\\'s notes'" in query


@pytest.mark.parametrize(
    ("message", "expected"),
    [
        ("Find pdf reports", "application/pdf"),
        ("Show me images", "image/"),
        ("Find spreadsheets or Excel files", "application/vnd.google-apps.spreadsheet"),
        ("Find folders named qr codes", "application/vnd.google-apps.folder"),
    ],
)
def test_common_natural_language_prompts(message, expected):
    params = params_from_message(message, now=datetime(2026, 5, 16, tzinfo=UTC))
    assert params.mime_type == expected


def test_natural_language_recent_and_before_date():
    params = params_from_message("Find recently modified reports before March 8", now=datetime(2026, 5, 16, tzinfo=UTC))
    assert params.modified_after is not None
    assert params.modified_before == datetime(2026, 3, 8, tzinfo=UTC)
    assert params.name == "report"


def test_no_results_response(monkeypatch):
    def fake_search_files(query: str, page_size: int = 10, order_by: str = "modifiedTime desc"):
        return []

    monkeypatch.setattr("app.services.search_engine.search_files", fake_search_files)
    result = search_drive(DriveSearchParams(name="missing", folder_id="folder123"))
    assert result["count"] == 0
    assert result["files"] == []
    assert result["query"]


def test_drive_api_error_behavior(monkeypatch):
    def fake_search_files(query: str, page_size: int = 10, order_by: str = "modifiedTime desc"):
        raise DriveSearchError("quota exceeded")

    monkeypatch.setattr("app.services.search_engine.search_files", fake_search_files)
    result = safe_search_drive(DriveSearchParams(name="report", folder_id="folder123"))
    assert result["error"] == "quota exceeded"
    assert result["count"] == 0
    assert result["files"] == []


def test_plural_name_fallback_retry(monkeypatch):
    calls: list[str] = []

    def fake_search_files(query: str, page_size: int = 10, order_by: str = "modifiedTime desc"):
        calls.append(query)
        if "name contains 'reports'" in query:
            return []
        if "name contains 'report'" in query:
            return [{"id": "1", "name": "Daily Report.pdf"}]
        return []

    monkeypatch.setattr("app.services.search_engine.search_files", fake_search_files)
    result = safe_search_drive(DriveSearchParams(name="reports", folder_id="folder123"))
    assert result["error"] is None
    assert result["count"] == 1
    assert len(calls) == 2
    assert "name contains 'report'" in result["query"]

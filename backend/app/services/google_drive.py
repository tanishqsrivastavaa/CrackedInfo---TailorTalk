import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly"
]


class DriveSearchError(Exception):
    pass


def get_drive_service():
    if settings.GOOGLE_SERVICE_ACCOUNT_JSON.strip():
        service_account_info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON)
        creds = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )
    elif settings.SERVICE_SECRET.strip():
        creds = service_account.Credentials.from_service_account_file(
            settings.SERVICE_SECRET,
            scopes=SCOPES,
        )
    else:
        raise DriveSearchError(
            "Missing Google credentials. Set GOOGLE_SERVICE_ACCOUNT_JSON (recommended for deployment) "
            "or SERVICE_SECRET (local file path)."
        )

    return build(
        "drive",
        "v3",
        credentials=creds
    )


def search_files(
    query: str,
    page_size: int = 10,
    order_by: str = "modifiedTime desc"
):
    service = get_drive_service()

    try:
        results = (
            service.files()
            .list(
                q=query,
                pageSize=page_size,
                spaces="drive",
                orderBy=order_by,
                fields="files(id,name,mimeType,modifiedTime,webViewLink)"
            )
            .execute()
        )

        files = results.get("files", [])

        return [
            {
                "id": file.get("id"),
                "name": file.get("name"),
                "mime_type": file.get("mimeType"),
                "modified_time": file.get("modifiedTime"),
                "web_view_link": file.get("webViewLink")
            }
            for file in files
        ]

    except HttpError as e:
        raise DriveSearchError(str(e)) from e

from app.core.config import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        settings.SERVICE_SECRET, scopes=SCOPES
    )

    return build("drive", "v3", credentials=creds)


def search_files(query: str, page_size: int = 10):
    service = get_drive_service()
    try:
        results = (
            service.files()
            .list(
                q=query,
                pageSize=page_size,
                fields="files(id,name,mimeType,modifiedTime,webViewLink)",
                spaces="drive",
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
                    "web_view_link": file.get("webViewLink"),
                }
                for file in files
        ]

        
    except HttpError as e:
        print(f"Drive API Error: {e}")
        return []


def search_by_name(name: str):
    query = f"name contains '{name}'"
    return search_files(query)


"""Handle Google Drive interactions using rclone backend."""
import json
from rclone_python import rclone
from .drive_verify import get_drive_service
from dataclasses import dataclass
import tempfile
import os
from googleapiclient.discovery import build

DRIVE_FOLDER = "1B1VaWp-mCKk15_7XpFnImsTdBJPOGx7a"

@dataclass
class DriveFile:
    id: str
    filename: str
    mimeType: str
    path: str

    def __hash__(self) -> int:
        return hash(self.id)
    def __eq__(self, other: object) -> bool:
        if isinstance(other, DriveFile):
            return self.id == other.id
        return False

def GetRcloneFlags() -> list[str]:
    """Generate rclone flags from local credentials and token files to avoid needing rclone.conf."""
    creds = get_drive_service()

    if not (creds and creds.client_id and creds.client_secret and creds.expiry):
        raise Exception("Google Drive credentials not found")

    # rclone expects the token in a specific JSON format
    rclone_token = {
        "access_token": creds.token,
        "token_type": "Bearer",
        "refresh_token": creds.refresh_token,
        "expiry": creds.expiry.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    return [
        "--config", "/dev/null",
        "--drive-client-id", creds.client_id,
        "--drive-client-secret", creds.client_secret,
        "--drive-token", f"'{json.dumps(rclone_token)}'"
    ]

def GetAllFiles():
    """Recursively list all files."""

    service = build("drive", "v3", credentials=get_drive_service())
    all_files = []

    def _recurse(current_folder_id, path=""):
        page_token = None
        query = f"'{current_folder_id}' in parents and trashed = false"
        while True:
            response = service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType)",
                pageSize=1000,
                pageToken=page_token
            ).execute()
            for f in response.get("files", []):
                f["path"] = f"{path}/{f['name']}".removeprefix("/")
                all_files.append(f)
                # If it's a folder, recurse into it
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    _recurse(f["id"], path=f["path"])
            page_token = response.get("nextPageToken")
            if not page_token:
                break

    _recurse(DRIVE_FOLDER)
    
    files = []
    for file in all_files:
        if file['mimeType'] != "audio/mpeg":
            continue
        files.append(DriveFile(
            id=file['id'],
            filename=file['name'],
            mimeType=file['mimeType'],
            path=file['path']
        ))
    return files

def DownloadFiles(files: list[DriveFile], dest_dir: str) -> None:
    """Downloads the list of files from the drive folder to the destination using rclone."""

    src_path = f":drive,root_folder_id={DRIVE_FOLDER}:"
    flags = GetRcloneFlags()

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("\n".join([f.path for f in files]))
        f.flush()
        f.close()

        try:
            rclone.copy(
                in_path=src_path, 
                out_path=dest_dir, 
                args=["--files-from", f.name, "--checkers", "8", *flags]
            )
        finally:
            os.remove(f.name)

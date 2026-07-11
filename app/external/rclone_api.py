"""Handle Google Drive interactions using rclone backend."""

import json
import logging
import os
import tempfile
from dataclasses import dataclass

from googleapiclient.discovery import build
from rclone_python import rclone

from .google_verify import get_google_credentials

DRIVE_FOLDER = "1B1VaWp-mCKk15_7XpFnImsTdBJPOGx7a"
log = logging.getLogger()


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


def get_rclone_flags() -> list[str]:
    """Generate rclone flags from local credentials and token files to avoid needing rclone.conf."""
    creds = get_google_credentials()

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
        "--config",
        "/dev/null",
        "--drive-client-id",
        creds.client_id,
        "--drive-client-secret",
        creds.client_secret,
        "--drive-token",
        f"'{json.dumps(rclone_token)}'",
    ]


# def get_all_files() -> list[DriveFile]:
#     """Recursively list all files."""
#     log.info("Scanning Drive. This may take a while...")

#     service = build(
#         "drive", "v3", credentials=get_drive_service(), cache_discovery=False
#     )
#     all_files = []

#     def _recurse(current_folder_id, path=""):
#         page_token = None
#         query = f"'{current_folder_id}' in parents and trashed = false"
#         while True:
#             response = (
#                 service.files()
#                 .list(
#                     q=query,
#                     fields="nextPageToken, files(id, name, mimeType)",
#                     pageSize=1000,
#                     pageToken=page_token,
#                     supportsAllDrives=True,
#                     includeItemsFromAllDrives=True,
#                 )
#                 .execute()
#             )
#             for f in response.get("files", []):
#                 f["path"] = f"{path}/{f['name']}".removeprefix("/")
#                 all_files.append(f)
#                 # If it's a folder, recurse into it
#                 if f["mimeType"] == "application/vnd.google-apps.folder":
#                     _recurse(f["id"], path=f["path"])
#             page_token = response.get("nextPageToken")
#             if not page_token:
#                 break

#     _recurse(DRIVE_FOLDER)

#     files = []
#     for file in all_files:
#         if file["mimeType"] != "audio/mpeg":
#             continue
#         files.append(
#             DriveFile(
#                 id=file["id"],
#                 filename=file["name"],
#                 mimeType=file["mimeType"],
#                 path=file["path"],
#             )
#         )
#     return files


def get_all_files() -> list[DriveFile]:
    log.info("Scanning Drive. This may take a while...")

    service = build(
        "drive", "v3", credentials=get_drive_service(), cache_discovery=False
    )

    folders = []

    # 1. Get all folders in the root drive folder
    page_token = None
    query = (
        f"'{DRIVE_FOLDER}' in parents and trashed = false"
        " and mimeType = 'application/vnd.google-apps.folder'"
    )
    while True:
        response = (
            service.files()
            .list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType)",
                pageSize=1000,
                pageToken=page_token,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        for f in response.get("files", []):
            if f["name"].lower().startswith("disc "):
                folders.append(f)
        page_token = response.get("nextPageToken")
        if not page_token:
            break

    log.debug(f"Found {len(folders)} folders matching the query.")

    # 2. For each matching folder, scan all mp3 files
    files = []
    for folder in folders:
        log.debug(f"Scanning folder: {folder['name']}")
        page_token = None
        query = (
            f"'{folder['id']}' in parents and trashed = false"
            " and mimeType = 'audio/mpeg'"
        )
        while True:
            response = (
                service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageSize=1000,
                    pageToken=page_token,
                    supportsAllDrives=True,
                    includeItemsFromAllDrives=True,
                )
                .execute()
            )
            for f in response.get("files", []):
                files.append(
                    DriveFile(
                        id=f["id"],
                        filename=f["name"],
                        mimeType=f["mimeType"],
                        path=f"{folder['name']}/{f['name']}",
                    )
                )
            page_token = response.get("nextPageToken")
            if not page_token:
                break

    return files


def download_files(files: list[DriveFile], dest_dir: str) -> None:
    """Downloads the list of files from the drive folder to the destination using rclone."""

    src_path = f":drive,root_folder_id={DRIVE_FOLDER}:"
    flags = get_rclone_flags()

    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("\n".join([f.path for f in files]))
        f.flush()
        f.close()

        try:
            rclone.copy(
                in_path=src_path,
                out_path=dest_dir,
                args=[
                    "--files-from",
                    f.name,
                    "--checkers",
                    "8",
                    "--transfers",
                    "6",
                    *flags,
                ],
            )
        finally:
            os.remove(f.name)

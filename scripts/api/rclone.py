"""Handle Google Drive interactions using rclone backend."""
import json
from pathlib import Path

from rclone_python import rclone

DEFAULT_DRIVE_ID = "1B1VaWp-mCKk15_7XpFnImsTdBJPOGx7a"


def GetRcloneFlags() -> list[str]:
    """Generate rclone flags from local credentials and token files to avoid needing rclone.conf."""
    creds = json.loads(Path("credentials.json").read_text())
    try:
        creds = creds["installed"]
    except KeyError:
        creds = creds["web"]

    token_data = json.loads(Path("token.json").read_text())

    # rclone expects the token in a specific JSON format
    rclone_token = {
        "access_token": token_data["token"],
        "token_type": "Bearer",
        "refresh_token": token_data["refresh_token"],
        "expiry": token_data["expiry"],
    }

    return [
        "--config",
        "/dev/null",
        "--drive-client-id",
        creds["client_id"],
        "--drive-client-secret",
        creds["client_secret"],
        "--drive-token",
        f"'{json.dumps(rclone_token)}'",
    ]


def GetAllFiles(root_folder_id: str | None = None) -> list[dict]:
    """List files using rclone with on-the-fly config."""
    if root_folder_id is None:
        root_folder_id = DEFAULT_DRIVE_ID

    remote_path = f":drive,root_folder_id={root_folder_id}:"
    flags = GetRcloneFlags()
    print(flags)

    try:
        files_data = rclone.ls(remote_path, args=["-R", *flags])

        return [
            {
                "id": f.get("ID"),
                "name": f.get("Path"),
                "mimeType": f.get("MimeType"),
            }
            for f in files_data
            if not f.get("IsDir") and f.get("MimeType") == "audio/mpeg"
        ]
    except Exception as e:
        print(f"Rclone listing error: {e}")
        return []


def DownloadFiles(dest_dir: str, root_folder_id: str | None = None) -> None:
    """Download all files from the drive folder to the destination using rclone."""
    if root_folder_id is None:
        root_folder_id = DEFAULT_DRIVE_ID

    src_path = f":drive,root_folder_id={root_folder_id}:"
    flags = GetRcloneFlags()

    rclone.copy(src_path, dest_dir, args=flags)

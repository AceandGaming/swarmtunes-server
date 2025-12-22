from scripts.api.drive_verify import get_drive_service
import googleapiclient.http as driveAPI
from aiohttp import ClientSession
from scripts.paths import PROCESSING_DIR as PENDING_DIR

drive = get_drive_service()
driveFiles = drive.files()

drive = "1B1VaWp-mCKk15_7XpFnImsTdBJPOGx7a"

def GetAllFilesInFolder(q):
    page_token = None
    all_files = []
    while True:
        response = driveFiles.list(
            q=q,
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token,
            pageSize=100
        ).execute()

        all_files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    return all_files

def GetAllFiles(rootFolderId: str|None = None):
    if rootFolderId is None:
        rootFolderId = drive
    allFiles = []
    def Search(folderId, path=""):
        nonlocal allFiles
        query = f"'{folderId}' in parents and trashed = false"

        files = GetAllFilesInFolder(query)

        for file in files:
            currentPath = f"{path}/{file['name']}"

            if file['mimeType'] == 'application/vnd.google-apps.folder':
                Search(file['id'], currentPath)
            elif file['mimeType'] == 'audio/mpeg':
                allFiles.append(file)

    Search(rootFolderId)
    return allFiles

def DownloadFile(fileId):
    request = driveFiles.get_media(fileId=fileId)
    with open(PENDING_DIR / fileId, 'wb') as f:
        downloader = driveAPI.MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

async def DownloadFileAsync(fileId, session: ClientSession):
    url = f"https://drive.google.com/uc?id={fileId}"

    async with session.get(url, allow_redirects=True) as response:
        response.raise_for_status()

        ct = response.headers.get("Content-Type", "")
        if "text/html" in ct:
            raise RuntimeError("Google Drive returned HTML, not a file")

        path = PENDING_DIR / fileId
        with open(path, "wb") as f:
            async for chunk in response.content.iter_chunked(64 * 1024):
                f.write(chunk)

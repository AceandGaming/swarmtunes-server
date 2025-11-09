from scripts.api.drive_verify import get_drive_service
import googleapiclient.http as driveAPI
from aiohttp import ClientSession
import re
from datetime import datetime
from scripts.paths import PROCESSING_DIR as PENDING_DIR
import string

drive = get_drive_service()
driveFiles = drive.files()

folderIds = {
    "evil": "16WT3-_bOG2I50YS9eBwNK9W99Uh-QhwK",
    "neuro": "118gr4QuaGQGKfJ0X8VBCytvPjdzPayPY",
    "duet": "16XWYR_-i0vAvKkmI9a77ZLiZTp20WHjs",
    "mashup": "1x8GPZgcIAK-THwiM4jZ2lUCmFFJnx91m"
}
def GetAllFilesInFolder(q):
    page_token = None
    all_files = []
    while True:
        response = driveFiles.list(
            q=q,
            fields="nextPageToken, files(id, name)",
            pageToken=page_token,
            pageSize=100
        ).execute()

        all_files.extend(response.get('files', []))
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
    return all_files

def GetAllFiles():
    neuroFiles = GetAllFilesInFolder(f"'{folderIds["neuro"]}' in parents and mimeType='audio/mpeg'")
    for f in neuroFiles:
        f["folder"] = "neuro"

    evilFiles = GetAllFilesInFolder(f"'{folderIds["evil"]}' in parents and mimeType='audio/mpeg'")
    for f in evilFiles:
        f["folder"] = "evil"

    duetFiles = GetAllFilesInFolder(f"'{folderIds["duet"]}' in parents and mimeType='audio/mpeg'")
    for f in duetFiles:
        f["folder"] = "duet"

    mashupFiles = GetAllFilesInFolder(f"'{folderIds["mashup"]}' in parents and mimeType='audio/mpeg'")
    for f in mashupFiles:
        f["folder"] = "mashup"

    files = neuroFiles + evilFiles + duetFiles + mashupFiles
    return files

def DownloadFile(file_id):
    request = driveFiles.get_media(fileId=file_id)
    with open(PENDING_DIR / file_id, 'wb') as f:
        downloader = driveAPI.MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

async def DownloadFileAsync(file_id, session: ClientSession):
    url = 'https://drive.google.com/uc?id=' + file_id
    async with session.get(url, ssl=False) as response:
        with open(PENDING_DIR / file_id, 'wb') as f:
            while chunk := await response.content.read(1024):
                f.write(chunk)

def SearchFiles(searchTerm: str, folder):
    folderId = folderIds.get(folder)
    if folderId is None:
        raise Exception("Folder invaild. Must be 'neuro', 'evil' or 'duet")
    files = GetAllFilesInFolder(f"'{folderId}' in parents and mimeType='audio/mpeg'")
    matches = []
    for file in files:
        name = file["name"].lower().replace("(evil)", "")
        if searchTerm.lower() in name:
            matches.append(file)
    return matches

cutoff = datetime.strptime("21/03/24", "%d/%m/%y")
def GenerateMetaDataFromFile(fileName):
    songData = {}
    fileName = fileName.replace("(evil)", "").replace(".mp3", "").strip()

    regex = re.search(r"(.*?) - (.*?)\s+?\((\d\d \d\d \d\d)\)", fileName)
    if not regex:
        songData["title"] = fileName
        songData["artist"] = "unknown"
        songData["date"] = "unknown"
        return songData

    dateString = regex.group(3).strip().replace(" ", "/")
    fileDate = datetime.strptime(dateString, "%d/%m/%y")
    songData["date"] = fileDate

    mode = 2 if fileDate < cutoff else 1

    if mode == 1:
        songData["title"] = regex.group(2).strip()
        artists = regex.group(1).split("&")
        for i, artist in enumerate(artists):
            artists[i] = artist.strip()
        songData["artist"] = ", ".join(artists)
    else:
        songData["title"] = string.capwords(regex.group(1).strip())
        artists = regex.group(2).split("&")
        for i, artist in enumerate(artists):
            artists[i] = artist.strip()
        songData["artist"] = string.capwords(", ".join(artists))

    return songData
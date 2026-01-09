from PIL import Image
import scripts.paths as paths
from zlib import adler32

def GetCover(path, scale):
    try:
        key = str(path).encode() + str(scale).encode()
        file = paths.COVER_CACHE / f"{adler32(key)}.webp"
        if file.exists():
            return file

        image = Image.open(path)
        image = image.resize((scale, scale))
        image.save(file, "webp")

        return file
    except (FileNotFoundError):
        return None
    
def GetCoverPathFromSong(song):
    if song.coverType == "custom":
        return paths.COVERS_DIR / f"{song.coverArt}.png"
    else:
        return paths.ART_DIR / f"{song.coverType}.png"
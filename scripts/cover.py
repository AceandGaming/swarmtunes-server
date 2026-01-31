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
    return paths.COVERS_DIR / f"{song.coverArt}.png"

def CreateArtworkFromSingers(singers):
    if len(singers) == 0:
        return None
    if len(singers) > 1:
        return "duet"
    singer = singers[0]
    if singer == "Neuro-sama":
        return "neuro"
    if singer == "Evil Neuro":
        return "evil"
    return None
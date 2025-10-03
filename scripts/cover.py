from PIL import Image
import scripts.paths as paths
import io

def GetCover(path, scale):
    try:
        image = Image.open(path)
        image = image.resize((scale, scale))

        buffer = io.BytesIO()
        image.save(buffer, format="webp")
        buffer.seek(0)
        return buffer
    except:
        return None
    
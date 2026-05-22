import app.downloader.metadata as metadata
from pathlib import Path


files = [f"/home/ace/Downloads/test{i}.mp3" for i in range(1, 10)]


for f in files:
    print(metadata.load_file_metadata(Path(f)))

#print(metadata.load_file_metadata(Path("/home/ace/Downloads/test8.mp3")))
from scripts.id_manager import IDManager
from scripts.types import *
from scripts.data_system import DataSystem
from datetime import datetime

IDManager.Load()

now = datetime.now()
DataSystem.songs.Create(title="test", artist="test", singers=["test"], date=now)
DataSystem.songs.Create(title="test2", artist="test", singers=["test"], date=now)
DataSystem.songs.Create(title="test3", artist="test", singers=["test"], date=now)
DataSystem.songs.Create(title="test4", artist="test", singers=["test"], date=now)
album = DataSystem.albums.CreateFromDate(now)

print(album.__dict__)

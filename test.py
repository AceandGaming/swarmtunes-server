import os
os.environ["DATA_PATH"] = "dev"
from scripts.download import *
from scripts.classes.user import UserManager, Admin, PlaylistManager
from scripts.classes.song import SongManager
from scripts.paths import *

SongManager.Load()
PlaylistManager.Load()
UserManager.Load()
user = UserManager.GetUser("ad9a41f6-cb84-43cf-a7a5-5ab323a1b0ca")
if user is None:
    raise Exception("User not found")
admin = Admin.PromoteUser(user)
UserManager.UpdateUser(admin)
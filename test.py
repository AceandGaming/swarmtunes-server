from scripts.id_manager import IDManager
from scripts.types import *
from scripts.data_system import DataSystem

IDManager.Load()

user = DataSystem.users.Create(username="test", password="a hash")
user.AddResolver((lambda id: None))
DataSystem.users.Save(user)
print(user.__dict__)

IDManager.Save()
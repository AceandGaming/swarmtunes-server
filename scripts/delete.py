from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path
import scripts.paths as paths
import json
from scripts.config import MAX_DELETED_FILES_SIZE

@dataclass
class DeletedFile:
    contents: str
    orginalPath: Path
    dateDeleted: datetime = field(default_factory=datetime.now)


class DeleteManager:
    @staticmethod
    def SaveDeleted(deleted: DeletedFile):
        with open(paths.DELETED_DIR / deleted.dateDeleted.isoformat(), "w") as f:
            data = {
                "contents": deleted.contents,
                "dateDeleted": deleted.dateDeleted.isoformat(),
                "orginalPath": str(deleted.orginalPath)
            }
            f.write(json.dumps(data, indent=2))

    @staticmethod
    def LoadDeleted(fileName: str):
        path = paths.DELETED_DIR / fileName
        if not path.exists():
            return None
        with open(path, "r") as f:
            data = json.load(f)
            deleted = DeletedFile(data["contents"], Path(data["orginalPath"]), datetime.fromisoformat(data["dateDeleted"]))

            return deleted
    
    @staticmethod
    def RecoverDeleted(deleted: DeletedFile):
        path = paths.DATA_DIR / deleted.orginalPath.parent.name / deleted.orginalPath.name
        if path.exists():
            raise Exception("File already exists")
        path.write_text(deleted.contents)

    @staticmethod
    def DeleteFile(path: Path):
        if not path.exists():
            print("Warning: Attempted to delete file that does not exist")
            return
        contents = path.read_text()
        
        deleted = DeletedFile(contents, path)
        
        DeleteManager.SaveDeleted(deleted)
        path.unlink()

    @staticmethod
    def PermentlyDeleteAll():
        for file in paths.DELETED_DIR.iterdir():
            file.unlink()

    @staticmethod
    def DeleteExtraFiles():
        if not paths.DELETED_DIR.exists():
            return
        class DatedFile:
            def __init__(self, path: Path, dateDeleted: datetime):
                self.path = path
                self.dateDeleted = dateDeleted

            def __lt__(self, other):
                return self.dateDeleted < other.dateDeleted

        files = []
        for file in paths.DELETED_DIR.iterdir():
            try:
                time = datetime.fromisoformat(file.name)
                files.append(DatedFile(file, time))
            except:
                pass
            

        files.sort(reverse=True)

        totalSize = 0
        for file in files:
            totalSize += file.path.stat().st_size
            if totalSize < MAX_DELETED_FILES_SIZE:
                continue
            file.path.unlink()


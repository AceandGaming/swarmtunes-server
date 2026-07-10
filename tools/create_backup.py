import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "app"))

from automated.backup import create_backup  # noqa: E402

while True:
    answer = input("Create full backup? [y/n]: ").lower()

    if answer in ("y", "yes"):
        create_backup(True)
        break
    elif answer in ("n", "no"):
        create_backup(False)
        break
    else:
        print("Invalid answer. Please enter 'y' or 'n'.")

import sys
from pathlib import Path

import questionary

project_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_dir / "app"))

from core.backup import create_backup  # noqa: E402

is_full = questionary.confirm("Full backup?", default=True).ask()
if is_full is None:
    exit(0)

name = questionary.text("Backup name:", default="Manual Backup").ask()
if name is None:
    exit(0)

create_backup(is_full, name)

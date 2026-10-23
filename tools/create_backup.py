import questionary

from st.core.backup import create_backup

is_full = questionary.confirm("Full backup?", default=True).ask()
if is_full is None:
    exit(0)

name = questionary.text("Backup name:", default="Manual Backup").ask()
if name is None:
    exit(0)

create_backup(is_full, name)

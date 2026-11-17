# How to use alembic
PS: I keep forgetting

## Create migration
```bash
uv run alembic revision --autogenerate -m "MESSAGE"
```

## Update
```bash
uv run alembic upgrade head
```

## Undo
```bash
uv run alembic downgrade -1
```

## Info commands
```bash
# alembic current
uv run alembic current

# Show migration history
uv run alembic history

# Check for model/schema differences
uv run alembic check
```
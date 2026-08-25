from pathlib import Path


MIGRATIONS_DIR = Path(__file__).resolve().parents[2] / "migrations"


def migration_files() -> list[Path]:
    return sorted(MIGRATIONS_DIR.glob("*.sql"))

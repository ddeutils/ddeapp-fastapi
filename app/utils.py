from pathlib import Path


def is_empty(_dir: Path) -> bool:
    """Return if folder is empty"""
    return not any(_dir.iterdir())

import uuid
from pathlib import Path
from typing import Iterable


def uuid_filename(ext: str) -> str:
    ext = (ext or "").lstrip(".")
    if ext:
        return f"{uuid.uuid4().hex}.{ext}"
    return uuid.uuid4().hex


def safe_join(base_dir: str | Path, *paths: str) -> Path:
    base = Path(base_dir).resolve()
    target = base
    for p in paths:
        target = target.joinpath(p)
    target = target.resolve()
    if not str(target).startswith(str(base)):
        raise ValueError("Path escapes base directory")
    return target


def ensure_not_symlink(path: str | Path) -> None:
    p = Path(path)
    if p.is_symlink():
        raise ValueError("Symlinks are not allowed")


def validate_extension(filename: str, allowed: Iterable[str]) -> None:
    ext = Path(filename).suffix.lower().lstrip(".")
    allowed = {e.lower().lstrip(".") for e in allowed}
    if ext not in allowed:
        raise ValueError("File extension not allowed")


def verify_magic(header_bytes: bytes, allowed_signatures: Iterable[bytes]) -> None:
    for sig in allowed_signatures:
        if header_bytes.startswith(sig):
            return
    raise ValueError("File signature not allowed")

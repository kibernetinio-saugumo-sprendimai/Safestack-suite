"""Small filesystem helpers shared by the standalone SafeStack tools."""
import os
import tempfile
from pathlib import Path


def _parent(path):
    parent = Path(path).expanduser().parent
    parent.mkdir(parents=True, exist_ok=True)
    if parent.is_symlink():
        raise ValueError("artifact parent must not be a symlink")
    return parent.resolve(strict=True)


def atomic_write(path, data, mode=0o600):
    target = Path(path).expanduser()
    parent = _parent(target)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, parent / target.name)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def read_regular(path):
    target = Path(path).expanduser()
    if target.is_symlink() or not target.is_file():
        raise ValueError("expected a regular, non-symlink file")
    return target.read_bytes()

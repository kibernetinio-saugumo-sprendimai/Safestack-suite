"""USB Sentinel: File intake integrity and SHA-256 scanning."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safestack_common import sha256_file


def scan(root):
    root = Path(root).resolve(strict=True)
    result = {}
    for p in root.rglob('*'):
        if not p.is_file() or p.is_symlink():
            continue
        try:
            result[str(p.relative_to(root))] = sha256_file(p)
        except (OSError, ValueError):
            continue
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="SafeStack USB Sentinel - Hash intake directory")
    p.add_argument('path', help="Intake path to scan")
    x = p.parse_args()
    for name, digest in scan(x.path).items():
        print(f"{digest}  {name}")


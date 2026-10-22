import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safestack_common import atomic_write, read_regular, sha256_file


def manifest(root, exclude=None):
    root = Path(root).resolve(strict=True)
    excluded = Path(exclude).resolve() if exclude else None
    result = {}
    for p in root.rglob('*'):
        if not p.is_file() or p.is_symlink() or (excluded and p.resolve() == excluded):
            continue
        result[str(p.relative_to(root))] = sha256_file(p)
    return result


def write(root, out):
    atomic_write(out, (json.dumps(manifest(root, out), indent=2) + '\n').encode())


def verify(root, manifest_path):
    expected = json.loads(read_regular(manifest_path).decode('utf-8'))
    current = manifest(root, manifest_path)
    return {
        'missing': sorted(set(expected) - set(current)),
        'changed': sorted(k for k in expected.keys() & current.keys() if expected[k] != current[k]),
        'new': sorted(set(current) - set(expected))
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="SafeStack Backup Guardian")
    s = p.add_subparsers(dest='cmd', required=True)
    w = s.add_parser('create', help="Create backup manifest")
    w.add_argument('root', help="Directory to index")
    w.add_argument('manifest', help="Output manifest file")
    v = s.add_parser('verify', help="Verify against manifest")
    v.add_argument('root', help="Directory to verify")
    v.add_argument('manifest', help="Input manifest file")
    x = p.parse_args()

    if x.cmd == 'create':
        write(x.root, x.manifest)
    else:
        print(json.dumps(verify(x.root, x.manifest), indent=2))


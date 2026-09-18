import argparse, hashlib, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safestack_common import atomic_write, read_regular

def manifest(root, exclude=None):
    root=Path(root).resolve(strict=True); excluded = Path(exclude).resolve() if exclude else None
    result = {}
    for p in root.rglob('*'):
        if not p.is_file() or p.is_symlink() or (excluded and p.resolve() == excluded):
            continue
        result[str(p.relative_to(root))] = hashlib.sha256(read_regular(p)).hexdigest()
    return result
def write(root,out): atomic_write(out, (json.dumps(manifest(root, out),indent=2)+'\n').encode())
def verify(root,manifest_path):
    expected=json.loads(read_regular(manifest_path)); current=manifest(root, manifest_path); return {'missing':sorted(set(expected)-set(current)),'changed':sorted(k for k in expected.keys()&current.keys() if expected[k]!=current[k]),'new':sorted(set(current)-set(expected))}
if __name__=='__main__':
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True); w=s.add_parser('create'); w.add_argument('root'); w.add_argument('manifest'); v=s.add_parser('verify'); v.add_argument('root'); v.add_argument('manifest'); x=p.parse_args(); write(x.root,x.manifest) if x.cmd=='create' else print(json.dumps(verify(x.root,x.manifest),indent=2))

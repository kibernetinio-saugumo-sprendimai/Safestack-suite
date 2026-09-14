import argparse, hashlib, json
from pathlib import Path

def manifest(root):
    root=Path(root); return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
def write(root,out): Path(out).write_text(json.dumps(manifest(root),indent=2)+'\n')
def verify(root,manifest_path):
    expected=json.loads(Path(manifest_path).read_text()); current=manifest(root); return {'missing':sorted(set(expected)-set(current)),'changed':sorted(k for k in expected.keys()&current.keys() if expected[k]!=current[k]),'new':sorted(set(current)-set(expected))}
if __name__=='__main__':
 p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True); w=s.add_parser('create'); w.add_argument('root'); w.add_argument('manifest'); v=s.add_parser('verify'); v.add_argument('root'); v.add_argument('manifest'); x=p.parse_args(); write(x.root,x.manifest) if x.cmd=='create' else print(json.dumps(verify(x.root,x.manifest),indent=2))

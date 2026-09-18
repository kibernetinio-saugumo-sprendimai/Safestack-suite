import argparse, hashlib
from pathlib import Path

def scan(root):
    root = Path(root).resolve(strict=True)
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}
if __name__=='__main__':
 p=argparse.ArgumentParser(); p.add_argument('path'); x=p.parse_args();
 for name,digest in scan(x.path).items(): print(digest+'  '+name)

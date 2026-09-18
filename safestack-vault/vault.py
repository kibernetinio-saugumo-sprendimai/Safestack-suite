"""Minimal encrypted JSON vault. The key file must be protected by the OS."""
import argparse, json, os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cryptography.fernet import Fernet
from safestack_common import atomic_write, read_regular

def create_key(path):
    atomic_write(path, Fernet.generate_key(), 0o600)
def put(vault,key,name,value):
    fernet = Fernet(read_regular(key))
    data = {}
    target = Path(vault)
    if target.exists():
        data = json.loads(fernet.decrypt(read_regular(target)))
    data[name] = value
    token=fernet.encrypt(json.dumps(data, separators=(',', ':')).encode())
    atomic_write(vault, token, 0o600)
def get(vault,key,name):
    data=json.loads(Fernet(read_regular(key)).decrypt(read_regular(vault)))
    return data[name]
if __name__=='__main__':
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
    k=s.add_parser('keygen'); k.add_argument('path'); a=s.add_parser('put'); a.add_argument('vault'); a.add_argument('key'); a.add_argument('name'); a.add_argument('value'); g=s.add_parser('get'); g.add_argument('vault'); g.add_argument('key'); g.add_argument('name')
    x=p.parse_args(); create_key(x.path) if x.cmd=='keygen' else (put(x.vault,x.key,x.name,x.value) if x.cmd=='put' else print(get(x.vault,x.key,x.name)))

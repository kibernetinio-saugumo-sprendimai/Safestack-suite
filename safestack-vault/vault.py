"""Minimal encrypted JSON vault. The key file must be protected by the OS."""
import argparse, json, os
from pathlib import Path
from cryptography.fernet import Fernet

def create_key(path):
    p=Path(path); p.write_bytes(Fernet.generate_key()); os.chmod(p,0o600)
def put(vault,key,name,value):
    token=Fernet(Path(key).read_bytes()).encrypt(json.dumps({name:value}).encode())
    Path(vault).write_bytes(token); os.chmod(vault,0o600)
def get(vault,key,name):
    data=json.loads(Fernet(Path(key).read_bytes()).decrypt(Path(vault).read_bytes()))
    return data[name]
if __name__=='__main__':
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True)
    k=s.add_parser('keygen'); k.add_argument('path'); a=s.add_parser('put'); a.add_argument('vault'); a.add_argument('key'); a.add_argument('name'); a.add_argument('value'); g=s.add_parser('get'); g.add_argument('vault'); g.add_argument('key'); g.add_argument('name')
    x=p.parse_args(); create_key(x.path) if x.cmd=='keygen' else (put(x.vault,x.key,x.name,x.value) if x.cmd=='put' else print(get(x.vault,x.key,x.name)))

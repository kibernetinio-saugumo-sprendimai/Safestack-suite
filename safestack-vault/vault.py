"""Minimal encrypted JSON vault. The key file must be protected by the OS."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cryptography.fernet import Fernet
from safestack_common import atomic_write, read_regular


def create_key(path):
    atomic_write(path, Fernet.generate_key(), 0o600)


def put(vault, key, name, value):
    fernet = Fernet(read_regular(key))
    data = {}
    target = Path(vault).expanduser()
    if target.exists():
        decrypted = fernet.decrypt(read_regular(target))
        data = json.loads(decrypted.decode('utf-8'))
        if not isinstance(data, dict):
            raise ValueError("vault content corrupted: expected JSON object")
    data[name] = value
    token = fernet.encrypt(json.dumps(data, separators=(',', ':')).encode('utf-8'))
    atomic_write(vault, token, 0o600)


def get(vault, key, name):
    decrypted = Fernet(read_regular(key)).decrypt(read_regular(vault))
    data = json.loads(decrypted.decode('utf-8'))
    if not isinstance(data, dict):
        raise ValueError("vault content corrupted: expected JSON object")
    if name not in data:
        raise KeyError(f"Key '{name}' not found in vault")
    return data[name]


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="SafeStack Vault - Minimal encrypted JSON secrets store")
    s = p.add_subparsers(dest='cmd', required=True)

    k = s.add_parser('keygen', help="Generate a new encryption key")
    k.add_argument('path', help="Output path for the key file")

    a = s.add_parser('put', help="Store a secret in the vault")
    a.add_argument('vault', help="Path to the vault file")
    a.add_argument('key', help="Path to the encryption key file")
    a.add_argument('name', help="Secret key name")
    a.add_argument('value', help="Secret value")

    g = s.add_parser('get', help="Retrieve a secret from the vault")
    g.add_argument('vault', help="Path to the vault file")
    g.add_argument('key', help="Path to the encryption key file")
    g.add_argument('name', help="Secret key name")

    x = p.parse_args()
    if x.cmd == 'keygen':
        create_key(x.path)
    elif x.cmd == 'put':
        put(x.vault, x.key, x.name, x.value)
    elif x.cmd == 'get':
        print(get(x.vault, x.key, x.name))


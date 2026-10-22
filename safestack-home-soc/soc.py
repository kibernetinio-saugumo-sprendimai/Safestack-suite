"""Read-only local network inventory."""
import argparse
import json
from pathlib import Path
import socket
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safestack_common import atomic_write


def inventory():
    host = socket.gethostname()
    try:
        addresses = socket.getaddrinfo(host, None)
        ips = sorted({a[4][0] for a in addresses if ':' not in a[4][0]})
    except (socket.gaierror, OSError):
        ips = ['127.0.0.1']

    try:
        proc = subprocess.run(
            ['route', '-n', 'get', 'default'],
            capture_output=True,
            text=True,
            timeout=3
        )
        routes = proc.stdout[:1000] if proc.returncode == 0 else 'unavailable'
    except (OSError, subprocess.SubprocessError):
        routes = 'unavailable'

    return {
        'hostname': host,
        'ipv4': ips,
        'default_route': routes
    }


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="SafeStack Home SOC - Read-only local network inventory")
    p.add_argument('--json', dest='json_path', help="Output file path for JSON export")
    x = p.parse_args()
    data = inventory()
    print(json.dumps(data, indent=2))
    if x.json_path:
        atomic_write(x.json_path, (json.dumps(data, indent=2) + '\n').encode('utf-8'))


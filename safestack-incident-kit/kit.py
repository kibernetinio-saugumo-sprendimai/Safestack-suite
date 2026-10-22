"""Incident collection kit."""
import argparse
import json
from pathlib import Path
import platform
import socket
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safestack_common import atomic_write


def collect(output):
    out = Path(output).expanduser()
    if out.is_symlink():
        raise ValueError("output directory must not be a symlink")
    out.mkdir(parents=True, exist_ok=True)
    info = {
        'hostname': socket.gethostname(),
        'platform': platform.platform()
    }
    try:
        proc = subprocess.run(
            ['ps', '-eo', 'pid,comm'],
            capture_output=True,
            text=True,
            timeout=5
        )
        info['processes'] = proc.stdout[:10000] if proc.returncode == 0 else 'unavailable'
    except (OSError, subprocess.SubprocessError):
        info['processes'] = 'unavailable'

    target = out / 'system.json'
    atomic_write(target, (json.dumps(info, indent=2) + '\n').encode('utf-8'))
    return target


if __name__ == '__main__':
    p = argparse.ArgumentParser(description="SafeStack Incident Kit - Collect system snapshot")
    p.add_argument('output', help="Output directory for incident bundle")
    x = p.parse_args()
    print(collect(x.output))


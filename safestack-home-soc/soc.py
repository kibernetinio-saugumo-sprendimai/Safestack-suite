"""Read-only local network inventory."""
import argparse, json, socket, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safestack_common import atomic_write

def inventory():
    host=socket.gethostname(); addresses=socket.getaddrinfo(host,None)
    ips=sorted({a[4][0] for a in addresses if ':' not in a[4][0]})
    try: routes=subprocess.run(['route','-n','get','default'],capture_output=True,text=True,timeout=3).stdout
    except OSError: routes='unavailable'
    return {'hostname':host,'ipv4':ips,'default_route':routes[:1000]}
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--json'); x=p.parse_args(); d=inventory(); print(json.dumps(d,indent=2));
    if x.json: atomic_write(x.json, (json.dumps(d,indent=2)+'\n').encode())

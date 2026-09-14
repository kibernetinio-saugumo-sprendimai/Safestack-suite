"""Read-only local network inventory."""
import argparse, json, socket, subprocess

def inventory():
    host=socket.gethostname(); addresses=socket.getaddrinfo(host,None)
    ips=sorted({a[4][0] for a in addresses if ':' not in a[4][0]})
    try: routes=subprocess.run(['route','-n','get','default'],capture_output=True,text=True,timeout=3).stdout
    except OSError: routes='unavailable'
    return {'hostname':host,'ipv4':ips,'default_route':routes[:1000]}
if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--json'); x=p.parse_args(); d=inventory(); print(json.dumps(d,indent=2));
    if x.json: open(x.json,'w').write(json.dumps(d,indent=2)+'\n')

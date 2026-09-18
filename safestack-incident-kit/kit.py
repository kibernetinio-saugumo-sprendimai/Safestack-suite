import argparse, json, platform, socket, subprocess
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from safestack_common import atomic_write

def collect(output):
    out=Path(output); out.mkdir(parents=True,exist_ok=True)
    info={'hostname':socket.gethostname(),'platform':platform.platform()}
    try: info['processes']=subprocess.run(['ps','-eo','pid,comm'],capture_output=True,text=True,timeout=5).stdout[:10000]
    except OSError: info['processes']='unavailable'
    target = out / 'system.json'
    atomic_write(target, (json.dumps(info,indent=2)+'\n').encode())
    return target
if __name__=='__main__': p=argparse.ArgumentParser(); p.add_argument('output'); x=p.parse_args(); print(collect(x.output))

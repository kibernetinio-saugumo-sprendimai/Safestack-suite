import argparse, json, platform, socket, subprocess
from pathlib import Path

def collect(output):
    out=Path(output); out.mkdir(parents=True,exist_ok=True)
    info={'hostname':socket.gethostname(),'platform':platform.platform()}
    try: info['processes']=subprocess.run(['ps','-eo','pid,comm'],capture_output=True,text=True,timeout=5).stdout[:10000]
    except OSError: info['processes']='unavailable'
    (out/'system.json').write_text(json.dumps(info,indent=2)+'\n'); return out/'system.json'
if __name__=='__main__': p=argparse.ArgumentParser(); p.add_argument('output'); x=p.parse_args(); print(collect(x.output))

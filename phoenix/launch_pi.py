"""Only tag and launch the front session; Core owns its own worker service."""
import json
import os
from pathlib import Path
import sys

def build(home,prefix,inherited,args):
    home=Path(home);prefix=Path(prefix);env=dict(inherited)
    env.pop('FEISHU_APP_ID',None);env.pop('FEISHU_APP_SECRET',None)
    env.update(PI_OFFLINE='1',A2A_SERVER_ENABLED='false',PHONEPI_ROLE='front')
    env.setdefault('PI_CODING_AGENT_DIR',str(home/'.pi/agent'))
    preload=prefix/'lib/libtermux-exec.so'
    if preload.exists():env['LD_PRELOAD']=str(preload)
    else:env.pop('LD_PRELOAD',None)
    state=Path(env.get('PHONEPI_JOB_STATE',home/'.local/share/phonepi-jobs'))
    try:enabled=json.loads((state/'config.json').read_text()).get('enabled')
    except (OSError,ValueError):enabled=False
    command=[str(prefix/'bin/node'),str(prefix/'lib/node_modules/@earendil-works/pi-coding-agent/dist/bundle/cli.js')]
    if enabled:command+=['--thinking','low']
    return command+args,env

if __name__=='__main__':
    prefix=os.environ.get('PREFIX','/data/data/com.termux/files/usr')
    command,env=build(Path.home(),prefix,os.environ,sys.argv[1:])
    os.execvpe(command[0],command,env)

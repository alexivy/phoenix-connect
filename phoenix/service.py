"""Phoenix Connect bridge lifecycle. Existing private config and owner binding."""
import contextlib
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import tomllib

os.umask(0o077)
HOME=Path.home()
ROOT=Path(os.environ.get('PHOENIX_CONNECT_STATE',HOME/'.pi-connect'))
CONFIG=ROOT/'config.toml'
PIDFILE=ROOT/'supervisor.pid'
SCRIPT=Path(__file__).resolve()

def owned_pid():
    try:
        pid=int(PIDFILE.read_text());args=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
        return pid if str(SCRIPT).encode() in args and b'run' in args else None
    except (OSError,ValueError):return None

def ready():
    if not CONFIG.exists():return False
    d=tomllib.loads(CONFIG.read_text());opts=d['projects'][0]['platforms'][0]['options']
    allowed=[s.strip() for s in opts.get('allow_from','').split(',') if s.strip() not in ('','pending-owner')]
    log=(ROOT/'onboarding.log').read_text(errors='replace') if (ROOT/'onboarding.log').exists() else ''
    return bool(opts.get('app_id') and opts.get('app_secret') and allowed and '*' not in allowed and '注册返回的 open_id 是机器人自身' not in log)

def main():
    ROOT.mkdir(parents=True,exist_ok=True,mode=0o700)
    action=sys.argv[1] if len(sys.argv)>1 else 'status'
    if action=='status':
        print(json.dumps({'running':bool(owned_pid()),'credentials_and_owner_ready':ready(),'controller':'phoenix-connect'}));return
    if action=='start':
        if not ready():raise SystemExit('Valid private config and explicit owner allowlist are required')
        if owned_pid():print('{"already_running":true}');return
        if PIDFILE.exists():
            try:os.kill(int(PIDFILE.read_text()),0)
            except (OSError,ValueError):pass
            else:raise SystemExit('Another bridge controller is running; stop it before migration')
        env=os.environ.copy();env.pop('LD_PRELOAD',None)
        with (ROOT/'supervisor.log').open('ab') as log:
            p=subprocess.Popen([sys.executable,str(SCRIPT),'run'],env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=log,start_new_session=True)
        print(json.dumps({'started':True,'pid':p.pid}));return
    if action=='stop':
        pid=owned_pid()
        if pid:os.kill(pid,signal.SIGTERM)
        print(json.dumps({'stop_requested':bool(pid)}));return
    if action!='run':raise SystemExit('start | stop | status')
    with (ROOT/'supervisor.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return
        PIDFILE.write_text(str(os.getpid()));stopping=False;child=None
        def stop(*_):
            nonlocal stopping
            stopping=True
            if child and child.poll() is None:child.terminate()
        signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
        env=os.environ.copy();env.pop('LD_PRELOAD',None);env.update(PI_OFFLINE='1',NO_COLOR='1')
        binary=Path(os.environ.get('PHOENIX_CONNECT_BINARY',HOME/'.local/bin/pi-connect'))
        cwd=Path(os.environ.get('PHOENIX_CONNECT_CWD',HOME/'phone-research'))
        try:
            while not stopping and ready():
                child=subprocess.Popen([str(binary),'--config',str(CONFIG)],cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
                with (ROOT/'bridge.log').open('a') as log:
                    for line in child.stdout:
                        if log.tell()>3_000_000:log.seek(0);log.truncate()
                        log.write(line);log.flush()
                child.stdout.close();child.wait()
                if not stopping:time.sleep(10)
        finally:
            if child and child.poll() is None:
                with contextlib.suppress(ProcessLookupError):child.terminate()
                with contextlib.suppress(subprocess.TimeoutExpired):child.wait(timeout=12)
            PIDFILE.unlink(missing_ok=True)

if __name__=='__main__':main()

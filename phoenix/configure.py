"""Explicitly register this installed adapter with Core's private config."""
from pathlib import Path
import json,os,sys
os.umask(0o077)
state=Path(os.environ.get('PHONEPI_JOB_STATE',Path.home()/'.local/share/phonepi-jobs'));state.mkdir(parents=True,exist_ok=True,mode=0o700)
p=state/'config.json';config=json.loads(p.read_text()) if p.exists() else {}
config['transport_command']=[sys.executable,str(Path(__file__).with_name('transport.py').resolve())]
temp=p.with_suffix('.new');temp.write_text(json.dumps(config));temp.replace(p)
print(json.dumps({'configured':True,'protocol':'phoenix.transport.v1'}))

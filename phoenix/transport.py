"""Versioned notification adapter. No credentials or recipient guessing."""
import http.client,json,os,socket,sys
from pathlib import Path

class TransportError(RuntimeError):
 def __init__(self,code):self.code=code;super().__init__(code)

class UnixHTTP(http.client.HTTPConnection):
 def __init__(self,path):super().__init__('localhost',timeout=8);self.path=str(path)
 def connect(self):
  self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);self.sock.settimeout(self.timeout);self.sock.connect(self.path)

def send(envelope,socket_path=None):
 if envelope.get('protocol')!='phoenix.transport.v1':raise ValueError('unsupported_protocol')
 route=envelope.get('route',{})
 if not route.get('project') or not route.get('session_key') or not envelope.get('message'):raise ValueError('explicit_route_and_message_required')
 path=socket_path or os.environ.get('PHOENIX_CONNECT_SOCKET') or Path.home()/'.pi-connect/data/run/api.sock'
 conn=UnixHTTP(path)
 try:
  body={'project':route['project'],'session_key':route['session_key'],'message':envelope['message']}
  conn.request('POST','/send',json.dumps(body,ensure_ascii=False).encode('utf-8'),{'Content-Type':'application/json'})
  response=conn.getresponse();raw=response.read(65536)
  if response.status!=200:raise TransportError('bridge_http_'+str(response.status))
  ack=json.loads(raw)
  if ack.get('status')!='ok':raise RuntimeError('invalid_bridge_acknowledgement')
  return {'protocol':'phoenix.transport.v1','status':'accepted','notification_id':str(envelope.get('notification_id',''))}
 finally:conn.close()

if __name__=='__main__':
 try:print(json.dumps(send(json.load(sys.stdin))))
 except Exception as e:
  print(json.dumps({'protocol':'phoenix.transport.v1','status':'failed','error_code':getattr(e,'code',type(e).__name__)}));raise SystemExit(1)

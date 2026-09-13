import json,pathlib,socket
r={}
root=pathlib.Path(__file__).parent
private=pathlib.Path('C:\\Users\\wogud\\AppData\\Local\\Temp\\do-math-native-iajjk6jp-private')
for label,action in [('workspace_write',lambda:(root/'allowed.txt').write_text('ok')),('outside_read',lambda:(private/'canary.txt').read_text()),('outside_write',lambda:(private/'blocked.txt').write_text('test')),('direct_socket',lambda:socket.create_connection(('127.0.0.1',51105),timeout=2).close())]:
 try: action();r[label]={'allowed':True}
 except Exception as e:r[label]={'allowed':False,'error':type(e).__name__,'winerror':getattr(e,'winerror',None)}
print(json.dumps(r))

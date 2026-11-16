import json,math,sys,glob
base=sys.argv[1]
def show(path,sel):
    d=json.load(open(path))
    for c in sel(d):
        k=c.get('capacity',c.get('k')); r=c.get('radius')
        if r: 
            x=r[0]/r[1]; print(path.split('/')[-1],k,"radius",x,"c=k*(x*e-1)=",k*(x*math.e-1))
show(base+'/rc9aee43/certificates-121-160.json', lambda d:[c for c in (d if isinstance(d,list) else d.get('columns',d.get('certificates',[]))) if c.get('capacity',c.get('k')) in (121,160)])
show(base+'/rc9aee43/ext-443-500.json', lambda d:[c for c in (d if isinstance(d,list) else d.get('columns',d.get('results',[]))) if c.get('capacity',c.get('k')) in (491,495,500)])

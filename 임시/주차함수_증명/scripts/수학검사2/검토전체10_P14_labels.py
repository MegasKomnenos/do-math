import re,glob,os,io,sys
base=r"C:\math\임시\주차함수_증명\장v2"
files=sorted(glob.glob(os.path.join(base,"*.md")))
heads={}
for f in files:
    txt=io.open(f,encoding='utf-8').read()
    for m in re.finditer(r'^\*\*(정리|보조정리|명제|정의|따름정리|관찰|가설|예|주의|약속|사실|추측) \{\{([^}]+)\}\}',txt,re.M):
        heads.setdefault(m.group(2),[]).append((os.path.basename(f),m.group(1)))
    for m in re.finditer(r'\{\{([^}]+)\}\}',txt):
        pass
print(len(heads))
for k,v in sorted(heads.items()):
    print(k,v)

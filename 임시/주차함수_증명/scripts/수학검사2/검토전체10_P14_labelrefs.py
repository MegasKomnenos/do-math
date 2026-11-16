import re,glob,os,io
base=r"C:\math\임시\주차함수_증명"
heads=set()
for f in glob.glob(os.path.join(base,"장v2","*.md")):
    txt=io.open(f,encoding='utf-8').read()
    for m in re.finditer(r'^\*\*(?:정리|보조정리|명제|정의|따름정리|관찰|가설|예|주의|약속|사실|추측) \{\{([^}]+)\}\}',txt,re.M):
        heads.add(m.group(1))
for fn in ["장부_v2.md","구조표_v2.md","의존지도_v2.md"]:
    txt=io.open(os.path.join(base,fn),encoding='utf-8').read().split('\n')
    print("==",fn)
    for i,l in enumerate(txt,1):
        for m in re.finditer(r'\{\{([^}]+)\}\}',l):
            lab=m.group(1)
            if lab not in heads:
                print(i,lab)

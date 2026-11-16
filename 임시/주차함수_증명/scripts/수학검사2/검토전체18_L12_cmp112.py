# L12 검산: 부록 D(장2–장6) 항목의 독립 재계산 줄·산술 등급·확인하는 진술을 11.2절 표의 행과 글자 단위로 견준다.
import re,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
root="C:/math/임시/주차함수_증명/장v2/"
items={}
for f in ["부록D_장2.md","부록D_장3.md","부록D_장4.md","부록D_장5A.md","부록D_장5B.md","부록D_장6.md"]:
    txt=open(root+f,encoding='utf-8').read()
    for blk in re.split(r'\n(?=### D\.)',txt):
        m=re.match(r'### D\.\{\{D:([^}]+)\}\} (.*)',blk)
        if not m: continue
        lab=m.group(1); head=m.group(2)
        stm=re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$',head.strip())
        rec=re.search(r'\*\*독립 재계산\.\*\* (.*)',blk)
        grade=re.search(r'\*\*산술 등급\.\*\* (.*)',blk)
        items[lab]=dict(file=f,stmt=stm.group(1) if stm else None,recalc=rec.group(1).strip() if rec else None,grade=grade.group(1).strip() if grade else None)
rows={}
for line in open(root+"장11.md",encoding='utf-8'):
    m=re.match(r'\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*) \|\s*$',line)
    if m: rows[m.group(1)]=m.groups()[1:]
for lab,it in items.items():
    print("==",lab,it['file'])
    if lab not in rows: print("  !! 11.2 표에 행 없음"); continue
    stmt,grade,loc,br,desc=rows[lab]
    if it['stmt']!=stmt: print("  진술 D:",it['stmt'],"\n  진술 11.2:",stmt)
    g=it['grade'] or ''
    print("  등급 D:",g[:90]); print("  등급 11.2:",grade,"| 위치",loc)
    r=it['recalc'] or ''
    mm=re.match(r'(〔.*?〕)\s*(.*)',r)
    if not mm: print("  !! D 독립 재계산 줄에 꺾쇠 없음"); continue
    dbr,ddesc=mm.groups()
    if dbr!=br: print("  꺾쇠 D   :",dbr,"\n  꺾쇠 11.2:",br)
    dd=ddesc.replace("이 문단 머리의 꺾쇠 괄호","「재계산」 열의 꺾쇠 괄호")
    if dd!=desc:
        import difflib
        print("  !! 서술 다름:")
        for op in difflib.SequenceMatcher(None,dd,desc).get_opcodes():
            if op[0]!='equal': print("    ",op[0],"D:",repr(dd[op[1]:op[2]]),"11.2:",repr(desc[op[3]:op[4]]))
print("11.2 행 가운데 D(장2–6)에 없는 것:",[k for k in rows if k not in items])

# 장1·장2가 인용한 라벨 {{장:이름}}마다, 그 장 파일에서 정의되는 진술 머리의 종류(정리/명제/보조정리/따름정리/정의)와
# 인용문에 붙은 종류 낱말이 맞는지 기계적으로 대조한다. (고정 문자열 비교)
import re,glob,os,sys
base='장v2'
files=glob.glob(base+'/*.md')
defs={}
hdr=re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의|문제) \{\{([^}]+)\}\}')
for f in files:
    for ln,line in enumerate(open(f,encoding='utf-8'),1):
        m=hdr.match(line)
        if m: defs.setdefault(m.group(2),[]).append((m.group(1),os.path.basename(f),ln))
cite=re.compile(r'(정리|명제|보조정리|따름정리|정의)?\s*\{\{([0-9A-Za-z]+:[^}]+)\}\}')
for target in ('장v2/장1.md','장v2/장2.md'):
    for ln,line in enumerate(open(target,encoding='utf-8'),1):
        if hdr.match(line):
            # skip own header label but check remaining cites on the line
            pass
        for m in cite.finditer(line):
            kind,lab=m.group(1),m.group(2)
            if lab.startswith('D:'): continue
            if lab not in defs:
                print(f"{target}:{ln}: 라벨 미정의 {lab}"); continue
            kinds={d[0] for d in defs[lab]}
            if kind and kind not in kinds:
                # could be 'A·B' list where kind word precedes earlier label; report
                print(f"{target}:{ln}: 종류 불일치? 인용 '{kind}' vs 정의 {defs[lab]} 라벨 {lab}")
print("defs count",len(defs))

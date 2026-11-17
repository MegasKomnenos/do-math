# 검토 23차 R1: 1·2장의 진술이 가진 부분 표지((가)…/(ㄱ)…)와, 모든 장 파일에서 그 진술을 부분 표지로 부르는 자리의 맞춤
import re,glob,io,sys
sys.stdout.reconfigure(encoding='utf-8')
files=sorted(x.replace(chr(92),'/') for x in glob.glob('장v2/*.md'))
text={f:io.open(f,encoding='utf-8').read().split('\n') for f in files}
head=re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s*\{\{([^}]+)\}\}')
parts={}
for f in ['장v2/장1.md','장v2/장2.md']:
    L=text[f]
    i=0
    while i<len(L):
        m=head.match(L[i])
        if m and '의 증명' not in L[i][:60]:
            lab=m.group(2); body=[L[i]]; j=i+1
            while j<len(L) and not L[j].startswith('**증명') and not head.match(L[j]) and not L[j].startswith('#'):
                body.append(L[j]); j+=1
            b='\n'.join(body)
            ps=set(re.findall(r'(?:(?<=[\s.])|^)\(([가나다라마바사아자차ㄱㄴㄷㄹㅁㅂㅅㅇ])\)',b,flags=re.M))
            parts[lab]=ps
            i=j
        else: i+=1
cite=re.compile(r'\{\{([^}]+)\}\}((?:\([가-힣ㄱ-ㅎ]\))+)')
bad=0
for f in files:
    for n,line in enumerate(text[f],1):
        for m in cite.finditer(line):
            lab=m.group(1)
            if lab in parts:
                for pch in re.findall(r'\(([가-힣ㄱ-ㅎ])\)',m.group(2)):
                    if pch not in parts[lab]:
                        bad+=1; print('MISMATCH',f,n,lab,pch,'has',sorted(parts[lab]))
for lab,ps in parts.items():
    if ps: print(lab,''.join(sorted(ps)))
print('bad',bad)

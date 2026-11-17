# -*- coding: utf-8 -*-
# 5절 셋째 열의 낱말마다 그 장의 파일(본문과 딸린 부록 D)에 고정 문자열로 있는지 센다. 0건만 후보로 찍는다.
# 조사·활용으로 꼴이 달라지는 낱말(「엄격히 증가한다」 등)은 줄기 몇 글자로도 다시 센다. 판단은 원문으로 한다.
import sys, io, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
def load(n,p):
    spec = importlib.util.spec_from_file_location(n,p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
t12 = load('t12','scripts/수학검사2/검토전체25_R13e_표12.py'); C = load('c','scripts/수학검사2/검토전체25_R13e_공통.py')
TXT = {ch: '\n'.join(io.open('장v2/%s.md'%f,encoding='utf-8').read() for f in fs) for ch,fs in C.FILES.items()}
ALL = '\n'.join(TXT.values())
for ln,c in t12.table(1191,1200):
    ch=int(c[0])
    for entry in c[2].split(';'):
        for w in re.split(r',|:', entry):
            w=w.strip()
            w=re.sub(r'\(.*?\)','',w).strip()
            if not w: continue
            n=TXT[ch].count(w)
            if n==0:
                # 띄어쓰기를 지운 꼴과 앞 줄기
                n2=TXT[ch].replace(' ','').count(w.replace(' ',''))
                stem=w[:max(2,len(w)-2)]
                print('장 %d 「%s」: 그 장 0건 (띄어쓰기 무시 %d건, 줄기 「%s」 %d건, 글 전체 %d건)'%(ch,w,n2,stem,TXT[ch].count(stem),ALL.count(w)))

# -*- coding: utf-8 -*-
# 쓰임: python -I 맨글자.py <바탕 글자> [장 번호 …]   (환경변수 없이; 꼴 수는 12개까지)
# 글자체 명령의 인수를 지운 뒤 수식 안에 남는 맨 이탤릭 글자의 꼴(글자와 그 뒤 3자)을 파일별로 센다.
# 여러 줄 $$…$$ 도 본다(공통 모듈).
import sys, io, re, collections, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('common','scripts/수학검사2/검토전체25_R13e_공통.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
BS=C.BS
base = sys.argv[1]
chs = [int(x) for x in sys.argv[2:]] or list(range(1,11))
if base.startswith(BS): pat = re.escape(base)+r'(?![A-Za-z])'
else: pat = r'(?<![A-Za-z'+re.escape(BS)+r'])'+re.escape(base)+r'(?![A-Za-z])'
for ch in chs:
    for f in C.FILES[ch]:
        cnt=collections.Counter(); first={}
        for i,sg in C.segments(f):
            t=C.strip_fonts(sg).replace('\n',' ')
            for m in re.finditer(pat,t):
                key=t[m.start():m.end()+3]
                cnt[key]+=1; first.setdefault(key,(i,t[max(0,m.start()-3):m.end()+12]))
        if cnt:
            print('%s: %d건 — %s'%(f,sum(cnt.values()), '; '.join('%s×%d(행 %d: %s)'%(k,v,first[k][0],first[k][1]) for k,v in cnt.most_common(12))))

# -*- coding: utf-8 -*-
# 쓰임: python -I 수식검색.py <방식 F|R> <패턴> [꼴너비] [파일 접두 …]
# 장 파일·부록의 수식($…$, 여러 줄 $$…$$) 안에서 패턴(F=고정 문자열, R=정규식)을 찾아 파일별 건수와 꼴을 센다.
import sys, io, re, glob, os, collections, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('common','scripts/수학검사2/검토전체25_R13e_공통.py')
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
mode, pat = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv)>3 else 14
pref = sys.argv[4:]
files = sorted(os.path.basename(f)[:-3] for f in glob.glob('장v2/*.md'))
if pref: files=[f for f in files if any(f.startswith(p) for p in pref)]
rx = re.compile(re.escape(pat) if mode=='F' else pat)
for f in files:
    cnt = collections.Counter(); first={}
    for i,sg in C.segments(f):
        sg=sg.replace('\n',' ')
        for m in rx.finditer(sg):
            form = sg[max(0,m.start()-4):m.end()+w]
            cnt[form]+=1; first.setdefault(form,i)
    if cnt:
        print('%s: %d건'%(f,sum(cnt.values())))
        for form,k in cnt.most_common(12):
            print('    %3d  %s   (첫 행 %d)'%(k,form,first[form]))

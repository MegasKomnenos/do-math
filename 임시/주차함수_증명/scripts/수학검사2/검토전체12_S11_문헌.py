# S11: 11.4절 문헌 표의 「쓰인 자리」를 본문·부록 D의 저자 이름 등장 자리(진술 문맥)와 견준다.
import re, io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
HDR = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의|관찰)\s+\{\{(\d+[AB]?:[^}]+)\}\}(?!의 증명)')
authors = ['Konheim','Foata','Pollak','Celano','Aguilar','Stanley','Knuth','Flajolet','Tanner','Robbins','Petersson','Janson','Ibragimov','Ahlfors','Graham','Patashnik','Fortuin','FKG','Jensen','Wallis','Corless','Lambert','Grimmett','Harris','Comtet','Faà','Apostol','Titchmarsh','Euler','Cauchy','편각 원리','표준']
import os
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10'] + [os.path.basename(f)[:-3] for f in sorted(glob.glob('장v2/부록D_*.md'))]
for a in authors:
    print('\n#####', a)
    for ch in files:
        sec = None; ctx = ('머리', None)
        for ln, line in enumerate(open(f'장v2/{ch}.md', encoding='utf-8'), 1):
            m = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)', line)
            if m: sec = m.group(2); ctx = ('절', sec)
            m2 = re.match(r'^### D\.\{\{D:([^}]+)\}\}', line)
            if m2: ctx = ('D', m2.group(1))
            h = HDR.match(line)
            if h: ctx = (h.group(1), h.group(2))
            elif re.match(r'^\*\*.*증명', line) and ctx[1]: ctx = ('증명', ctx[1])
            if a in line:
                for mm in re.finditer(re.escape(a), line):
                    s0 = max(0, mm.start()-60); e0 = min(len(line), mm.end()+60)
                    print(f'  {ch}:{ln} §{sec} [{ctx[0]} {ctx[1]}] …{line[s0:e0].strip()}…')
            if '∎' in line and ctx[0] == '증명': ctx = ('뒤', ctx[1])

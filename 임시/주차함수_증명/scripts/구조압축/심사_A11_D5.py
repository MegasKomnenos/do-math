# -*- coding: utf-8 -*-
"""D5: 「…의 증명에서 보았듯」류 인용(다른 진술의 '증명'을 근거로 끌어 쓰는 자리) 전수 수집.
패턴 여럿을 써서 누락을 줄이고, 각 자리에 (파일, 행, 둘러싼 진술 라벨, 인용된 라벨, 문장)을 적는다.
"""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
files = sorted(glob.glob(os.path.join(ROOT, '장v2', '장*.md')), key=lambda p: (len(os.path.basename(p)), p))
files += sorted(glob.glob(os.path.join(ROOT, '장v2', '부록*.md')))
HEAD = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의)\s+(\{\{[^}]+\}\})')
LAB = re.compile(r'\{\{([^}]+)\}\}')
# 핵심 패턴: 「<종류> {{라벨}}(항목)?의 증명<조사>」 — 이어지는 말로 '근거로 쓰는' 쓰임을 가른다
P_MAIN = re.compile(r'(정리|보조정리|명제|따름정리)\s+\{\{([^}]+)\}\}((?:\([가-힣ㄱ-ㅎ0-9a-z]+\))?(?:·\([가-힣ㄱ-ㅎ]\))*)의 증명(?!됨)([^.。]{0,40})')
# 보조 패턴: 라벨 없이 '그 증명', '위 증명', '같은 증명', '앞의 증명' + 근거 동사
P_AUX = re.compile(r'(그|위|같은|앞의|이) 증명(에서|이|은|의|안|에)([^.。]{0,30})')
# 식 번호로 증명 안의 식을 부르는 자리: 「(6.2)」꼴은 따로 세지 않음(진술 밖 식 번호는 설계된 인용)
VERBS = ['보았', '본 ', '보인', '보였', '세운', '세웠', '얻은', '얻었', '적은', '적었', '밝힌', '밝혔', '쓴 ', '썼', '유도', '정의한', '정의했', '도입', '잡은', '둔 ', '두었', '구한', '구했', '준 ', '주었', '따르', '처럼', '같이', '대로', '그대로', '되풀이', '반복', '거쳐', '따라', '쓰면', '쓰듯', '쓴다', '쓴 것', '한 ', '했', '같은 ', '동일', '마찬가지', '항등식', '식 (', '단계', '첫째', '둘째', '셋째', '넷째', '안의', '안에서', '안에', '에서 ']
def classify(tail):
    t = tail
    if re.match(r'\s*(을|를)\s*(마친다|끝낸다|닫는다|완성|마무리)', t): return 'own-proof-close'
    return 'cite'
out = []
tot = 0
for f in files:
    name = os.path.basename(f)
    lines = open(f, encoding='utf-8').read().split('\n')
    cur = None
    for i, ln in enumerate(lines, 1):
        m = HEAD.match(ln)
        if m:
            cur = m.group(2)
        for mm in P_MAIN.finditer(ln):
            kind, lab, item, tail = mm.group(1), mm.group(2), mm.group(3), mm.group(4)
            # 자기 증명 안에서 '정리 X의 증명을 마친다' 류는 제외
            if cur and ('{{'+lab+'}}') == cur and re.match(r'\s*(을|를|이|은)\s*(마친다|끝낸다|닫는다|완성|마무리|끝|마친|시작|여기서)', tail):
                continue
            # 머리 표지 안의 「…의 증명에 의존」은 제외(1.5절 규약의 덧붙임)
            if HEAD.match(ln) and ('의존' in tail[:12]):
                continue
            s = max(0, mm.start()-60); e = min(len(ln), mm.end()+60)
            ctx = ln[s:e].replace('\n',' ')
            out.append((name, i, cur, lab+item, classify(tail), ctx))
            tot += 1
print('총', tot, '건')
from collections import Counter
print('파일별:', dict(Counter(o[0] for o in out)))
print('둘러싼 진술 수(라벨 기준):', len(set(o[2] for o in out)))
print('인용된 증명 수(라벨+항목 기준):', len(set(o[3] for o in out)))
print()
for o in out:
    print(f'{o[0]}:{o[1]} | 안: {o[2]} | 인용: {o[3]} | {o[4]} | …{o[5]}…')
print()
print('--- 보조 패턴(라벨 없는 「그/위/같은/앞의 증명…」) ---')
for f in files:
    name = os.path.basename(f)
    lines = open(f, encoding='utf-8').read().split('\n')
    for i, ln in enumerate(lines, 1):
        for mm in P_AUX.finditer(ln):
            s = max(0, mm.start()-70); e = min(len(ln), mm.end()+40)
            print(f'{name}:{i} | …{ln[s:e]}…')

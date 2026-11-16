# -*- coding: utf-8 -*-
"""I14: (1) 7절 첫 열 글자가 1.1/1.2에 있는가, (2) 3절 낱말의 첫 정의 절 앞 사용, (3) 금지·폐기 낱말, (4) 영어 병기 횟수."""
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
L = open(os.path.join(ROOT,'장부_v2.md'),encoding='utf-8').read().split('\n')
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
sec_re = re.compile(r'^###\s+(\d+\.\d+)')
# 장 파일을 (절, 행, 텍스트) 열로
seq = []
for ch in order:
    sec = ch.replace('장','').rstrip('AB')+'.0'
    for i,l in enumerate(open(os.path.join(ROOT,'장v2',ch+'.md'),encoding='utf-8'),1):
        m = sec_re.match(l)
        if m: sec = m.group(1)
        seq.append((sec, ch, i, l))
def seckey(s):
    a,b = s.split('.'); return (int(a), int(b))

print("=== (1) 7절 첫 열의 글자가 1.1/1.2 글자 열에 있는가")
norm = lambda s: re.sub(r'\s+','',s)
g12 = set()
for i in list(range(28,42))+list(range(49,342)):
    cell = L[i-1].split(' | ')[0].lstrip('| ')
    for g in re.findall(r'\$([^$]+)\$', cell):
        for part in re.split(r',\s*', g):
            g12.add(norm(part))
    g12.add(norm(cell.strip('$')))
# 1.1의 글자 열은 "$N:=n-k$" 같은 꼴 → 바탕 글자만도 넣는다
g12 |= {'n','m','t','N','k','\\ell','y','Y','i','j','u','v','r','\\nu','d','q'}
notfound = []
for i in range(1237,1440):
    l = L[i-1]
    if not l.startswith('| $') and not l.startswith('| ('): continue
    cell = l.split(' | ')[0].lstrip('| ')
    for g in re.findall(r'\$([^$]+)\$', cell):
        for part in re.split(r',\s*(?=[\\A-Za-z(])', g):
            p = norm(part)
            # 인수를 뗀 꼴도 허용
            p0 = re.sub(r'\([^()]*\)$','',p)
            ok = any(x==p or x==p0 or x.startswith(p0+'(') or x.startswith(p0+',') or (p0 and p0 in x and len(p0)>=3) for x in g12)
            if not ok: notfound.append((i, part.strip()))
for i,p in notfound: print(f"  행{i}: {p}")
print("  (7절 첫 열 글자 가운데 1.1/1.2에서 찾지 못한 것 수:", len(notfound), ")")

print("\n=== (2) 3절 낱말: 선언된 첫 정의 절보다 앞에 나타나는 자리 (1.4·1.5 제외)")
words = []
for i in range(509,724):
    l = L[i-1]
    m = re.match(r'^\| ([^|]+) \| ([^|]*) \| ([^|]+) \| ([^|]*) \|', l)
    if not m: continue
    wcell, sec = m.group(1), m.group(3).strip()
    secs = re.findall(r'\d+\.\d+', sec)
    if not secs: continue
    first = min(secs, key=seckey)
    for w in re.split(r',\s*', wcell):
        w = re.sub(r'\$[^$]*\$','',w).strip()
        w = re.sub(r'\(.*?\)','',w).strip()
        if len(w) < 2 or w in ('행','열','칸','몫','틈','홈','핵','띠','층','자리','위치','좌표','수열','수준','경계','무게','질량','결손','초과','꼬리','걸음','단계','조립','흡수','착지','생존','문턱','조각','상자','셀','덮개','격자','가족','머묾','갱신','보행','다리','사슬','연쇄','환경','봉투','배치','지위','식별자','표지','함의','동치','검사','고리','면적','캡','깊이','형제','꺾인 무게','벌크','감사','극','줄기','이득','손실','반례','단봉','증인','봉우리','고원','상한·하한','상단·하단','개수열','토막','얼린','기울임','평평한','되먹임','상위해','타일','유색','무색','껍질','바닥','쿠션','조화수','자유 비','원 비교','선도항','주항','동률','막힘','임계점','최빈점','해싱 극한','위치쌍','횡단','경계 응답','이음 행','기저량','떠돌기','방문 확률'):
            continue
        words.append((i, w, first))
for i,w,first in words:
    hits = [(s,ch,ln) for (s,ch,ln,txt) in seq if w in txt]
    early = [(s,ch,ln) for (s,ch,ln) in hits if seckey(s) < seckey(first) and s not in ('1.4','1.5')]
    if early:
        print(f"  행{i} 「{w}」 선언 {first} ← 앞선 자리: {early[:4]}{' …' if len(early)>4 else ''}")

print("\n=== (3) 금지·폐기 낱말의 출현(장부 3절 「첫 판의 낱말」·8절 규칙 4)")
banned = ['마디','뿌리 문제','뿌리 명제','공표','노드','프런티어','생산자','peer','인스턴스','운영자','블록','조각남','조각나','체류','순증가','강단봉','윤곽 함수','멈춤 확률','멈출 확률','환경 무게','갱신 창','층 구조','층층','창 행','넓은 창','중앙 증가','중앙 비교','원천 질량','머묾 이득','동반 숲','나머지 숲','선호 목록','보증 수준','골격 수준','초과 수준','자르는 자리','미달 수','열 값','점질량','두 이웃 수준','수준 확률','나무 차분','나무 행 차분','허용 숲 수','창 질량','핵 질량','포착된','표지','세션','검토','칸 하계','거대 블록','평평한 핵 ','영차 모멘트','핵심 조건']
for b in banned:
    hits = [(ch,ln,txt.strip()[:0]) for (s,ch,ln,txt) in seq if b in txt]
    if hits:
        chs = {}
        for ch,ln,_ in hits: chs.setdefault(ch,[]).append(ln)
        print(f"  「{b}」: " + '; '.join(f"{c}:{v[:5]}{'…' if len(v)>5 else ''}" for c,v in chs.items()))

print("\n=== (4) 영어 병기 출현 횟수(8절 규칙 8: 첫 정의 자리에 한 번)")
for e in ['random walk','ladder epoch','size-biased','renewal function','critical Boltzmann law','h-transform','hitting time','linear probing','parking function','unimodal','log-concave','exponential formula','Borel–Tanner','Fortuin','Fekete']:
    hits = [(ch,ln) for (s,ch,ln,txt) in seq if e in txt]
    print(f"  {e}: {len(hits)} {hits[:6]}")

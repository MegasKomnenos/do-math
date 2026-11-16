# P7a: 식 번호 「(a.b)」 바로 뒤 조사가 끝 숫자의 읽기와 맞는지 센다(조립기의 라벨 규칙과 같은 읽기).
import re, glob, io, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
bat={'0':'ㅂ','1':'ㄹ','2':'','3':'ㅁ','4':'','5':'','6':'ㄱ','7':'ㄹ','8':'ㄹ','9':''}
pairs={'은':'는','는':'은','이':'가','가':'이','을':'를','를':'을','과':'와','와':'과'}
rx=re.compile(r"\((\d+\.\d*(\d))\)(으로|이다|이라|이고|이며|이면|이나|은|는|이|가|을|를|과|와|로|다|라|고|며|면|나)(?=$|[^가-힣])")
tot=0
for f in sorted(glob.glob(os.path.join(ROOT,'장v2','*.md'))):
    bad=[]
    for i,ln in enumerate(io.open(f,encoding='utf-8'),1):
        for m in rx.finditer(ln):
            b=bat[m.group(2)]; p=m.group(3)
            if p in ('은','이','을','과'): want=p if b else pairs[p]
            elif p in ('는','가','를','와'): want=p if not b else pairs[p]
            elif p=='으로': want='으로' if (b and b!='ㄹ') else '로'
            elif p=='로': want='로' if (not b or b=='ㄹ') else '으로'
            elif p.startswith('이') and len(p)==2: want=p if b else p[1:]
            elif p in ('다','라','고','며','면','나'): want=p if not b else '이'+p
            else: continue
            if want!=p: bad.append((i,m.group(0),want))
    if bad:
        tot+=len(bad); print(os.path.basename(f),len(bad),bad[:12])
print('총',tot)

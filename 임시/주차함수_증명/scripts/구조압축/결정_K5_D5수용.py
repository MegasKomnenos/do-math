# -*- coding: utf-8 -*-
"""결정 K5 검산 2 — D5 수용 검사. 장1–장10에서 「<종류> {{라벨}}(항목)?의 증명」 인용(증명 머리·자기 증명 마무리 제외)과
대명사형(「그/위/같은/앞의 증명에서 보았듯」) 실질 인용을 세고, 허용 목록(C류: 전방 안내·순환 없음 설명)에 없는 자리를 보고한다.
수리 뒤 다시 돌려 「허용 밖 0건」이면 통과. 사용: python -I 결정_K5_D5수용.py [--list]  (출력 결정_K5_D5수용_out.txt)"""
import re, os, io, sys
ROOT = r'C:\math\임시\주차함수_증명'
OUT = os.path.join(ROOT, 'scripts', '구조압축', '결정_K5_D5수용_out.txt')
FILES = ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md']  # 9장 제거 뒤(옛 10장=9장; 보증 10장은 증명 없음)
HEAD = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의)\s+(\{\{[^}]+\}\})')
A = re.compile(r'(정리|보조정리|명제|따름정리)\s+\{\{([^}]+)\}\}((?:\([가-힣ㄱ-ㅎ0-9a-z]+\))?(?:·\([가-힣ㄱ-ㅎ]\))*)의 증명(?!됨)')
B = re.compile(r'(그|위|같은|앞의|이)\s*증명(에서|이|을|의)\s*(보았듯|보인|쓴|적은|세운|따르|그대로)')
# 허용(C류): 숙주 라벨 또는 산문 자리(파일:행)와 인용 라벨의 쌍. 수리 뒤 남아도 되는 「안내」 문장만 적는다.
ALLOW = {
    ('장2.md', '2:old-2-20'),      # 2.5절 산문: 「이 식은 아래 명제의 증명에 쓰인다」 전방 안내(D1 2장 쪽이 2.21을 지우면 함께 사라진다)
    ('장5A.md', '5:old-5-4'),      # 5.2 산문: Newton 인증 안내(C2 채택 시 소멸)
    ('장6.md', '5:old-5-18'),      # 6장 머리·6.3 산문: 의존 안내·순환 없음 설명
    ('장8.md', '8:old-6-28'),      # 8.2 산문: 가정을 8.19(가)로 채운다는 안내
}
rows = []
for f in FILES:
    lines = io.open(os.path.join(ROOT, '장v2', f), encoding='utf-8').read().split('\n'); cur = None
    for i, ln in enumerate(lines, 1):
        m = HEAD.match(ln)
        if m: cur = m.group(2)
        for mm in A.finditer(ln):
            lab = mm.group(2)
            if ln[mm.end():mm.end()+6].startswith('.**'):
                continue  # 증명 머리
            if cur and '{{'+lab+'}}' == cur and re.match(r'\s*(을|를)\s*(마친다|끝낸다|닫는다|완성|마무리)', ln[mm.end():]):
                continue  # 자기 증명 마무리
            rows.append(('A', f, i, cur or '-', lab + mm.group(3), ln[max(0, mm.start()-80):mm.end()+80]))
        for mm in B.finditer(ln):
            rows.append(('B', f, i, cur or '-', '?', ln[max(0, mm.start()-80):mm.end()+80]))
outl = []
a_rows = [r for r in rows if r[0] == 'A']; b_rows = [r for r in rows if r[0] == 'B']
viol = [r for r in a_rows if (r[1], r[4].split('(')[0]) not in ALLOW]
outl.append(f'A형(라벨 명시) {len(a_rows)}건 | 허용 목록 안 {len(a_rows)-len(viol)}건 | 허용 밖 {len(viol)}건 | 대명사형 후보 {len(b_rows)}건(손으로 가른다)')
outl.append('판정: ' + ('통과(허용 밖 0)' if not viol else '미통과'))
outl.append('\n## 허용 밖 A형')
for r in viol:
    outl.append(f'{r[1]}:{r[2]} | 숙주 {r[3]} | 인용 {r[4]}\n    …{r[5]}…')
outl.append('\n## 대명사형 후보(B형; 자기 증명 되가리킴이 대부분 — 실질 인용만 손으로 가른다)')
for r in b_rows:
    outl.append(f'{r[1]}:{r[2]} | 숙주 {r[3]}\n    …{r[5]}…')
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(outl) + '\n')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print('\n'.join(outl[:3]))
if '--list' in sys.argv: print('\n'.join(outl[3:]))

# -*- coding: utf-8 -*-
"""외부 피드백 넷째 묶음 A(장1234) — ZV9의 자리 확인 검산(읽기 전용).

항목마다 현행 장 파일에서 「전」 문구(첫째 단계) 또는 「후」 문구(둘째 단계)를 고정 문자열로
찾아 행 번호를 적고, 바꾸는 토큰이 저장소의 장 파일·장부·구조표·부록에 몇 번 남는지를 센다.
실행: python -I scripts/수학검사2/검토_외부피드백_1116_ZV9_자리확인.py [--after]
"""
import sys, io, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AFTER = '--after' in sys.argv

def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8', newline='') as f:
        return f.read()

def find_lines(text, needle):
    return [i + 1 for i, l in enumerate(text.split('\n')) if needle in l]

# 항목: (번호, 파일, 전 문구, 후 문구 또는 None(둠))
ITEMS = [
    ('A1 2.4 증명 표지', '장v2/장2.md',
     '섬유들은 $\\mathrm{PF}_n$을 겹치지 않게 나누고, 섬유별 개수를 $\\sigma$에 대해 더하면 누적 개수가 된다.',
     '**증명.** 섬유들이 $\\mathrm{PF}_n$을 겹치지 않게 나누므로'),
    ('A1 2.4 견줌 문장(둠)', '장v2/장2.md',
     '정리 {{2:old-2-3}}과 따름정리 {{2:old-2-4}}의 공식은 문제의 원 논문', None),
    ('A2 2.18 증명 첫 문장', '장v2/장2.md',
     '**증명.** 섬유의 크기가 $\\prod_ih_i$이므로, 균등 주차함수의 결과 순열은',
     '**증명.** 정리 {{2:old-2-3}}에 따라 섬유의 크기가 $\\prod_ih_i$이므로, 균등 주차함수의 결과 순열은'),
    ('A3 2.29 증명 첫 문장', '장v2/장2.md',
     '모든 차가 문턱 자리에 있는 주차함수를 세면, 용량이 $k$보다 작은 자리는 $h_i$가지',
     '모든 차가 문턱 자리에 있는 주차함수를 정리 {{2:old-2-3}}의 곱 구조로 세면, 용량이 $k$보다 작은 자리는 $h_i$가지'),
    ('A3 2.7절 준비 문단(둠)', '장v2/장2.md',
     '정리 {{2:old-2-3}}에 따라 자리 $i$에 선 차의 변위 $d_{\\sigma_i}$는 $h_i-1$까지만 가능하므로', None),
    ('A4 2.51 (가) 903', '장v2/장2.md',
     '지정 사슬 정리의 (가)에 있는 수에 $t=n-r$을 넣으면',
     '정리 {{2:chain-expansion}}(가)의 수에 $t=n-r$을 넣으면'),
    ('A4 2.51 (라) 909', '장v2/장2.md',
     '둘째 식은 지정 사슬 정리 (나)의 수를 풀어 쓴 것이다.',
     '둘째 식은 정리 {{2:chain-expansion}}(나)의 수를 풀어 쓴 것이다.'),
    ('A5 2.44 정의 차용(둠)', '장v2/장2.md',
     '을 정리 {{2:old-2-40}}의 식으로 모든 $n\\ge1$에서 정의하면', None),
    ('A6 2.15 두 주장(둠) — 2.36이 쓰는 자리', '장v2/장2.md',
     '보조정리 {{2:old-2-14}}의 분해 $\\mathfrak v_k(Z,H)=', None),
    ('A7 2.9절 준비 문단(둠)', '장v2/장2.md',
     '정리 {{2:old-2-11}} 뒤의 표현에 따라 $M^T_t$는', None),
    ('A8 지수 공식 145(둠)', '장v2/장2.md',
     '정리 {{2:old-2-10}}에 따라 허용 숲의 지수 생성함수는 $A_\\ell$이므로 지수 공식은', None),
    ('A8 지수 공식 691(둠)', '장v2/장2.md',
     '과 지수 공식 $A_\\ell=\\exp T_\\ell$을 세 수준', None),
    ('A8 지수 공식 728(둠)', '장v2/장2.md',
     '**증명.** $A_k=A_{k-1}e^{\\mathcal B_k}$, $A_{k-2}=A_{k-1}e^{-\\mathcal B_{k-1}}$이므로', None),
    ('A9 4.10 Bor 이웃비', '장v2/장4.md',
     '$\\mathrm{Bor}(j+1)/\\mathrm{Bor}(j)=e^{-1}(1+1/j)^{j-1}$이므로',
     '보조정리 {{2:old-2-26}}(나)에서 $\\mathrm{Bor}(j+1)/\\mathrm{Bor}(j)=e^{g(j)-1}=e^{-1}(1+1/j)^{j-1}$이므로'),
    ('A3′ 2.29 따름정리 증명 표지', '장v2/장2.md',
     '이고, $j\\ge2$ 항을 버리면 한 칸 차분의 하계가 나온다.',
     '**증명.** 위의 전개에서 $j=1$ 항이 $e_n=2E2_{n,k}$이고'),
    # 셋째 단계(ZV14 묶음 F 4번 (c)안을 받음): 보조정리 old-2-45(2.47)에 걸음 수를 고정한 식
    ('F4 2.47 진술(걸음 수 고정 식)', '장v2/장2.md',
     '마르코프 사슬이다. 초과 $1\\le q<q_0$에 대해',
     '\\Pr^y(q_i=q)=\\mathrm{tilt}_{q_0}(q)\\,\\mathrm{Bor}^{*i}(q_0-q),\\qquad \\Pr^y('),
    ('F4 2.47 증명(첫 식 구절)', '장v2/장2.md',
     '곧 $\\mathrm{Bor}^{*i}(q_0-q)$이고, $i$에 대해 더하면',
     '이것이 걸음 수 $i$를 고정한 첫 식이고, $i$에 대해 더하면'),
]

print('모드:', '둘째 단계(후 문구)' if AFTER else '첫째 단계(전 문구)')
bad = 0
for name, rel, before, after in ITEMS:
    text = read(rel)
    needle = (after if (AFTER and after) else before)
    lines = find_lines(text, needle)
    tag = '후' if (AFTER and after) else '전'
    status = 'OK' if lines else 'NOT FOUND'
    if not lines:
        bad += 1
    print(f'{name:40s} {rel:14s} {tag} 행={lines} {status}')
    if AFTER and after:
        stale = find_lines(text, before)
        if stale:
            print(f'  !! 전 문구가 남아 있음: 행={stale}')
            bad += 1

# 토큰 전수(고정 문자열)
SCOPE = sorted(glob.glob(os.path.join(ROOT, '장v2', '장*.md'))) + [
    os.path.join(ROOT, p) for p in ('장부_v2.md', '구조표_v2.md', '장v2/부록A.md', '장v2/부록C.md')]
TOKENS = ['지정 사슬 정리', '{{2:old-2-3}}', '{{2:old-2-26}}(나)', '{{2:chain-expansion}}(가)', '{{2:chain-expansion}}(나)']
print('\n토큰 전수(장v2/장*.md·장부·구조표·부록A·C; 고정 문자열):')
for tok in TOKENS:
    total = 0
    where = []
    for p in SCOPE:
        with open(p, encoding='utf-8', newline='') as f:
            t = f.read()
        c = t.count(tok)
        if c:
            total += c
            where.append(f'{os.path.relpath(p, ROOT)}:{c}')
    print(f'  {tok!r}: {total}  ({", ".join(where)})')

# 줄 끝 검사(LF만인지)
for rel in ('장v2/장2.md', '장v2/장4.md'):
    raw = open(os.path.join(ROOT, rel), 'rb').read()
    crlf = raw.count(b'\r\n'); lf = raw.count(b'\n')
    print(f'{rel}: CRLF {crlf}개, LF {lf}개, 바이트 {len(raw)}')

sys.exit(1 if bad else 0)

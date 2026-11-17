# -*- coding: utf-8 -*-
# R10: appendix C word table: does each "record term" occur in any record markdown / record.json?
# (locator: a zero hit is then confirmed by a second grep with spacing variants)
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(here, '..', '..')
rec = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
cited = set()
for line in io.open(os.path.join(root, '장v2', '부록B.md'), encoding='utf-8'):
    m = re.match(r'^\| (r[0-9a-f]{7}) \|.*`([^`]+)` \|$', line.rstrip())
    if m: cited.add(m.group(2))
texts_c = []; texts_all = []
tot = 0
for d in sorted(os.listdir(rec)):
    for dp, dn, fn in os.walk(os.path.join(rec, d)):
        for f in fn:
            if f.endswith('.md') or f == 'record.json':
                p = os.path.join(dp, f)
                try:
                    if os.path.getsize(p) > 3_000_000: continue
                    t = io.open(p, encoding='utf-8', errors='ignore').read()
                except Exception: continue
                tot += len(t)
                texts_all.append(t)
                if d in cited: texts_c.append(t)
print('chars loaded', tot, 'files', len(texts_all), 'cited files', len(texts_c))
big_all = '\n'.join(texts_all); big_c = '\n'.join(texts_c)
def nos(s): return re.sub(r'\s+', '', s)
big_all_n = nos(big_all); big_c_n = nos(big_c)
on = False
for i, line in enumerate(io.open(os.path.join(root, '장v2', '부록C.md'), encoding='utf-8'), 1):
    if line.startswith('### 낱말'): on = True; continue
    if line.startswith('### 기록이'): on = False
    if not on or not line.startswith('| ') or line.startswith('| 이 글의 용어') or line.startswith('|---'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    cell = c[1]
    # candidate terms: split by , ; and strip parentheticals and corner quotes
    cell2 = re.sub(r'\([^()]*\)', '', cell)
    parts = re.split(r'[,;]', cell2)
    terms = []
    for p in parts:
        p = p.strip()
        q = re.findall(r'「([^」]+)」', p)
        if q: terms.append(q[0])   # the record-side word is the first quoted one in "「A」는 「B」"
        elif p and not p.startswith('—') and p != '같음' and '$' not in p: terms.append(p)
    res = []
    for t in terms:
        tn = nos(t)
        if not tn: continue
        a = big_all_n.count(tn); cc = big_c_n.count(tn)
        if cc == 0: res.append('%s [cited:%d all:%d]' % (t, cc, a))
    if res: print('C%d %s | %s\n      -> %s' % (i, c[0], cell[:120], ' ; '.join(res)))
print('---- refined list (whitespace-insensitive counts: cited 75 records / all 350 records)')
lst = ["용량 구간 길이","초과 수준","골격 수준","골격 값","자리 이름","넷째 갈래","넓은 창","조각남","조각나","환경이 조각","미달 수","결손의 원천","살아남","열별 증가 문턱","증가 경계","반감 문턱","무거운 자리","가벼운 자리","무거운 환경","수준 위험률","구간 상한","구간 하한","뿌리 문제","뿌리 명제","Robbins 오차","자유 비","두 꼬리 정리","착지 창 열 값","가중 창 질량","보증 수준","층층 구조","층 구조","강단봉성","순증가","윤곽 함수","양측 경계","첫 층 블록","블록 나무","소인 블록","띠 전파","띠 비교","중앙 비교","중앙 증가","자르는 자리","자르는 크기","동반 숲","나머지 숲","상해","머묾 이득","꼭대기 이득","멈춤 확률","창 척도","노드 위치","결손 창","다섯 조각","두 조각 적분","네 조각","조건부 로그오목","꼭대기 자식","성장률","선호 목록","원천 질량","블록 원천","방법의 문턱","넘침","체류 법칙","체류 꼴","간격열","크기열","걸음열","톱니","빈틈","홈","구멍","환경 무게","source-wise comparison","두 꼬리","미달"]
for t in lst:
    tn = nos(t)
    print('%s: %d / %d' % (t, big_c_n.count(tn), big_all_n.count(tn)))
print('---- extra')
for t in ["source-wise","sourcewise","source comparison","source-comparison","원천별 비교","heavy path","heavy-path","supersolution","audit","core","Poisson 걸음","Borel 걸음","마디 SRC","SRC⁺","SRC+","(V)","끝점에서","관계","증인","창 맨 앞","미결","q-flq-relation","green-reconstruction","mode-formula-crosscheck","c-threshold-subtree","heavy-path-recurrence","convex-bonferroni","uniform-moving-tail","chain-normalization","exact-green-connection","positive-source-representation","source-comparison-implies-S","inverse-renewal-form","renewal-fkg","endpoint-comparison","colored-count-mean","doubly-marked-curvature","boundary-gain-lemma","matched-third-kernels","kernel-bounds","renewal-bounds","c-sharp","p-bulk-point-mass","prime-decomposition","exact-identities","fixed-bound","green-marker-majorant-all-n","rel-qstar-wlflat","c-ledger"]:
    tn = nos(t)
    print('%s: %d / %d' % (t, big_c_n.count(tn), big_all_n.count(tn)))
print('---- contexts')
import re as _re
for t in ["미달", "증가 문턱", "증가문턱", "자리 이름", "갈래", "열 값", "구간 길이"]:
    tn = t
    ms = [m.start() for m in _re.finditer(_re.escape(tn), big_all)]
    print('##', t, len(ms))
    seen = set()
    for p in ms[:400]:
        ctx = big_all[max(0, p-18):p+len(tn)+14].replace('\n', ' ')
        key = ctx[10:30]
        if key in seen: continue
        seen.add(key)
        if len(seen) <= 6: print('     …%s…' % ctx)

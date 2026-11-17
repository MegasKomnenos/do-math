# -*- coding: utf-8 -*-
# 수리 V6 — 늦게 온 계약 변경 4(W2·X1-1: 정리 `2:old-2-40` → 정의 「문턱 나무 손실과 줄기 이득」; FL_n·KD_n·PAIR_n·「다섯 몫」 소멸)와
#  뒤의 장 번호 치환에 대비한 「옛 9장」 표지(세션 알림): 장부·부록 A·C·구조표.
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
ROOT = os.path.join(HERE, '..', '..')
LEDGER = os.path.join(ROOT, '장부_v2.md')
A = os.path.join(ROOT, '장v2', '부록A.md')
C = os.path.join(ROOT, '장v2', '부록C.md')
S = os.path.join(ROOT, '구조표_v2.md')

KD_ROW = (r'| $\mathrm{KD}^\prime_n$ | KD·로마체 이름 | 둘째 층 크기의 자식에서 물려받는 상속 몫 $\mathrm{KD}^\prime_n=\sum_{m=2k+1}^{n-1}(k+n-m)\binom{n-1}mp_{n-1-m}d_{m,k}$'
          r'(정리 `{{7:old-6-21}}`의 항등식 $A_{n,k-1}(\star)(n)=d_{n,k}-\mathrm{KD}^\prime_n$의 항; 10장이 받아 쓴다) | 7.7 | 7, 10 | $KD^\prime_t$, $KD^\prime_n$(6.8·2023, 8.1·3103) | — |')
R6F_LEDGER = (r'| $\Theta_n$, $\mathrm{BV}_n$, $b^{(2)}_m$, $\delta_t$, $\mathcal U_k(m)$, $\mathfrak b_m$, $\tilde{\mathfrak a}_n$, $s_N(k)$, $\pi_n(m)$, $d_{m,k}$ | [r6f5f48f] §2–3 | '
              r'$\Theta_n$, $BV_n$(이탤릭), $b^+_m+b^-_m$, $\delta_s$, $U_k(L)$, $V_m$, $\tilde a_n=A_{n,k-1}e^{-n}/n!$, $s_N$, $\varpi_m(s)$, $d_m$ | '
              r'$\Theta_n$은 없음(확인), $\mathrm{BV}_n$은 로마체 이름(글자체); 글자(두 수준 개수); $s\to t$; $L\to m$; 글자체; 글자체(볼츠만판); 용량 인수 명시; $\varpi$를 쓰지 않음($m$은 숲 크기); 둘째 첨자 $k$ 명시 |')
R6F_C = R6F_LEDGER.replace('$\\Theta_n$은 없음(확인), ', '$\\Theta_n$은 없음, ')
CROSS_LEDGER = (r'| 교차항(정리 `{{2:tree-expansion}}`(가)의 두 합; 글자 없음) | [r2e22726]; [r05cf8c9], [rb6a2cd0] | 항등식 (3.1)의 두 나머지(글자 없음); $\mathcal X_n$ | '
                r'글자 없이 풀어 적음; $\mathcal X_n$은 $2k+1\le n\le3k-1$에서 이 두 합의 값(범위 명시) |')
CROSS_C = CROSS_LEDGER.replace('`{{2:tree-expansion}}`', '{{2:tree-expansion}}')

ops12 = [
    ('sub', r'| $b^{T}_{t,\ell}$ |', r'(다섯 몫의 계수 $u_s=b^T_{t,k}$, $v_s=b^T_{t,k-1}$)', ''),
    ('sub', r'| $\mathrm{BV}_n$ |', '줄기 이득(다섯 몫)', '줄기 이득(정의 `{{2:old-2-40}}`; 문턱 나무 손실 $\\Theta_n$과 견주는 양)'),
    ('del_row', r'| $\mathrm{FL}_n$ |'),
    ('del_row', r'| $\mathrm{PAIR}_n$ |'),
    ('set_row', r'| $\mathrm{KD}_n$ |', KD_ROW),
]
ops13 = [
    ('sub', r'| $\mathsf r^{\mathrm{thr}}_k=s_{2k}(k+1)/s_{2k-1}(k)$(결손 고정', r"$\mathrm{KD}'_n$(둘째 층 크기의 자식에서 물려받는 상속 몫), ", ''),
]
ops2 = [
    ('sub', '표 2의 78행(Q1–Q78)과 장부 v2 2절의 설계 확정분을 합쳐 양', 'Q45·Q46·Q48', 'Q36·Q45·Q46·Q48'),
    ('set_row', '| (Q36) 첫 층 선속 |', r'| (Q36) 첫 층 선속 | 뺌 — 2026-11-17 구조 압축 계약 변경 4(W2·X1-1)로 $\mathrm{FL}_n$ 소멸(2.10절은 두 양 $\Theta_n$·$\mathrm{BV}_n$만 정의) | $FL^{(5)}_n$, 「첫 층 블록이 내는 순 반응」 | 뺌 |'),
]
ops3 = [
    ('sub', '| 첫 층 나무 |', '2.10의 첫 층 선속과 7.5의 첫 층 상속이', '7.5의 첫 층 상속이'),
    ('del_row', '| 다섯 몫 |'),
]
ops4 = [
    ('sub', '기록이 붙인 이름은 아래 표의 라벨이 놓이는 진술 머리의 괄호에만 적고', '(2026-11-15 4차 판정 1절 1항으로 5.5.3절에서 옮기며 라벨을 바꿈).',
     '(2026-11-15 4차 판정 1절 1항으로 5.5.3절에서 옮기며 라벨을 바꿈). 뺌 행의 「옛 9장」은 2026-11-17 결정 K6로 지운 첫째 증명(P◇ 경로)의 장이고, 그 라벨은 중괄호 없이 `(9:…)`로 적는다 — 뒤의 장 번호 치환과 무관하다.'),
]
ops7 = [
    ('del_row', r'| $\mathrm{PAIR}_n$ |'),
    ('set_row', '| 교차항(정리 `{{2:tree-expansion}}`(가)', CROSS_LEDGER),
    ('set_row', r'| $\Theta_n$, $\mathrm{FL}_n$, $\mathrm{BV}_n$,', R6F_LEDGER),
    ('sub', r'| $\mu_m(k)$, $\mathrm{cl}^\pm_m$', r'글자($FL$은 1.2 $\mathrm{FL}_n$과 다른 양)', '글자'),
]
opsA = [
    ('sub', r'| $b^{T}_{t,\ell}$ |', r'(다섯 몫의 계수 $u_s=b^T_{t,k}$, $v_s=b^T_{t,k-1}$)', ''),
    ('sub', r'| $\mathrm{BV}_n$ |', '줄기 이득(다섯 몫)', '줄기 이득(정의 {{2:old-2-40}}; 문턱 나무 손실 $\\Theta_n$과 견주는 양)'),
    ('del_row', r'| $\mathrm{FL}_n$ |'),
    ('del_row', r'| $\mathrm{PAIR}_n$ |'),
    ('del_row', r'| $\mathrm{KD}_n$ |'),
    ('ins_after', r'| $\mathrm{Quad}_n, \mathrm{Stem}_n$ |', [r'| $\mathrm{KD}^\prime_n$ | 둘째 층 크기의 자식에서 물려받는 상속 몫 $\mathrm{KD}^\prime_n=\sum_{m=2k+1}^{n-1}(k+n-m)\binom{n-1}mp_{n-1-m}d_{m,k}$(정리 {{7:old-6-21}}의 항등식 $A_{n,k-1}(\star)(n)=d_{n,k}-\mathrm{KD}^\prime_n$의 항; 10장이 받아 쓴다) | 7.7 | — |']),
]
opsC = [
    ('del_row', '| 다섯 몫 |'),
    ('del_row', r'| $\mathrm{PAIR}_n$ |'),
    ('set_row', '| 교차항(정리 {{2:tree-expansion}}(가)', CROSS_C),
    ('set_row', r'| $\Theta_n$, $\mathrm{FL}_n$, $\mathrm{BV}_n$,', R6F_C),
    ('sub', r'| $\mu_m(k)$, $\mathrm{cl}^\pm_m$', r'글자($FL$은 1.2 $\mathrm{FL}_n$과 다른 양)', '글자'),
]
opsS = [
    ('sub', '| 2.10 지수 공식과 다섯 몫 분해 |', ' | 첫 판 2.10 | 옮김 |',
     ' (2026-11-17 계약 변경 4 W2·X1-1: 절 제목 「지수 공식과 표시 나무 전개」; 정리 `{{2:old-2-40}}`은 정의 「문턱 나무 손실과 줄기 이득」으로 격하(범위 둘째 층 $2k<n\\le3k$) — 항등식과 $\\mathrm{FL}_n$·$\\mathrm{KD}_n$·$\\mathrm{PAIR}_n$·「다섯 몫」 소멸; 진술 3 그대로(정의 1)) | 첫 판 2.10 | 옮김 |'),
    ('sub', '| 1.4 주 정리와 증명의 지도 |', 'W1이 등록부 167·174행의 소비 자리를 고쳤다)', 'W1이 등록부의 소비 자리를 고쳤고, 계약 변경 4로 둘째 항등식 자리는 표시 나무 전개가 되었다)'),
    ('sub', '작성일 2026-11-12. 결정 102', '이 물결로 죽은 라벨은 아래에서 중괄호 없이 적는다.', '이 물결로 죽은 라벨은 아래에서 중괄호 없이 적는다. 「옛 9장」은 그렇게 지운 첫째 증명(P◇ 경로)의 장이며, 이 표의 장·절 번호와 라벨 접두는 설계 때(결정 102)의 것이다.'),
]

OLD9_LEDGER = [('뺌 — 9장 삭제', '뺌 — 옛 9장(첫째 증명) 삭제', 39)]
OLD9_S = [
    ('9장 제거 물결', '옛 9장 제거 물결', None),
    ('K6으로 9장을 지우고 10장을 남겼다', 'K6으로 옛 9장(첫째 증명)을 지우고 10장(FLQ 경로)을 남겼다', 2),
    ('— 9장 삭제로 본문 진술', '— 옛 9장 삭제로 본문 진술', 1),
    ('결정 K6·V1 — 9장 삭제', '결정 K6·V1 — 옛 9장 삭제', 6),
    ('앞뒤 장의 9장 자리', '앞뒤 장의 옛 9장 자리', 1),
    ('9장 절 31행과 9장만 쓰던', '옛 9장 절 31행과 옛 9장만 쓰던', 1),
    ('이름 표의 9장 행 34', '이름 표의 옛 9장 행 34', 1),
    ('낱말 표의 9장 낱말 행', '낱말 표의 옛 9장 낱말 행', 1),
    ('글자 표의 9장·소멸', '글자 표의 옛 9장·소멸', 1),
    ('W9: 9장 3→0', 'W9: 옛 9장 3→0', 1),
]


def plain_replace(path, pairs, dry):
    text = io.open(path, encoding='utf-8').read()
    assert '\r' not in text
    for old, new, n in pairs:
        c = text.count(old)
        assert c > 0 and (n is None or c == n), (path, old, c, n)
        text = text.replace(old, new)
        print(f'{os.path.basename(path)}: {old!r} → {new!r} ×{c}')
    if not dry:
        io.open(path, 'w', encoding='utf-8', newline='\n').write(text)


if __name__ == '__main__':
    dry = '--dry' in sys.argv
    apply(LEDGER, ops12, dry=dry, region=('### 1.2', '### 1.3'))
    apply(LEDGER, ops13, dry=dry, region=('### 1.3', '## 2. '))
    apply(LEDGER, ops2, dry=dry, region=('## 2. ', '## 3. '))
    apply(LEDGER, ops3, dry=dry, region=('## 3. ', '## 4. '))
    apply(LEDGER, ops4, dry=dry, region=('## 4. ', '## 5. '))
    apply(LEDGER, ops7, dry=dry, region=('## 7. ', '## 8. '))
    plain_replace(LEDGER, OLD9_LEDGER, dry)
    apply(A, opsA, dry=dry)
    apply(C, opsC, dry=dry)
    apply(S, opsS, dry=dry)
    plain_replace(S, OLD9_S, dry)

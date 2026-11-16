# 전체 독립 검토 3차 뒤의 수리 — TD 보고 (`장v2/부록D_장*.md`, 7B 제외)

작성: 2026-11-15. 서식은 `파견/정합3_공통맥락_1115.md` 6절(1–7절)과 `파견/전체검토3_수리_공통_1115.md` 3절을 따른다. 절 단위로 나누어 여러 번에 걸쳐 쓴다. 행 번호는 수리 뒤 파일의 것이다(이번 수리는 행을 더하거나 빼지 않아 수리 전과 같다).

## 1. 읽은 범위

- 안내 문서: `파견/전체검토3_수리_공통_1115.md` 전문; `파견/정합3_공통맥락_1115.md` 1·2·4·5·6절; `파견/전체검토_수리_공통_1115.md` 1·2절; `파견/전체검토2_수리_공통_1115.md` 1절; `파견/전체_독립검토3_파견문_1115.md` 「판단의 방식」 절(30–60행); `파견/전체검토3_판정_1115.md` 머리(「큰 판단 넷」과 변경 없음 목록)와 「TD」 절.
- 검토 보고: `대조v2/수학검사2/검토전체3_I12.md` 전부(1–6절); `검토전체3_I13.md` 전부(2.2의 7B-1은 T7 몫이라 읽고 손대지 않음); `검토전체3_I3.md`·`_I4.md`·`_I6.md`의 5절.
- 고치는 파일: `장v2/부록D_장5A.md` 전문(1–148행; D.exact-n20000, D.c50, D.newton-m170, D.tail-T1-partAB, D.bernstein-signs, D.band-A-certification, D.critical-window-rig), `부록D_장5B.md` 전문(1–115행; D.window-mass-constant, D.zeta-constants, D.band-check, D.induction-rows), `부록D_장7A.md` 전문(1–222행; D.column-certification-k500, D.seed-certificates-k120, D.self-consistent-constants, D.xcert-partAB, D.polar-blocks-488). `부록D_장2.md`·`장3.md`·`장4.md`·`장6.md`·`장8.md`·`장9.md`·`장10.md`는 I12·I13이 지적을 내지 않았고 이번 인계 항목도 닿지 않아 열어 확인만 했다(7절의 전수 검색 범위에는 든다).
- 항목이 확인하는 본문: `장v2/장5A.md` 33–37행(명제 witness-position-bound 머리·진술·증명), 39–50행(정리 old-5-2 머리·진술·증명), 597–628행(보조정리 sign-sandwich 진술 (가)–(마)와 증명), 670–676행(정리 old-5-7 머리·증명 전체); `장v2/장5B.md` 349–351행(정리 old-5-32 머리·증명의 $\theta$·$\mu$ 단조 방향 문장), 131–133행(보조정리 zeta-constants), 419–431행(명제 band-inequality); `장v2/장8.md` 285·364·370·424·431·437·453행(보조정리 zeta-constants를 의존으로 선언한 네 진술과 끝값을 쓰는 세 자리); `장v2/장9.md` 189·877행(보조정리 psi-two-sided·psi-low 머리); `장v2/장11.md` 29·33·37·45–48·104행(11.2 표의 해당 행과 11.3 세 제타 상수 행); `장v2/장1.md` 1.5절 205–206행(산술 등급 「binary64 사전 오차 해석」·「〈정밀도〉 평가」의 정의).
- 기록(읽기 전용): `r9e782f5…/producer/code/truncated_system.py` 20–60행(`buffer`의 쓰임 `keep=max(last+buffer+1,1)`, 씨앗 검사 `seed_ok=all(v>=0 for v in s[cut:r+L])`), `producer/certificate-method.md` 78–90행, `producer/certificate-k*.json` 119개(열쇠 `cut`·`r`·`buffer`·`degrees`·`smoothed_initial`), `peer-additions.md` §1(문턱 $\tau_k$, $\tau_{120}=143$); `rf451d83…/review/feedback.md` 68–78행(층 A-int의 $\kappa_K$ 고침과 $R_U$ 재조립, 8개 구간 재실행), `review/evidence/kappa/aint_kfix.jsonl`(110행); `rad00a59…/evidence/peer/cert_S_tiers.txt`(넷째 줄 $T=120$의 $\beta=0.040834$), `sc_thresholds.py`(후보 $T\in\{10,15,\dots,100\}$)·`sc_thresholds.txt`; `r690be93…/evidence/producer/certify_entry.py`(정리 EI 인증 — $j=1$ 항은 `hi*(1+err)` 한 항), `certify_concavity.py`(꼬리 오목성 T 인증 — `p[0]=-…`, `p[1]+=3·…/S…`가 $-\mathrm{nS}+\mathrm{pS}x^{3/2}$), `tail-proof.md` 125–136행($N_S$·$P_S$의 식).
- 자료: `원고_자료/세션_재계산/r8a9b11e/ul_iv_fixed.py` 105–140행(`cell`·`Tcell`: $\theta$ 자리의 끝점 선택), `r89eb039_polar_iv/out/consts_check.txt`($\Gamma(5/3)$ 괄호 `valid=False`).
- 다시 센 것(`python -I`): 119개 인증서에서 $\sum_k(\mathfrak d_k+k+1-\mathfrak k_k)=34{,}571$, $\sum_k\lvert\text{smoothed\_initial}\rvert=49{,}372$, $\sum(\deg+1)=116{,}128$; $k=120$에서 마지막 차 재귀로 $A_{n,118},A_{n,119},A_{n,120}$($n\le146$)을 정확 정수로 계산해 $d_{n,120}<0$인 $n$이 정확히 $120\le n\le142$이고 $n\ge143$에서 양임을 확인($A_{5,0}=5!$, $A_{5,4}=6^4$로 재귀 검산); $\Gamma(5/3)$ 기록 괄호의 아래 끝 $0.90274529295093364$과 참값 $0.9027452929509336113\ldots$의 차 $2.9\times10^{-17}$.
- 읽기 전용 검사기: `python -I scripts/_check_지위서식.py` → 「문제 0건」; `python -I scripts/불변식_v2.py` → 「불변식 통과」.
- 인계 파일: `대조v2/수학검사2/인계_전체3_T3.md`(8행; 1번이 부록D_장5A의 $P_{\mathrm E}$·$P_{\mathrm A}$, 7번이 critical-window-rig 알림)와 `수리_전체3_T3.md` 2–7절을 처음 시작 뒤에 다시 확인해 읽고 반영했다. `인계_전체3_T4.md`·`_T6.md`는 이 보고를 마치는 시점(세 번 확인)에 없다. 세션이 전달한 `인계_전체3_T8.md`(장8 → 부록D_장8의 $\xi_1$)도 읽었다. 6절에 적는다.

## 2. 고친 것

지적 번호와 함께 적는다. 모두 Edit 도구로 자리마다 손으로 고쳤고, 고친 문장은 앞뒤와 함께 다시 읽었다.

| 번호 | 지적 | 자리 | 전 → 후 | 까닭(확인한 것) |
|---|---|---|---|---|
| 1 | I12 (2) | `부록D_장5A.md` 19행, D.exact-n20000 「독립 재계산」 꺾쇠 | 「산술 정확 정수·유리수·방향 반올림 구간·binary64 사전 오차 해석」 → 「…·binary64 사전 오차 해석·배정밀도 평가」 | 서술 (ㅂ) 「기록의 검토가 같은 자료에서 배정밀도로 재계산했다」에 해당하는 산술이 꺾쇠에 없었다. 1.5절 206행이 「배정밀도 평가」를 등급으로 정하고, D.critical-window-rig·D.theorem-U-constant의 꺾쇠가 같은 경우에 그 낱말을 쓴다. |
| 2 | I12 (2) | 같은 행, (ㄹ) 끝 문장 | 「정리 {{5:old-5-2}}의 방법으로 $n\le20000$을 다시 계산한 결과도 $19{,}996$개 행의 …에서 불일치가 없다(D.{{D:c50}})」 → 「정리 {{5:old-5-2}}의 방법으로 $n\le20000$을 다시 계산한 재인증 C20도, 기록의 계산(binary64 사전 오차 해석)과 이 글의 재계산(방향 반올림 구간) 모두 $19{,}996$개 행의 …에서 불일치가 없다(D.{{D:c50}})」 | 꺾쇠의 「binary64 사전 오차 해석」이 서술 어디에 닿는지 없었다. D.c50 「독립 재계산」을 읽으면 기록의 C20(`full20000_rows.tsv`, binary64 사전 오차 해석; 기록의 `full20000_compare_published.txt`가 (ㄹ) 자료와 대조)과 이 글의 C20(방향 반올림 구간; 「$19{,}996$행에서 D.exact-n20000(ㄹ)의 행별 자료와 불일치 $0$」)이 둘 다 (ㄹ)의 자료와 맞으므로, 두 계산을 밝혀 꺾쇠의 산술 넷이 모두 서술에 닿게 했다. 11.2 표 29행 5열은 세션 sync(인계). |
| 3 | I3 5절 | `부록D_장5A.md` 27행, D.c50 「확인하는 진술」 끝 문장 | 「같은 프로그램으로 $5\le n\le20000$을 계산한 결과가 D.{{D:exact-n20000}}(ㄹ)의 행별 자료와 일치한다.」 → 「…일치하고, 그 행들에서도 $\lceil(n-1)/2\rceil\le\ell\le n-2$의 모든 인접 쌍이 미결 없이 엄격 증가 또는 엄격 감소로 판정된다(명제 {{5:witness-position-bound}}의 증명이 봉우리가 한 칸임을 여기서 끌어 쓴다).」 | 장5A 37행(명제의 증명)이 「그 재인증은 같은 행들의 오른쪽 절반에 있는 모든 인접 쌍을 엄격 증가 또는 엄격 감소로 판정했으므로 … 고원이 없고」라 기대고, 장5A 50행(정리 old-5-2 증명 끝)이 같은 주장을 「부록 D.c50의 재인증 C20」으로 돌린다. D의 결과 줄(42행 「C20: … 인접 쌍의 엄격 감소 $5{,}797{,}956$, 미결 $0$」)에는 있었으나 확인하는 진술 줄에 없었다. |
| 4 | I12 (3) | `부록D_장5B.md` 24행, D.window-mass-constant 「알고리즘」 | 「$\theta$ 자리에는 앞 인자 $\mathfrak h_0^2\theta$, $\theta^3$, $\theta$와 지수 $e^{\theta^3\mathfrak h_0/(3\mu^2)}$에서는 $\theta_b$를 넣고, 지수 $e^{-(\theta-\mathfrak h_0)\mu/2-\theta^2/(2\mu)}$와 $\mathcal K$의 두 인수에서는 $\theta_a$를 넣는다」 → 「$\theta$ 자리에는 앞 인자 $\theta$와 지수 $e^{\theta^3\mathfrak h_0/(3\mu^2)}$에서는 $\theta_b$를 넣고, 지수 $e^{-(\theta-\mathfrak h_0)_+\mu/2-\theta^2/(2\mu)}$와 $\mathcal K$의 두 인수에서는 $\theta_a$를 넣는다」 | 같은 항목 14행의 $\mathcal T_{\max}$에는 $\theta$가 앞 인자 $\theta/\sqrt{2\pi}$, 두 지수, $\mathcal K$의 두 인수에만 들고 「$\mathfrak h_0^2\theta$」「$\theta^3$」이라는 인자는 없다. 코드 `ul_iv_fixed.py` `Tcell`은 `H0*H0*Zb*…`와 `Zb*I_iv(...)`(앞 인자 $\theta$를 대괄호 안에 분배한 것)와 `exp(Zb**3*H0/(3*gk*gk))`에 $\theta_b$를, `ap=(Za-H0)_+/2`·`bp=Za²/2`로 지수와 $\mathcal K$에 $\theta_a$를 쓴다. 장5B 351행(정리 old-5-32 증명)도 「앞 인자 $\theta$와 $e^{\theta^3\mathfrak h_0/(3\mu^2)}$는 $\theta$에 증가하고」라고만 적는다. |
| 5 | 4의 보완(스스로) | 같은 행, 다음 문장 | 「$\mu^{-3/2}$, $e^{-(\theta-\mathfrak h_0)\mu/2}$, $e^{\theta^3\mathfrak h_0/(3\mu^2)}$, $\mathcal K$에서는 격자 아래 끝을」 → 「$\mu^{-3/2}$, $e^{-(\theta-\mathfrak h_0)_+\mu/2}$, …」 | 식 줄(14·22행)과 코드(`ap=max(0,…)`)는 모두 $(\theta-\mathfrak h_0)_+$다. 4에서 같은 지수를 $_+$로 적었으므로 한 문단 안에서 같은 인자가 두 꼴로 적히지 않게 맞추었다. 첫 열세 셀($\theta<0.0342$)에서 $_+$가 실제로 작동한다. |
| 6 | I12 (4) | `부록D_장5B.md` 59행, D.zeta-constants 「결과」 끝 문장 | 「이 구간이 쓰이는 곳은 8장의 정리 {{8:pieces-k-monotone}}·{{8:jensen-H-ii}}와 9장의 보조정리 {{9:psi-two-sided}}·{{9:psi-low}}이고 그 증명들에서는 진술의 끝값 $\mathsf z_{-1/2}\ge-0.20789$, $\mathsf z_{1/2}\ge-1.46036$, $\mathsf z_{3/2}\le2.61238$만 쓴다.」 → (삭제) | 장8 424·453행(정리 closed-form-envelope·보조정리 table-tolerance)도 보조정리 zeta-constants에 의존을 선언하고, 장8 370행이 $\mathsf z_{1/2}\le-1.46035$를, 431행이 $\mathsf z_{-1/2}\le-0.20788$을, 437행이 $\lvert\mathsf z_{1/2}\rvert\ge1.46035$를 써서 「…만 쓴다」가 사실과 다르다. 이 문장은 계산 명세가 아니라 다른 장의 인용 현황이고 그 역할은 11.3 104행(세 제타 상수 행)이 맡고 있으므로, 고쳐 남기면 8·9장이 바뀔 때마다 다시 어긋날 자리라 지웠다(판정 「적용」과 같음). |
| 7 | I13 7A-1 | `부록D_장7A.md` 37행, D.seed-certificates-k120 「알고리즘」 (1) | 「각 단계에서 계수가 음이 아닌 항은 버려 하계 벡터 $\psi^{[\mathfrak d_k]}$를 만든다」 → 「각 단계에서 각 성분의 마지막 음수 계수 뒤로 인증서의 `buffer`개 항까지만 남기고 그 뒤의 계수가 음이 아닌 꼬리를 버려 하계 벡터 $\psi^{[\mathfrak d_k]}$를 만든다」 | `truncated_system.py` 36–37행 `last=max(j: v<0)`, `keep=max(last+buffer+1,1)`, `assert all(v>=0 for v in vals[keep:])`. `certificate-method.md` 83행도 같다. 종전 서술 「계수가 음이 아닌 항은 버려」는 음이 아닌 항을 모두 버리는 것으로 읽힌다. |
| 8 | I13 7A-1 | 같은 행, (3) | 「$\mathfrak k_k\le n<\mathfrak d_k+k+1$(인증서의 `buffer`만큼 더 넓게)에서」 → 「$\mathfrak k_k\le n<\mathfrak d_k+k+1$에서」 | 씨앗 검사는 52행 `seed_ok=all(v>=0 for v in s[cut:r+L]) and s[cut]>0`($L=k+1$)로 정확히 $[\mathfrak k_k,\mathfrak d_k+k+1)$에서 하고 `buffer`와 무관하다. $k=2$($\lvert\text{smoothed\_initial}\rvert=17=\mathfrak d+k+2$, `buffer`$=4$)·$k=120$($831$, `buffer`$=240$)에서도 저장 길이가 `buffer`와 무관함을 확인. |
| 9 | I13 7A-2 | `부록D_장7A.md` 39행, 「범위」 | 「검사한 씨앗은 $49{,}372$개다」 → 「검사 구간의 씨앗은 $34{,}571$개(저장된 초기값은 열마다 $0\le n\le\mathfrak d_k+k+1$로 모두 $49{,}372$개)다」 | 119개 인증서에서 직접 더해 $\sum(\mathfrak d_k+k+1-\mathfrak k_k)=34{,}571$, $\sum\lvert\text{smoothed\_initial}\rvert=49{,}372$($=\sum(\mathfrak d_k+k+2)$), $\sum(\deg+1)=116{,}128$. 같은 줄의 「검사한 씨앗 구간 $\mathfrak k_k\le n<\mathfrak d_k+k+1$」과 수가 맞지 않았다. |
| 10 | I13 7A-3 | `부록D_장7A.md` 43행, 「결과」 괄호 | 「($k=120$에서 $n=142$의 $d_{n,k}$는 음수이나 $2k-1=239$ 밖이다)」 → 「(각 열에서 $n$이 작을 때의 음수, 예컨대 $k=120$의 $120\le n\le142$는 직접 비교 범위 $\max(16,2k-1)\le n$ 아래에 있다)」 | 직접 계산으로 $k=120$의 음수는 $120\le n\le142$ 전부이고 $n\ge143$은 양(기록 `peer-additions.md` §1의 $\tau_{120}=143$과 같다). $n=142$ 하나만 적으면 그 점만 음수로 읽힌다. I13 4-1의 「괄호를 지우는 길」보다 고쳐 두는 쪽을 택했다. 직접 비교 범위가 $\max(16,2k-1)$에서 시작하는 까닭을 한 예로 보이는 괄호여서 정보가 있다. |
| 11 | I13 4-2(판단 위임) | `부록D_장7A.md` 57행, D.self-consistent-constants 「알고리즘」 (1) | 「$\mathcal J^{\mathrm S}$는 몇 후보 가운데 $\mathfrak B_0$를 가장 작게 하는 값으로 골랐다.」 → (삭제) | 기록 `sc_thresholds.py`의 후보는 $T\in\{10,15,20,25,30,35,40,50,60,70,80,100\}$이고 그 안에서는 참이나, 같은 기록의 `cert_S_tiers.txt` 넷째 줄은 $T=120$이 층 3에서 더 작은 $\mathfrak B_0=0.040834$를 준다고 적어 「가장 작게 하는」을 글자대로 읽는 독자에게 어긋난다. 이 문장은 매개변수를 고른 경위(연구 과정)이고, 확인하는 진술 (1)이 $\mathcal J^{\mathrm S}=25,70,100$을 입력으로 고정하므로 계산을 재현하는 데 필요하지 않다. 범위를 적어 남기는 길(「후보 $\mathcal J^{\mathrm S}\le100$ 가운데」)보다 지우는 쪽이 원칙 8(연구 기록의 흔적)·10에 맞다. |
| 12 | I13 7A-4 | `부록D_장7A.md` 112행, D.xcert-partAB 「독립 재계산」 둘째 문장 | 「층 A-int, 층 A″-1의 36구간, 층 A″-2의 72구간은 기록의 검토가 다시 실행했고, 그 재실행의 최대 $R_U$는 A-int $1.975861$, A″-1 $1.8697$, A″-2 $1.9969851$이다.」 → 「층 A″-1의 36구간과 층 A″-2의 72구간은 기록의 검토가 고친 코드로 다시 실행했고(최대 $R_U$는 각각 $1.8697$, $1.9969851$), 층 A-int의 110구간은 기록의 검토가 $\kappa_K$ 하계를 고친 값으로 창 꼬리를 다시 계산해 $R_U$를 다시 조립했다(8개 구간은 끝까지 재실행; 최대 $R_U$ $1.975861$).」 | `rf451d83…/review/feedback.md` 「고침과 재계산(검토자)」 문단: 110개 구간 전부에서 $\kappa_{\mathrm{code}}$·$\kappa_{\mathrm{fix}}$·$\Delta\Phi^{\mathrm U}$·$\bar w_{1,2}$를 다시 계산하고 기록된 $R_U$에서 $C$를 풀어 $R_U$를 다시 조립; 끝까지 재실행한 것은 8개 구간; 최대 $R_U$ $1.975861$([7884,8078]). `aint_kfix.jsonl` 110행, 필드 `R_U_fix`. 「다시 실행했고」로 세 층을 묶으면 A-int의 보증 방식이 실제보다 세게 읽힌다. |
| 13 | I13 7A-4의 보완 | 같은 행, 꺾쇠의 범위 | 「층 A″-1·A″-2·A-int는 재실행」 → 「층 A″-1·A″-2는 재실행, 층 A-int는 재조립과 8구간 재실행」 | 12와 같은 사실을 꺾쇠가 아직 옛 꼴로 들고 있었다. 11.2 표 47행 5·6열은 세션 sync(인계). |
| 14 | I13 4-3 | `부록D_장7A.md` 199행, D.polar-blocks-488 「산술 등급」 끝 | (끝에 두 문장 추가) 「기록 코드의 상수 괄호 가운데 $\Gamma(5/3)$의 괄호 $[0.90274529295093364,0.90274529295093375]$는 아래 끝이 참값 $0.9027452929509336113\ldots$보다 $3\times10^{-17}$ 커서 참값을 담지 않는다. 이 글의 계산은 자기 포위(mpmath `iv`, 소수 $40$자리)를 쓰므로 이 괄호에 기대지 않고, 그 차(상대 $3\times10^{-17}$)는 $\varsigma$-구간 계산의 가장 빠듯한 여유(상대 $4.8\times10^{-6}$)보다 열 자리 넘게 작다.」 | `consts_check.txt`: `Gamma(5/3) code bracket [0.90274529295093364, 0.90274529295093375] … bracket valid=False`, mpmath 50자리 참값 `0.902745292950933611296…`. 같은 항목 216행이 「상수 … 의 괄호는 mpmath `iv`(40자리)로 만들어 확인했다」고 이 글의 괄호만 말하므로, 기록 계산을 적는 자리인 「산술 등급」 줄에 기록 괄호의 사실과 이 글의 계산이 영향받지 않는 까닭을 적었다. 여유 $4.8\times10^{-6}$은 같은 항목의 결과 줄(「$\varsigma$-구간 계산에서 가장 빠듯한 $\varsigma$ 괄호의 상대 여유는 $4.8\times10^{-6}$」)의 값이다. |

| 15 | T8 인계(세션 전달) | `부록D_장8.md` 7행, D.window-mass-env 「알고리즘」 (가) | 「처음 셀 $(0,\xi_1]$은 단조 상하계로 따로 막는다」 → 「처음 셀, 곧 $0$에서 격자의 첫 점까지는 단조 상하계로 따로 막는다」 | 같은 항목 5행(「식」)이 $\xi_i=0.0005\,i$를 원천 표의 점으로 정의하므로 D 안에서도 $\xi_1$은 표의 점 $0.0005$로 읽히는데, (가)의 「처음 셀」은 표의 점이 아니라 $q$마다 다른 기하 격자(셀 길이 $\le\min(0.01\xi,0.005)$)의 첫 셀이다. 격자의 글자는 D 안에 따로 정의되어 있지 않다(장8 8.1절의 $\xi_q=q/k^{2/3}$, 8.2절의 표 점 $\xi_i$와도 겹친다). 본문 장8 549행(정리 old-6-28 증명; T8이 고침)과 같은 뜻을 글자 없이 적었다. |
| 16 | T3 인계 1(SM 8) | `부록D_장5A.md` 92행, D.bernstein-signs 「확인하는 진술」 (ㄴ) | $P_{\mathrm E}(x^{3/2})$ → $\mathrm{Pol}_{\mathrm E}(x^{3/2})$ | 장5A 676행의 새 이름과 맞춤(5B 기저량 $P_n(y)$가 5장 전역이라 첨자 붙은 이탤릭 $P$가 한 장 안 두 뜻). |
| 17 | T3 인계 1(SM 8) | `부록D_장5A.md` 112행, D.band-A-certification 「확인하는 진술」 | $P_{\mathrm A}(x^{3/2})$ → $\mathrm{Pol}_{\mathrm A}(x^{3/2})$ | 장5A 822·824행과 맞춤. |
| 18 | T3 인계 1(SM 8) | `부록D_장5A.md` 114행, 같은 항목 「식」 | $P_{\mathrm A}(x_{\mathrm m})+\max\lvert P_{\mathrm A}'\rvert$ → $\mathrm{Pol}_{\mathrm A}(x_{\mathrm m})+\max\lvert\mathrm{Pol}_{\mathrm A}'\rvert$ | 위와 같음(한 행의 두 자리). |

첫 회차에 고친 자리는 열여덟이다(지적에 따른 것 열둘, 그 보완으로 스스로 고친 것 둘 — 5·13, 세션이 전달한 T8 발견 하나 — 15, T3 인계 반영 셋 — 16·17·18).

### 2.2 둘째 회차 — T4·T6·T14 인계 반영(세션이 다시 부른 뒤)

`인계_전체3_T4.md`(TD 행 1–10), `인계_전체3_T6.md`(TD 행 1–5), `인계_전체3_T14.md`(1·5), `인계_전체3_세션.md`(1), `수리_전체3_T7.md`(7A 98행 $\mathfrak f_j$ 알림)를 읽고 반영했다. 반영 전에 5B 256–262행(bt-tail (나)의 $\mathcal I(\varsigma,\mathfrak b;\mathfrak W_0)$), 325행($\varsigma_z\mathfrak W_0=\frac{\theta-\mathfrak h}2\mathfrak W_0\mathfrak h^2$), 419–431행(band-inequality의 새 글자 $\chi_{\mathrm w}$·$\chi_2$·$\lambda_a,\lambda_b$·$\bar\varrho_0$와 $(5.4)$), 7A 870행($\mathcal G_k(x)=\sum_{n>k}\mathrm{pr}_{n,k}e^{\varsigma n/k}$)·280행($\mathcal G_y:=C_y-\mathcal C_y$), 장6 854·864행(lemma-F·lemma-E의 $\tau$), 장부 1189행(9장 여유 글자)을 열어 새 글자가 본문과 같은지 확인했다.

| 번호 | 인계 | 자리 | 전 → 후 | 까닭(확인한 것) |
|---|---|---|---|---|
| 19 | T4 1 | `부록D_장5B.md` 13행 D.window-mass-constant 「식」 | $\mathcal K(\sigma,\mathfrak b;\mu)=\dots$의 $\mathcal K\to\mathcal I$, $\sigma$ 다섯 → $\varsigma$ | 5B 256–262행 bt-tail (나)의 $\mathcal I(\varsigma,\mathfrak b;\mathfrak W_0)$ 닫힌 꼴과 글자까지 같게. |
| 20 | T4 2 | 14행 $\mathcal T_{\max}$ | $\mathcal K\bigl(\frac{(\theta-\mathfrak h_0)_+}2,\frac{\theta^2}2;\mu\bigr)\to\mathcal I\bigl(\cdots\bigr)$ | 5B 325행 $\mathcal I\bigl(\frac{\theta-\mathfrak h}2,\frac{\theta^2}2;\mathfrak W_0\mathfrak h^2\bigr)$와 맞춤. |
| 21 | T4 3 | 22행 | 「bt-tail(나)의 $e^{-\sigma\mathfrak W_0}$($\sigma=(\theta-\mathfrak h)/2$, $\mathfrak W_0\mathfrak h^2\ge\mu$)에서 온」 → 「bt-tail(나)의 $e^{-\varsigma\mathfrak W_0}$에 $\varsigma=\varsigma_z=(\theta-\mathfrak h)\mathfrak h^2/2$를 넣고 $\mathfrak W_0\mathfrak h^2\ge\mu$를 쓴 것(정리 {{5:old-5-32}}의 증명)에서 온」 | bt-tail (나)에 이제 $\sigma$가 없고, 옛 「$\sigma=(\theta-\mathfrak h)/2$」는 척도를 뺀 값이라 $e^{-\sigma\mathfrak W_0}$와 맞지 않았다. 5B 325행이 $\varsigma_z\mathfrak W_0=\frac{\theta-\mathfrak h}2\mathfrak W_0\mathfrak h^2$, 곧 $\varsigma_z=(\theta-\mathfrak h)\mathfrak h^2/2$를 준다($\mathfrak h=Y^{-1/3}$, $\theta=z\mathfrak h$에서 $(z-1)/(2Y)$와 같다). |
| 22 | T4 4 | 24행 「알고리즘」 | $\mathcal K$ 두 자리 → $\mathcal I$; $\theta$-셀 끝 $\theta_a,\theta_b$는 그대로 | 글자 이름만. $\theta_a,\theta_b$는 척도 변수 $\theta$의 셀 끝이라 I4-5 대상이 아니다(T4 4). |
| 23 | T4 5 | 69행 D.band-check 「확인하는 진술」 | $[\theta_a,\theta_b]\to[\lambda_a,\lambda_b]$; $(5.53)\to(5.4)$ | 5B 419–421행. |
| 24 | T4 6 | 71행 「식」 | $\bar\varrho$ 여섯 → $\bar\varrho_0$, $\theta_a$ 둘 → $\lambda_a$, $\theta_b$ 셋 → $\lambda_b$ | 5B 421·428행의 $\bar\varrho_0:=0.75(1.1\lambda_bn)^{2/3}+1$, $\bar{\mathfrak c}_0$, $\bar\epsilon_0$ 식과 글자까지 같다. |
| 25 | T4 7 | 74행 | $\mathrm{hov}(\rho_0,Q_{\mathrm w})\to\mathrm{hov}(\rho_0,\chi_{\mathrm w})$, $\theta_a\to\lambda_a$, $\theta_b\to\lambda_b$ | 5B 424행. |
| 26 | T4 7 | 75행 | $Q_2$ 둘 → $\chi_2$, $\theta$ 셋 → $\lambda$, $\bar\varrho\to\bar\varrho_0$ | 5B 425행. |
| 27 | T4 7 | 76행 | $\theta_a^{-1/2}(1-\theta_b)^{-3/2}\to\lambda_a^{-1/2}(1-\lambda_b)^{-3/2}$ | 5B 426행. |
| 28 | T4 7 | 77행 | $\theta_a$·$\theta_b$ 넷 → $\lambda$ | 5B 426행. |
| 29 | T4 7 | 78행 | $\bar\varrho$ 둘 → $\bar\varrho_0$, $\theta_a$ 둘 → $\lambda_a$ | 5B 427행. |
| 30 | T4 8 | 83행 「알고리즘」 | $0.4(1-\theta_b)n\ge6(\theta_bn)^{2/3}+1\to0.4(1-\lambda_b)n\ge6(\lambda_bn)^{2/3}+1$ | 5B 421행의 조건. |
| 31 | T4 9 | 89행 「결과」 | $(5.53)\to(5.4)$ | I4-2(89행은 I4가 적지 않은 자리; T4가 찾음). |
| 32 | T4 10 | 91행 「독립 재계산」 | $7.72(\theta_an-1)^{-1/3}\to7.72(\lambda_an-1)^{-1/3}$ | I4-5. 11.2 표 38행 6열은 세션 sync(인계). |
| 33 | T6 1 | `부록D_장7A.md` 53행 D.self-consistent-constants 「확인하는 진술」 | $(\varsigma,\mathcal J^{\mathrm S},k^{\mathrm S}_0)$, $\mathfrak j^\ast(\varsigma)$, $k_{\mathrm R}(\varsigma)$의 $\varsigma$ 셋 → $\mathfrak L$ | 7A 7.2절(lemma-R-sc·self-consistent-S·cor-S-prime)의 비 하계 상수가 $\mathfrak L\in(2,e)$가 되었다(I6 U1). 이 항목의 $\varsigma$ 열다섯은 모두 그 상수이고 7.3의 $\varsigma_k$가 아님을 한 자리씩 읽어 확인. |
| 34 | T6 1 | 55행 「식」 | $\varsigma$ 열하나 → $\mathfrak L$($\mathfrak j^\ast$, $k_{\mathrm R}$, $\bar{\mathfrak x}_\varkappa$, $\underline{\mathfrak q}_\varkappa$, $\mathfrak E_\infty$ 셋, $\Xi^{(k^{\mathrm S}_0)}$, $\mathfrak A_0$) | 위와 같음. |
| 35 | T6 1 | 57행 「알고리즘」 | $\varsigma/e\to\mathfrak L/e$ | 위와 같음. 51–69행에 $\varsigma$ 0건 확인. |
| 36 | T6 2 | 77행 D.xcert-partAB (1) | $\mathfrak X_i=n_{\mathrm X}(k)-\mathfrak o_ik\to-\mathfrak D_ik$ | 7A 717–733행 X-cert의 창 지표가 $\mathfrak D_i$. 파일 안 `\mathfrak o` 22자리가 모두 이 지표(77·87·96·98·100·102행)임을 확인하고 바꿈. |
| 37 | T6 2 | 87행 (2) | $\sum_{\mathfrak o_ik+1<j\le\mathfrak J}$, 「창은 $\mathfrak o=(3,4)$」 → $\mathfrak D$ | 위와 같음. |
| 38 | T6 2 | 96행 (3) | $\sum_{j>\mathfrak ok+1}$, 「창 $\mathfrak o=(4,7)$」, $e^{-\vartheta\mathfrak o}$ → $\mathfrak D$ | 위와 같음. |
| 39 | T6 2 | 98행 (4) | 「다중 창 $\mathfrak o_1=4$, $\mathfrak o_{i+1}=\lceil1.65\mathfrak o_i\rceil$」 → $\mathfrak D$ | 위와 같음. |
| 40 | T6 2 | 100행 (5) | $\sum_{j>\mathfrak ok+1}$, $e^{-\mathfrak o\vartheta}$, $-\mathfrak o_ik_{\mathrm{lo}}$ → $\mathfrak D$ | 위와 같음. |
| 41 | T6 2 | 102행 (6) | $\mathfrak o_1$, $\mathfrak o_{i+1}$, $\mathfrak o_{\mathfrak I}$, $\bar\omega(\mathfrak o)$, $e^{-\mathfrak o\vartheta}$, $\bar\omega(\mathfrak o_i)$ 둘 등 열 자리 → $\mathfrak D$ | 위와 같음. |
| 42 | T6 4 (ㄱ) | 89행 (3) | 「$\mathcal J(\varsigma):=\sum_{n>k}\mathrm{pr}_{n,k}e^{\varsigma n/k}$에 대해」 → 「$\mathcal J(\varsigma):=\sum_{n>k}\mathrm{pr}_{n,k}e^{\varsigma n/k}$(7.2절의 $\mathcal G_k(x)$, 곧 정리 {{7:seed-transfer}}(가)의 $\mathcal G_y$($y=k$)를 $x=e^{-1+\varsigma/k}$에서 $\varsigma$의 함수로 적은 것; 명제 {{7:polar-W}}의 증명이 쓰는 꼴)에 대해」 | 7A 870행(polar-W 증명)이 이제 $\mathcal G_k(x)=\sum_{n>k}\mathrm{pr}_{n,k}e^{\varsigma n/k}$로 적고 $\mathcal J$를 쓰지 않으므로, 부록의 $\mathcal J$ 가족(장부 414행 등록)을 두고 정의 자리에서 본문의 양과 잇는다(T6의 (ㄱ)). $\mathcal G_y:=C_y-\mathcal C_y$(7A 280행)에 $\mathrm{pr}_{n,k}=C_{n,k}e^{-n}/n!$, $x^n=e^{-n}e^{\varsigma n/k}$를 넣으면 같다. |
| 43 | T6 3 | 137행 D.polar-blocks-488 (4) | $\theta_a\ge\gamma\sqrt{\cdots}$, $(1-\gamma^2)$, $6\gamma^2e^{-1}=1.99$의 $\gamma$ 셋 → $\Upsilon$ | 7A 754–818행 보조정리 lemma-P-pole·명제 polar-R의 매개변수가 $\Upsilon$(I6 P4의 T6 처리). $\gamma_k$(75·89·96·122행)는 T6 6번대로 둔다. |
| 44 | T6 3 | 189행 (11) | $\gamma=0.95$, $\theta_a:=\gamma\sqrt{\cdots}$, $(1-\gamma^2)$ → $\Upsilon$ | 위와 같음. |
| 45 | T6 3 | 220행 「코드의 변수」 | 「`tau_par`는 $\gamma$」 → $\Upsilon$ | 위와 같음(기록 코드의 $\tau$가 이 글의 $\Upsilon$). |
| 46 | T6 5 | 145행 (6)(ㄴ)(ㄷ) | 「$N_\nu:=k_\nu+i$, $\mathfrak g^{(k_\nu)}_i(m)=(k_\nu-m)m^{-3/2}(N_\nu-m)^{-3/2}$($\nu=1,2$)」 → 「$N_1:=k_1+i$, $N_2:=k_2+i$, $\mathfrak g^{(k_1)}_i(m)=\cdots(N_1-m)^{-3/2}$, $\mathfrak g^{(k_2)}_i(m)=\cdots(N_2-m)^{-3/2}$」; 「$N=N_\nu$에 대해 … $\int\mathfrak g^{(k_\nu)}_i$」 → 「$N=N_1$ 또는 $N_2$에 대해 … $\int\mathfrak g^{(N-i)}_i$」 | 1.5절 전역 좌표 $\nu=n-2k$를 지표로 쓰고 있었다(I6 P6). 지표를 없애고 두 끝을 직접 적었다. 같은 항목의 다른 $\nu$는 모두 전역 좌표의 뜻. |
| 47 | T14 1 | `부록D_장6.md` 5행 D.theorem-U-constant 「알고리즘」 | $e^{1.5\lambda}=(1-\sigma)^{-3/2}\to e^{1.5\tau}=(1-\sigma)^{-3/2}$ | 장6 864행 lemma-E의 치환 $\phi_{\mathcal F}(\sigma)=\mathcal F(-\log(1-\sigma))$의 변수가 $\tau$(T14; 1장 전역 $\lambda=k/n$ 회피). 부록D_장6에 $\tau$ 0건이었다. |
| 48 | T14 5(세션 지시) | `부록D_장9.md` 41행 D.band-LP 「알고리즘」 (라) | 쌍대 변수 $\lambda$ 일곱 → $\kappa$ | 코드 변수의 백틱 인용이 아니라 수식 글자($\lambda\ge0$, $r_t\ge\lambda-(\lambda-r_t)^+$, $\lambda\,\mathsf v(k)$ …)다. 1장 전역 $\lambda=k/n$을 국소로 다시 쓴 것이라 바꾸었다. $\kappa$는 장부 1189행 9장 여유 그리스 목록에 있고 `장9.md`·`부록D_장9.md`에 0건(함께 0건인 후보 $\tau$·$\sigma$는 1.2 전역이라 피함; $\zeta$는 여유 목록에 없음). 장부 1.3 9장 묶음에 등록은 SL(인계). |

둘째 회차에 고친 자리는 서른이다(5B 열넷, 7A 열넷, 6 하나, 9 하나). 두 회차 합계 마흔여덟.

**T7 알림의 확인(변경 없음).** `부록D_장7A.md` 98행(D.xcert-partAB (4) 층 A″-1)의 $\mathfrak f_1,\dots,\mathfrak f_r$은 「정수 묶음 $[\mathfrak n_1,\mathfrak n_2]$ 위에서 양이고 단조인 인자」, 곧 묶음 괄호의 곱 인자이고, 7B 7.6절의 $\mathfrak f_j$(한 걸음 결합의 양; 큰 판단 1로 T7이 지웠음)와 다른 양이다. 7B에는 이제 $\mathfrak f_j$가 없으므로 겹침도 없다. 같은 행의 $\mathfrak r$(셀 적분의 기울기)은 세션 인계 1대로 둔다(7B theorem-W (나) 증명의 $\mathfrak r=n/k$와 둘 다 증명·명세 안의 국소).

**T6 4의 알림 둘에 대한 판단(변경 없음).** (ㄱ) 한 부록 파일 안의 $\mathcal J$ 두 뜻 — D.self-consistent-constants의 $\mathcal J^{\mathrm S}$(7.2절 정리 S 진술의 절단 지표, 위 첨자 S가 붙은 고정 이름)와 D.xcert-partAB의 함수 $\mathcal J(\varsigma)$ 가족. 서로 다른 항목에 있고 꼴(정수 매개변수 대 $\varsigma$의 함수)과 첨자가 달라 독자가 멈추지 않는다고 보았다. $\mathcal J(\varsigma)$ 가족을 $\mathcal G_k$ 꼴로 바꾸면 89–102·122·126·133·137·150–152·177·214·220행 스무 자리 넘게 닿고 7B의 D 항목(T7 몫)의 인용도 함께 봐야 하므로, 정의 자리에 본문과의 연결을 적는 (ㄱ)을 택했다. (ㄴ) 94행의 $\Omega(\varsigma)$와 7.3의 $\Omega^{\mathrm{pr}}$·$\Omega_j$ — 바탕 글자만 같고 꾸밈이 다르며 94행 정의가 그 자리에 있다. 두지만 인계에 알림으로 남긴다. **100행의 첨자 없는 $\gamma$ 넷**($\upsilon^{-3/2}e^{\gamma\upsilon}$ 등; I6 5절이 「$\gamma_k$를 첨자 없이 적은 것」이라 한 자리)은 T6이 $\gamma_k$를 두기로 하여 파일 안 충돌(polar의 $\gamma\to\Upsilon$)이 풀렸으므로 손대지 않았다. 다만 그 $\gamma$가 $\gamma_k$ 자체인지 $k$-구간의 상계인지는 층 A″-2 코드(`xcert_iv/layerA2.py` 41행 상수 `C775`)를 끝까지 따라가지 않아 확인하지 못했다(6절).

## 3. 지적을 받았으나 고치지 않은 것과 그 까닭

- **I3 5절 셋째 항목(D.bernstein-signs에 $\mathrm{nS}$·$\mathrm{pS}$ 이름을 적는 것) — 고치지 않음. 판정 문서의 「적용」과 다르게 판단했다.** 장5A 613행 보조정리 sign-sandwich (라)는 「$\frac{r^{3/2}}e\mathcal Q^{(3)}_{n,r,1}\le-\mathrm{nS}+\mathrm{pS}x^{3/2}$ … 두 상수는 부록 D.bernstein-signs에서 $r$ 칸마다 계산된다」고 적지만, 기록 r690be93을 열어 보면 이 두 상수는 **셋째 차분(꼬리 오목성 정리 T)** 인증 `certify_concavity.py`의 `p[0]=-SQLO·IPLO·(1-3/(2R))(1-1/(12R²))(1/2-11/(24R²))`, `p[1]+=3·SQHI·IPHI/S/(1-1/(S+A))³/(1-η)`(기록 `tail-proof.md` 129–133행의 $N_S$, $P_S$)이다. D.bernstein-signs (ㄴ)이 적는 계산은 **둘째 차분(정리 old-5-7, EI)** 인증 `certify_entry.py`이고, 그 $j=1$ 항은 `hi*(1+err)` 한 항(장5A 674행 「$j=1$ 항 $\frac{r^{1/2}}e\mathcal Q^{(2)}_{n,r,1}=r^{1/2}\mathrm{nf}(n,r)\mathrm{Ren}(r+1)$도 … 같은 방식의 상계를 받는다」)이어서 $-\mathrm{nS}+\mathrm{pS}x^{3/2}$ 꼴이 나오지 않는다. 꼬리 오목성 정리 T 자체는 이 글에 없고(구조표 59행: 5.3은 뺌), (라)를 부르는 자리도 저장소에 없다(장5A 613·623행 자신뿐; `sign-sandwich}}(라)` 0건). 그러므로 D에 두 이름을 적으면 D가 하지 않는 계산을 적는 것이 된다. 맞는 처리는 5A 쪽(T3·SL 범위)에서 (라)의 마지막 문장을 지우거나 (라) 자체를 지우는 것이며, 인계에 적었다(5절 1).
- **I13 4-1(D.seed-certificates-k120 결과 줄 괄호를 아예 지우는 길)** — 지우지 않고 고쳤다(2절 10). 괄호는 직접 비교 범위가 $\max(16,2k-1)$에서 시작하는 까닭(그 아래에 음수가 있음)을 보이는 유일한 자리라 정보가 있다.
- **I12 4절 둘째 항목(부록 D의 「기록의 값」 설명 문장들)** — I12가 문제로 올리지 않았고 판정에도 없다. 그대로 둔다.
- **I3 5절 둘째 항목(D.critical-window-rig 「식」 줄의 $0.1268$·$0.1267$ 문장)** — 판정대로 둔다. T3 인계 7도 「변경 제안 없음」. D는 기록 계산과 이 글의 재계산을 구별해 적는 자리이고, 본문(904·952행)에서 그 사정이 빠진 뒤에는 이 줄이 유일한 자리가 되어 오히려 남아야 한다.
- **I12 (2)의 두 선택지** — 「binary64 사전 오차 해석」을 지우는 길이 아니라 남기고 서술을 맞추는 길을 택했다(판정과 같음). 기록의 C20이 실제로 (ㄹ)의 자료와 대조되었으므로(기록 `full20000_compare_published.txt`) 그 산술은 꺾쇠에 있어야 한다.

## 4. 지적 밖에서 스스로 발견해 고친 것

| 자리 | 전 → 후 | 까닭 |
|---|---|---|
| `부록D_장5B.md` 24행 | $e^{-(\theta-\mathfrak h_0)\mu/2}$ → $e^{-(\theta-\mathfrak h_0)_+\mu/2}$($\mu$ 문장) | 2절 5. 같은 문단의 같은 인자를 식 줄과 같은 꼴로. |
| `부록D_장7A.md` 112행 꺾쇠 | 「층 A″-1·A″-2·A-int는 재실행」 → 「층 A″-1·A″-2는 재실행, 층 A-int는 재조립과 8구간 재실행」 | 2절 13. 7A-4의 사실을 꺾쇠도 옛 꼴로 들고 있었다. |

읽으면서 의심했으나 두어도 된다고 본 것: D.exact-n20000 「산술 등급」 줄(15행)의 「(ㅂ)의 기록 계산은 배정밀도 평가이고 … 이 글의 재계산은 방향 반올림 구간이다」는 이미 2차에서 맞춰진 문장이고 이번 꺾쇠 수정과 맞물린다. D.window-mass-constant 24행 「셀 $[\theta_a,\theta_b]\times[\omega_j,\omega_{j+1}]$」의 $\theta_a,\theta_b$는 $\theta$-셀의 끝이고 D.band-check(69–91행)의 $\theta_a,\theta_b$는 $\lambda$-소구간의 끝이다(I4 5절). 둘째 것은 T4가 $\lambda_a,\lambda_b$로 바꾸기로 했으므로(I4-5) T4의 인계를 받아 band-check 쪽만 바꾼다(6절).

## 5. 인계한 것

인계 파일 `대조v2/수학검사2/인계_전체3_TD.md`에 첫 회차 여섯, 둘째 회차 넷(7–10: 11.2 표 38행 sync, 장부 1.3 9장 묶음의 $\kappa$ 등록, 장부 414행의 부록 D 글자($\mathcal J$ 가족·$\mathfrak D_i$) 확인, $\Omega(\varsigma)$·100행 $\gamma$ 알림)을 적었다. 첫 회차의 「미수령 인계 때 바뀔 자리」 절은 반영이 끝나 지웠다.

1. T3(또는 SL·세션) — 장5A 613행 보조정리 sign-sandwich (라)의 「두 상수는 부록 D.{{D:bernstein-signs}}에서 $r$ 칸마다 계산된다」: D는 그 계산(셋째 차분 인증)을 적지 않으며 (라)를 부르는 자리도 없다. 문장 삭제 또는 (라) 삭제 제안(3절 첫 항목).
2. 세션(11.2 표 sync) — 장11 29행 5열(D.exact-n20000 꺾쇠: 「배정밀도 평가」 추가)과 6열((ㄹ) 끝 문장).
3. 세션(11.2 표 sync) — 장11 47행 5열(D.xcert-partAB 꺾쇠의 범위 문구)과 6열(층 A-int 서술).
4. 세션 — `장v2/_tmp/독해보고_1114/편집전/부록D_장7A.md`·`inv_*.json`은 수정 전 사본·목록이라 옛 글귀가 남는다(손대지 않음, 알림).
5. T4(5B)·T6(7A) — 인계 파일이 아직 없어 부록 D 반영을 못 했다(6절). 받을 항목 목록을 인계 파일 끝에 적어 두었다.
6. SL — 장부 1.3 377·379·380행의 $P_{\mathrm E}$·$P_{\mathrm A}$는 T3 인계 5가 이미 적었다(TD는 알림만).

## 6. 확인하지 못한 것, 막힌 것, 판정과 다르게 판단한 것

- **(둘째 회차에서 해소) 첫 회차에 받지 못했던 인계 `인계_전체3_T4.md`·`_T6.md`는 세션이 다시 부른 뒤 받아 2.2절대로 모두 반영했다.** 아래 문단은 첫 회차의 기록이다. 그때 적어 둔 자리 수(5B 열넷, 7A 열넷)와 실제 반영 수가 같다. 둘째 회차에 확인하지 못한 것 하나: `부록D_장7A.md` 100행의 첨자 없는 $\gamma$ 넷이 $\gamma_k$인지 $k$-구간 상계인지(2.2절 끝). 첫 회차 기록: 이 보고를 쓰는 시점(수정 뒤 두 번 다시 확인)에 둘 다 없다. 그러므로 다음을 반영하지 못했다. (ㄱ) T4: 부록D_장5B 69·89행의 $(5.53)$→$(5.4)$(와 94행 부근의 $(5.52)$가 있으면 $(5.3)$), 71·75·78행의 $\bar\varrho$→$\bar\varrho_0$, 69·71·74–78·83·91행의 $\theta_a,\theta_b$→$\lambda_a,\lambda_b$(band-check만; window-mass-constant 24행의 $\theta$-셀 끝 $\theta_a,\theta_b$는 둔다), 13·14·22·24행의 $\mathcal K$→새 필기체 글자(window-mass-constant; 22행 「$e^{-\sigma\mathfrak W_0}$($\sigma=(\theta-\mathfrak h)/2$…)」의 $\sigma$는 bt-tail (나) 진술의 것이라 둔다), 74행의 $Q_{\mathrm w}$→새 글자. (ㄴ) T6: 부록D_장7A 51–69행 D.self-consistent-constants의 7.2절 $\varsigma$(열다섯 자리; $\varsigma\in(2,e)$ 뜻)→새 그리스 글자, 75·89·96·122행의 $\gamma_k$(와 89행 $\gamma_{\min},\gamma_{\max}$, 100행 $e^{\gamma\upsilon}$)→$\varsigma_k/k$ 풀어 적기 또는 T6의 처리대로, 77·87·98·100·102행의 $\mathfrak o_i$($\mathfrak o_1$ 포함)→새 프락투어. 자리 수는 위 전수 검색으로 세어 두었다. 세션이 다시 부르면 그때 반영한다.
- **판정과 다르게 판단한 것 하나**: I3 5절의 $\mathrm{nS}$·$\mathrm{pS}$(3절 첫 항목). D에 적지 않고 5A 쪽 수정을 인계했다.
- **I13 4-2(판단 위임)**: 문장을 지웠다(2절 11). 범위를 적어 남기는 길도 참이지만, 매개변수를 고른 경위는 계산 명세가 아니다.
- **세션 전달(T8 발견)**: D.window-mass-env의 $\xi_1$을 글자 없이 적었다(2절 15). D 안에서 격자의 글자가 따로 정의되어 있지 않고 같은 항목의 $\xi_i$(표의 점)와 겹치므로 「그대로 둔다」는 길은 택하지 않았다.
- 2차에서 고친 자리(exact-n20000 (ㅂ) 등)는 I12가 문제 삼지 않았다(꺾쇠만 (2)). 11.2 표 5·6열은 손대지 않았다(세션 sync).
- 읽기 전용 검사기 둘은 수정 뒤 통과했다(`_check_지위서식.py` 「문제 0건」, `불변식_v2.py` 「불변식 통과」). 조립·PDF·생성기는 돌리지 않았고, 라벨 뒤 조사·자리표시자(D.critical-window-rig `[D15:…]`)·돌고 있는 계산 폴더는 손대지 않았다.

## 7. 흔적 검색 결과

검색 범위: `장v2/*.md` 전부(부록 A·B·C·D 포함), `장부_v2.md`, `구조표_v2.md`, `원고_자료/README.md`; 생성물 `의존지도_v2.md`·`원고_자료/재실행표.md`도 함께 돌렸다(`grep -rn -F`, `장v2/_tmp/` 제외). `대조v2/` 아래 검토 보고·사본과 `원고.md`(조립본)의 옛 꼴은 이력이라 세지 않는다.

| 검색한 문자열 | 범위 | 남은 수 | 남은 자리와 까닭 |
|---|---|---|---|
| `49{,}372` | 위 범위 | 1 | 부록D_장7A 39행(고친 문장 안의 「저장된 초기값 … 모두 $49{,}372$개」; 옳게 남음) |
| `34{,}571` | 위 범위 | 1 | 부록D_장7A 39행(새 수) |
| `n=142` | 위 범위 | 0 | — (`장v2/_tmp/독해보고_1114/편집전/부록D_장7A.md`에만 남음 — 수정 전 사본) |
| `buffer` | 위 범위 | 1 | 부록D_장7A 37행(고친 (1) 문장의 「인증서의 `buffer`개 항」; 옳게 남음). `buffer`만큼 더 넓게` 0건 |
| `만큼 더 넓게` | 위 범위 | 0 | — |
| `가장 작게 하는 값` / `몇 후보` | 위 범위 | 0 | — |
| `이 구간이 쓰이는 곳은` | 위 범위 | 0 | — |
| `다시 실행했고, 그 재실행` | 위 범위 | 1 | 장11 47행 6열(세션 sync; 인계 3) |
| `A-int는 재실행` | 위 범위 | 1 | 장11 47행 5열(세션 sync; 인계 3) |
| `앞 인자 $\mathfrak h_0^2` / `\mathfrak h_0^2\theta` | 위 범위 | 0 | — |
| `binary64 사전 오차 해석; 자료 기록·이 글〕 (ㄱ)` | 위 범위 | 0 | — (부록D_장5A 19행은 새 꺾쇠; 장11 29행 5열은 옛 꺾쇠로 남음 — 세션 sync, 인계 2) |
| `재인증 C20도` | 위 범위 | 1 | 부록D_장5A 19행(새 문장) |
| `P_{\mathrm E}` | 위 범위 | 2 | 장부 377·379행(SL — T3 인계 5) |
| `P_{\mathrm A}` | 위 범위 | 2 | 장부 379·380행(SL — T3 인계 5) |
| `\mathrm{Pol}_` | 위 범위 | 6 | 장5A 676·822·824행(T3), 부록D_장5A 92·112·114행(이번) |
| `xi_1]` / `처음 셀 $(0` | 위 범위 | 0 | — |
| `Gamma(5/3)` | 위 범위 | 2 | 부록D_장7A 108행(xcert-partAB 산술 등급의 상수 목록)·199행(이번에 더한 문장) — 둘 다 옳게 있음 |
| `witness-position-bound` | 부록D_장5A | 2 | 1행(exact-n20000 머리)·27행(이번 c50 문장) — 옳게 있음 |
| `zeta-constants` | 위 범위 | 장8 4·장9 2·장11 3·장5B 2·장부 1·README 3 | 삭제한 문장이 라벨을 들고 있던 자리는 부록D_장5B 59행 하나였고, 나머지는 의존 선언·11.2/11.3 표·장부 4절·README 자료 표로 모두 옳게 있음 |
| 생성물(`49{,}372`, `n=142`, `A-int는 재실행`, `P_{\mathrm E}`, `P_{\mathrm A}`, `xi_1]`) | 의존지도·재실행표 | 0 | 라벨·번호·수치(재실행표에 드는 것)를 바꾸지 않아 생성물에 닿는 변경 없음 |

첫 회차에는 진술을 지우거나 옮기지 않았고 식 번호도 바꾸지 않았다. 둘째 회차의 검색(같은 범위, `grep -F`; 둘째 회차 뒤 `_check_지위서식.py` 「문제 0건」, `불변식_v2.py` 「불변식 통과」):

| 검색한 문자열 | 범위 | 남은 수 | 남은 자리와 까닭 |
|---|---|---|---|
| `(5.53)` | 위 범위 | 0 | — (부록D_장5B 69·89행을 $(5.4)$로; 장5B는 T4가 끝냄. 장부·부록 A의 $(5.50)$은 T4 인계 11–13, SL) |
| `(5.4)` | 부록D_장5B | 2 | 69·89행(새 번호; 5B 410·419·431행과 같은 번호) |
| `\mathcal K` | 부록D_장5B | 0 | — (13·14·24행 넷 → $\mathcal I$). 5A의 전역 $\mathcal K_{n,k}(y)$는 부록D_장5A·장5A에 그대로(다른 양) |
| `\mathcal I(` | 부록D_장5B | 1 | 13행(새 이름; 14·24행은 `\mathcal I\Bigl(`·`$\mathcal I$`) |
| `\sigma` | 부록D_장5B | 0 | — (13행 다섯 → $\varsigma$, 22행 문장 고침) |
| `Q_{\mathrm w}`, `Q_2` | 위 범위 | 장부 383·384행만 | 부록D_장5B 0건(74·75행 → $\chi$); 장부는 T4 인계 16·17(SL) |
| `\chi_` | 부록D_장5B | 3 | 74행 1, 75행 2(새 글자; 5B 419–431행과 같음) |
| `\theta_a`, `\theta_b` | 부록D_장5B | 24행 2·5 | D.window-mass-constant의 $\theta$-셀 끝(T4 4: 그대로 둠). band-check(69–91행)는 0건 |
| `\lambda_a` | 부록D_장5B | 69·71·74·75·76·77·78·91행 | 모두 band-check의 새 글자 |
| `\bar\varrho` 단독(첨자 없음) | 부록D_장5B | 3·18·24행 | D.window-mass-constant의 함수 $\bar\varrho(\theta)$(scaled-integrand (마); 다른 양, 그대로). band-check 71·75·78행은 모두 $\bar\varrho_0$ |
| `7.72(\theta_an-1)` | 위 범위 | 1 | 장11 38행 6열(세션 sync; 인계 7) |
| `\varsigma` | 부록D_장7A 51–69행 | 0 | — (열다섯 → $\mathfrak L$). 파일의 나머지 $\varsigma$는 7.3의 $\varsigma_k$·$\varsigma_{\mathrm L}$·$\varsigma_{\mathrm U}$ 등 다른 양 |
| `\mathfrak L` | 부록D_장7A | 53행 3·55행 11·57행 1 | 새 글자. 7B 627–631행의 $\mathfrak L$은 세션이 $\mathfrak r$로 바꿈(세션 인계 1) |
| `\mathfrak o` | 부록D_장7A·장7A·장7B·부록D_장7B | 0 (부록D_장7A) | 22자리 → $\mathfrak D$. 장부 396·398행은 T6 인계 9·12(SL) |
| `\mathfrak D` | 부록D_장7A | 77·87·96·98·100·102행 22자리 | 새 글자(7A 717–733행과 같음) |
| `\gamma` 첨자 없음 | 부록D_장7A | 100행 4, 102행 4($\gamma'_j$), 108행 1(Higham $\gamma_n$ 문맥) | 137·189·220행의 매개변수 $\gamma$ 일곱은 $\Upsilon$로. 100행 넷은 둠(2.2절 끝), 102행은 상수 $\gamma'_j$(다른 양), 108행은 표준 Higham 상수 |
| `\Upsilon` | 부록D_장7A | 137행 3·189행 3·220행 1 | 새 글자(7A 754–818행과 같음). 1.2 $\Upsilon_k$(6장)와 바탕 글자가 같으나 7장 여유 글자(T6 근거) |
| `k_\nu`, `N_\nu`, `\nu=1,2` | 부록D_장7A | 0 | — (145행) |
| `\mathcal G_k` | 부록D_장7A | 1 | 89행(새 연결 구절) |
| `1.5\lambda` | 위 범위 | 0 | — ; `1.5\tau` 부록D_장6 5행 1(새). 부록D_장6의 `\tau` 1건, `\lambda` 0건 |
| `\lambda` | 부록D_장9 | 0 | — (41행 일곱 → $\kappa$). `\kappa` 부록D_장9 7건(모두 41행), 장9 0건 |
| 생성물·11.2 | 장11 38·29·47행 | 3행 | 세션 sync(인계 2·3·7) |

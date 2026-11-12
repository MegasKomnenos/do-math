# -*- coding: utf-8 -*-
"""대조 보고 Q(`대조/의존지도_대조_Q.md`)의 정정 제안(5절)을 의존지도.md 3절·4절에 반영하고, 장부 1.1절에 누락 행을 더한다."""
import io

p = "임시/주차함수_증명/의존지도.md"
s = io.open(p, encoding="utf-8").read()
a = s.index("## 3. Q⋆₂ 경로(8장)의 행")
b = s.index("## 4. 대조 서브에이전트가 확인할 것")

new3 = r"""## 3. Q⋆₂ 경로(8장)의 행

대조 보고 `대조/의존지도_대조_Q.md`(2026-11-12, 프런티어 판 382 기준)를 반영한 판. 26행 모두 기록 원문으로 판정되었고(일치 22, 정정 4, 미확인 0), 미지지 입력·철회·우려·변환표 어긋남은 없다. 검토 정정 넷(정리 P의 ε는 결합 확률, 생산자 CF의 비단조 예는 CF(6674)→CF(6675), §4.6의 "CF"는 CF♮의 오기, r3d0856b §5.5 표의 300·600 행은 (나)의 꼴)을 8장이 반영한다.

| 새 글의 자리 | 진술 | 입력 | 지위 | 비고 |
|---|---|---|---|---|
| 2.5 | 무거운 사슬 공식 $\Pr_N(M\le y-1)=E\prod_{S_i>y}(y/S_i)$ ($N\le2y+1$) | 기존 정리 2.13 = [r39ea75d]/heavy-path-recurrence | 증명 | 4-8 확인: 같은 진술. 8장은 2.5절의 정리 2.13을 가리킨다 |
| 2.11 | Borel 갱신 집합 $H_B(r)$, 갱신 항등식 (G1)(G2) | 용어집 borel-renewal-set([r6a8c8b6]), [r030ffae] §1(주장 ID 없음, 본문 항등식) | 증명 | [re71a735]는 $H_B$를 쓰지 않고 $u(j)=j\mathrm{Bor}(j)=\mathrm{Ren}(j)$를 쓴다 |
| 2.11 | 보조정리 B(갱신 다리): $\delta\le y+2$, $1\le b<c<\delta$ | [re71a735] §4.2(c-lemmaB) | 증명 | |
| 8.1 | 명제 $Q^\star_2$의 진술(프런티어 qstar-second-layer 절과 같음: $k\ge6667$, $\max(2k+103,20001)\le t\le3k$), 정리 R($2k+1\le t\le3k$에서 $A_{t,k-1}[\mathrm{src}_k(t)+\mathrm{FL}_k(t)]=d_{t,k}-KD'_t$) | [r3d0856b] §0.1, 정리 R=[r317d678]/c-thmR = 기존 정리 6.20의 항등식 | 증명 | |
| 8.1 | 보조정리 1(장부), $2k+1\le t\le3k$ | [r3d0856b] §2.1 = [r317d678]/c-ledger | 증명 | |
| 8.1 | 보조정리 2(분할 무게 $w_m$: 망원 비, 단조성, Borel 꼴) | [r3d0856b] §2.2(p-weights); 입력 [r051bfe1]/c-sharp($\mathfrak r_N\le((k+1)/k)^{k-1}$), [r317d678]/c-thmQ2(같은 단조성 논증) | 증명 | |
| 8.1 | 보조정리 3(문턱 예산 $\Lambda_\nu$), $k\ge2$, $1\le\nu\le k$ | [r3d0856b] §2.3(p-budget-identity) | 증명 | |
| 8.1 | 명제 4(예산 분해), 명제 6(꼬리합 꼴), 명제 5(피벗) | [r3d0856b] §2.4–2.5(p-decomposition: c-ledger 위; p-tail-pivot) | 증명 | |
| 8.2 | 명제 S (가)(나)(다), $k\ge3$, $1\le\nu\le k-1$ | [r3d0856b] §3.5(q-sojourn-form); 입력 (다)에 [r845b205]/c-sojourn(체류 꼴), [r98fb348]/c-propN($DD_m=(k+1)W-(k-1)W$의 동일시), [r60a6f55]/size-coupling(머묾 $\ge0$) | 증명(대수 항등식) | 273개 경우($3\le k\le9$, $1\le\nu\le k-1$, $k\le m_0\le2k$)에서 (가)(나)를 정확 유리수로 확인. 명제 S의 $W^{(\ell)}_n=F_n(\ell)-F_{n-1}(\ell-1)$은 새 원고 $\sigma_{n-1}(\ell)$ |
| 8.3 | 명제 FLQ의 진술(프런티어 qstar2-first-layer-tail 절과 같음), 함의 FLQ∧띠⇒$Q^\star_2$ | [r3d0856b] §5.1(q-flq-relation); 입력 [r317d678]/c-ledger, c-thmQ2, [r051bfe1]/c-sharp, 노드 bvtheta-band([r030ffae]/band-node = theorem-B-triple + $n\ge20001$) | 증명(공표 입력 위; band-node는 binary64 상자 검사의 컴퓨터 보조) | 주장문의 "$t=3k$에서 FLQ는 (V)와 r317 정리 T로 성립"은 [r317d678]/c-row3k에 기댐 |
| 8.4 | 명제 T($t<3k$, $\nu\le k-1$; (나)를 문턱 뒤 머묾 질량 하나로 줄임) | [r3d0856b] §5.4(q-t-route); 입력: 명제 S(8.2), 보조정리 2(e)(8.1), 정리 F′([r7e03176]/p-thmF-prime), 따름정리 E([r7e03176]/p-row-averaging-e3)와 행 $2k$ 단조 구간의 $(k-1)c_{2k}(k)\le\tilde g(k)$([r317d678]/c-bk-bound), 정리 S (라)([r845b205]/p-split), 정리 U의 정수판([r845b205]/p-tv-proof; 상수 $C_U=50.62$는 [r845b205] 검토의 위합으로 [r317d678]/c-vcore-quant (2.5)가 채택. 기록 p-thmU의 진술은 50.6), θ=1 체류 법칙([r98fb348]/c-thmS), 크기 결합([r60a6f55]/size-coupling), 무거운 사슬 공식(2.5), r317 정리 T 걸음 3의 τ·두 나무 논증([r317d678]/c-row3k) | 증명(공표 입력 위) | 범위 $k\ge6667$, $\max(2k+103,20001)\le t<3k$. 정리 U의 적분 위합은 배정밀도 |
| 8.4 | 명제 W(창의 생존 상계 $W_b$), $y\ge1$, $y\le N\le2y+1$ | [r3d0856b] §5.4(q-window-survival); 입력 무거운 사슬 공식(2.5) | 증명(공표 입력 위) | |
| 8.5 | 보조정리 1(h-변환), 보조정리 2(얼린 볼록성 = [r845b205]/c-fixed-chain-convexity), 정리 A | [re71a735] §3.1(p-frozen-split: heavy-path-recurrence·c-fixed-chain-convexity 위; p-thmA) | 증명 | |
| 8.5 | 정리 B, 보조정리 3(Borel–Tanner 방문), 보조정리 4·5(정리 C 안), 보조정리 N, 정리 C | [re71a735] §3.2(p-thmB, p-lemma3, c-lemmaN, p-thmC) | 증명 | 보조정리 N은 생산자 셈 근거의 정정 |
| 8.5 | 명제 M♮(CF♮$\ge DDL_2$, $k\ge6667$에서 감소) | [re71a735] §3.3(c-propM-complete) | 증명(여섯 단계; $J_1',J_2'$는 30자리 수치 적분) | 생산자의 명제 M(CF의 단조성)은 거짓이고 쓰이지 않음. 비단조 예: CF(6674)=0.143725→CF(6675)=0.143787 |
| 8.5 | 보조정리 SS(상해 원리), 정리 S′($y\ge6666$, $1\le d\le y+2$에서 $\mathfrak s_d(y)\le\min(1,1.15(y+d)/d^{3/2})$) | [re71a735] §3.4(p-lemmaSS, p-thmSprime) | 증명 | 상수 문턱 $2/\sqrt\pi=1.12838$ |
| 8.5 | 명제 X·D | [re71a735] §3.5(p-propX, p-propD); 입력 θ=1 체류 법칙([r98fb348]/c-thmS), 벌크 점질량 상계([r7e03176]/p-bulk-point-mass), 정리 S′(8.5) | 명제 X: 증명(공표 입력 위; 벌크 점질량 상계는 $n\le20000$ 정수 인증과 right-bulk-increase에 기댐). 명제 D: 증명(정리 A의 따름) | |
| 8.5 | 정리 P(점질량의 사슬 표현), 보조정리 F | [re71a735] §3.6(p-thmP, p-lemmaF) | 증명 | ε는 결합 확률로 읽는다(검토 정정). 보조정리 F는 최종 증명에 쓰이지 않고 그 다듬은 꼴(보조정리 R)이 쓰임 |
| 8.6 | 보조정리 J, R, R′($x$-감소: $y\ge6669$, $x\in[1.04,2^{2/3}]$, $\delta=xy^{2/3}\ge562$) | [re71a735] §4.2(c-lemmaJ, c-lemmaR); 보조정리 R은 size-coupling | 증명 | |
| 8.6 | 명제 U($\nu$에 무관한 머묾 상계 $\mathcal U(k;\bar\nu)$, $k$에 감소) | [re71a735] §4.3(c-propU); 입력 θ=1 체류 법칙, 벌크 점질량 상계, 정리 S′, 명제 X | 증명 | 검토 단서: $S$를 $[\eta_k,0.6]$으로 바꾸는 단계는 $\eta_k\ge A_c/c$일 때만 정당하고 쓰인 세 $\bar\nu$에서 성립(한 줄 보충) |
| 8.6 | 상쇄 보조정리, 명제 L(가족별 하계, $k$에 증가) | [re71a735] §4.4(c-propL); 입력 명제 T·W(8.4), 정리 S′, 명제 M♮ | 증명 | 첫 도달 몫 $3\nu/k$와 줄기 하계 손실 $3\nu/k$의 첫 차수 상쇄 |
| 8.6 | (나)의 네 가족 검사(시작점 6668·8065·9551·9705; 여유 +0.589·+0.505·+0.467·+0.205), (가)의 창 밖·창 안·가장자리 | [re71a735] §4.5–4.6(c-na, c-ga); 입력: 명제 S·T·W(8.2·8.4), 정리 C·명제 M♮·정리 S′(8.5), 보조정리 J·R·R′·명제 U·명제 L(8.6), 창 밖 논증 [r3d0856b]/q-flq-a-window(§5.5), right-bulk-increase(노드 s02738f…-right-bulk-increase, [r8a9b11e]/peer-theorem-W), 중앙 증가([rce3dc75]/central-gap-closed), $n\le20000$ 정수 인증의 최빈 위치 상계(출처 후보 [rce3dc75]/integer-certificate, [r19de912]/right-half-unimodal-finite, mode-formula-crosscheck; 8장 집필 때 확정), 따름정리 E·정리 F′·벌크 점질량 상계·θ=1 체류 법칙 | 비형식(공표 입력 위; 시작점 검사는 배정밀도, 구간 인증 아님) | (가) 최소 여유 +0.236(1a, $\delta=2$). 1a는 30자리 독립 재계산. §4.6의 "CF"는 CF♮의 오기 |
| 8.6 | 정리 FLQ(c-flq; 해 sol-flq) | [re71a735] §4.7; 입력 c-na, c-ga(8.6); $t=3k$는 노드 prob-first-layer-tail(V)과 [r317d678]/c-row3k(정리 T; 상수 $c(k)$는 [r317d678]/c-vcore-quant) | 비형식(공표 입력 위; 시작점 검사 배정밀도, 구간 인증 아님) | 범위 $k\ge6667$, $\max(2k+103,20001)\le t\le3k$ |
| 8.6 | r317 정리 T($t=3k$ 행의 FLQ): $(\star)(3k)\ge0.18w_k$ 꼴의 논증 | [r317d678]/c-row3k = 기존 정리 6.20의 둘째 문장(6.8에 있음), (V)=노드 prob-first-layer-tail | 비형식(정리 6.18에 기댐) | 8.6은 6.8의 정리 6.20을 가리킨다 |
| 8.7 | 사슬 (1) FLQ ∧ 띠 ⇒ $Q^\star_2$: [r3d0856b]/q-flq-relation(관계 s3ecdd70…-rel-flq-band-implies-qstar2). (2) V ⇒ V*: [raad7e6d]/p-ladder(관계 s7a2a959…-rel-v-implies-vstar; 기존 명제 6.17 사다리). V 자체: [r845b205]/p-rel-core-v(관계 sb3bdcc7…-rel-core-implies-v; 전제 prob-first-layer-core=[r317d678]/sol-vcore, ul-near-window, ul-far-window, ul-small-k-bulk; 기존 6.7). (3) source-side ∧ V* ∧ $Q^\star_2$ ⇒ qstar-columns-from-3131: [raad7e6d]/p-rel-qstar(관계 …-rel-vstar-implies-qstar). source-side: [r79ee9e0]/c-src-plus(해 sol-source-side; 기존 명제 6.16; 극 영역은 [rf451d83] binary64 인증서). (4) qstar-columns-2001-3130 ∧ from-3131 ⇒ one-step-local: [r207f124]/qstar-split-cover(관계 rel-qstar-column-split); 2001–3130: [r207f124]/qstar-finite-range(해 sol-qstar-columns-2001-3130; 컴퓨터 보조 증명, binary64와 Part B 인증 자료; 기존 6.5). (5) one-step-local ⇒ $W_L^\flat$: [r3172894]/rel-qstar-wlflat(관계 rel-qstar-implies-wlflat; 기존 명제 6.14와 6.5절 끝 문단). (6) 이후 $W_L^\flat$⇒$W_L$⇒L⇒T, 네 위치쌍 ⇒ 뿌리: 7.5와 같음 | 프런티어 판 376(판 382에서 같음, 대조 Q; 판 377–382의 기록 여섯은 노드·관계·해를 등록하지 않음) | 증명(입력의 지위를 물려받음: 띠의 binary64 상자 검사, 원천 쪽 극 영역의 binary64 인증서, 열 2001–3130의 컴퓨터 보조 증명) | 4-9 확인: 여섯 고리 모두 기록에 관계가 있고 supported, 전제 모두 established |
| 8.8 | 정리 FO(첫 차수 생존 법칙 $1-\mathfrak s_u(y)=\mathcal I_1u^{3/2}/y\,(1+o(1))$) | [re71a735] §6(c-first-order-survival) | 증명 | FLQ의 증명에는 쓰이지 않음(이해) |

"""
s = s[:a] + new3 + s[b:]

# 4절 항목 갱신
old11 = "11. 두 경로의 의존 기록 전부에 대해 프런티어(판 376 이후 현재 판 포함)에 concern이나 철회가 붙었는지. 현재 판 번호를 함께 적는다."
assert s.count(old11) == 1
s = s.replace(old11, "11. 두 경로의 의존 기록 전부에 대해 프런티어(판 376 이후 현재 판 포함)에 concern이나 철회가 붙었는지. 현재 판 번호를 함께 적는다. **결과(대조 P·Q, 2026-11-12): 현재 판 382. 의존 기록 전부 concerns 빈 목록, 노드 절에 철회·우려 표시 없음. 판 377–382의 기록 여섯은 노드·관계·해를 등록하지 않음.**")
old13 = "13. [re71a735] §4.8의 \"쓰인 입력과 그 지위\" 표가 [rb1d8cd5](flat-core)의 명제 1이나 다른 주장을 입력으로 쓰는지. 쓰면 어느 주장 ID인지."
assert s.count(old13) == 1
s = s.replace(old13, old13 + " **결과(대조 Q): 쓰지 않음.** 2.11의 조건부 행은 삭제했다.")
old14 = "14. [re71a735]가 '보렐 갱신 면적' $\\mathfrak A_D$([rb1d8cd5]/borel-renewal-area)을 쓰는지."
assert s.count(old14) == 1
s = s.replace(old14, old14 + " **결과(대조 Q): 쓰지 않음.**")
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("의존지도 3절·4절 갱신")

# 장부 1.1 보충
p2 = "임시/주차함수_증명/장부_기호용어이름.md"
t = io.open(p2, encoding="utf-8").read()
old = r"| $DD_m=(k+1)s_d(k+1)-2ks_d(k)+(k-1)s_d(k-1)$, $d=m-k+1$ | [re71a735] | $DD(m-1,k-1)$ | [re71a735] §1이 같음을 적음. 8장은 $DD_m:=DD(m-1,k-1)$로 두고 그 자리에서 밝힌다 |"
assert t.count(old) == 1
t = t.replace(old, r"| $DD_m=(k+1)s_d(k+1)-2ks_d(k)+(k-1)s_d(k-1)$, $d=m-k+1$ | [re71a735], [r3d0856b](명제 S의 $DD_m$, 같은 정의) | $DD(m-1,k-1)$ | [re71a735] §1이 같음을 적음. 8장은 $DD_m:=DD(m-1,k-1)$로 두고 그 자리에서 밝힌다 |" + "\n" + r"| $W^{(\ell)}_n:=F_n(\ell)-F_{n-1}(\ell-1)$ ($F_n(\ell)=\Pr_n(M\le\ell)$ 규약) | [r3d0856b] 명제 S, [re71a735] §2 | $\sigma_{n-1}(\ell)$ | $=s_n(\ell+1)-s_{n-1}(\ell)$. 명제 S의 Stays와 경계항이 이 기호로 정의된다(대조 Q 5절 (사)) |")
io.open(p2, "w", encoding="utf-8", newline="\n").write(t)
print("장부 1.1 보충")

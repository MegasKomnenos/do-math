# 수리 전체23 ZL — 묶음 4: 장부 3절의 새 행, 4절 머리말, 6절, 7절. 쌍마다 그 행을 읽고 손으로 정한 것.
import os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "수리전체23_ZL_apply.py"), encoding="utf-8").read())
NL = chr(10)
E = [
# 3절 새 행 「열 질량」(R5 5절, Z5 인계 7) — 「열 값」 행 바로 뒤
(r"9.3의 첫 층 열 값 — 명제 $\mathsf{FLQ}$의 이름) | 5.5 | 같음(2026-11-15 I14-6으로 Q2의 「쓰지 않는」 열에서 옮겨 등재) |",
 r"9.3의 첫 층 열 값 — 명제 $\mathsf{FLQ}$의 이름) | 5.5 | 같음(2026-11-15 I14-6으로 Q2의 「쓰지 않는」 열에서 옮겨 등재) |" + NL +
 r"| 열 질량 | 한 수준의 질량을 첫 층의 크기에 걸쳐 더한 것 — 수준 $\ell$의 열 질량 $\sum_mc_m(\ell)$(6.5절 머리 문단이 정의하고 같은 절이 V-핵심의 보존량 $2$를 풀이할 때 쓴다; 한 행에서 읽는 값인 「열 값」과 다른 낱말 — 2026-11-17 23차 R5 5절·Z5·ZL 등재) | 6.5 | 같음 |"),
# 3절 새 행 「이 글의 재계산」(Z10 인계) — 「기록의 첫째 작성자 …」 행 바로 뒤
(r"2026-11-15 8차 N12-3·Y11 (ㄱ)·YL 등재) | 10.1 | —(새 낱말; 기록 폴더의 producer·peer·review) |",
 r"2026-11-15 8차 N12-3·Y11 (ㄱ)·YL 등재) | 10.1 | —(새 낱말; 기록 폴더의 producer·peer·review) |" + NL +
 r"| 이 글의 재계산 | 이 글을 쓰며 기록의 계산과 따로 새로 한 계산(부록 D 항목의 「산술 등급」·「독립 재계산」 줄과 10.2절이 쓰는 말이고 10.1절이 풀어 준다 — 기록의 검토를 거치지 않았으며 근거는 자료 묶음의 코드와 출력이다; 2026-11-17 23차 R10 [10.1-가]·Z10·ZL 등재) | 10.1 | —(새 낱말) |"),
# 4절 머리말 (R13 장부-7)
(r"그 라벨은 중괄호 없이 `(9:…)`로 적는다 — 뒤의 장 번호 치환과 무관하다.",
 r"그 라벨은 중괄호 없이 `(9:…)`로 적는다 — 뒤의 장 번호 치환과 무관하다. `(10:…)`는 그 뒤의 장 번호 치환(옛 10장→9장, 옛 11장→10장) 전의 옛 10장(FLQ 경로; 현행 9장)에서 빼거나 다른 절로 옮기며 이름을 바꾼 진술의 옛 라벨이다(스무 행). 옛 10장의 진술 가운데 살아 있는 것은 제자리의 `{{9:…}}`이거나 절을 옮기며 라벨을 바꾼 `{{6:old-8-19}}`–`{{6:old-8-23}}`·`{{6:old-8-25}}`·`{{2:supersolution}}`이고, 그 대응은 이 표의 뺌 행 주석과 대응표의 「옮김」 행이 적는다(2026-11-17 23차 R13 [장부-7]·ZL — 의존지도 1.1절이 옮김의 근거로 이 머리말을 가리킨다)."),
# 6절 (R2 5절 2)
(r"(바탕 글자만 쓰는 이탤릭; 3.1의 해싱 극한 $X$는 예외)", r"(바탕 글자만 쓰는 이탤릭; 3.1절이 정의하는 극한 $X$는 예외)"),
# 7절 (R10 C-마)
(r"| $\mathfrak a_j$, $t_v$, $H_s(F)$, $Z_k(F)$, $\mathsf x_k$, $Q_{k-1}(x)$, $\Pr^\sigma_{n,k}$ | [rbeae3a3] |",
 r"| $\mathfrak a_j$, $t_v$, $H_t(F)$, $Z_k(F)$, $\mathsf x_k$, $Q_{k-1}(x)$, $\Pr^\sigma_{n,k}$ | [rbeae3a3] |"),
(r"| 글자체; $s\to t$; 글자; 없음; 글자체; 첨자 용량↔수준 한 칸; 같은 무게의 숲 판(기댓값 꼴 $\mathbb E_{n,k}$ L48·56·68; 공간만 다름) |",
 r"| 글자체; $s\to t$; 글자와 나무 크기 $s\to t$; 없음; 글자체; 첨자 용량↔수준 한 칸; 같은 무게의 숲 판(기댓값 꼴 $\mathbb E_{n,k}$ L48·56·68; 공간만 다름) |"),
(r"| $\mathbb E_L$ | [r9bf2dc6] | $E_L$ | 글자체 |", r"| $\mathbb E_m$ | [r9bf2dc6] | $E_L$ | 글자체; 숲 크기 $L\to m$ |"),
(r"| $\mathrm{pos}_L$ | [r5bbc534] | $e$(마지막 차 $L$이 주차한 자리) | 글자; 첨자 $L\to n$ |", r"| $\mathrm{pos}_n$ | [r5bbc534] | $e$(마지막 차 $L$이 주차한 자리) | 글자; 첨자 $L\to n$ |"),
# 7절 (Z5 2)
(r"| $\mathfrak w_n(t)$, $\tilde{\mathfrak w}_n(t)$ | [r4868e30]; [rb6a2cd0], [rcb2e2d4]; [r33475a7] | $\varpi_n(N)$; $\varpi_n(s)$; $\mathcal T_n(t)$, $\tilde\pi_n(t)$ | 인수 $N\to t$; $s\to t$; 없음 |",
 r"| $\mathfrak w_n(t)$ | [r4868e30]; [rb6a2cd0], [rcb2e2d4]; [r33475a7] | $\varpi_n(N)$; $\varpi_n(s)$; $\mathcal T_n(t)$(그 기록의 정규화 $\tilde\pi_n(t)=\mathcal T_n(t)/p_n$은 이 글에서 글자 없이 $\mathfrak w_n(t)/p_n$) | 인수 $N\to t$; $s\to t$; 없음 |"),
# 7절 새 행 (R7b 5절 6 — 기록 원문 확인: [raad7e6d] exposition L72·94·99, [r317d678] L37–39·168·330, [r3d0856b] L56·57)
(r"| $w_m$, $\mathfrak u_n$ | [r3d0856b], [re71a735] | $w_m=\binom{t-1}mp_mA_{t-1-m,k-1}/A_{t,k-1}$, $N_{thr}$ | $t\to n$ |",
 r"| $w_m$, $\mathfrak u_n$ | [r3d0856b], [re71a735] | $w_m=\binom{t-1}mp_mA_{t-1-m,k-1}/A_{t,k-1}$, $N_{thr}$ | $t\to n$ |" + NL +
 r"| $w_m$, $\mathfrak u_n$, $\mathrm{Left}_n$, $\mathrm{Quad}_n$, $\mathrm{Stem}_n$, $\mathrm{KD}^\prime_n$ | [raad7e6d]; [r317d678]; [r3d0856b] | $w_m=\varpi_t(m+1)/(t\,A_t)$, $\mathrm{Left}_t$, $\mathrm{Quad}_t$, $\mathrm{Stem}_t$ (L72·94·99); $w_m$, $N_{thr}=w_{t-k}A_{t-k,k}/p_{t-k}$, $\mathrm{Left}_t$, $\mathrm{Quad}_t$, $\mathrm{Stem}_t$, $KD^\prime_t$ (L37–39·168·330); $\mathrm{Quad}_t$, $\mathrm{Stem}_t$, $KD^\prime_t$ (L57) | $t\to n$; [raad7e6d]의 $w_m$은 같은 무게($\varpi_t(m+1)/(tA_t)=\binom{t-1}mp_mA_{t-1-m,k-1}/A_{t,k-1}$); $N_{thr}\to\mathfrak u_n$은 글자($A_{t-k,k}/p_{t-k}=s_{t-k}(k+1)$); 나머지는 없음(확인) — 2026-11-17 23차 R7b 5절 6·ZL |"),
]
apply(os.path.join(HERE, "..", "..", "장부_v2.md"), E)

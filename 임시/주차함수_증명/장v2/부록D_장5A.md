### D.{{D:exact-n20000}} 모든 $n\le20000$의 단봉성을 이루는 네 조각의 정수 구간 인증과 증인 위치 (정리 {{5:old-5-1}}, 명제 {{5:witness-position-bound}})

**확인하는 진술.** (ㄱ) $12\le n\le10000$에서 $b_{n,0}<b_{n,1}<\dots<b_{n,k_n-1}$. (ㄴ) $10001\le n\le20000$에서 $b_{n,0}\le b_{n,1}\le\dots\le b_{n,k_n}$. (ㄷ) $16\le n\le20000$에서 $b_{n,k_n-1}<b_{n,k_n}$(정리 {{4:old-4-5}}의 유한 범위; 그 계산 명세는 4장의 부록 D 항목에 있다). (ㄹ) $5\le n\le20000$, $(n-1)/2\le\ell\le n-3$의 모든 위치에서 $b_{n,\ell}\le b_{n,\ell+1}$이 성립하거나 $b_{n,\ell}>b_{n,\ell+1}$, $b_{n,\ell+1}^2>b_{n,\ell}b_{n,\ell+2}$, $b_{n,\ell}+b_{n,\ell+2}<2b_{n,\ell+1}$이 함께 성립하며, 각 행에서 앞의 종류의 위치가 모두 뒤의 종류의 위치보다 앞에 있다. (ㅁ) $n\le300$의 모든 행은 정확한 정수로 단봉이다. (ㅂ) $50\le n\le20000$에서 $n+1-\ell^\ast_n-0.59963(n+1)^{2/3}-1.24847(n+1)^{1/3}\in[0.85,1.99]$.

**식.** (ㄱ) 열 $k$의 지수 생성함수 $\sum_n\mathfrak a_nx^n$을 지수 공식의 세 급수로 계산한다. 코드의 변수 `T_k`는 이 글의 절단 나무 함수 $T_{\le k}(x)$, `G_k`는 $e^{T_{\le k}(x)}$, `Q_k`는 $\sum_{j<k}p_jx^j/j!$, `H_k`는 미분방정식 `H_k' = k Q_k H_k + k (G_k - Q_k)`의 해, `E_k = G_k/(1-H_k)`는 $\sum_n\mathfrak a_n(\mathrm{rc}\,x)^n$($\mathrm{rc}$는 수치 범위를 맞추는 양의 유리 반지름), `g_n`·`h_n`·`e_n`은 그 세 급수의 $x^n$ 계수이고, 이들은 모든 항이 음이 아닌 세 재귀로 계산된다. 비교식은 용량 $k-1,k,k+1$의 세 열에서 `e_n^{(k+1)} - 2 e_n^{(k)} + e_n^{(k-1)}` $=\frac{\mathrm{rc}^n}{n!}d_{n,k}$다. (ㄴ) 정리 {{2:old-2-6}}을 $n!$로 나눈 $n\,\mathfrak a_n=\sum_{j=1}^n\min(j,k)\,\mathfrak a_{j-1}\mathfrak a_{n-j}$와 판정 $\mathfrak a^{(k+1)}_n+\mathfrak a^{(k-1)}_n\ge2\mathfrak a^{(k)}_n$(용량 $k-1,k,k+1$의 세 열). (ㄹ) 미달 수 $A^c_{n,\ell}$의 양의 선형 재귀($k=\ell+1$, $k+1\le n\le2k+1$)
$$
A^c_{n,k-1}=\sum_{i=0}^{n-k-1}\binom{n-1}i(n-k-i)p_ip_{n-1-i}+\sum_{i=0}^{n-k-2}\binom{n-1}i(k+i+1)p_iA^c_{n-1-i,k-1}
$$
의 정규화(코드의 `s_m`은 $p_m/(m!\,\mathrm{rc}^m)$, `e_{n,k}`는 $A^c_{n,k-1}/(n!\,\mathrm{rc}^n)$)와 $b_{n,k-1}/(n!\,\mathrm{rc}^n)=$ `e_{n,k-1} - e_{n,k}`. 모든 항이 음이 아니므로 하한끼리·상한끼리 계산하면 참값을 담는 구간이 전파된다. (ㅁ) 정리 {{2:old-2-6}}의 마지막 차 재귀를 정수로 계산한 전 행. (ㅂ) 각 행의 (ㄹ) 자료에서 첫 번째 엄격 감소 위치가 봉우리 $\ell^\ast_n$이다.

**알고리즘.** (ㄱ) 고정소수점 $2^{144}$(열 인증)·$2^{128}$(행 인증)의 정수 구간 $[L,U]$로 세 급수의 계수를 계산한다. 합성곱은 분할 정복과 Kronecker 포장으로 정확히 하고, 몫은 끝점마다 내림·올림한다. 판정은 정수 비교 $\mathrm{lo}(e^{(k+1)}+e^{(k-1)})-2\,\mathrm{hi}(e^{(k)})>0$이다. 용량 $k\le500$은 열 단위로 모든 $n\ge2k+1$을 덮되 큰 $n$은 띠 전파 $10A_{n,k}\ge17A_{n,k-1}$로 닫고, $501\le k\le4999$는 행 단위로 $n\le10000$을 덮는다. (ㄴ) 첫째 프로그램은 56비트 가수의 정수 구간으로 $n\,\mathfrak a_n$의 재귀를 계산하고(항 하한은 내림, 상한은 올림, 128비트 합산 뒤 $n$으로 나눔) 비엄격 판정 $\mathrm{lo}+\mathrm{lo}\ge2\,\mathrm{hi}$를 쓴다. 독립 프로그램은 IEEE binary64의 방향 반올림(아래 끝 열은 내림, 위 끝 열은 올림)으로 같은 재귀를 계산하고 엄격 판정을 쓴다. (ㄹ) 각 위치에서 세 항의 구간 $[l_i,u_i]$($i=0,1,2$)를 보고 $u_0\le l_1$이면 감소의 전제가 배제된 것으로, 아니면 $l_1^2>u_0u_2$로 엄격 로그오목을, $u_0+u_2<2l_1$로 엄격 오목을, $u_1<l_0$로 엄격 감소를 판정한다. 어느 판정도 내리지 못하면 미결로 센다. 값은 $2^{-110}$ 단위의 128비트 정수 구간이고 재귀의 모든 곱과 합은 256비트 정수로 정확히 누적하며 마지막 나눗셈 한 번에서만 내림·올림한다. 가중치(합 지표에 $k+1$을 더한 정수와 `s` 값의 곱)는 열마다 정확히 미리 곱한다. 각 행에서 전제 배제 위치의 마지막 첨자가 첫 엄격 감소 위치보다 앞인지를 따로 검사한다. (ㅁ) Python 정수로 용량 $1$ 이상 $300$ 이하의 모든 열을 계산해 행을 만들고 단봉성과 엄격 증가를 정확히 비교한다. (ㅂ) 행별 자료의 봉우리 열을 읽어 두 항 공식과의 차를 계산한다.

**범위.** (ㄱ) 열 인증 $k\le500$: 직접 비교 $19{,}982{,}310$개와 띠 비교 $10{,}103{,}865$개($k=161$–$500$), $k=121$–$160$은 $386{,}260$·$198{,}790$개; 행 인증 $501\le k\le4999$, $n\le10000$: 비교 $20{,}245{,}500$개. (ㄴ) $10001\le n\le20000$, $1\le\ell\le k_n-1$: 비교 $74{,}995{,}000$개. (ㄹ) $5\le n\le20000$: 위치 $99{,}970{,}002$개. (ㅁ) $n\le300$ 전 행. (ㅂ) $50\le n\le20000$의 $19{,}951$개 행.

**산술 등급.** (ㄱ)(ㄴ 첫째 프로그램)(ㄹ)(ㅁ) 정확 정수·유리수(정수 구간, 부동소수 없음). (ㄴ 둘째 프로그램) 방향 반올림 구간(binary64). 정리의 결론은 정수 프로그램만으로 따르며 binary64 프로그램은 엄격성의 상호 검산이다.

**결과.** (ㄱ) 실패 $0$. 최소 상대 여유는 열 인증에서 $k=500$, $n=1001$의 $1.38\times10^{-5}$, 행 인증에서 $(n,k)=(9999,4999)$의 $2.255\times10^{-7}$. (ㄴ) 두 프로그램 모두 실패 $0$. 최소 여유는 $(n,k)=(19999,10000)$에서 첫째 프로그램 $2.636\times10^{-7}$, 독립 프로그램 $2.636\times10^{-7}$($\ell=9999$; 첫째 프로그램의 자료에서 $(19999,9999)$는 $2.638\times10^{-7}$), 구간의 상대 폭은 $10^{-11}$ 이하다. (ㄹ) 전제 배제 $94{,}192{,}042$곳, 엄격 로그오목 $5{,}777{,}960$곳(그 전부에서 엄격 오목과 엄격 감소도 인증), 미결 $0$, 모든 행에서 전제 배제 위치가 엄격 감소 위치보다 앞. 최대 결손 구간 폭 $15$단위($2^{-110}$ 단위). (ㅁ) 모든 행이 단봉이고, $b_{n,0}<\dots<b_{n,k_n-1}$은 정확히 $n\in\{5,7,9,11\}$에서만 깨진다. (ㅂ) 차는 $50\le n\le900$에서 $[0.890,1.987]$, $901\le n\le20000$에서 $[0.851,1.876]$이다.

**독립 재계산.** (ㄱ) 원 인증의 코드와 다른 재귀의 독립 프로그램이 $k=121,128,140,160,161$ 열과 $k=501,2500,4999$ 행에서 같은 판정과 같은 최소 여유를 냈고, 검토가 제3의 구현으로 $k=150,200$ 전체 열과 행 표본 7개를 재확인했다. (ㄴ) 두 프로그램이 서로 독립이고 모든 열에서 같은 판정을 냈다. 검토가 두 프로그램을 다시 빌드해 열 표본을 바이트 단위로 재현했다. (ㄹ) 첫 Python 정수 구간 프로그램($n\le2000$, $\mathrm{rc}=2718281828/10^9$, 정밀도 $2^{-96}$)과 독립 C 프로그램($n\le20000$, $\mathrm{rc}=87/32$)이 $n\le2000$의 $997{,}002$개 위치에서 바이트 단위로 같은 분류를 냈다. 검토가 C 프로그램을 다시 빌드해 $n\le20000$ 전체를 재실행했고 행별 자료가 바이트 단위로 같았다. 정리 {{5:old-5-2}}의 방법으로 $n\le20000$을 다시 계산한 결과도 $19{,}996$개 행의 (위치 수, 증가 수, 마지막 증가 위치)에서 불일치가 없다(D.{{D:c50}}). (ㅁ) 검토가 별도의 정확 정수 구현으로 같은 결과를 얻었고, $n\le6$은 모든 선호 목록의 전수 주차와 일치했다. (ㅂ) 검토가 같은 자료에서 재계산했다.

**자료.** 경로 접두는 `records/`다. (ㄱ) `rc9aee436a1c34c438719b6c5d5ed79b5/evidence/producer/code/positive_columns.py`, `evidence/producer/output/certificates-121-160.json`, `evidence/peer/code/extend_columns.py`, `rowwise_left.py`, `indep_lastcar.py`, `evidence/peer/output/ext-161-360.json`, `ext-361-442.json`, `ext-443-500.json`, `rw-10000-a.json`–`rw-10000-g.json`, `summary-all.json`, `review/evidence/rerun-k500.json`, `rev-col-k150.json`, `rev-col-k200.json`. (ㄴ) `r15df76b551d04c339b06b6f48cdb0891/evidence/producer/code/leftcert.c`, `leftcert_build1.c`, `leftcert_build2.c`, `evidence/producer/run/left20000_k501-2875.tsv`, `left20000_k2876-5250.tsv`, `left20000_k5251-7625.tsv`, `left20000_k7626-9999.tsv`, `evidence/producer/run2/small20000_k2-250.tsv`, `small20000_k251-500.tsv`, `center20000_k5001-8000_center.tsv`, `center20000_k8001-10000_center.tsv`, `evidence/peer/code/pcertv.c`, `evidence/peer/run/pv_k2-2501.tsv`, `pv_k2502-5001.tsv`, `pv_k5002-7501.tsv`, `pv_k7502-10000.tsv`, `evidence/peer/checks/compare_runs.json`, `coverage_producer.json`. (ㄷ) `rce3dc75b9fc040fd8925fa3a73b0d753/evidence/peer/icert/icert.c`, `out_8_10000.txt`, `icert_summary.json`. (ㄹ) `r19de912cab694b4f803d322834e9500a/evidence/peer/cert/qr_cert2.c`, `gen_s.py`, `v2run20000-rows.tsv`, `v2run20000-summary.json`, `v2run20000.log`, `class-hashes.txt`, `evidence/producer/certify_right_half.py`, `right-half-certificate-2000.json`, `evidence/peer/checks/producer-rerun-summary.json`, `review/evidence/peer-rerun/`. (ㅁ) `r6373c701c0bb48fca5803f5578c75e60/evidence/peer/code/exact_rows.py`, `evidence/peer/output/exact-rows-300.json`, `review/evidence/code/my_exact_rows.py`. (ㅂ) `r19de912cab694b4f803d322834e9500a/evidence/peer/checks/mode_offset.py`, `mode_offset.json`(입력은 `v2run20000-rows.tsv`의 봉우리 열).

**출처.** [rc9aee43] §5–6, `review/feedback.md`; [r15df76b] §3–5, §7; [rce3dc75] §8.2; [r19de912] §3, §9, `review/feedback.md`; [r6373c70] §3.1.

### D.{{D:c50}} $20001\le n\le50000$의 오른쪽 절반 인증 C50과 $n\le20000$의 재인증 C20 (정리 {{5:old-5-2}})

**확인하는 진술.** $20001\le n\le50000$, $(n-1)/2\le\ell\le n-3$의 모든 위치에서 $b_{n,\ell}<b_{n,\ell+1}$ 또는 $b_{n,\ell+1}^2>b_{n,\ell}b_{n,\ell+2}$가 인증되고, $\lceil(n-1)/2\rceil\le\ell\le n-2$의 모든 인접 쌍에서 $b_{n,\ell}<b_{n,\ell+1}$ 또는 $b_{n,\ell}>b_{n,\ell+1}$이 인증되며, 각 행의 마지막 증가 위치가 $n-2-\max\{m\ge171:m^{3/2}+9m\le n\}$ 이상이다. 같은 프로그램으로 $5\le n\le20000$을 계산한 결과가 D.{{D:exact-n20000}}(ㄹ)의 행별 자료와 일치한다.

**식.** 최대 나무 법칙 $\pi_n(s)=\binom ns s^{s-1}p_{n-s}/p_n=\mathrm{Bor}(n+1-s)\,\mathrm{hB}(s)/\mathrm{hB}(n+1)$($\mathrm{hB}(x):=e\,\mathrm{Bor}(x)$를 실수로 연장한 것)와 두 재귀($n\le2k+1$)
$$
s_n(y)=\pi^0_n(y)+\sum_{t=k+1}^{n}\pi_n(t)\,\frac kt\,s_{t-1}(y),\qquad
c_n(y)=\sum_{t=k+1}^{n}\frac{\pi_n(t)}t\bigl[s_{t-1}(y+1)+y\,c_{t-1}(y)\bigr]
$$
의 $\mathrm{hB}$-정규화 꼴(코드의 `Y`, `Z`; 이 글의 $s_n(y)$, $c_n(y)$에 $\mathrm{hB}(n+1)$을 곱한 것) $Y^{(k)}_m=\mathrm{hB}(m+1)-\sum_{s=k+1}^m\mathrm{Bor}(m+1-s)\mathrm{hB}(s)+k\sum_{s=k+1}^m\mathrm{Bor}(m+1-s)Y^{(k)}_{s-1}/s$, $Z^{(k)}_n=\sum_{s=k+1}^n\mathrm{Bor}(n+1-s)\bigl[Y^{(k+1)}_{s-1}+kZ^{(k)}_{s-1}\bigr]/s$. 비교는 $Z$로 한다($b_{n,k}\le b_{n,k+1}\iff Z^{(k)}_n\le Z^{(k+1)}_n$; 공통 인자 $\mathrm{hB}(n+1)/p_n$이 양수). 유일한 뺄셈은 $\mathrm{hB}(m+1)-\sum_s\mathrm{Bor}(m+1-s)\mathrm{hB}(s)$이다.

**알고리즘.** 표 $\mathrm{Bor}(j)$, $\mathrm{hB}(x)$($1\le j,x\le120010$)를 45자리로 계산해 올바르게 반올림한 binary64로 저장한다. 재귀를 열 단위로 binary64로 계산하고, 사전 오차 해석으로 각 값의 상대 오차 한계 $\mathrm{eps}$을 함께 전파한다. 규칙은 표 값 $1.01u$, 정수 나눗셈 $(\mathrm{eps}+2.02u)(1+10^{-6})$, 길이 $L$의 음이 아닌 내적 $\mathrm{eps}_{\max}+\gamma_{m(L)+2}$($m(L)=54+\lceil L/512\rceil$회의 반올림), 두 음이 아닌 수의 합 $\max(\mathrm{eps}_1,\mathrm{eps}_2)+u$, 유일한 뺄셈은 절대 오차 한계로 처리하고 결과가 그 한계의 두 배보다 작으면 중단, 한계 계산 자체의 반올림 $10u$이다($u=2^{-53}$). 판정은 $\mathrm{Zh}^{(k+1)}(1-\mathrm{eps}'-4u)>\mathrm{Zh}^{(k)}(1+\mathrm{eps}+4u)$(엄격 증가), 그 반대(엄격 감소), $\mathrm{lo}(Z^{(k+1)})^2(1-4u)>\mathrm{hi}(Z^{(k)})\mathrm{hi}(Z^{(k+2)})(1+4u)$(엄격 로그오목)이고, 어느 것도 아니면 미결이다. 행마다 봉우리까지 엄격 증가·그 뒤 엄격 감소인지와 마지막 증가 위치가 $n-2-\mathfrak m(n)$ 이상인지를 후처리로 검사한다. 컴파일은 재결합을 금지하는 옵션으로 한다.

**범위.** 행 $30{,}000$개, $\mathsf Q_R$ 위치 $524{,}955{,}000$개, 인접 쌍 $524{,}985{,}000$개. 재인증 C20은 $5\le n\le20000$의 위치 $99{,}970{,}002$개, 인접 쌍 $99{,}989{,}998$개.

**산술 등급.** binary64 사전 오차 해석. 최대 상대 오차 한계는 $2.03\times10^{-9}$(조건 $\mathrm{eps}\le1.4\times10^{-8}$ 충족)이고, 보증은 IEEE binary64 반올림 모형과 컴파일러의 재결합 금지에 기댄다. 정수 구간 인증보다 한 단계 약한 보증이다.

**결과.** 엄격 증가 인증 $504{,}674{,}626$곳, 엄격 로그오목 인증 $20{,}280{,}374$곳, 미결 $0$. 인접 쌍은 엄격 증가 $504{,}674{,}626$, 엄격 감소 $20{,}310{,}374$, 미결 $0$. $\mathsf Q_R(n)$·오른쪽 절반 엄격 단봉·$\mathsf W(n)$ 모두 $30{,}000/30{,}000$행. 최소 안전 배수(여유/오차 한계)는 쌍 비교에서 $8.99$($(n,\ell)=(47277,46447)$), 로그오목 비교에서 $4.22\times10^4$. C20은 미결 $0$, 최대 상대 오차 한계 $7.40\times10^{-10}$, $19{,}996$행에서 D.{{D:exact-n20000}}(ㄹ)와 불일치 $0$. 봉우리의 두 항 공식과의 차는 $20001\le n\le50000$에서 $[0.844,1.849]$다.

**독립 재계산.** 첫 시도의 코드는 없고 인증은 재개 세션의 단독 계산이다. 검토가 소스를 줄 단위로 감사하고 표를 독립 계산하고(최대 오차 $0.994u$) 재빌드해 두 조각($k=22297$–$25270$, $32857$–$49999$)을 재실행했으며 행 파일이 바이트 단위로 같았다. $n=47277$ 등에서 $2^{256}$ 고정소수점 마지막 차 재귀로 참값을 계산해 구간 안에 있음을 확인했다. $n\le60$의 $169$개 표본에서 실제 상대 오차는 한계의 $2.2\%$ 이하다.

**자료.** `records/r59c82d760e9c4ddcaae2d587db28a914/evidence/code/qrcert.c`, `make_tables.py`, `bor.bin`, `h.bin`, `tables_manifest.json`, `postprocess_rows.py`, `merge_chunks.py`, `evidence/runs/ext50000_summary.json`, `ext50000_rows.tsv`, `ext50000_post.json`, `e50_1_summary.json`–`e50_6_summary.json`, `full20000_summary.json`, `full20000_rows.tsv`, `full20000_compare_published.txt`, `t60_validate.json`, `evidence/exact_check.json`.

**출처.** [r59c82d7] §4–6, `review/feedback.md`.

### D.{{D:sharp-546-certificates}} 마지막 102항의 백 개 다항식 인증서와 직접 표 (정리 {{5:old-5-3}}, 보조정리 {{5:sharp-546}})

**확인하는 진술.** 각 $2\le r\le101$에서 어떤 정수 $\mathrm{sh}\ge0$에 대해 $\mathcal X(I+\mathrm{sh})$의 모든 계수가 $0$ 이하이고 상수항이 음이며 $\mathfrak B+\mathrm{sh}\le546$($\mathfrak B=2r+1$)이다. $2\le r\le101$, $r+1\le n\le1114$의 모든 위치에서 $b_{n,n-r-1}>b_{n,n-r}$이면 $K_r(n)<0$이다. $K_{101}(545)>0$이다.

**식.** 보조정리 {{5:tail-poly}}의 $K_r(n)$과 $\kappa_{r,j}$, 보조정리 {{5:rational-cert}}의 절단 하계 $\mathrm{lb}(\tau)$와 다항식 $\mathcal X(I)$, 보조정리 {{5:sharp-546}}의 경계 $\mathrm e_-\frac{(2\tau-1)(\tau-1)}{2\tau}\le\tau(1+\frac1\tau)^{\tau-1}\le\mathrm e_+\frac{6\tau^3}{6\tau^2+9\tau-5}$($\mathrm e_-=2718281828/10^9$, $\mathrm e_+=2718281829/10^9$). $\mathrm e_-<e<\mathrm e_+$는 $\sum_{i\le14}1/i!$과 나머지 상계 $16/(15\cdot15!)$로 유리수 연산으로 확인한다. 직접 표는 정리 {{2:old-2-6}}의 마지막 차 재귀와 미달 수의 정확한 정수값으로 네 항 $b_{n,n-r-2},\dots,b_{n,n-r+1}$을 계산한다.

**알고리즘.** 각 $r$에서 $\mathcal X$의 정수 계수를 만들고, 평행이동 $\mathrm{sh}$를 배증·이분 탐색으로 찾는다. 계수가 모두 $0$ 이하인 다항식은 양의 평행이동에서도 그러하므로 한 번 조건이 성립하면 더 큰 이동에서도 성립한다. 직접 표는 다항식 전개 없이 결손의 재귀를 정수로 반복하고, 재귀가 적용되지 않는 작은 크기는 마지막 차 재귀로 계산하며, $n\le205$의 겹치는 $10{,}812$개 값을 두 식으로 대조한다.

**범위.** 인증서 $100$개($2\le r\le101$), 계수 $20{,}103$개. 직접 표는 $2\le r\le101$, $r+1\le n\le1114$의 $106{,}250$개 위치.

**산술 등급.** 정확 정수·유리수.

**결과.** $100$개 인증서가 모두 성공하고 시작점 $\mathfrak B+\mathrm{sh}$의 최댓값은 $546$이다. 직접 표에서 조건부 오목성의 실패는 없다. $K_{101}(545)>0$이 정확한 세 정수와 그 차로 보존되어 시작점 $546$이 오목성 명제에 대해 최적이다. 거친 상계 $\frac{11}4\tau$로 만든 첫 인증은 시작점이 $r=101$에서 $1114$까지 커진다.

**독립 재계산.** 거친 상계의 인증($100$개, 이동 분자 계수 $25{,}054$개, $60{,}263{,}411$바이트)을 독립 재계산이 다시 생성해 SHA-256이 일치했고, Horner 방식으로 기준 분자를 다시 만들어 양의 상수배로 일치함을 확인했다. 정밀 상계의 인증은 재개 세션의 계산이고 검토가 지지했다. 첫 인증의 유한 검사($n<N_r$의 $33{,}112$개 위치, 감소 전제 참 $10$곳)와 재개 세션의 직접 표가 겹치는 범위에서 일치한다.

**자료.** `records/ra88ba51bd28b432fa06bdb9478f1c284/evidence/peer/code/certify.py`, `evidence/peer/sharp-certificates.json.gz`, `certificate-summary.json`, `evidence/peer/code/tail_table.py`, `evidence/peer/tail-table.json`, `evidence/peer/code/algebra_checks.py`, `algebra-checks.json`, `small-checks.json`, `evidence/producer/results/finite-tail-verification.json`.

**출처.** [ra88ba51] §4–6, `verification.md`.

### D.{{D:newton-m170}} 원천별 비교 $(\mathrm G)_d$의 Newton 전진 차분 인증 (정리 {{5:old-5-4}})

**확인하는 진술.** 모든 $2\le r\le170$, $1\le d\le r-1$에서 정리 {{5:old-5-4}}의 증명에 적은 정수값 다항식 $\mathrm{Nw}_{r,d}(\mathrm{nv})$($\mathrm{nv}=k-r-1\ge0$)의 전진 차분 $\Delta^i\mathrm{Nw}_{r,d}(0)$이 모두 음이 아니고 $\mathrm{Nw}_{r,d}(0)>0$이며, 차수 $r+d+3$ 너머의 차분이 $0$이다.

**식.** $\mathrm{Nw}_{r,d}(\mathrm{nv})=15!\,\bigl[2\mathrm e_{15}\,k^2(k+1)\Gamma_{r-1}(k+2;n)\mathrm{sd}_d(k)-(2k^2+5k+4)\Gamma_r(k-1;n)\mathrm{sd}_d(k+1)\bigr]$, $\mathrm e_{15}=\sum_{j\le15}1/j!$, $n=k+r$, $k=r+1+\mathrm{nv}$. $\Gamma_d(\ell;n)$은 보조정리 {{5:fixed-size-response}}의 재귀 $\Gamma_d=(1+\frac y{n-d+1})\Gamma_{d-1}+\sum_{j\ge2}\mathrm{tw}_j\Gamma_{d-j}$로 계산한다. $\mathrm{Nw}_{r,d}(\mathrm{nv})=\sum_i\Delta^i\mathrm{Nw}_{r,d}(0)\binom zi$이고 $\mathrm{nv}\ge0$에서 $\binom zi\ge0$이다.

**알고리즘.** 각 $(r,d)$에서 $\mathrm{nv}=0,\dots,2r+2$의 $\mathrm{Nw}_{r,d}(\mathrm{nv})$를 정확한 정수로 계산해 전진 차분표를 만들고 부호를 검사한다. $2\le r\le40$에서는 첫 인증이 단항 기저의 유리계수 다항식 $780$개($35{,}100$개 계수)로 비음성을 확인했고, 재인증이 그 기호 산술을 쓰지 않고 Green 재귀의 정확한 값을 Newton 차분으로 보간해 저장 계수와 비교했다.

**범위.** $2\le r\le170$, $1\le d\le r-1$의 $14{,}365$개 다항식. $r=45$에서 $0.5$초, $r=150$에서 약 $2$분.

**산술 등급.** 정확 정수·유리수.

**결과.** $14{,}365$개 다항식 모두에서 전진 차분이 음이 아니고 실패가 없다. $2\le r\le40$의 $780$개는 첫 인증의 단항 계수와 계수까지 동일하며 음수 계수 $0$개, 영 상수항 $0$개, 압축 파일 해시 일치.

**독립 재계산.** $2\le r\le40$은 서로 다른 두 방법이 일치했다. $41\le r\le170$은 재인증의 계산이고 검토가 지지했다.

**자료.** `records/r708d99cec0604c698f2362e68068ad8d/evidence/peer/cert_newton_summary.json`과 범위별 JSON, `evidence/peer/recheck_certificate.py`, `recheck_certificate_out.json`, `evidence/peer/verify_P_poly.py`, `evidence/peer/verify_reduction.py`, `evidence/producer/work/renewal_poly_results.json`.

**출처.** [r708d99c] §5.1–5.3.

### D.{{D:tail-T1-partAB}} 꼬리 정리 T1의 두 부분 (A)·(B)의 구간 계산 (정리 {{5:old-5-5}}, 보조정리 {{5:lemma-L}})

**확인하는 진술.** (A) $171\le r\le9999$의 모든 정수 $r$에서 $\mathfrak k_r=\lceil r^{3/2}+8r\rceil$, $\rho_r=\mathfrak k_r/(\mathfrak k_r+r)$에 대해 $\mathrm{tm}_{r-1}(\rho_r)$의 하계 $\mathrm{eb}_r$과 정리 {{5:old-5-5}}의 증명의 다항식 $\mathrm{Pc}(\mathfrak k_r)$의 하계가 양수다. (B) $\mathfrak L(10^4)\ge0.845204$이고, $t\ge100$에서 $t(\frac12+2\mathfrak L(10^4)-\sqrt{3\pi/2})+\frac12-[\frac1{3t}+\frac8{3t^2}+\frac{2.507}{t^2}+\frac{1+2.1709t}{t^3}]\ge0.0196\,t+0.496$이다.

**식.** (A) 기울인 생일 법칙의 가중치 $\mathrm{bw}_0=1$, $\mathrm{bw}_{j+1}=\mathrm{bw}_j\,\rho_r\frac{j+2}{j+1}\cdot\frac{r-1-j}{r}$와 $\mathrm{tm}_{r-1}(\rho_r)=\sum_jj\,\mathrm{bw}_j/\sum_j\mathrm{bw}_j$. 분자는 $j\le J_2=12(\lfloor\sqrt r\rfloor+1)+10$까지만 더해 하계로, 분모의 꼬리는 비 $\mathrm{bw}_{j+1}/\mathrm{bw}_j$가 $j$에 대해 감소하므로 $\mathrm{bw}_{J_2}\Xi/(1-\Xi)$로 위에서 막는다. (B) 보조정리 {{5:lemma-L}}의 $\mathfrak L(r)$과 그 재료 $\mathfrak M_0,\dots,\mathfrak M_5$, $\mathfrak M^{(6)}_2$, $\kappa_2,\dots,\kappa_5$, $\mathfrak C_1,\dots,\mathfrak C_4$. $\mathfrak M_0=\int_0^\infty e^{-y-y^2/2}dy$는 교대급수 $\sum_i(-1)^i2^{(i-1)/2}\Gamma(\frac{i+1}2)/i!$의 부분합으로 감싸고(항의 크기 감소를 구간으로 확인), $\mathfrak M_1=1-\mathfrak M_0$, $\mathfrak M_{q+1}=q\mathfrak M_{q-1}-\mathfrak M_q$, $\kappa_q$는 유일한 임계점 $y_\ast=(-1+\sqrt{1+4q})/2$의 값, $\mathfrak M_2-\mathfrak M_2^{(6)}\le e^{-6}(6+\frac16)e^{-18}$.

**알고리즘.** (A) 각 $r$에서 위 합을 방향 반올림 구간으로 계산하고 $\mathrm{Pc}(\mathfrak k_r)$의 하계의 부호를 본다. (B) 상수를 구간으로 계산하고 부등식의 두 변을 구간으로 비교한다.

**범위.** (A) $9{,}829$개의 $r$. (B) 상수 한 벌.

**산술 등급.** 방향 반올림 구간(30자리).

**결과.** (A) 모두 양수이고 $\mathrm{Pc}(\mathfrak k_r)/\sqrt r$의 최솟값은 $r=9999$의 $0.1654$다. 실행 시간 $9$분. (B) 통과. 상수의 값은 $\mathfrak M_0,\dots,\mathfrak M_5=0.65568,0.34432,0.31136,0.37728,0.55680,0.95233$, $\mathfrak C_1=0.95235$, $\mathfrak C_2=0.61306$, $\mathfrak C_3=0.24718$, $\mathfrak C_4=0.04287$이다. 검산으로 $\mathrm{tm}_{r-1}(e^{-1/\sqrt r})/\sqrt r$의 실제 값은 $r=10^4,2\cdot10^4,10^5$에서 $0.8935,0.8967,0.9009$이고 하계 $\mathfrak L(r)$은 $0.8452,0.8622,0.8852$다.

**독립 재계산.** 재개 세션의 계산이고 검토가 지지했다. 창의 경계 $r=171,300,1000,2000$, $k=\mathfrak k_r$에서 실제 여유 $n^{2/3}(\beta-\mathrm{sd}_1/\mathrm{sd}_0)=1.929,1.944,1.965,1.973$을 배정밀도로 대조했다(증명이 아니라 진단).

**자료.** 코드의 변수 `k0`는 이 글의 $\mathfrak k_r$, `E0`는 $\mathrm{eb}_r$, `t_j`는 $\mathrm{bw}_j$, `L`은 $\mathfrak L$이다. `records/r0dc57fab33ca460ba929db8de09b26a0/evidence/peer/code/cert_tail_alpha1.py`, `evidence/peer/data/cert_tail_alpha1_171_9999.json`, `evidence/peer/code/tail_alpha_scan.py`, `evidence/peer/data/tail_alpha_scan.json`, `evidence/peer/code/S_float.py`.

**출처.** [r0dc57fa] §10.2.

### D.{{D:bernstein-signs}} 세 Bernstein 부호 인증: 핵 계수 경계의 두 다항식, 꼬리 오목성의 76개 $r$ 칸, 진입 증가의 35개 $r$ 칸 (보조정리 {{5:kernel-bounds}}, 정리 {{5:old-5-6}}, 정리 {{5:old-5-7}})

**확인하는 진술.** (ㄱ) 보조정리 {{5:kernel-bounds}}의 증명의 두 유리 다항식 $P_\mathrm{ag}'$, $Q_\mathrm{ag}'$의 $[0,\frac13]$ 위 Bernstein 계수가 모두 양수이고, 그 증명의 다항식 항등식이 성립한다. (ㄴ) 정리 {{5:old-5-6}}의 증명에서 각 $r$ 칸 $\mathrm S_-^2\le r\le \mathrm S_+^2$의 상계 다항식 $P_{\mathrm S}(x^{3/2})$를 $x^{3/2}=\frac{\mathrm S_+}{\mathrm S_++12}\mathrm{bv}$, $\mathrm{bv}\in[0,1]$로 바꾸어 차수 $192$의 Bernstein 기저로 전개한 계수가 모두 음수다. (ㄷ) 정리 {{5:old-5-7}}의 증명에서 각 $r$ 칸의 상계 다항식 $P_{\mathrm E}(x^{3/2})$를 $x^{3/2}=\frac{16}{25}+\frac{\mathrm {bv}}{100}$으로 바꾸어 차수 $96$의 Bernstein 기저로 전개한 계수가 모두 음수다.

**식.** (ㄱ) $\vartheta=1/m$, $\Psi=\vartheta/(2+\vartheta)$에서 $\log(1+\vartheta)=2\sum_j\frac{\Psi^{2j+1}}{2j+1}$의 절단 $L_\mathrm{ag}'(\Psi)$과 꼬리 상계 $U_\mathrm{ag}'(\Psi)=L_\mathrm{ag}'+\frac{2\Psi^9}{9(1-\Psi^2)}$을 넣은 도함수의 분자 $\frac{2\Psi^3P_\mathrm{ag}'(\Psi)}{1155(1-\Psi)^3}$, $-\frac{\Psi^4Q_\mathrm{ag}'(\Psi)}{945(1-\Psi)^3(1+\Psi)}$. (ㄴ) 보조정리 {{5:sign-sandwich}}(나)의 Laurent 다항식 $\mathrm{Lp}^\pm_j$($2\le j\le12$)의 단항식 계수 $[z^{r+3}]w^i$를 (다)의 유한 곱으로 적고 $r\in[\mathrm S_-^2,\mathrm S_+^2]$에서 감싼 정규화 계수의 유리 구간, 홀수 $j$에 상계·짝수 $j$에 하계, 첫 사슬 항의 상계 $-\mathrm{nS}+\mathrm{pS}\,x^{3/2}$($\mathrm{nS}=\mathsf o^-\pi^-(1-\frac3{2\mathrm S_-^2})(1-\frac1{12\mathrm S_-^2})(\frac12-\frac{11}{24\mathrm S_-^2})$, $\mathrm{pS}=\frac{3\mathsf o^+\pi^+}{\mathrm S_-(1-\frac1{\mathrm S_-+12})^3(1-\mathrm{rq}^\ast)}$; $\mathsf o^\pm$는 $\frac1{\sqrt2}$의, $\pi^\pm$는 $\frac1{\sqrt\pi}$의 검증된 유리 하·상계, $\mathrm{rq}^\ast=\frac{1+3/\mathrm S_-^2}{\mathrm S_-+12}$), (마)의 $j\ge13$ 꼬리(13번째 상계의 $10$배; 연속 항 비의 제곱이 모든 칸에서 $\frac{81}{100}$ 미만), 보조정리 {{5:last-gap}}의 인자 $\frac65$, 가중치 경계 $1\le W_n\le(1-\mathrm{rq}_r)^{-j-2}$. (ㄷ) 보조정리 {{5:parity-tail}}의 두 경계($\mathrm{er}_j(\mathrm{rq}_\ast)$의 지수함수는 $0\le q<16$에서 $e^{q}\le(1-q/16)^{-16}$으로 유리화한다; 코드 `certify_entry.py`의 `expbound`)와 정규화 $\mathfrak s/e$, $\mathrm{rq}_\ast=\frac{13}{20}\cdot\frac{1+3/\mathrm S_-^2}{\mathrm S}_-$, 보조정리 {{5:marked-recursion}}의 $\mathcal Z^{(2)}_j$, $\mathcal Y_j$에 보조정리 {{5:kernel-bounds}}(K1)의 하계와 보조정리 {{5:kernel-C-bound}}의 상계를 넣은 Laurent 다항식($\mathcal Y_j$의 $zC'$ 경계는 $C$의 경계에 $z\frac d{dz}$를 적용), $j\ge13$ 꼬리는 $\mathcal Z^{(2)}_2\preceq2(1-z)^{-2}$와 $\mathrm{dc}'_{j+1}=\frac34(\vartheta'_j+2)\mathrm{dc}'_j$의 기하급수.

**알고리즘.** (ㄱ) 다항식 항등식을 기호 산술로 확인하고 Bernstein 계수를 정확한 유리수로 계산한다. (ㄴ)(ㄷ) $r$ 칸마다 Laurent 다항식을 정확한 유리수로 만들고, 각 단항식의 $z^{r+3}$(또는 $z^{r+2}$) 계수를 부호를 유지하며 유리 구간으로 감싸고, 홀짝 부호 배치대로 상·하계를 택해 $x^{3/2}$의 유리 계수 다항식을 만든 뒤 Bernstein 기저로 바꾸어 계수 부호를 본다. $r$ 칸은 (ㄴ) $\mathrm S_-=13$($r=169$)부터 $\mathrm S_-=1000$의 무한 칸까지 $76$개, (ㄷ) $\mathrm S_-=23$($r=529$)부터 무한대까지 $35$개로 빈틈없이 잇는다.

**범위.** (ㄱ) $w\in[0,\frac13]$. (ㄴ) $r\ge169$, $n\ge r^{3/2}+12r$. (ㄷ) $r\ge529$, $\frac{16}{25}\le x^{3/2}\le\frac{13}{20}$.

**산술 등급.** 정확 정수·유리수(Python 정수와 분수).

**결과.** (ㄱ) 항등식과 Bernstein 양성이 성립한다. (ㄴ) $76$개 칸 모두 계수가 음수이고 전체 최대 계수는 $-7.64\times10^{-5}<-\frac1{20000}$. (ㄷ) $35$개 칸 모두 계수가 음수이고 전체 최대 계수는 $-0.02965<-\frac1{40}$.

**독립 재계산.** 독립 재계산이 첫 인증의 세 스크립트를 재실행해 출력 JSON 다섯 개가 바이트 단위로 같았다. (ㄱ)은 60자리 계산으로 $m\le3000$ 전부와 $m\le10^7$의 $400$개 표본에서 계수 부등식을 직접 대조했다(최소 정규화 여유 $0.0005$ 이상). (ㄴ)(ㄷ)의 핵 포함 구간은 실제 $\mathcal Z^{(3)}_j$, $\mathcal Z^{(2)}_j$, $\mathcal Y_j$ 계수와 $r\le20000$의 $3103$곳, $r\le1.05\times10^6$의 $1938$곳에서 대조해 위반 $0$. 실제 원 개수에서 (ㄴ)의 경계 $n=\lceil r^{3/2}+12r\rceil$, $r=169,\dots,700$의 $532$곳과 (ㄷ)의 창 양 끝 $1144$곳($r=529,\dots,1100$)의 정규화 값이 각각 $-0.364$, $-0.057$ 이하였고, $(r,n)=(169,4225),(170,4257)$은 정확 정수로 셋째 차분이 음수였다. (ㄷ)이 증가를 예측하는 D.{{D:exact-n20000}}(ㄹ)의 $18719\le n\le20000$의 $6481$개 위치가 모두 인증된 증가 구간 안에 있다.

**자료.** `records/r690be93802cc4cd1af3b6d76cb16d4e5/evidence/producer/kernel-proof.md`, `kernel_audit.py`, `concavity-A12-certificate.json`, `entry-slope-certificate.json`, `check_certificates.py`, `direct_checks.py`, `evidence/peer/k1k2_check_output.json`, `evidence/peer/reproduction/`, `evidence/peer/kernel_sample/`, `dense_scan.json`, `scan_TE.json`, `exact_spot.json`, `tsv_crosscheck_output.txt`, `window_check.json`; 핵 계수 경계의 원형은 `records/r77983552ef714100b038b18367877aa6/evidence/producer/effective-concavity-proof.md`, `kernel-check.json`.

**출처.** [r690be93] §4, §5.3, §7.4, §11; [r7798355] `evidence/producer/effective-concavity-proof.md` §3.

### D.{{D:band-A-certification}} 꼬리 띠 A·A⁺의 직사각형 인증 (정리 {{5:old-5-12}})

**확인하는 진술.** 좌표 $(\mathfrak s^{-1},x^{3/2})$의 각 직사각형에서 정리 {{5:old-5-12}}의 증명의 상계 다항식 $P_{\mathrm A}(x^{3/2})$가 $-\frac1{100}$ 미만이다.

**식.** 보조정리 {{5:weight-envelope}}(다)의 첫째 보정($\mathrm{Rm}_j$; 띠 A)과 둘째 보정($\mathrm{Rm}^{(2)}_j$; 띠 A⁺), 보조정리 {{5:marked-recursion}}·{{5:marked-chain-rec}}의 $\mathcal Z^{(2)}_j$, $\mathcal Y_j$, $\mathcal O_j$에 보조정리 {{5:kernel-sandwich}}(가)의 $C_-$(A) 또는 보조정리 {{5:kernel-bounds}}(K1)(A⁺)의 하계와 $C_+$의 상계를 넣은 Laurent 다항식, 단항식 계수의 유한 곱(보조정리 {{5:sign-sandwich}}(다)), Wallis 하계 $(1-\frac32\mathfrak s^{-2})/\sqrt\pi$(첫 인증) 또는 $(1/\sqrt\pi)/(1+\frac54\mathfrak s^{-2})$(재인증; 보조정리 {{5:kernel-sandwich}}(나)), 정규화 계수 $(x^{3/2})^j\Delta^2\mathrm{Ch}_j/r^{3j/2-2}$, $(x^{3/2})^{j+1}\mathfrak s^{-1}\Delta^2\mathcal U_j/r^{3j/2-1}$, $(x^{3/2})^{j+2}\mathfrak s^{-2}\Delta^2\mathcal N_j/r^{3j/2}$, 꼬리 $\mathrm{Tl}_{K+1}/(1-\Xi)$(보조정리 {{5:omitted-tail}}(다); 첫 인증은 $j\ge25$에서 비가 $\frac12$ 미만임을 보여 $2\mathrm{Tl}_{25}$로 덮음), 나머지 $\mathrm{Rm}_j$ 대신 첫 인증은 정수 지수 $j+2$의 Taylor 나머지를, 재인증은 $(1-\mathrm{rq})^{-(j+1)}(1+\frac{\mathrm {rq}}{2(1-\mathrm{rq})})-1-(j+\frac32)\mathrm{rq}$를 썼다. 띠 (A⁺)의 뒤 세 조각은 $x^{3/2}$ 구간 $[x_0,x_1]$에서 $P_{\mathrm A}(x_{\mathrm m})+\max|P_{\mathrm A}'|\frac{x_1-x_0}2$로 상계하고, 둘째 조각은 $\mathfrak s^{-1}$ 행 $[u_0,u_1]$에서 $x^{3/2}\le u_0^{-3}/20001$인 직사각형만 평가한다.

**알고리즘.** Laurent 계수를 정확한 유리수로 생성하고, 직사각형마다 양의 항의 계수에는 $\mathfrak s^{-1}$의 최댓값, 음의 항에는 최솟값을 넣어 $x^{3/2}$의 다항식을 만든 뒤 구간 산술로 상계를 평가한다. 양의 계수의 하계가 음이면 $0$으로 자른다.

**범위.** (A) 첫 인증: $\mathfrak s^{-1}\in[0,\frac{41}{1000}]$, $x^{3/2}\in[\frac{73}{100},\frac65]$를 폭 $\frac2{1000}$ 이하로 나눈 $4935$개($21\times235$), $K=24$. 독립 재인증: $82\times235=19{,}270$개($\mathfrak s^{-1}$ 폭 $\frac1{2000}$, $x^{3/2}$ 폭 $\frac1{500}$), $K=30$. (A⁺) 네 조각: $[\frac65,\frac32]$, $r\ge833$, $K=30$, 격자 $\frac1{2000}\times\frac1{500}$, $10{,}500$개; $[\frac32,\frac95]$, $r\ge966$·$n\ge20001$, $K=30$, $\frac1{4000}\times\frac1{500}$, $18{,}797$개; $[\frac95,\frac{21}{10}]$, $r\ge2164$, $K=40$, $12{,}900$개; $[\frac{21}{10},\frac{12}5]$, $r\ge10000$, $K=48$, $6{,}000$개.

**산술 등급.** Laurent 계수는 정확 정수·유리수. 직사각형 평가는 (A) 첫 인증은 120비트 고정소수점 정수 구간, (A) 재인증과 (A⁺) 200비트 방향 반올림 구간(mpmath).

**결과.** (A) 첫 인증의 최악 상계 $-20763942788699649828208058950993518/2^{120}\approx-0.01562$, 실패 $0$. 독립 재인증의 최악 $-0.04599$($\mathfrak s^{-1}\in[\frac{81}{2000},\frac{82}{2000}]$, $x^{3/2}\in[0.730,0.732]$), 실패 $0$. 첫 인증의 최악값이 $x^{3/2}=\frac65$ 끝에 있었던 것은 격자 손실이다. (A⁺) 최악 상계 $-0.1821$, $-0.1468$, $-0.01555$, $-0.01743$, 실패 $0$. 같은 틀을 $[\frac95,\frac{21}{10}]$에서 $r\ge1091$ 전체로 넓히면 $r\approx2114$–$2163$에서 여유를 잃고 더 작은 $r$에서 양수가 되며($+0.29$까지), $[\frac{21}{10},\frac{12}5]$는 $r<10000$에서 양수가 된다($+1.60$까지). 첫째 보정만으로 $[\frac65,\frac32]$를 인증하면 $r\ge1232$에서만 성공한다. 실제 값은 $r^2(b_{n,n-r}-b_{n,n-r-1})/p_n\in[0.069,0.253]$으로 주장의 $7$–$25$배다(배정밀도 진단, 증명 아님).

**독립 재계산.** 재인증이 첫 인증의 코드를 줄 단위로 읽고 재실행해 같은 최악값과 실패 $0$을 얻은 뒤, Laurent 다항식(기호 전개), 구간 산술(mpmath), 절단($K=30$), Wallis 하계, 나머지, 격자가 모두 다른 구현으로 (A)를 다시 인증했다. 생성함수 재귀는 $j\le6$, $r\le14$의 $270$개 계수와 $j\le20$의 기호 결과에서 직접 열거와 일치했다. D.{{D:exact-n20000}}(ㄹ)의 행 자료에서 (A)가 증가를 예측하는 $943{,}380$개 위치($7814$개 행)가 모두 인증된 증가 위치였다.

**자료.** `records/r13b0b8f020b04cd8869347c2af7ff7e6/evidence/producer/output/critical-strip-certificate.json`, `code/cert_critical_strip.py`, `certificate-run.log`, `verification.json`, `evidence/peer/code/indep_cert.py`, `indep_cert2.py`, `indep_cert3.py`, `evidence/peer/indep_cert_A.json`, `cert2_12_15.json`, `cert3_15_18.json`, `cert3_18_21_r2164.json`, `cert3_21_24_r10000.json`, `cert3_18_21.json`, `cert3_21_24.json`, `indep_cert_ext15.json`, `reproduction/critical-strip-certificate-rerun.json`, `laurent_series_check.json`, `gf_identity_check.json`, `J_identity_check.json`, `tsv_crosscheck.json`, `strip_sample.json`.

**출처.** [r13b0b8f] §7–8.

### D.{{D:critical-window-rig}} 임계 창 인증의 둘러싸기 설계, 상자 모임, 구간 검증 상수와 사후 정정 (정리 {{5:old-5-13}}, 보조정리 {{5:cut-rep}})

**확인하는 진술.** $\mathrm{ku}$의 상자 $44$개와 $\hat x\in[1.4,10]$의 셀마다 $\inf(\Upsilon_e-\Upsilon_B)>0$. 보조정리 {{5:cut-rep}}(라) 뒤의 경로 회전에 쓰이는 부채꼴 $|\varphi|\le\frac12$, $-\frac\pi8\le\arg\hat\varphi\le0$ 위의 상수들.

**식.** 보조정리 {{5:hat-normalization}}의 $\Upsilon_e$, $\Upsilon_B$, $\Omega_e$, $\Omega_B$, $\mathrm{ch}_0,\mathrm{ch}_1,\mathrm{ch}_2$, $\hat{\mathrm{Wr}}_j$, $\hat{\mathfrak J}$, $\mathrm{Ce}_m$, $\mathrm{Cb}$와 보조정리 {{5:cut-rep}}(라)의 $\mathrm{Bt}$, $\mathfrak I$, $\mathrm{nu}$, $\mathrm{qy}$, $\mathrm{Zh}$. 구간 검증 상수(반직선 $0\le|\varphi|\le\frac12$, $400$셀): $\max|\mathrm{lg}|=1.0199$(코드는 $1.03$), $\min\mathrm{Re}\,\hat L/|\hat\varphi|^2=0.3534$($0.34$), $\arg\mathrm{qy}\in[-48.21^\circ,-45.00^\circ]$($[-48.5^\circ,-45^\circ]$; 따라서 $\mathrm{Zh}$가 닫힌 위반평면에 있으면 $|\mathrm{ku}\mathrm{qy}-\mathrm{Zh}|\ge\sin45^\circ|\mathrm{Zh}|>0.69|\mathrm{Zh}|$), $|\hat L|/|\hat\varphi|^2\le0.505$($0.507$), $|\mathrm{qy}|/|\hat\varphi|^2\le0.528$($0.545$), $0<\mathrm{ag}'\le1$에서 $0.4999\le|\xi-1|/\mathrm{ag}'^2\le0.617$(하계 $0.494$, 상계 $0.438\cdot1.3$), $\mathrm{Im}(\xi-1)/\mathrm{ag}'^3\ge0.1667$($0.15$). 실수축 나머지의 $\log\mathrm{et}(\frac12)\ge0.1268$은 참값 $0.126776$보다 조금 크게 적힌 오기이며 그 영향은 $e^{-1260}$ 규모다. 꼬리 상수: $\mathrm{ag}\le1$에서 $1-\cos\mathrm{ag}\ge0.458\mathrm{ag}^2$, $|\mathfrak I|\le N_{\mathrm{tot}}/(0.69\cdot0.438\hat{\mathrm{ag}}'^2)+\mathrm{far}_0$, $\mathrm{far}_0\le e^{-800}$. 정수 $k$ 의존의 둘러싸기: $e^{\mathrm{rb}_k}\in[1,e^{\mathrm{ku}^3/12}]$, $\mathrm{Bor}(k+j'')/\mathrm{Bor}(k)\in[e^{-1/(12k)},e^{1/(12k)}](1+j''/k)^{-3/2}$. $\hat x$ 셀 $[\hat x_{\mathrm m}-\frac{\mathrm{cw}}2,\hat x_{\mathrm m}+\frac{\mathrm{cw}}2]$의 여백 $=\inf(\Upsilon_{e,0}-\Upsilon_{B,0})-\frac{\mathrm{cw}}2\sup|\Upsilon_{e,1}-\Upsilon_{B,1}|-\frac{\mathrm{cw}^2}8(L_e+L_B)-(\text{꼬리}_e+\text{꼬리}_B)$. $\hat x$ 도함수는 피적분함수에 $(e^{\mathrm i\mathrm{ag}}-1-\mathrm i\mathrm{ag})/\mathrm{ku}^2$을 곱한 것이다.

**알고리즘.** (a) 꼬리 $\hat{\mathrm{ag}}\ge6$은 Gauss 모멘트 $\int_6^\infty\hat{\mathrm{ag}}^{2m+1}e^{-\mathrm{tl}\hat{\mathrm{ag}}^2}d\hat{\mathrm{ag}}$의 닫힌 꼴로, $\mathrm{ag}\in[1,\pi]$는 $|\mathrm{Bor}^{\mathrm{tail}}_ke^{k(1-\mathrm{pt}')^2/2}|\le2e^{k(1-\cos\mathrm{ag}')^2}$으로 막는다($\hat x\ge1.4$에서 $10^{-100}$ 이하). (b) 주부 $\hat{\mathrm{ag}}\le6$은 격자 $480$칸($d=\frac1{80}$)의 사다리꼴 공식에 오차항 $\frac{d^2}4\mathrm{diam}(f'(\text{셀}))$, 안쪽 누적은 사다리꼴에 $\frac{d^3}{12}|g''|$; $\mathrm{ku}_{\mathrm b}\le0.003$인 상자는 첫 $8$셀을 $8$개로 다시 나눈다. (c) $\mathrm{Bt}$는 반직선의 $|\hat\varphi|\in[0,10]$을 이차 간격 $300$셀의 중점법과 $|f''|$ 상계로, $[10,\frac12\mathrm{ku}^{-3/2}]$은 $|\mathrm{nu}|\le1.03|\hat\varphi|^2e^{-0.34|\hat\varphi|^2}$과 $|\mathrm{ku}\mathrm{qy}-\mathrm{Zh}|\ge0.69|\mathrm{Zh}|$로, 호와 실수축 나머지는 $\mathrm{far}_0$으로 막는다. $\mathrm{ku}$ 상자 처리는 Taylor 영역(상자 중점 둘레의 이차 Taylor; 정정판은 분모 $\mathrm{ku}\mathrm{qy}-\mathrm{Zh}$ 꼴)와 기하 영역($0.69|\mathrm{Zh}|\ge20\mathrm{ku}_{\mathrm b}$일 때 분모의 기하급수 전개)이고 마지막 상자는 둘의 합집합이다. (d) $\hat{\mathrm{Wr}}_j=2^{-j}\int s^{2+2j}(1-\mathrm{ku} s)^{-1}e^{-\kappa_\rho(s)}\hat S(s)ds$($v=\mathrm{ku} s$)를 $s$ 격자 $6400$칸의 단조 상·하합과 명시 꼬리로, Borel 꼬리 합은 $S_k/\mathrm{Bor}(k)\in[e^{-1/(12k)}(k\Phi(k\alpha)-1),e^{1/(12k)}k\Phi(k\alpha)]$, $\Phi(z)=\int_0^\infty(1+y)^{-3/2}e^{-zy}dy$의 단조 표로 둘러싼다. (e) $\hat x$ 셀은 중점의 값과 도함수의 일차 전개에 $\frac{\mathrm{cw}^2}8\sup|F''|$을 더한다.

**범위.** $\mathrm{ku}\in(0,10001^{-1/3}]$: 폭 $0.0015$의 상자 A00–A29($0.04641\to0.0015$), 비 $1.25$의 기하 상자 G00–G11($0.0015\to1.0308\times10^{-4}$), 얇은 G12, 마지막 G13 $=[0,1.0307\times10^{-4}]$($k\ge9.13\times10^{11}$과 $k=\infty$). 상자마다 $\hat x\in[1.4,10]$을 $\mathrm{cw}=0.2$의 $43$셀로 덮고, 다섯 상자(A29, G06, G07, G08, G13)의 첫 셀 $[1.4,1.6]$은 $\mathrm{cw}=0.1$(A29는 $[1.4,1.8]$을 $0.08$)로 재인증.

**산술 등급.** 방향 반올림 구간(mpmath.iv, 30자리). 급수는 명시적 꼬리와 함께 자른다.

**결과.** 모든 셀의 여백이 양수다. 원 최소 여백은 $0.001584$(G07, $\hat x\in[9.8,10]$). 사후 감사가 둘러싸기가 참값을 놓칠 수 있는 결함 다섯을 찾았다. F1(셀 내부 누적 적분의 둘러싸기 $\mathrm{cum}_i+[0,1]\cdot\mathrm{cell}_i$가 피적분함수의 부호 변화에서 성립하지 않음; 올바른 둘러싸기 $\mathrm{cum}_i+[0,d]\cdot G_i$와의 차를 셀마다 계산해 바깥 인자의 닫힌 꼴 상계로 여백 감소량을 상계; 최악 셀에서 $2.3$–$3.6\times10^{-5}$, 첫 셀에서 최대 $4.8\times10^{-3}$이나 그 셀의 여백은 $0.046$ 이상), F2(Taylor 영역의 반직선 꼬리에서 $\mathrm{nu}$, $\mathrm{qy}$의 $\mathrm{ku}$ 도함수 항 누락; $100$배 안전 계수), F5($|\mathrm{nu}_{\mathrm{ku}\mathrm{ku}}|$ 식의 여분 항; F2와 합쳐 상자당 $9.6\times10^{-7}$ 이하), F3($\hat{\mathrm{Wr}}_0$ 꼬리의 불완전 감마 상계; $4\times10^{-11}$ 이하), F4(먼 윤곽의 $\mathrm{far}_0$ 누락과 $\log\mathrm{et}(\frac12)$의 오기; $e^{-800}$ 규모). 정정 후 모든 상자·셀의 최소 여백은 $0.00156$(G07, $\hat x\in[9.8,10]$)이다. 여백은 $\hat x$와 함께 줄어 최악 셀은 언제나 $\hat x\in[9.8,10]$이다(예: A 상자에서 $\Upsilon_{e,0}\in[0.0087,0.0107]$, $\Upsilon_{B,0}\in[0.0060,0.0067]$). 상자 A00의 자료로 $\hat x\in[10,12]$를 시험하면 모든 셀이 양수였으나(여백 $0.0017\to0.0006$) 모든 상자에 적용하지 않았다.

**독립 재계산.** 상자 모임: $44$개 인증 JSON의 $\mathrm{ku}$ 구간이 빈틈없이 $[0,10001^{-1/3}]$을 덮고 셀이 $[1.4,10]$을 덮음을 확인. 참값 포함: 정리 {{4:old-4-5}}의 증명의 양의 재귀를 독립 구현해($n\le7$ 전수 주차와 일치) 상자 A00, A01, A05, A10, A15, A20의 $k$ 표본에서 창의 모든 정수 $r$의 $\Upsilon_e$, $\Upsilon_B$를 배정밀도로 계산해 인증 Taylor 모형 안에 듦을 확인($154{,}089$개 위치, 실패 $0$, 최소 여유 $3.02\times10^{-4}$; 같은 계산에서 $e_n/B_{n,k-1}\ge1.54$). $\mathrm{Bt}$ 포함: 보조정리 {{5:cut-rep}}(다)의 실수축 적분을 40자리로 독립 구현해 $9$개 상자 양끝의 $1{,}045$개 점에서 포함을 확인(최소 상대 여유 $0.043\%$, G13의 $k=10^{18}$); $k=400,4000,10001$에서 (다) 자체를 유한합과 상대 $10^{-37}$ 안에서 대조. 상수: 위의 구간 검증. F1–F5를 고친 코드로 $44$개 상자 전체를 다시 실행하지는 않았고(약 $40$ CPU시간), 정정은 저장된 자료와 닫힌 꼴 상계로 했다.

**자료.** `records/ra4c01fca85d24f5cb35be1ec80d8e1c8/evidence/producer-code/`(rig_*.py), `evidence/certificates/cert2/`, `cert3/`(상자별 JSON), `evidence/certificates/ubox_00_ext_xhat10-12.json`, `evidence/peer/coverage_check.py`, `coverage_check.out`, `exact_en_B.py`, `contain_check.py`, `contain_*.log`, `h_exact.py`, `check_h_contain.py`, `h_contain.jsonl`, `check_constants.py`, `check_xi.py`, `aposteriori_F1b.py`, `F1_percell.py`, `F1_all.jsonl`, `F1_table.md`, `bound_F2_F5.py`.

**출처.** [ra4c01fc] §5, §7.1–7.2, §8.1–8.5.

# -*- coding: utf-8 -*-
"""결정 124(15차 독립 검토와 G 물결 수리), 번역측 전달 18절, 작업 장부 현재 상태 줄을 덧붙인다. 2026-11-16 14:1x."""
import io
ROOT = r"C:\math\임시\주차함수_증명"
DEC = ROOT + r"\대조v2\장부_설계_세션결정.md"
TR = ROOT + r"\대조v2\수학검사2\번역측_전달_1115.md"
LG = ROOT + r"\작업_장부.md"

d124 = r"""
124. **전체 독립 검토 15차(F1–F14; 이력 비공개)와 그 수리(G 물결)(2026-11-16 12:2x–14:1x).** 열다섯 보고(`대조v2/수학검사2/검토전체15_F*.md`; F7a·F7b): 검토자 셈으로 수학 0·사실 3·정합 7·문면 12. F1(장1·2)·F4(5B 본문)·F5(장6)·F7b(7B 뒤)는 문제 없음, F14는 대응표·의존지도·구조표 0건. 사실 셋은 D.xcert-partAB 식 (1) 근방 항의 계승 $j!\to i!$(보조정리 fourier-lemmas(바)·재계산 코드는 안쪽 첨자 — 적힌 대로도 유효한 상계였으나 재현이 어긋남; GD), 장부 1.1 「쓰이는 장」 과대 기재와 7절 머리말의 기록 셋 자리(GL). 수리는 판정 없이 작업자가 정했다(`파견/전체검토15_수리_공통_1116.md` 4절; G11은 앞 단계 인계 때문에 뒤에 파견). **큰 결정:** **G6 — 7.3절 극의 로그 $\varsigma_k$와 비 $\gamma_k$를 로마체 $\mathrm{lp}_k:=k\log(e\rho_k)$·$\mathrm{lpr}_k:=\mathrm{lp}_k/k$로**(같은 토큰 `\varsigma_k`가 장6 914행·장10 153·177행에서는 머묾 질량 $\varsigma_k(k)$였고 7B 523행은 그 함수 꼴 그대로 — 3차 SL이 「7장 국소」로 예외 처리한 자리; 7A·7B 24토큰·부록D_장7A·7B 약 430+71토큰·11.3 103행·장부·부록 A·C 연동; GL은 R1′대로 전역 등록); **정리 transfer-F → 보조정리**(쓰이지 않는 (가)와 dip$_k$ 문단 제거, (나)만 기록 그대로 — 작성자 판단 표지·† 제거; 이름 「갱신 창 꼬리의 상계」; 4절 종류 열은 `_sync_4절이름.py`가 종류도 맞추도록 넓힘); polar-W(가)의 $1.446/\sqrt k$ 상계 삭제(결정 107 선례; D 120행 둘). **G3 — 보조정리 response-kernel·fixed-size-response 삭제**(결론이 어느 증명에도 쓰이지 않음; inverse-renewal에 $\mathrm{gn}_d$ 정의와 두 줄 계산을 옮겨 자족화; 라벨 400→398), $\mathfrak I\to\mathrm{hl}$(cut-rep(라)의 반직선 적분; 5.4.2절의 $\mathfrak J$와 인쇄 구별), $\Delta^3f(y)$ 풀어 적기, suff-cond(가) 증명의 $L_1,L_2,L_3$ 정의 문장, old-5-13 증명의 상자 $U$·셀 $X$ 풀어 적기, FKG 둘째 괄호 「(표준)」. **G4 — 5B 꼬리 창 폭 $\varrho_0\to\mathrm{wid}$, 포락선 $\bar\varrho_0\to\overline{\mathrm{wid}}$**(63토큰; D.band-check 9토큰; 장부 378·381행). G9 — 9.1절 국소 합 $\mathfrak s_1,\mathfrak s_2\to\mathrm{rs}_1,\mathrm{rs}_2$(부록D_장7A가 같은 글리프를 또 다른 뜻으로 써 세 뜻 — 14차 J9의 둠을 새 사실로 뒤집음; GD는 D의 $\mathfrak s_1$을 $\mathrm{lp}_\ast:=\mathrm{lp}_{\mathrm U}(10^{30})$과 자유 변수 $\mathrm{lp}$로), 336행 「2.4절에서 적었듯」 문장을 실제 까닭으로, 185행 $\varsigma_2\to\varsigma$. G2 — 장4 418행 나무 함수 특이점 전개의 세 문장 유도($\mathfrak u$), 장3 143–167행 자유 지표 $k\to i$. G1 — 1.5절 180행에 「4·5장의 수준 $\ell$로 적는 명제 $\mathsf Q$·$\mathsf W$·$\mathsf W^\sharp$와 그 위치에서는 $k=\ell+1$로 읽는다」. G5 — 장6 489행 $X$를 $(n+1)^{1/3}$로 풀어 적음. G7 — 7.4절 머리 「닫을 입력을 세운다」(7A 887행도 G6가 같은 방향), theorem-W $0.14$는 일곱째로 둠(「여유를 두고」 한 마디도 사족으로 봄). G8 — 장 머리 21행에서 착지 창(숲 크기 $k+q$)과 조립의 「창 착지」(크기 $k+q$ 나무에 내려서는 걸음)를 함께 정의해 한 칸 차이를 밝힘(13차 C8 처분의 재조정), 583행 축약; 7:explicit-bounds와의 중복은 둠. G10 — 45행 첫째 사실을 10.3절 222행의 한 줄 유도로, old-8-17의 $\theta_i\to\mathrm{ex}_i$, old-8-37 글귀를 주 정리와 맞춤. GD — 위 둘에 더해 D.zeta-constants 알고리즘 줄의 기록 상수를 코드 구간 그대로(하계의 근거를 「결과」 줄의 재계산 구간으로). G11 — 103행 $\mathrm{lp}_{\mathrm L}$·$\mathrm{lp}_{\mathrm U}$, 141행 response-kernel 제거. GL — 부록 B 머리말의 「지식 저장소의 판 415…438·우려·철회」를 「2026-11-13에 보관된 상태 … 그 뒤 고쳐지거나 거두어진 기록 없음」으로, 부록 C 55–56행 「첫 판·7A 집필자」 제거, 1.1 $t$·$u$ 행, 6절 선언 둘(극한 $X$·$o(\cdot)$ 예외), 7절 머리말, $(\mathrm P\Diamond)$ 꼬리표 등록, 1.3 365·371·377·378·381·393·394·397·398·402·409·411행, 4절 뺌 행 둘, 부록 C 283행·구조표 85행 등 46자리. 오독·둠: F3 5절 1·F14-4(본문 $o(n^{2/3})$ — 선언 범위를 고침), F7b 5절 2(중복 증명 — 보존), F11 4절 셋(취향). **세션:** `_sync_4절이름.py` 종류 열, `_gen_재실행표.py`·`_재실행표_여유.json`의 $\varsigma$·$1.446$ 토큰, 16차 파견문(E)·공통(I) 준비. 파이프라인 14:06: 조립 2,352,252바이트·10,956행·라벨 398·부록 D 42; 의존지도 398·뺌 53·입력 381·순환 0·상호 인용 묶음 17·문헌 83; 불변식·괄호·지위·자리표시자·조사 0; 자료묶음 592·1271·문제 0; SHA 관문 0; 스냅샷 14:07. **사용자에게 올릴 것:** 정리 theorem-W의 $0.14$(10–15차 일곱 번 지적·일곱 번 둠 — 「둔다」로 못 박을지).
"""

tr18 = r"""
## 18. 전체 독립 검토 15차 수리 뒤의 변경(11-16 14:1x)

결정 124. 정본은 `대조v2/수학검사2/인계_전체15_G*.md`(G1–G11·GD·GL).

- **진술의 삭제와 번호.** 보조정리 `{{5:response-kernel}}`·`{{5:fixed-size-response}}`를 지웠다(원문은 `인계_전체15_G3.md` 첫머리). 5A 진술 둘 줄고 전체 라벨 400→398; 5.2.2절 안의 번호가 당겨진다. 보조정리 `{{5:inverse-renewal}}`은 진술에 $\mathrm{gn}_d:=\Gamma_d(y;n)/(n)_d$(옛 $\mathrm{fs}'_d$)를 직접 정의하고 증명 첫머리에 두 줄 계산을 품는다. 정리 `{{7:transfer-F}}`는 **보조정리**가 되었고 (가)·dip$_k$ 문단이 사라져 (나) 하나(번호 없음), 이름 「갱신 창 꼬리의 상계」, 머리 「[증명됨; rb7effe0]」. 명제 `{{7:polar-W}}`(가)의 $\mathfrak P_k(n)\le1.446/\sqrt k$ 주장 삭제.
- **글자(전역).** 7.3절 극의 로그 $\varsigma_k\to\mathrm{lp}_k:=k\log(e\rho_k)$, 비 $\gamma_k\to\mathrm{lpr}_k$, 자유 변수 $\varsigma\to\mathrm{lp}$, $\varsigma_{\mathrm L},\varsigma_{\mathrm U}\to\mathrm{lp}_{\mathrm L},\mathrm{lp}_{\mathrm U}$, 「$\varsigma$-구간」→「$\mathrm{lp}$-구간」(7A·7B·부록D_장7A·7B·11.3 103행·장부·부록 A 227행·부록 C 555행). 머묾 질량 $\varsigma_m(\ell)$ 가족·9.2 $\gamma_m$·level-chain(다) $\gamma^{(z)}$·Higham 상수 $\gamma_n$은 그대로. 부록D_장7A의 상수 $\mathfrak s_1\to\mathrm{lp}_\ast:=\mathrm{lp}_{\mathrm U}(10^{30})$, [A9]의 자유 인수 $\mathfrak s_1\to\mathrm{lp}$.
- **글자(국소).** 5B 꼬리 창 폭 $\varrho_0\to\mathrm{wid}$, $\bar\varrho_0\to\overline{\mathrm{wid}}$(5B 63토큰; D.band-check 9토큰; 장부 378·381행). 5A $\mathfrak I\to\mathrm{hl}$(cut-rep(라) 반직선 적분; D.critical-window-rig 134·136행). 9.1절 명제 prop-6 증명 $\mathfrak s_1,\mathfrak s_2\to\mathrm{rs}_1,\mathrm{rs}_2$; 185행 $\varsigma_2\to\varsigma$. 장3 143–167행 자유 지표 $k\to i$($i'$). 장4 418행 $\mathfrak u:=1-T(e^{-1-\Upsilon})$(유도 세 문장). 10.5절 old-8-17 $\theta_i\to\mathrm{ex}_i$(6.5절 글자). 장6 489행·5A 798행의 국소 $X$·$U$는 글자 없이 풀어 적음. 5A 340행 $L_1,L_2,L_3$ 정의 문장(등록). $(\mathrm P\Diamond)$ 꼬리표를 장부 1.2·부록 A에 등록.
- **낱말·서술.** 1.5절 180행 한 문장(4·5장의 $\ell$ 명제는 $k=\ell+1$로 읽음). 5A 148행 $\Delta^3f$ 풀어 적기, 278행 「(표준)」. 7A 731행 `**증명.**`, 805행 「따름정리 flat-threshold(나)의 모멘트 판정」, 878행·7B 3행 「닫을 입력을 세우고 … 7.5절의 따름정리 qstar-implies-wlflat이 닫는다」. 장8 21행 착지 창/창 착지 정의, 583행 축약. 장9 336행 두 문장. 장10 45·222행(첫째 사실의 자리 이동), 767행 주 정리 글귀. 장11 141행. 부록 B 머리말 3행, 부록 C 55–56행. D.xcert-partAB 식 (1) $j!\to i!$, D.zeta-constants 알고리즘 줄의 구간 상수 `ZM12_ABS`, D.Q-fin·D.polar 등은 lp 꼴.
- **장부·부록 A·C·구조표.** `인계_전체15_GL.md`·`수리_전체15_GL.md`가 정본 — 1.1 $t$·$u$ 행, 1.2 305·339행(lp·(P◇)), 1.3 365·371·377·378·381·393·394·397·398·402·409·411행, 2절 433행, 4절 뺌 행 둘·995행(생성 동기화), 5절 1208행, 6절 1221·1240행(선언 예외), 7절 머리말·1387행, 부록 A 227·274·295행 등 4, 부록 C 55–56·191·192·283·555행, 구조표 85행 등 3.
"""

STATE = (
    "\n- 14:1x 15차 수리 회수·파이프라인·PDF(이 세션): G1·G2·G3·G4·G5·G6·G7(두 단계)·G8·G9·G10·GD(두 단계)·G11·GL 열셋 회수(보고·인계 `대조v2/수학검사2/수리_전체15_G*.md`·`인계_전체15_G*.md`; 결정 124 — 큰 것: 7.3절 ς_k·γ_k→lp_k·lpr_k(전역 등록), transfer-F 정리→보조정리, response-kernel·fixed-size-response 삭제(라벨 398), ϱ₀→wid, 𝔍→hl, 𝔰₁·𝔰₂→rs, polar-W 1.446 삭제, 장8 착지 창 정의 재조정). "
    "세션: `_sync_4절이름.py` 종류 열 동기화 추가, `_gen_재실행표.py`·`_재실행표_여유.json` 옛 토큰(ς-구간·ς_L) → lp, 16차 파견문 `전체_독립검토16_파견문_1116.md`(태그 E)·공통 `전체검토16_수리_공통_1116.md`(태그 I) 준비. 파이프라인 14:06: 4절 2칸(transfer-F 종류·이름), 11.2 6열 3행, 조립 2,352,252바이트·10,956행·라벨 398·부록 D 42, 의존지도 398·뺌 53·입력 381·순환 0·묶음 17·문헌 83, 불변식·괄호·지위·자리표시자·조사 0, 자료묶음 592·1271·문제 0, SHA 관문 0, 스냅샷 14:07, 재실행표 재생성. PDF 렌더(`_pdf검사/md2pdf_1116_1408.log`) 배경. 번역 18절. 차례별 지적 수: 10차 ~50, 11차 38, 12차 33, 13차 29, 14차 19, 15차 22. "
    "**사용자 올림:** theorem-W 0.14(일곱 번 지적·일곱 번 둠 — 「둔다」로 못 박을지)."
)

s = io.open(DEC, encoding="utf-8").read(); assert "124. **" not in s
io.open(DEC, "w", encoding="utf-8", newline="\n").write(s.rstrip("\n") + "\n" + d124.lstrip("\n"))
t = io.open(TR, encoding="utf-8").read(); assert "## 18." not in t
io.open(TR, "w", encoding="utf-8", newline="\n").write(t.rstrip("\n") + "\n" + tr18.lstrip("\n"))
g = io.open(LG, encoding="utf-8").read()
A = "- 13:0x 15차 독립 검토 회수(이 세션):"
i = g.find(A); assert i > 0
j = g.find("\n", i)
io.open(LG, "w", encoding="utf-8", newline="\n").write(g[:j] + STATE + g[j:])
print("결정 124·번역 18절·장부 ok")

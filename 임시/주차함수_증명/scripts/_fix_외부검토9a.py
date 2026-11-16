# -*- coding: utf-8 -*-
"""아홉째 묶음 일괄 처리 1부(결정 90): 문면·수치 교정(장6·장8·장9·장10·장부_v2·부록D_장9·부록D_장10)과
D.15·D.28·D.5의 자리표시자 판(계산이 끝나면 [Dn:…]을 채운다). 앵커 횟수가 1이 아니면 쓰지 않는다. 멱등.
--show 는 2부에서 손볼 자리의 문맥만 출력한다."""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv
SHOW = "--show" in sys.argv


def rd(rel):
    return io.open(os.path.join(ROOT, rel), encoding="utf-8").read()


def wr(rel, s):
    io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)


# (파일, 원문, 바꿈) — 원문은 정확히 한 번 있어야 한다(이미 바뀐 경우는 바꿈이 있으면 통과).
EDITS = [
    # (f) 6.3절 생존확률 설명
    ("장v2/장6.md",
     r"을 쓴다. 크기 $y+d-1$의 숲에 용량 $y$를 넘는 나무가 없을 확률이고 $\mathfrak s_1(y)=1$이다.",
     r"을 쓴다. 길이 $y+d-1$의 균등 주차함수가 문턱 $y$를 살아남을 확률, 곧 최대 변위가 $y-1$ 이하일 확률이고 $\mathfrak s_1(y)=1$이다."),
    # (a) 정리 6.45의 𝗏 값
    ("장v2/장6.md",
     r"이고, $\mathsf v$는 $k\ge3131$에서 증가하며 $\mathsf v(3131)=0.082$, $\mathsf v(6667)=0.7654$, $\mathsf v(10^4)=0.99$, $k\to\infty$에서 $\mathsf v(k)\to2$다.",
     r"이고, $\mathsf v$는 $k\ge3131$에서 증가하며 $\mathsf v(3131)>0.082$, $\mathsf v(6667)>0.7654$, $\mathsf v(10^4)>0.992$, $k\to\infty$에서 $\mathsf v(k)\to2$다."),
    ("장v2/장6.md", r"$k=3131$에서 이 값은 $24000/2263^{3/2}=0.2229$다.", r"$k=3131$에서 이 값은 $24000/2263^{3/2}<0.22294$다."),
    ("장v2/장6.md", r"$k=3131$에서 $2-0.2229-0.7900=0.9871$이다.", r"$k=3131$에서 $2-0.22294-0.79001>0.98705$이다."),
    ("장v2/장6.md", r"최솟값은 $\mathsf v(3131)=0.9871-0.9048=0.0823>0.082$이며",
     r"최솟값은 $\mathsf v(3131)=2-0.222938-0.790002-0.904795=0.082265\ldots>0.082$이며"),
    ("장v2/장6.md", r"$\mathsf v(6667)=2-0.0735-0.5411-0.6200=0.7654$, $\mathsf v(10^4)=2-0.0600-0.4418-0.5062=0.992$이며",
     r"$\mathsf v(6667)=2-0.073494-0.541103-0.619997=0.765405\ldots>0.7654$, $\mathsf v(10^4)=2-0.060006-0.441753-0.506225=0.992015\ldots>0.992$이며"),
    ("장v2/장10.md", r"$\mathsf v(k)\ge\mathsf v(6667)=0.7654$", r"$\mathsf v(k)\ge\mathsf v(6667)>0.7654$"),
    ("장v2/장9.md", r"$\mathsf v(k)\ge\mathsf v(6668)=0.7654$", r"$\mathsf v(k)\ge\mathsf v(6668)>0.7654$"),
    ("장부_v2.md", r"$k$에 증가; $\mathsf v(6667)=0.7654$)", r"$k$에 증가; $\mathsf v(6667)>0.7654$)"),
    ("장부_v2.md", r"| (Q76) 함수 $\mathsf v(k)$의 값 | $\mathsf v(6667)=0.7654$, $\mathsf v(6668)=0.7654$(네 자리로 통일; 정확한 값은 부록 D) |",
     r"| (Q76) 함수 $\mathsf v(k)$의 값 | $\mathsf v(6667)>0.7654$, $\mathsf v(6668)>0.7654$(네 자리 하계로 통일; 정확한 값은 부록 D) |"),
    ("장부_v2.md", r"명명된 상수 함수. $\mathsf L_\ast(6668)=1.206$)", r"명명된 상수 함수. $\mathsf L_\ast(6668)\ge1.206$)"),
    # (b) D.43과 9장
    ("장v2/부록D_장9.md",
     r"$\mathsf L_\ast(6668)=\mathcal J_1(6668)+\mathcal J_2(6668)+\mathcal J_3(6668)+\mathcal J_4(6668)=1.206$이고, 특히 $\mathsf L_\ast(6668)>1.0845$다.",
     r"$\mathsf L_\ast(6668)=\mathcal J_1(6668)+\mathcal J_2(6668)+\mathcal J_3(6668)+\mathcal J_4(6668)\ge1.206$이고, 특히 $\mathsf L_\ast(6668)>1.0845$다."),
    ("장v2/부록D_장9.md",
     r"비교 상수 $1.0845=(1+\bar{\mathfrak d}/2)/(1-\bar{\mathfrak d}/2)$, $\bar{\mathfrak d}=6.62/\sqrt{6668}$;",
     r"비교 상수 $1.0845$는 띠 요구값 $(1+\bar{\mathfrak d}/2)/(1-\bar{\mathfrak d}/2)$의 상계, $\bar{\mathfrak d}=6.62/\sqrt{6668}$;"),
    ("장v2/부록D_장9.md",
     r"$\mathsf L_\ast(6668)\in[1.20601,1.20607]$, 곧 $\mathsf L_\ast(6668)=1.206$이며 아래 끝이 $1.0845$보다 $0.1215$ 크다",
     r"$\mathsf L_\ast(6668)\in[1.20601,1.20607]$, 곧 $\mathsf L_\ast(6668)\approx1.206$이고 증명에 쓰이는 하계 $\mathsf L_\ast(6668)\ge1.206$이 나오며, 아래 끝이 $1.0845$보다 $0.1215$ 크다"),
    ("장v2/장9.md", r"\ \ge\ \mathsf L_\ast(6668)=1.206", r"\ \ge\ \mathsf L_\ast(6668)\ \ge\ 1.206"),
    ("장v2/장9.md",
     r"$\mathsf L_\ast(6668)$은 초등 적분의 구적값이고, 이 값은 부록 D.{{D:AR-integrals}}의 계산으로 확인된다.",
     r"$\mathsf L_\ast(6668)$은 초등 적분의 구적값($\approx1.20604$)이고, 하계 $1.206$은 부록 D.{{D:AR-integrals}}의 계산으로 확인된다."),
    ("장v2/장9.md", r"($\mathsf L_\ast(6668)=1.206>1.0845$)", r"($\mathsf L_\ast(6668)\ge1.206>1.0845$)"),
    # (g) 8.27 용어
    ("장v2/장8.md", r"상가평균–상승평균 부등식 $(k+q)(m+1-k-q)\le((m+1)/2)^2$", r"산술–기하 평균 부등식 $(k+q)(m+1-k-q)\le((m+1)/2)^2$"),
    # (d) D.46 recheck_1a 상수 단서
    ("장v2/부록D_장10.md",
     r"치환 꼴로 두 적분을 다시 적분해 $\mathrm{DDL}^\natural(9705)$를 소수 넷째 자리 $0.1133$까지 재현했다.",
     r"치환 꼴로 두 적분을 다시 적분해 $\mathrm{DDL}^\natural(9705)$를 소수 넷째 자리 $0.1133$까지 재현했다. 그 코드와 기록의 `cf.py`는 상수를 아래로 반올림한 $0.708345$, $2.528570$으로 두어 $\mathfrak j_2=2.7171423\ldots$, $\mathfrak j_1=0.7998520\ldots$을 얻었고, 그 $\mathrm{DDL}^\natural$은 위의 값보다 $2.7\times10^{-6}$ 이하만큼 작으며 넷째 자리는 같다."),
    # D.15 자리표시자 판(고친 코드의 전체 재실행을 전제; 계산 뒤 [D15:…]을 채운다)
    ("장v2/부록D_장5A.md",
     r"### D.{{D:critical-window-rig}} 임계 창 인증의 둘러싸기 설계, 상자 모임, 구간 검증 상수와 사후 정정 (정리 {{5:old-5-13}})",
     r"### D.{{D:critical-window-rig}} 임계 창 인증의 둘러싸기 설계, 상자 모임과 구간 검증 상수 (정리 {{5:old-5-13}})"),
    ("장v2/부록D_장5A.md",
     r"(상자 중점 둘레의 이차 Taylor; 정정판은 분모 $\mathrm{ku}\mathrm{qy}-\mathrm{Zh}$ 꼴)",
     r"(상자 중점 둘레의 이차 Taylor; 분모는 $\mathrm{ku}\mathrm{qy}-\mathrm{Zh}$ 꼴)"),
    ("장v2/부록D_장5A.md",
     r"안쪽 누적은 사다리꼴에 $\frac{d^3}{12}|g''|$;",
     r"안쪽 누적은 사다리꼴에 $\frac{d^3}{12}|g''|$, 셀 안의 누적 적분은 $\mathrm{cum}_i+[0,d]\cdot G_i$($G_i$는 셀 $i$ 위 피적분함수의 둘러싸기)로 감싼다;"),
    # D.28 자리표시자 판
    ("장v2/부록D_장7A.md",
     r"**산술 등급.** 방향 반올림 구간. 144비트 고정소수점 정수 구간이고 독립 재계산은 160비트다.",
     r"**산술 등급.** 방향 반올림 구간. 144비트 고정소수점 정수 구간이고, 기록의 독립 재계산은 160비트, 이 글의 재계산은 [D28:비트]비트다."),
    ("장v2/부록D_장7A.md",
     r"〔구현 다른 방법·같은 식의 새 구현; 범위 부분(k=121,128,140,160,161과 정수 부등식); 산술 방향 반올림 구간·정확 정수·유리수; 자료 기록〕",
     r"〔구현 다른 방법·같은 식의 새 구현; 범위 전체; 산술 방향 반올림 구간·정확 정수·유리수; 자료 기록·이 글〕"),
    ("장v2/부록D_장7A.md",
     r"정수 부등식은 기록의 작성자와 검토가 각각 정확히 계산했다.",
     r"정수 부등식은 기록의 작성자와 검토가 각각 정확히 계산했다. 이 글을 쓰며 같은 마지막 차 재귀를 정확한 큰 정수 합성곱의 온라인 분할 정복으로 새로 구현해 $121\le k\le500$의 $380$열 전부를 [D28:비트]비트 정수 구간으로 다시 인증했다(작업자 [D28:작업자]개, [D28:시간]). 모든 열에서 직접 차분과 띠 비교가 통과했고, 직접 차분의 최소 상대 여유는 $k=500$에서 [D28:최소여유]로 기록의 값과 [D28:차이] 안에서 같다."),
    ("장v2/부록D_장7A.md",
     r"`records/rc9aee436a1c34c438719b6c5d5ed79b5/evidence/peer/output/indep-lastcar-161.json`" + "\n",
     r"`records/rc9aee436a1c34c438719b6c5d5ed79b5/evidence/peer/output/indep-lastcar-161.json`; `원고_자료/세션_재계산/column_k500_iv/`([D28:파일]; 코드, 열별 인증 JSON, 실행 기록)" + "\n"),
    # D.5 자리표시자 판
    ("장v2/부록D_장4.md",
     r"〔구현 같은 식의 새 구현·다른 방법; 범위 부분($k=8$–$1000$ 전부와 $1000<k\le10000$의 $107$개, (ㄴ)은 전체); 산술 정확 정수·유리수; 자료 기록〕",
     r"〔구현 같은 식의 새 구현·다른 방법; 범위 전체; 산술 정확 정수·유리수; 자료 기록·이 글〕"),
    ("장v2/부록D_장4.md",
     r" 표본 밖의 $k$는 C 프로그램의 올바른 실행에 기댄다.",
     r" 이 글을 쓰며 같은 검토 코드(`rev_icert_unpaired_fast.py`)를 $1001\le k\le10000$의 $9000$열 전부에 돌려 C 출력과 비트 단위로 같음을 확인했다(작업자 [D5:작업자]개, [D5:시간]). 그러므로 $19985$개 판정 모두에서 두 구현의 출력이 같다."),
    ("장v2/부록D_장4.md",
     r"`rev_icert_dense.out`, `rev_icert_small.out`, `rev_small_exact_out.json`." + "\n",
     r"`rev_icert_dense.out`, `rev_icert_small.out`, `rev_small_exact_out.json`; `원고_자료/세션_재계산/icert_py_full/`([D5:파일]; 실행 기록과 열별 대조 결과)." + "\n"),
]

# D.15의 결과·독립 재계산·자료 줄은 통째로 바꾼다.
D15_RESULT = (r"**결과.** 모든 상자·셀의 여백이 양수다. 최소 여백은 [D15:최소여백](G07, $\hat x\in[9.8,10]$)이다. "
              r"여백은 $\hat x$와 함께 줄어 최악 셀은 언제나 $\hat x\in[9.8,10]$이다(예: A 상자에서 $\Upsilon_{e,0}\in[0.0087,0.0107]$, $\Upsilon_{B,0}\in[0.0060,0.0067]$).")
D15_RECOMP_TAIL_OLD = r"상수: 위의 구간 검증. F1–F5를 고친 코드로"
D15_RECOMP_NEW_TAIL = (r"상수: 위의 구간 검증. 이 글을 쓰며 위의 알고리즘을 그대로 구현한 코드로 $44$개 상자와 첫 셀 재인증 다섯을 모두 다시 돌렸다(작업자 [D15:작업자]개, [D15:시간]). "
                       r"모든 셀의 여백이 양수이고 최솟값은 [D15:최소여백](G07, $\hat x\in[9.8,10]$)이며, 상자별 최소 여백은 기록의 인증서가 저장한 값과 [D15:차이] 안에서 같다. "
                       r"저장된 인증서만 읽어 모든 셀의 여백이 양수임을 다시 확인하는 작은 검증기([D15:검증기])를 함께 둔다.")
D15_TAG_OLD = r"〔구현 다른 방법·인증서 판독; 범위 부분(참값 대조는 표본 상자·표본점)·전체(정정 후 여백의 부호); 산술 배정밀도 평가·40자리 평가·방향 반올림 구간; 자료 기록·이 글〕"
D15_TAG_NEW = r"〔구현 같은 코드 재실행·다른 방법·인증서 판독; 범위 전체(여백의 부호)·부분(참값 대조는 표본 상자·표본점); 산술 배정밀도 평가·40자리 평가·방향 반올림 구간; 자료 기록·이 글〕"
D15_DATA = (r"**자료.** `records/ra4c01fca85d24f5cb35be1ec80d8e1c8/evidence/producer-code/`(rig_*.py), `evidence/certificates/cert2/`, `cert3/`(상자별 JSON), "
            r"`evidence/peer/coverage_check.py`, `coverage_check.out`, `exact_en_B.py`, `contain_check.py`, `contain_*.log`, `h_exact.py`, `check_h_contain.py`, `h_contain.jsonl`, "
            r"`check_constants.py`, `check_xi.py`; `원고_자료/세션_재계산/critical_window_rerun/`([D15:파일]; 코드, 상자별 인증 JSON, 실행 기록, 검증기).")

SHOW_AT = [
    ("장v2/장8.md", "1.009"), ("장v2/장9.md", "1.009"), ("장v2/장9.md", "48966"),
    ("장v2/부록D_장7A.md", "코드를 고"), ("장v2/부록D_장7A.md", "Gamma(5/3)"), ("장v2/부록D_장7A.md", r"\Gamma(5/3)"),
    ("장v2/부록D_장8.md", "1.0091269"), ("장v2/부록D_장9.md", "1.149357"), ("장v2/부록D_장7B.md", "2.437"),
    ("장v2/부록D_장9.md", "38886"), ("장v2/부록D_장5B.md", "1.072666"), ("장v2/부록D_장5B.md", "SQ2PI_INV"),
]


def main():
    if SHOW:
        for rel, key in SHOW_AT:
            s = rd(rel)
            for m in re.finditer(re.escape(key), s):
                ln = s.count("\n", 0, m.start()) + 1
                a = max(0, m.start() - 220); b = min(len(s), m.end() + 260)
                print(f"[{rel}:{ln}] …{s[a:b]}…".replace("\n", " ⏎ ")); print()
        return
    texts = {}
    bad = 0
    for rel, old, new in EDITS:
        s = texts.get(rel) or rd(rel)
        n = s.count(old)
        if n == 0 and new in s:
            print("이미:", rel, old[:50]); texts[rel] = s; continue
        if n != 1:
            print(f"앵커 {n}회: {rel} {old[:70]!r}"); bad += 1; texts[rel] = s; continue
        texts[rel] = s.replace(old, new); print("고침:", rel, old[:50])
    # D.15 통째 줄
    rel = "장v2/부록D_장5A.md"
    s = texts.get(rel) or rd(rel)
    i = s.find("### D.{{D:critical-window-rig}}"); j = s.find("\n### D.", i + 1)
    blk = s[i:j]
    lines = blk.split("\n")
    for k, l in enumerate(lines):
        if l.startswith("**결과.**"):
            if l != D15_RESULT:
                if "사후 감사가" not in l: print("D.15 결과 줄 앵커 없음"); bad += 1
                else: lines[k] = D15_RESULT; print("D.15 결과 줄 교체")
        elif l.startswith("**독립 재계산.**"):
            if D15_TAG_NEW in l and "[D15:검증기]" in l:
                print("D.15 독립 재계산 이미")
            elif D15_TAG_OLD in l and D15_RECOMP_TAIL_OLD in l:
                head = l[:l.find(D15_RECOMP_TAIL_OLD)]
                lines[k] = head.replace(D15_TAG_OLD, D15_TAG_NEW) + D15_RECOMP_NEW_TAIL; print("D.15 독립 재계산 줄 교체")
            else:
                print("D.15 독립 재계산 앵커 없음"); bad += 1
        elif l.startswith("**자료.**"):
            if l != D15_DATA:
                if "aposteriori_F1b.py" not in l: print("D.15 자료 줄 앵커 없음"); bad += 1
                else: lines[k] = D15_DATA; print("D.15 자료 줄 교체")
    texts[rel] = s[:i] + "\n".join(lines) + s[j:]
    if bad:
        print("문제", bad, "— 쓰지 않음"); sys.exit(1)
    if DRY:
        print("(dry)"); return
    for rel, t in texts.items():
        wr(rel, t)
    print("기록함", len(texts), "파일")


if __name__ == "__main__":
    main()

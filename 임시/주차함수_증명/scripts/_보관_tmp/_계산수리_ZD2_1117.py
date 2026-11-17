# -*- coding: utf-8 -*-
"""22차 ZD2 인계 「세션」 1–4·7–9의 집행(2026-11-17 21:xx).
(1) moment_cert_iv에서 첫째 범위(A3) 파일·운영 스크립트·미등재 작업 스크립트를 보관으로; summarize_nb.py RANGES → A5; run_ct.sh; README 490행 문단.
(2) 「직접 차분」→「직접 비교」: _gen_재실행표.py 73행, _재실행표_여유.json 10행, README 492행.
(3) _gen_재실행표.py moment CONFIG(cmd·outputs·expect·time).
(4) four_families_DDLnat의 작업 메모 둘 보관.
SHA 표 갱신(_patch_README_세션파일.py)과 summarize_nb.py 재실행은 이 스크립트 뒤 셸에서."""
import io, os, shutil
ROOT = r"C:\math\임시\주차함수_증명"
CALC = os.path.join(ROOT, "원고_자료", "세션_재계산")
KEEP = os.path.join(ROOT, "대조v2", "보관_자료_1117", "세션_재계산_미등재_1117")
os.makedirs(KEEP, exist_ok=True)

def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, s): io.open(p, "w", encoding="utf-8", newline="\n").write(s)
def sub1(s, a, b, n=1):
    c = s.count(a); assert c == n, (a[:70], c); return s.replace(a, b)

moved = []
def mv(rel):
    src = os.path.join(CALC, rel); dst = os.path.join(KEEP, rel)
    assert os.path.exists(src), src
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.move(src, dst); moved.append(rel)

# (1) A3 파일 여덟 + 운영 스크립트 둘 + 미등재 작업 스크립트(make_draft*) + 작업 메모 둘
for i in range(4):
    mv(f"moment_cert_iv/sweep_ct_A3_s{i}.jsonl"); mv(f"moment_cert_iv/sweep_ct_A3_s{i}.log")
for rel in ["moment_cert_iv/handoff_A3.py", "moment_cert_iv/launch_handoff.py",
            "moment_cert_iv/make_draft.py", "moment_cert_iv/make_draft_v2.py",
            "column_k500_iv/make_draft.py", "column_cert_iv/make_draft.py", "icert_py_full/make_draft.py",
            "four_families_DDLnat/변경.md", "four_families_DDLnat/결과_요약.md"]:
    mv(rel)

# summarize_nb.py
p = os.path.join(CALC, "moment_cert_iv", "summarize_nb.py"); s = rd(p)
s = sub1(s, 'nb = {k_: v for k_, v in load("sweep_ct_").items() if k_[0] in ("A3", "A5")}', 'nb = {k_: v for k_, v in load("sweep_ct_").items() if k_[0] in ("A5",)}')
s = sub1(s, 'RANGES = ("A3", "A5")  # (A1)(A2) were removed from the item', 'RANGES = ("A5",)  # (A1)(A2)(A3) were removed from the item (A3 on 2026-11-17: the text does not use columns 501-840)')
wr(p, s)

# run_ct.sh
p = os.path.join(CALC, "moment_cert_iv", "run_ct.sh"); s = rd(p)
s = sub1(s, "# order A5 -> A3 (A1, A2 removed from the item), one output file per range (resumable: rerun this script).",
            "# range A5 only (A1, A2, A3 removed from the item), one output file per range (resumable: rerun this script).")
s = sub1(s, "for rg in A5 A3; do", "for rg in A5; do")
s = sub1(s, "echo ALL_CT_DONE >> sweep_ct_A3.log", "echo ALL_CT_DONE >> sweep_ct_A5.log")
wr(p, s)

# README 490·492행
R = os.path.join(ROOT, "원고_자료", "README.md"); s = rd(R)
s = sub1(s, "부록 D의 모멘트 판정 항목(두 범위의 재귀 인증)을 구간 산술로", "부록 D의 모멘트 판정 항목(재귀 인증)을 구간 산술로")
s = sub1(s, "(벗어나면 척도 $\\beta$를 고쳐 다시 돈다; (A3)는 짧은 선행 실행으로 미리 고친다)", "(벗어나면 척도 $\\beta$를 고쳐 다시 돈다)")
s = sub1(s, "1500열 60,479,535개 위치 전부 통과(실패 0; (A5) 1160열은 프로세스 1개 `mcert_iv.py sweep_nb A5 sweep_ct_A5.jsonl --low --count`, (A3) 340열은 claim 파일로 열을 나눈 샤드 4개 `sweep_ct_mp.py A3 <i>`; 열별 소요 시간 합 219,744초(다른 계산과 코어를 나눠 써서 CPU 시간보다 길다); `sweep_ct_A5.jsonl`·`sweep_ct_A3_s0.jsonl`–`sweep_ct_A3_s3.jsonl`과 로그).",
            "(A5) 1160열 40,638,833개 위치 전부 통과(실패 0; 프로세스 1개 `mcert_iv.py sweep_nb A5 sweep_ct_A5.jsonl --low --count`; `sweep_ct_A5.jsonl`과 로그). 기록의 (A3) 340열(열 $501\\le k\\le840$)도 같은 판으로 통과했으나 본문이 그 범위를 쓰지 않아 항목과 묶음에서 뺐다(2026-11-17 22차; `sweep_ct_mp.py`는 그때 쓴 샤드 도구다).")
s = sub1(s, "기록의 다섯 실행 A1–A5(글이 쓰는 두 범위는 A3·A5이고, A1·A2는 어느 장도 쓰지 않는 추가 계산이다)", "기록의 다섯 실행 A1–A5(글이 쓰는 범위는 A5이고, 나머지 넷은 어느 장도 쓰지 않는 추가 계산이다)")
s = sub1(s, "항목의 1500열에서 두 판의 열별 최솟값 하계는", "항목의 1160열에서 두 판의 열별 최솟값 하계는")
s = sub1(s, " `make_draft.py`·`make_draft_v2.py`는 결과에서 부록 D 항목 본문을 만든다. `handoff_A3.py`·`launch_handoff.py`는 (A3) 샤드의 기동 순서를 자동화한 운영 스크립트다.", "")
s = sub1(s, "직접 차분 20,368,570개·비 비교 10,302,655개", "직접 비교 20,368,570개·비 비교 10,302,655개")
# column_k500 문단·다른 문단의 make_draft 언급
for a in ["`make_draft.py`는 결과에서 부록 D 항목 본문을 만든다. ", " `make_draft.py`는 결과에서 부록 D 항목 본문을 만든다."]:
    s = s.replace(a, "")
print("README make_draft 잔존:", s.count("make_draft"))
wr(R, s)

# (2)(3) _gen_재실행표.py
G = os.path.join(ROOT, "scripts", "_gen_재실행표.py"); s = rd(G)
s = sub1(s, "380열 실패 0(직접 차분 20,368,570개·비 비교 10,302,655개)", "380열 실패 0(직접 비교 20,368,570개·비 비교 10,302,655개)")
s = sub1(s, '''             "python -I sweep_ct_mp.py A3 0", "python -I sweep_ct_mp.py A3 1", "python -I sweep_ct_mp.py A3 2", "python -I sweep_ct_mp.py A3 3",
''', "")
s = sub1(s, 'expect="(A3)(A5) 1500열 60,479,535개 위치 전부 통과(fails 0; BLAS 없는 연산 수 한계 판, 샤드 넷은 동시에 띄움); 상대 여유 하계의 최솟값 $0.137916$((A3) $k=840$); BLAS 행렬곱 대조 판(`sweep 0 2`·`sweep 1 2`)과 1500열 판정 일치; $n_{\\\\mathrm M}(k)$ 1160열 기록과 일치"',
            'expect="(A5) 1160열 40,638,833개 위치 전부 통과(fails 0; BLAS 없는 연산 수 한계 판); 상대 여유 하계의 최솟값 $0.567392$($(n,k)=(10001,2000)$); BLAS 행렬곱 대조 판(`sweep 0 2`·`sweep 1 2`)과 1160열 판정 일치; $n_{\\\\mathrm M}(k)$ 1160열 기록과 일치"')
s = sub1(s, '''        outputs=[S + "moment_cert_iv/summary_noblas.txt", S + "moment_cert_iv/sweep_ct_A5.jsonl", S + "moment_cert_iv/sweep_ct_A3_s0.jsonl", S + "moment_cert_iv/sweep_ct_A3_s1.jsonl",
                 S + "moment_cert_iv/sweep_ct_A3_s2.jsonl", S + "moment_cert_iv/sweep_ct_A3_s3.jsonl", S + "moment_cert_iv/summary.txt", S + "moment_cert_iv/sweep_p0.jsonl",''',
            '''        outputs=[S + "moment_cert_iv/summary_noblas.txt", S + "moment_cert_iv/sweep_ct_A5.jsonl", S + "moment_cert_iv/summary.txt", S + "moment_cert_iv/sweep_p0.jsonl",''')
s = sub1(s, 'time="BLAS 없는 판: (A5) 프로세스 1개(다른 계산과 코어를 나눔; 11-13 22:29–11-15 14:14), (A3) 샤드 4개(11-15 14:14·15:37–21:00); 열별 소요 시간 합 219,744초. 대조 BLAS 판: 프로세스 2개(BLAS 스레드 1)로 2시간 10분(15:25–17:36; 부록 D 범위 밖 열 포함), CPU 합 15,164초 가운데 (A3)(A5) 9,786초"',
            'time="BLAS 없는 판: (A5) 프로세스 1개(다른 계산과 코어를 나눔; 11-13 22:29–11-15 14:14). 대조 BLAS 판: 프로세스 2개(BLAS 스레드 1)로 2시간 10분(15:25–17:36; 부록 D 범위 밖 열 포함), CPU 합 15,164초"')
wr(G, s)
J = os.path.join(ROOT, "scripts", "_재실행표_여유.json"); s = rd(J)
s = sub1(s, '"직접 차분의 최소 상대 여유', '"직접 비교의 최소 상대 여유')
wr(J, s)

# 보관 README
K = os.path.join(ROOT, "대조v2", "보관_자료_1117", "README.md"); s = rd(K)
add = ("\n- **`세션_재계산_미등재_1117/`** (2026-11-17 21:xx 이동; 원래 `원고_자료/세션_재계산/` 아래 같은 상대 경로) — 22차 R12 4절·5절과 ZD2 인계 「세션」 1·9: 부록 D.moment-certification에서 뺀 첫째 범위(A3; 열 501–840)의 출력 `sweep_ct_A3_s0..3.jsonl/.log` 여덟과 그 샤드 기동 스크립트 `handoff_A3.py`·`launch_handoff.py`; 부록 D 항목 본문을 만들던 작업 스크립트 `make_draft*.py` 다섯(moment_cert_iv 둘·column_k500_iv·column_cert_iv·icert_py_full); 작업 메모 `four_families_DDLnat/변경.md`·`결과_요약.md`. 자료 묶음·README SHA 표에서 함께 뺐다.\n")
assert "세션_재계산_미등재_1117" not in s
wr(K, s.rstrip("\n") + "\n" + add)
print("moved", len(moved), moved)
print("ok")

# -*- coding: utf-8 -*-
"""_계산수리_ZD_1117.py의 뒤 절반(README·PARAS·재실행표 CONFIG·summarize_nb 주석). 앞 절반(이동·ivbox_lib·band_iv·test_exact)은 17:1x에 끝났고,
README의 남은 'bprime'은 SHA 표 행 하나(패치 스크립트 --remove로 지움)라 검사를 그 행만 허용하도록 고쳤다."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
CALC = os.path.join(ROOT, "원고_자료", "세션_재계산")

def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, s): io.open(p, "w", encoding="utf-8", newline="\n").write(s)
def sub1(s, old, new, n=1):
    c = s.count(old); assert c == n, (old[:60], c); return s.replace(old, new)

R = os.path.join(ROOT, "원고_자료", "README.md"); s = rd(R)
s = sub1(s, "`bprime_boxes/ivbox_lib.py`(띠 상자가 이것을 쓴다)", "`band_boxes/ivbox_lib.py`(띠 상자가 이것을 쓴다)")
s = sub1(s, "`세션_재계산/bprime_boxes/ivbox_lib.py`는 `band_boxes/band_iv.py`가 쓰는 공용 구간 성분이다.",
            "`세션_재계산/band_boxes/ivbox_lib.py`는 같은 폴더의 `band_iv.py`가 쓰는 구간 성분이다.")
s = sub1(s, "식 (8.30) 자체를 아래에서 막는다", "식 (8.23) 자체를 아래에서 막는다")
s = sub1(s, "$\\Omega$는 `bprime_boxes/ivbox_lib.py`의 정확 정의를 쓴다", "$\\Omega$는 같은 폴더의 `ivbox_lib.py`의 정확 정의를 쓴다")
s = sub1(s, "모멘트 판정 항목 (ㄱ)(두 범위의 재귀 인증)", "모멘트 판정 항목(두 범위의 재귀 인증)")
s = sub1(s, "재귀 (7.2)·(7.3)에 $\\hat{\\mathfrak a}_n$을 곱해", "재귀 (7.1)과 모멘트 재귀 (7.2)에 $\\hat{\\mathfrak a}_n$을 곱해")
s = sub1(s, "$(1\\pm u)^r$", "$(1\\pm\\mathsf p)^r$")
rest = [l for l in s.split("\n") if "bprime" in l]
assert rest == ["| `세션_재계산/bprime_boxes/ivbox_lib.py` | `be4fd555118b17a998788b6484b31252a705c6aba29b97716ba5604776674b0f` |"], rest
wr(R, s)

P = os.path.join(ROOT, "scripts", "_patch_README_세션파일.py"); s = rd(P)
s = sub1(s, '    ("bprime_boxes/ivbox_lib.py",\n     "`세션_재계산/bprime_boxes/ivbox_lib.py`는 `band_boxes/band_iv.py`가 쓰는 공용 구간 성분이다.',
            '    ("band_boxes/ivbox_lib.py",\n     "`세션_재계산/band_boxes/ivbox_lib.py`는 같은 폴더의 `band_iv.py`가 쓰는 구간 성분이다.')
s = sub1(s, "식 (8.30) 자체를 아래에서 막는다", "식 (8.23) 자체를 아래에서 막는다")
s = sub1(s, "$\\\\Omega$는 `bprime_boxes/ivbox_lib.py`의 정확 정의를 쓴다", "$\\\\Omega$는 같은 폴더의 `ivbox_lib.py`의 정확 정의를 쓴다")
for old, new in [("모멘트 판정 항목 (ㄱ)(두 범위의 재귀 인증", "모멘트 판정 항목(두 범위의 재귀 인증"),
                 ("재귀 (7.2)·(7.3)에 $\\\\hat{\\\\mathfrak a}_n$을 곱해", "재귀 (7.1)과 모멘트 재귀 (7.2)에 $\\\\hat{\\\\mathfrak a}_n$을 곱해"),
                 ("$(1\\\\pm u)^r$", "$(1\\\\pm\\\\mathsf p)^r$")]:
    print("PARAS", repr(old[:30]), s.count(old)); s = s.replace(old, new)
assert "bprime" not in s
wr(P, s)

G = os.path.join(ROOT, "scripts", "_gen_재실행표.py"); s = rd(G)
s = sub1(s, 'scripts=[S + "band_boxes/band_iv.py", S + "band_boxes/band_summary.py", S + "band_boxes/run_all.sh"],',
            'scripts=[S + "band_boxes/band_iv.py", S + "band_boxes/ivbox_lib.py", S + "band_boxes/band_summary.py", S + "band_boxes/run_all.sh"],')
s = sub1(s, 'time="약 14초(`check_table_iv_out.txt`의 time 줄)"', 'time="약 6초(`check_table_iv_out.txt`의 time 줄)"')
s = sub1(s, "표 검사 14초(각 출력의 total 줄)", "표 검사 6초(각 출력의 total·time 줄)")
wr(G, s)

p = os.path.join(CALC, "moment_cert_iv", "summarize_nb.py"); s = rd(p)
s = sub1(s, "# Exit status 0 only if all 7619 columns are present and every verdict agrees.",
            "# Exit status 0 only if every column of the sweep is present and every verdict agrees.")
wr(p, s)
print("ok")

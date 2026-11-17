# -*- coding: utf-8 -*-
"""ZD 인계(2026-11-17) 「세션」 1·2·4의 코드·폴더·README 글 수정(재실행·SHA 갱신은 따로).
1. bprime_boxes/ivbox_lib.py -> band_boxes/ivbox_lib.py 이동, bprime_boxes/ 삭제.
2. ivbox_lib.py: Z32를 ia.py 값으로, 1행 주석, 죽은 메서드 Grid.env 삭제, 'D.band:' 주석.
3. band_iv.py: 머리 주석 (a)-(d) -> 한 줄, LIB 두 줄 -> sys.path.insert(0, HERE).
4. moment_cert_iv/test_exact.py 주석 (7.3) -> (7.2).
5. README.md 46·476·478·490행과 _patch_README_세션파일.py PARAS의 같은 문구.
6. _gen_재실행표.py CONFIG band-boxes scripts에 ivbox_lib.py 추가.
"""
import io, os, re, shutil
ROOT = r"C:\math\임시\주차함수_증명"
CALC = os.path.join(ROOT, "원고_자료", "세션_재계산")
os.chdir(ROOT)

def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, s): io.open(p, "w", encoding="utf-8", newline="\n").write(s)
def sub1(s, old, new, n=1):
    c = s.count(old); assert c == n, (old[:60], c); return s.replace(old, new)

# 1. 이동
src = os.path.join(CALC, "bprime_boxes", "ivbox_lib.py"); dst = os.path.join(CALC, "band_boxes", "ivbox_lib.py")
assert os.path.exists(src) and not os.path.exists(dst)
shutil.move(src, dst)
shutil.rmtree(os.path.join(CALC, "bprime_boxes"))
assert not os.path.exists(os.path.join(CALC, "bprime_boxes"))

# 2. ivbox_lib.py
s = rd(dst)
s = sub1(s, "box certificates of D.bprime-boxes and D.band-boxes.", "box certificates of D.band-boxes.")
s = sub1(s, "Z32 = iv.mpf(['2.61237337287942872041', '2.61237534874723228113'])",
            "Z32 = iv.mpf(['2.61237534856196187337', '2.61237534874727088315'])")
env_block = re.compile(r"\n    # --- D\.bprime: environment weight[^\n]*\n    def env\(self, yl, zeta_hi, SC_hi\):\n[^\n]*\n[^\n]*\n")
assert len(env_block.findall(s)) == 1, env_block.findall(s)
s = env_block.sub("\n", s)
s = sub1(s, "    # --- D.band: window weight", "    # --- window weight")
assert ".env(" not in s
wr(dst, s)

# 3. band_iv.py
p = os.path.join(CALC, "band_boxes", "band_iv.py"); s = rd(p)
old_head = ("# (D.band-boxes):  (a) LB^low >= 1.009 on k >= 6668, 103 <= nu <= 0.48k   [hazard version, record cert_assembly_lowH.py]\n"
            "#                  (b) LB^low >= 1     on k >= 1e5,  103 <= nu <= 0.57k   [hazard version]\n"
            "#                  (c) LB^low(h:=0) >= 1 on k >= 6668, nu <= 0.44k        [record cert_assembly_low.py]\n"
            "#                  (d) LB^low(h:=0) >= 1 on k >= 1e5,  nu <= 0.53k        [record cert_assembly_low.py]\n")
s = sub1(s, old_head, "# (D.band-boxes): LB^low >= 1 on k >= 6668, 103 <= nu <= 0.48k   [hazard version, record cert_assembly_lowH.py]\n")
s = sub1(s, "LIB = os.path.normpath(os.path.join(HERE, '..', 'bprime_boxes'))\nsys.path.insert(0, LIB)\n", "sys.path.insert(0, HERE)\n")
assert ".env(" not in s and "bprime" not in s
wr(p, s)

# 4. test_exact.py 주석
p = os.path.join(CALC, "moment_cert_iv", "test_exact.py"); s = rd(p)
s = sub1(s, "independently also Zflat, ZH, Z from (7.3) directly", "independently also Zflat, ZH, Z from (7.2) directly")
wr(p, s)

# 5. README·PARAS
R = os.path.join(ROOT, "원고_자료", "README.md"); s = rd(R)
s = sub1(s, "`bprime_boxes/ivbox_lib.py`(띠 상자가 이것을 쓴다)", "`band_boxes/ivbox_lib.py`(띠 상자가 이것을 쓴다)")
s = sub1(s, "`세션_재계산/bprime_boxes/ivbox_lib.py`는 `band_boxes/band_iv.py`가 쓰는 공용 구간 성분이다.",
            "`세션_재계산/band_boxes/ivbox_lib.py`는 같은 폴더의 `band_iv.py`가 쓰는 구간 성분이다.")
s = sub1(s, "식 (8.30) 자체를 아래에서 막는다", "식 (8.23) 자체를 아래에서 막는다")
s = sub1(s, "$\\Omega$는 `bprime_boxes/ivbox_lib.py`의 정확 정의를 쓴다", "$\\Omega$는 같은 폴더의 `ivbox_lib.py`의 정확 정의를 쓴다")
s = sub1(s, "모멘트 판정 항목 (ㄱ)(두 범위의 재귀 인증)", "모멘트 판정 항목(두 범위의 재귀 인증)")
s = sub1(s, "재귀 (7.2)·(7.3)에 $\\hat{\\mathfrak a}_n$을 곱해", "재귀 (7.1)과 모멘트 재귀 (7.2)에 $\\hat{\\mathfrak a}_n$을 곱해")
s = sub1(s, "$(1\\pm u)^r$", "$(1\\pm\\mathsf p)^r$")
assert "bprime" not in s, [m.start() for m in re.finditer("bprime", s)]
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

# 4b. summarize_nb.py 주석(열 수 7619는 옛 판)
p = os.path.join(CALC, "moment_cert_iv", "summarize_nb.py"); s = rd(p)
s = sub1(s, "# Exit status 0 only if all 7619 columns are present and every verdict agrees.",
            "# Exit status 0 only if every column of the sweep is present and every verdict agrees.")
wr(p, s)

# 6. _gen_재실행표.py
G = os.path.join(ROOT, "scripts", "_gen_재실행표.py"); s = rd(G)
s = sub1(s, 'scripts=[S + "band_boxes/band_iv.py", S + "band_boxes/band_summary.py", S + "band_boxes/run_all.sh"],',
            'scripts=[S + "band_boxes/band_iv.py", S + "band_boxes/ivbox_lib.py", S + "band_boxes/band_summary.py", S + "band_boxes/run_all.sh"],')
wr(G, s)
print("ok")

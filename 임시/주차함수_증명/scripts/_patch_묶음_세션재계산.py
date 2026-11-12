# -*- coding: utf-8 -*-
"""자료 묶음 README에 「세션이 만든 수정판」 절(세션 재계산 파일과 SHA-256)을 「## 파일 목록」 앞에 넣고,
ul_iv_fixed.py 115행의 낡은 주석을 바꾼 수정 내용에 맞게 고친다."""
import hashlib
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROOT, "원고_자료")
SUB = os.path.join(BUNDLE, "세션_재계산", "r8a9b11e")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for ch in iter(lambda: f.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


# 1. 주석 정정
p = os.path.join(SUB, "ul_iv_fixed.py")
s = io.open(p, encoding="utf-8", newline="").read()
old = "    pref = SQ2PI_INV                  # exp(-(zeta-H0)_+ zeta/2) decreasing in zeta"
if old in s:
    s = s.replace(old, "    pref = SQ2PI_INV                  # tail factor exp(-(zeta-H0)_+ zeta/2) replaced by its trivial upper bound 1 (record review, feedback section 3.3); the constant 1/sqrt(2 pi) is kept")
    io.open(p, "w", encoding="utf-8", newline="").write(s)
    print("comment fixed")

# 2. README 절
files = []
for root_, _, fs in os.walk(SUB):
    for fn in sorted(fs):
        fp = os.path.join(root_, fn)
        rel = os.path.relpath(fp, BUNDLE).replace("\\", "/")
        files.append((rel, sha(fp)))
sec = ["## 세션이 만든 수정판(세션_재계산/)", "",
       "부록 D의 두 항목(`D.{{D:window-mass-constant}}`, `D.{{D:column-moment-constant}}`; 조립 뒤 번호)이 기대는 수정판 코드는 연구 기록에 서술로만 있고 파일로는 없다(기록 [r8a9b11e]의 검토 `review/feedback.md` §3.3·§4.3). "
       "글을 조립한 세션이 2026-11-13에 기록의 `evidence/peer/ul_iv.py`·`c3_iv.py`를 복사해 서술대로 한 줄씩 고친 판을 만들고 다시 실행했다. 고친 줄: `ul_iv_fixed.py` 115행 `pref = SQ2PI_INV`(꼬리 인자 $e^{-(\\theta-\\mathfrak h_0)_+\\theta/2}$를 자명한 상계 1로; 앞 상수 $1/\\sqrt{2\\pi}$는 유지), "
       "`c3_iv_fixed.py` 43행 `iv.mpf('0.75') / (p * q * q)`(옛 `iv.mpf('0.75') * h ** 3 / (p * q * q)`). 실행: `python -I ul_iv_fixed.py 25000 1600 1200 0.1 6400 4`(약 3분; $\\mathsf w_0\\ge0.71216801$), `python -I ul_iv_fixed.py 25000 800 600 0.1 3200 4`($0.70623905$), `python -I run_c3_fixed_nocheck.py 2000`($C_{\\mathrm{III}}\\le1.5033946$; 수정판의 자체 점검 `check_against_float()`는 옛 float 식과 비교하므로 드라이버가 본 루프만 실행한다). 출력은 `outputs_fixed/`에 있다. 이 파일들은 기록의 원본이 아니라 세션이 만든 것이다.", "",
       "| 경로 | SHA-256 |", "|---|---|"]
for rel, d in files:
    sec.append(f"| `{rel}` | `{d}` |")
sec_text = "\n".join(sec) + "\n\n"
rp = os.path.join(BUNDLE, "README.md")
r = io.open(rp, encoding="utf-8").read()
if "## 세션이 만든 수정판" not in r:
    assert r.count("## 파일 목록") == 1
    r = r.replace("## 파일 목록", sec_text + "## 파일 목록")
    io.open(rp, "w", encoding="utf-8", newline="\n").write(r)
    print("README section added:", len(files), "files")
else:
    print("README already has the section")

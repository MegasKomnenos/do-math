# -*- coding: utf-8 -*-
"""태그 9 수학 검사 둘째의 수정 스크립트(멱등). 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.
사용: python -I scripts/수학검사2/9_fix.py [--dry]
수정(모두 장v2/장9.md, 종류 4 수치·반올림 방향):
  (1) 243행 정리 {{9:head-sum-1}} 5단계 「$0.7978\\sqrt\\xi\\ge0.1382>0.0605$」 -> 「$\\ge0.1381>0.0605$」
      (0.7978*sqrt(0.03) = 0.138183 < 0.1382; 하계를 올려 적은 것. 결론 >0.0605는 그대로)
  (2) 251행 6단계 「$\\mathfrak u_q\\le0.002359$」 -> 「$\\le0.002360$」
      ((1+1/3131)^2 (u0+u0^3)^2/2 = 0.00235911 > 0.002359; 상계를 내려 적은 것. 뒤의 e^{u_q}<=1.00237은 그대로)
  (3) 259행 정리 {{9:head-sum-2}} 증명 (iii) 「$m_0\\ge574\\ge171$」 -> 「$m_0\\ge573\\ge171$」
      (20001^{2/3}-6*20001^{1/3} = 573.96, 내림은 573. 쓰이는 결론 m_0>=171은 그대로)
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, "장v2", "장9.md")
DRY = "--dry" in sys.argv[1:]

FIXES = [
    ("1 0.1382->0.1381", r"$0.7978\sqrt\xi\ge0.1382>0.0605=0.8848\upsilon_0$", r"$0.7978\sqrt\xi\ge0.1381>0.0605=0.8848\upsilon_0$"),
    ("2 u_q 0.002359->0.002360", r"$\mathfrak u_q\le0.002359$", r"$\mathfrak u_q\le0.002360$"),
    ("3 m_0 574->573", r"$m_0\ge574\ge171$", r"$m_0\ge573\ge171$"),
]

def main():
    with io.open(PATH, "r", encoding="utf-8", newline="") as f:
        s = f.read()
    crlf = s.count("\r\n"); lf = s.count("\n") - crlf
    changed = False
    for name, old, new in FIXES:
        c_old = s.count(old); c_new = s.count(new)
        if c_old == 0 and c_new == 1:
            print("[%s] 이미 적용됨" % name); continue
        if c_old != 1:
            print("[%s] 앵커 %d회 — 건너뜀" % (name, c_old)); continue
        print("[%s] 앵커 1회 -> 치환%s" % (name, " (dry)" if DRY else ""))
        if not DRY:
            s = s.replace(old, new); changed = True
    if changed:
        with io.open(PATH, "w", encoding="utf-8", newline="") as f:
            f.write(s)
        print("기록함. 줄끝 LF %d, CRLF %d 보존" % (lf, crlf))
    else:
        print("변경 없음")

if __name__ == "__main__":
    main()

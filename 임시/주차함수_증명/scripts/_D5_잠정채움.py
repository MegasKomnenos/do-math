# -*- coding: utf-8 -*-
"""D.5(central-gap-integer)의 자리표시자 셋을 잠정값으로 채우거나(fill) 자리표시자로 되돌린다(restore).

사용: python -I scripts/_D5_잠정채움.py fill | restore | status

fill    장v2/부록D_장4.md의 `[D5:작업자]`·`[D5:시간]`·`[D5:파일]`을 아래 잠정값으로 바꾸고, 바꾼 값을
        scripts/_D5_잠정채움.json에 적는다(되돌리기용). 이어 11.2 행은 `_sync_11_2행.py central-gap-integer`로 맞춘다.
restore JSON의 값을 자리표시자로 되돌린다(원본 스크립트 완주 뒤 `make_draft.py` → `_apply_D초안.py` 경로를 쓰기 위해).
status  현재 조각에 자리표시자와 잠정값 가운데 무엇이 있는지 보인다.

잠정값의 뜻(2026-11-15 15:4x 사용자 결정 「잠정 판정으로 일단 채움」):
  작업자 = launches.txt의 최대 W(이미 4; 재기동도 4), 시간 = 원본의 열별 시간 합 114.4시간 + 남은 773열 예상 35시간 ≈ 150시간,
  파일 수 = 완료 묶음 85 + 복구될 .part 3 + 남은 묶음 약 8 ≈ 96.  셋 다 원본 완주 뒤 실측으로 덮어쓴다.
판정(9000열 전부 비트 동일, 불일치 0)은 새 구현 773열 + 원본 8,227열의 잠정 판정이다(scripts/_tmp_perf_1115/run/verdict_interim.json).
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPX = os.path.join(ROOT, "장v2", "부록D_장4.md")
REC = os.path.join(ROOT, "scripts", "_D5_잠정채움.json")
REL = "원고_자료/세션_재계산/icert_py_full"
FILL = {
    "[D5:작업자]": "$4$",
    "[D5:시간]": "$150$시간",
    "[D5:파일]": "`%s/rev_icert_unpaired_fast.py`, `worker.py`, `out_*.txt`($96$개), `summary.json`" % REL,
}


def block(s):
    i = s.find("### D.{{D:central-gap-integer}}")
    j = s.find("\n### D.", i + 1)
    return i, (j if j > 0 else len(s))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    s = io.open(APPX, encoding="utf-8").read()
    i, j = block(s)
    if i < 0:
        sys.exit("D.5 블록 없음")
    blk = s[i:j]
    if mode == "status":
        for t, v in FILL.items():
            print(t, "자리표시자" if t in blk else ("잠정값" if v in blk else "없음"))
        return
    if mode == "fill":
        missing = [t for t in FILL if t not in blk]
        if missing:
            sys.exit("자리표시자 없음(이미 채워졌나?): %s" % missing)
        for t, v in FILL.items():
            if blk.count(t) != 1:
                sys.exit("자리표시자 %s 가 %d번" % (t, blk.count(t)))
            blk = blk.replace(t, v)
        left = re.findall(r"\[D5:[^\]]*\]", blk)
        io.open(APPX, "w", encoding="utf-8", newline="\n").write(s[:i] + blk + s[j:])
        json.dump(FILL, io.open(REC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("채움 완료; 남은 D5 토큰:", left)
        return
    if mode == "restore":
        rec = json.load(io.open(REC, encoding="utf-8"))
        for t, v in rec.items():
            if blk.count(v) != 1:
                sys.exit("잠정값 %r 가 %d번(손으로 바뀌었나?)" % (v, blk.count(v)))
            blk = blk.replace(v, t)
        io.open(APPX, "w", encoding="utf-8", newline="\n").write(s[:i] + blk + s[j:])
        print("되돌림 완료; 토큰:", [t for t in rec if t in blk])
        return
    sys.exit("모드: fill | restore | status")


if __name__ == "__main__":
    main()

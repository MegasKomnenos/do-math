# 수리 전체24 ZL — 손으로 정한 (옛 문자열 → 새 문자열) 쌍을 한 자리씩 적용하는 도우미.
# 쌍마다 옛 문자열이 파일에 정확히 한 번(또는 지정한 횟수) 있어야 하고, 하나라도 어긋나면 아무것도 쓰지 않는다. 줄 끝은 LF 그대로.
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
def apply(path, edits, dry=False):
    b = open(path, "rb").read()
    assert b"\r" not in b, "CR 있음"
    s = b.decode("utf-8")
    n0 = s.count("\n")
    for k, e in enumerate(edits, 1):
        old, new = e[0], e[1]
        want = e[2] if len(e) > 2 else 1
        c = s.count(old)
        if c != want:
            raise SystemExit(f"중단 — #{k}: 출현 {c}회(기대 {want}): {old[:80]!r}")
        if old == new:
            raise SystemExit(f"중단 — #{k}: 옛·새가 같다")
        s = s.replace(old, new)
    out = s.encode("utf-8")
    assert b"\r" not in out
    if dry:
        print(f"{path}: {len(edits)}쌍 확인(쓰지 않음)")
        return
    open(path, "wb").write(out)
    print(f"{path}: {len(edits)}쌍 적용, {len(b)} → {len(out)}바이트, 줄 수 {n0} → {s.count(chr(10))}")

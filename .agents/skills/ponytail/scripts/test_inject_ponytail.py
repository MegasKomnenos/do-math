"""inject_ponytail 자기검사.

보장하는 거동: 주입문이 고정 머리로 시작하고, frontmatter와 원본 추적 절이 제거되며,
본문 규범 절은 남고, hook stdout 캡 10,000자를 넘지 않는다.
"""
from inject_ponytail import build

out = build()
assert out.startswith("PONYTAIL MODE ACTIVE — level: full\n\n"), "머리 불일치"
assert "name: ponytail" not in out, "frontmatter 잔존"
assert "원본 추적" not in out, "메타 절 잔존"
assert "02c0712c" not in out, "원본 해시 잔존"
assert "## 사다리" in out and "## 경계" in out, "본문 규범 절 결손"
assert "ponytail:" in out, "마커 규약 결손"
assert len(out) <= 10000, f"hook stdout 캡 초과: {len(out)}자"
print(f"OK: 주입문 {len(out)}자")

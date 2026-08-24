"""ponytail 각색본 본문을 세션 컨텍스트에 주입한다 (SessionStart·SubagentStart hook).

frontmatter와 「원본 추적」 절은 세션 규범이 아니라 파일 메타데이터이므로 주입에서 뺀다.
"""
import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "SKILL.md"
WARN_AT = 9000  # ponytail: hook stdout 캡 10,000자의 경고선, 본문이 자라면 분할을 검토


def build() -> str:
    body = SKILL.read_text(encoding="utf-8")
    body = re.sub(r"\A---\n.*?\n---\n", "", body, count=1, flags=re.S)
    body = re.sub(r"^## 원본 추적\n.*?(?=^## )", "", body, count=1, flags=re.S | re.M)
    return "PONYTAIL MODE ACTIVE — level: full\n\n" + body.strip() + "\n"


if __name__ == "__main__":
    out = build()
    if len(out) > WARN_AT:
        print(f"[ponytail-hook 경고] 주입문 {len(out)}자, 캡 10,000자 접근")
    print(out)

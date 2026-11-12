# -*- coding: utf-8 -*-
"""장부 v2 초안(1·2·3·5·6·7절)을 장부_v2.md에 합친다.

- 장부_v2.md의 1·2·3·5·6·7절 본문을 장부_v2_초안.md의 같은 번호 절로 바꾼다(0·4·8절은 유지).
- 4절의 이 글 이름 「반감 문턱」을 「반감 경계」로(세션 결정 10).
- 0절 R1′ 뒤에 세션 결정 2·16의 조항(예외 d·x, 1장 전역 기호의 국소 재사용 금지)을 더하고,
  글자 결정의 기록 파일 셋을 가리키는 줄을 둔다.
사용: python 장부v2_합침.py [--dry]
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEDGER = os.path.join(ROOT, "장부_v2.md")
DRAFT = os.path.join(ROOT, "장부_v2_초안.md")

SEC_RE = re.compile(r"^## (\d)\. ", re.M)


def split_sections(text):
    """{번호: (머리줄 포함 본문)}과 머리(0절 앞) 반환. 절 번호는 '## N. ' 꼴."""
    heads = [(m.start(), int(m.group(1))) for m in SEC_RE.finditer(text)]
    pre = text[: heads[0][0]] if heads else text
    secs = {}
    for idx, (pos, num) in enumerate(heads):
        end = heads[idx + 1][0] if idx + 1 < len(heads) else len(text)
        secs[num] = text[pos:end]
    return pre, secs


R1P_ADD = (
    " 두 예외가 있다. 바탕 글자 $d$는 변수 $d$(결손)·$d_i$(변위)·$d_{n,k}$(한 칸 차분)에, 바탕 글자 $x$는 좌표 $x$·$\\hat x$와 함수 $x_t(y)$에 함께 쓰이며, 첨자의 수와 꼴로 갈린다(세션 결정 2). "
    "1장이 정의하는 전역 기호($\\ell^\\ast$, $k_n$, $\\lambda$, $\\zeta$, $x$·$\\hat x$ 등)는 어느 장에서도 국소 기호로 다시 쓰지 않는다(세션 결정 16)."
)

DECISION_NOTE = (
    "- **글자 결정의 기록.** 1·2·3·5·6·7절의 모든 글자·낱말 결정의 까닭은 `대조v2/장부_설계_결정록.md`에, "
    "그 가운데 세션이 정한 것은 `대조v2/장부_설계_세션결정.md`에, 반영 결과는 `대조v2/장부_설계_반영.md`에 있다. "
    "집필자는 이 사전만 보고 쓰며 결정록은 열지 않아도 된다.\n"
)


def main():
    dry = "--dry" in sys.argv
    ledger = io.open(LEDGER, encoding="utf-8").read()
    draft = io.open(DRAFT, encoding="utf-8").read()
    l_pre, l_secs = split_sections(ledger)
    d_pre, d_secs = split_sections(draft)
    for n in (1, 2, 3, 5, 6, 7):
        assert n in d_secs, f"초안에 {n}절 없음"
        assert n in l_secs, f"장부에 {n}절 없음"
    # 0절: R1′ 조항 추가, 결정 기록 줄 추가
    s0 = l_secs[0]
    key = "정규화가 다른 양은 다른 양이므로 각각 한 글자를 갖되 한 글자만 갖는다."
    assert s0.count(key) == 1, "R1′ 끝 문장을 찾지 못함"
    if R1P_ADD.strip() not in s0:
        s0 = s0.replace(key, key + R1P_ADD)
    if "글자 결정의 기록" not in s0:
        s0 = s0.rstrip("\n") + "\n" + DECISION_NOTE + "\n"
    l_secs[0] = s0
    # 4절: 반감 문턱 → 반감 경계
    s4 = l_secs[4]
    n_half = s4.count("| 반감 문턱 |")
    s4 = s4.replace("| 반감 문턱 |", "| 반감 경계 |")
    l_secs[4] = s4
    # 1·2·3·5·6·7절 교체(초안의 절은 머리줄 그대로)
    for n in (1, 2, 3, 5, 6, 7):
        body = d_secs[n]
        if not body.endswith("\n\n"):
            body = body.rstrip("\n") + "\n\n"
        l_secs[n] = body
    # 머리: 「채움 전」 표현 제거
    pre = l_pre.replace("(채움 전)", "")
    out = pre + "".join(l_secs[n] for n in sorted(l_secs))
    # 절 머리의 「(채움 전…)」 꼬리 제거
    out = re.sub(r"^(## \d\. [^\n(]+)\([^)\n]*채움 전[^)\n]*\)", r"\1", out, flags=re.M)
    print("절별 행 수:", {n: l_secs[n].count("\n") for n in sorted(l_secs)})
    print("4절 반감 문턱→반감 경계:", n_half)
    if dry:
        return 0
    io.open(LEDGER, "w", encoding="utf-8", newline="\n").write(out)
    print("written", LEDGER, len(out), "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

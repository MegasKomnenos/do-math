# -*- coding: utf-8 -*-
"""X4 (ㄴ) 항목 글자: 「{{라벨}}(가)」「{{라벨}}의 (ii)」「D.{{D:…}} (나)」 꼴 인용의 항목이 현행 진술 본문에 있는지. 읽기 전용."""
import glob, io, os, re
from collections import defaultdict
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CH = os.path.join(ROOT, "장v2")
files = sorted(glob.glob(os.path.join(CH, "장*.md"))) + sorted(glob.glob(os.path.join(CH, "부록D_장*.md")))
others = [os.path.join(ROOT, "장부_v2.md"), os.path.join(ROOT, "구조표_v2.md")] + [os.path.join(CH, f"부록{x}.md") for x in "ABC"]
def rel(p): return os.path.relpath(p, ROOT)
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{([^}]+)\}\}(?!의 증명)")
DHEAD = re.compile(r"^### D\.\{\{([^}]+)\}\}")
ITEM = r"\((?:[가-힣]|[ㄱ-ㅎ]|[ivx]+|[a-zA-Z]′?|\d{1,2}|[A-Z]\d|[가-힣]′)\)"
CITE_ITEM = re.compile(r"\{\{([^}]+)\}\}(?:의)?\s*((?:" + ITEM + r")(?:\s*[·,]?\s*(?:" + ITEM + r"))*)")
ITEM_RE = re.compile(ITEM)
texts = {p: io.open(p, encoding="utf-8").read().split("\n") for p in files + others}
# 진술 본문(머리부터 증명 시작·다음 머리·절 머리 전까지)
body = {}
for p in files:
    lines = texts[p]
    for i, ln in enumerate(lines):
        m = HEAD.match(ln)
        if m:
            lab = m.group(2); buf = [ln]
            for j in range(i+1, min(i+80, len(lines))):
                l2 = lines[j]
                if l2.startswith("**증명") or HEAD.match(l2) or l2.startswith("###") or re.match(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{[^}]+\}\}의 증명", l2):
                    break
                buf.append(l2)
            body[lab] = ("\n".join(buf), rel(p), i+1)
        m = DHEAD.match(ln)
        if m:
            lab = m.group(1); buf = [ln]
            for j in range(i+1, len(lines)):
                if lines[j].startswith("### "): break
                buf.append(lines[j])
            body[lab] = ("\n".join(buf), rel(p), i+1)
def items_of(lab):
    return set(ITEM_RE.findall(body[lab][0])) if lab in body else None
n_cite = 0; bad = []; by_label = defaultdict(set)
for p in files + others:
    for no, ln in enumerate(texts[p], 1):
        for m in CITE_ITEM.finditer(ln):
            lab = m.group(1); its = ITEM_RE.findall(m.group(2))
            n_cite += 1
            have = items_of(lab)
            for it in its:
                by_label[lab].add(it)
                if have is None or it not in have:
                    bad.append((rel(p), no, lab, it, ln[max(0, m.start()-50):m.end()+30]))
print("## 항목 글자 붙은 인용 토큰:", n_cite, "| 라벨 수:", len(by_label))
print("## 현행 본문에 없는 항목 인용:", len(bad))
for b in bad: print("  ", b)
print()
print("## 라벨별 인용된 항목과 본문의 항목(참고)")
for lab in sorted(by_label):
    have = items_of(lab)
    print(f"   {lab}: 인용 {sorted(by_label[lab])} | 본문 {sorted(have) if have is not None else '정의 없음'}")

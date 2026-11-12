# -*- coding: utf-8 -*-
"""둘째 판 장별 명세와 파견문을 처음부터 다시 만든다.

순서: 라벨 등록부(_gen_라벨_v2.py) → 명세 초안(_draft_장v2_spec.py) → 진술 확정(명세v2_수정.py)
      → 다른 장 참조(의존지도 v2 1절) → 장 수준 META(명세v2_META.py) → [--briefs] 파견문 생성(_gen_장v2_파견문.py)
사용: python 명세v2_빌드.py [--briefs] [--check]
"""
import io, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SPEC = os.path.join(ROOT, "파견", "명세v2")
PY = sys.executable


def run(script, *args):
    r = subprocess.run([PY, os.path.join(HERE, script), *args], capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print(r.stdout); print(r.stderr)
        raise SystemExit(f"{script} failed")
    return r.stdout


def fill_refs():
    F = os.path.join(ROOT, "의존지도_v2.md")
    s = io.open(F, encoding="utf-8").read()
    sec1 = s.split("## 1. 진술별 입력 표", 1)[1].split("## 2.", 1)[0]
    LAB = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
    refs = {ch: set() for ch in range(1, 12)}
    for ln in sec1.split("\n"):
        if not ln.startswith("| `{{"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        m = LAB.search(cells[0])
        if not m:
            continue
        ch = int(m.group(1))
        for m2 in LAB.finditer(cells[5] if len(cells) > 5 else ""):
            if int(m2.group(1)) != ch:
                refs[ch].add(m2.group(0))
    # 진술별 입력(의존지도 1절 「입력: 이 글의 다른 진술」)을, 명세에 입력이 비어 있는 진술에 채운다.
    inputs_of = {}
    for ln in sec1.split("\n"):
        if not ln.startswith("| `{{"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        m = LAB.search(cells[0])
        if not m:
            continue
        inputs_of[m.group(0)] = [x.group(0) for x in LAB.finditer(cells[5] if len(cells) > 5 else "")]
    for ch in range(1, 12):
        p = os.path.join(SPEC, f"장{ch}.json")
        j = json.load(io.open(p, encoding="utf-8"))
        j["refs"] = sorted(refs[ch], key=lambda x: (int(LAB.match(x).group(1)), x))
        for sec in j["sections"]:
            for it in sec["items"]:
                if not it.get("inputs") and it["label"] in inputs_of:
                    it["inputs"] = inputs_of[it["label"]]
        io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(j, ensure_ascii=False, indent=1))


def fill_letters():
    """장부 v2 5절(장별 배정과 여유 글자)이 채워져 있으면 defines/free_letters를 명세에 넣는다."""
    F = os.path.join(ROOT, "장부_v2.md")
    s = io.open(F, encoding="utf-8").read()
    if "## 5. 장별 배정과 여유 글자" not in s:
        print("장부 5절 없음"); return
    sec5 = s.split("## 5. 장별 배정과 여유 글자", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for ln in sec5.split("\n"):
        if not ln.startswith("|") or ln.startswith("|---") or ln.startswith("| 장"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        m = re.match(r"(\d+)", cells[0])
        if not m:
            continue
        rows[int(m.group(1))] = cells
    if not rows:
        print("장부 5절 채움 전"); return
    for ch in range(1, 12):
        p = os.path.join(SPEC, f"장{ch}.json")
        j = json.load(io.open(p, encoding="utf-8"))
        c = rows.get(ch)
        if c:
            j["defines"] = [x for x in [c[1], c[2]] if x and x != "—"]
            j["free_letters"] = [c[3]] if c[3] and c[3] != "—" else []
        io.open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(j, ensure_ascii=False, indent=1))
    print("letters filled for", sorted(rows))


def main():
    briefs = "--briefs" in sys.argv
    check = "--check" in sys.argv
    print(run("_gen_라벨_v2.py").strip())
    print(run("_draft_장v2_spec.py").strip())
    print(run("명세v2_수정.py").strip())
    fill_refs(); print("refs filled")
    print(run("명세v2_META.py").strip())
    if check or briefs:
        for ch in range(1, 12):
            spec = os.path.join(SPEC, f"장{ch}.json")
            if check:
                out = run("_gen_장v2_파견문.py", spec, "--check")
                prob = [l for l in out.split("\n") if l.startswith("문제:") or l.startswith(" - ")]
                print(f"장{ch} check:", " | ".join(prob) if prob else "0")
            if briefs:
                print(run("_gen_장v2_파견문.py", spec).strip())


if __name__ == "__main__":
    main()

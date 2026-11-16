# -*- coding: utf-8 -*-
"""R2 (ㄷ): scripts/부록_v2.py의 build_A·build_C를 건조 실행해 생성본을 얻고, 현재 장v2/부록A.md·부록C.md와 행 단위로 대조한다. 파일에 쓰지 않는다."""
import io, os, sys, difflib
ROOT = r"C:\math\임시\주차함수_증명"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("buro", os.path.join(ROOT, "scripts", "부록_v2.py"))
buro = importlib.util.module_from_spec(spec); spec.loader.exec_module(buro)
ledger = io.open(buro.LEDGER, encoding="utf-8").read()
texts = buro.chapter_texts()
body = "\n".join(texts.values())
A, missing_A = buro.build_A(ledger, body)
C = buro.build_C(ledger)
curA = io.open(os.path.join(buro.CHAP_DIR, "부록A.md"), encoding="utf-8").read()
curC = io.open(os.path.join(buro.CHAP_DIR, "부록C.md"), encoding="utf-8").read()
out = io.StringIO()
def dump(name, gen, cur):
    g = gen.split("\n"); c = cur.split("\n")
    out.write(f"==== {name}: 생성본 {len(g)}행 / 현재 {len(c)}행\n")
    sm = difflib.SequenceMatcher(None, g, c, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal": continue
        out.write(f"--- {tag} 생성 {i1+1}-{i2} / 현재 {j1+1}-{j2}\n")
        for ln in g[i1:i2]: out.write("  G| " + ln + "\n")
        for ln in c[j1:j2]: out.write("  C| " + ln + "\n")
dump("부록A", A, curA)
dump("부록C", C, curC)
out.write("\n본문에 바탕 토큰 없는 1.2 행: %d\n%s\n" % (len(missing_A), "\n".join(missing_A)))
res = out.getvalue()
sys.stdout.buffer.write(res.encode("utf-8"))

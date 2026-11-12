# -*- coding: utf-8 -*-
"""조립본(또는 지정 파일들)의 모든 수식 구간을 KaTeX(md2pdf가 쓰는 설치본)로 렌더해 오류를 보고한다.
사용: python _katex_check.py [파일 ...]   (기본: 원고.md)
Node와 %LOCALAPPDATA%/md2pdf/node_modules/katex가 있어야 한다.
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files = sys.argv[1:] or [os.path.join(ROOT, "원고.md")]
MATH = re.compile(r"\$\$(.+?)\$\$|\$(.+?)\$", re.S)
items = []
for p in files:
    s = io.open(p, encoding="utf-8").read()
    for m in MATH.finditer(s):
        seg = m.group(1) if m.group(1) is not None else m.group(2)
        ln = s.count("\n", 0, m.start()) + 1
        items.append({"f": os.path.basename(p), "ln": ln, "d": m.group(1) is not None, "tex": seg})
tmp = os.path.join(tempfile.gettempdir(), "katex_check_items.json")
io.open(tmp, "w", encoding="utf-8").write(json.dumps(items, ensure_ascii=False))
katex_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "md2pdf", "node_modules", "katex")
js = r"""
const fs = require('fs');
const katex = require(process.argv[2]);
const items = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
let bad = 0;
for (const it of items) {
  try {
    katex.renderToString(it.tex, {throwOnError: true, displayMode: it.d, strict: 'ignore', trust: true,
      macros: {"\\mathscr": "\\mathcal", "\\varnothing": "\\emptyset"}});
  } catch (e) {
    bad++;
    const msg = String(e.message || e).split('\n')[0].slice(0, 160);
    console.log(`${it.f}:${it.ln}: ${msg} | ${it.tex.slice(0, 100).replace(/\n/g, ' ')}`);
  }
}
console.log(`수식 ${items.length}개, 오류 ${bad}개`);
"""
jsp = os.path.join(tempfile.gettempdir(), "katex_check.js")
io.open(jsp, "w", encoding="utf-8").write(js)
r = subprocess.run(["node", jsp, katex_dir, tmp], capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout[-20000:])
if r.returncode != 0:
    print("node 오류:", r.stderr[-800:])

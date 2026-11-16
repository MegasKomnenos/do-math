r"""md2pdf — 수식이 있는 Markdown 문서를 읽기 좋은 PDF로 조판한다.

경로: Markdown ─(markdown-it-py)→ HTML ─(KaTeX, Node)→ 수식 HTML ─(Playwright·Chromium 계열)→ PDF

    python 도구/md2pdf.py 입력.md [-o 출력.pdf] [옵션]

필요한 것
  - Python 패키지: markdown-it-py, mdit-py-plugins, playwright  (pip install markdown-it-py mdit-py-plugins playwright)
  - Node.js(npm 포함): KaTeX를 처음 한 번 %LOCALAPPDATA%/md2pdf 에 내려받는다 (npm install katex@0.16)
  - 브라우저: Edge·Chrome·Playwright chromium 중 하나
  - 선택: PyMuPDF(fitz). 있으면 차례에 쪽 번호를 넣는다.

처리 요지
  - 수식 구간($…$, $$…$$)을 Markdown 해석에서 보호하고 KaTeX로 서버 쪽에서 렌더링한다.
    유니코드 위·아래 첨자(₀ ⁺ 등)와 프라임(′)은 KaTeX 글꼴에 없으므로 TeX 표기로 바꾼다.
  - 정리·정의·명제·보조정리·따름정리로 시작하는 문단과 「증명.」 문단을 알아보고 블록으로 꾸민다. 문단 끝의 ∎는 오른쪽으로 보낸다.
  - 2단계 제목마다 새 쪽에서 시작하고(--no-section-break 로 끔), 차례를 만든다(--no-toc 로 끔).
  - 본문은 명조(Noto Serif KR → MaruBuri → 나눔명조 → 바탕), 제목은 고딕 계열. 어절 단위 줄바꿈(keep-all)과 행두·행말 금칙(line-break: strict)을 켠다.
  - 디스플레이 수식이 행 폭을 넘치면 최상위 관계·연산 기호에서 줄을 바꾸고, 그래도 넘치면 그 수식만 글자를 줄인다.
  - 쪽 번호는 꼬리글에 넣고, 제목 구조를 PDF 책갈피(outline)로 넣는다.

종료 코드: 0 성공 / 1 변환 실패 / 2 사용·환경 오류
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from string import Template

# ──────────────────────────────────────────────────────────────────────────────
# 1. 설정과 상수
# ──────────────────────────────────────────────────────────────────────────────

KATEX_SPEC = "katex@0.16"
DEFAULT_CACHE = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".cache") / "md2pdf"

FONT_BODY = '"Noto Serif KR", "MaruBuri", "NanumMyeongjo", "Batang", "Noto Serif CJK KR", serif'
FONT_HEAD = '"Noto Sans KR", "NanumBarunGothic", "Malgun Gothic", "Noto Sans CJK KR", sans-serif'
FONT_MONO = '"Cascadia Mono", "Consolas", "D2Coding", monospace'

STATEMENT_HEAD = re.compile(r"^(정의|정리|명제|보조정리|따름정리|문제|추측|가설|관찰|예|예제|주의|참고|노트)\b")
PROOF_HEAD = re.compile(r"^(증명|.*의 증명|증명의 (요지|구조|개요))\b")

# 유니코드 첨자·프라임 → TeX 표기 (KaTeX 글꼴에 없는 글자)
SUB_MAP = {c: str(i) for i, c in enumerate("₀₁₂₃₄₅₆₇₈₉")}
SUB_MAP.update({"₊": "+", "₋": "-", "₌": "=", "₍": "(", "₎": ")", "ₙ": "n", "ₖ": "k", "ₘ": "m", "ᵢ": "i", "ⱼ": "j"})
SUP_MAP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
           "⁺": "+", "⁻": "-", "⁼": "=", "⁽": "(", "⁾": ")", "ⁿ": "n", "ⁱ": "i"}
SUB_RE = re.compile("[" + "".join(map(re.escape, SUB_MAP)) + "]+")
SUP_RE = re.compile("[" + "".join(map(re.escape, SUP_MAP)) + "]+")


def allow_breaks_at_commas(tex: str) -> str:
    """긴 인라인 수식에서 최상위(중괄호 밖, \\left…\\right 밖)의 「, 」 뒤에 줄바꿈 기회를 둔다.
    KaTeX는 \\allowbreak 자리에서 base 조각을 나누고, 인쇄 단계가 그 사이에 <wbr>을 넣는다."""
    out, depth, left = [], 0, 0
    i, n = 0, len(tex)
    while i < n:
        c = tex[i]
        if c == "\\" and i + 1 < n:
            nxt = tex[i + 1]
            if nxt in "{}":   # \{ \} 집합 괄호도 묶음으로 센다
                depth += 1 if nxt == "{" else -1
                out.append(tex[i:i + 2]); i += 2; continue
            m = re.match(r"\\(left|right)\b", tex[i:])
            if m:
                left += 1 if m.group(1) == "left" else -1
                out.append(m.group(0)); i += len(m.group(0)); continue
            out.append(c); i += 1; continue
        if c in "{([":
            depth += 1
        elif c in "})]":
            depth -= 1
        elif c == "," and depth == 0 and left <= 0 and i + 1 < n and tex[i + 1] not in "}])":
            # 최상위 쉼표(목록 구분자) 뒤. 뒤에 공백이 있으면 그대로 두고, 없으면 한 칸 둬서 \allowbreak가 다음 글자와 붙지 않게 한다
            out.append(",\\allowbreak" + ("" if tex[i + 1] == " " else " ")); i += 1; continue
        out.append(c); i += 1
    return "".join(out)


def normalize_tex(tex: str, display: bool = False) -> str:
    """KaTeX가 그리지 못하는 유니코드 글자를 TeX 표기로 바꾸고, 긴 인라인 수식에 줄바꿈 기회를 둔다."""
    if not display and len(tex) >= 30 and "," in tex:
        tex = allow_breaks_at_commas(tex)
    tex = SUB_RE.sub(lambda m: "_{" + "".join(SUB_MAP[c] for c in m.group(0)) + "}", tex)
    tex = SUP_RE.sub(lambda m: "^{" + "".join(SUP_MAP[c] for c in m.group(0)) + "}", tex)
    tex = tex.replace("′", "'").replace("″", "''").replace("‴", "'''")
    tex = tex.replace("−", "-")  # U+2212 minus
    tex = tex.replace("–", r"\text{–}").replace("—", r"\text{—}")  # 줄표는 글자로 둔다
    # \tag{...}의 인자는 글 모드다. 첨자·명령이 들어 있으면 수식 모드로 감싼다 (\tag{R_0} → \tag{$R_0$})
    tex = re.sub(r"\\tag\{((?:[^{}]|\{[^{}]*\})*)\}",
                 lambda m: m.group(0) if not re.search(r"[_^\\]", m.group(1)) or m.group(1).startswith("$")
                 else r"\tag{$" + m.group(1) + "$}", tex)
    return tex


# ──────────────────────────────────────────────────────────────────────────────
# 2. KaTeX (Node) 도우미
# ──────────────────────────────────────────────────────────────────────────────

KATEX_HELPER_JS = r"""
// stdin: {"katex": "<dir>", "items": [{"tex": "...", "display": true|false}, ...]}
// stdout: {"html": [...], "errors": [{"i": n, "msg": "..."}], "warnings": {"code: msg": count}}
const fs = require('fs');
const path = require('path');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const katex = require(path.join(input.katex, 'node_modules', 'katex'));
const html = [], errors = [], warnings = {};
const strict = (code, msg) => {
  if (code === 'unicodeTextInMathMode') return 'ignore';   // \text{한글} 등은 정상 용법
  const k = code + ': ' + msg; warnings[k] = (warnings[k] || 0) + 1; return 'ignore';
};
input.items.forEach((it, i) => {
  const base = { displayMode: !!it.display, strict, trust: false, output: 'htmlAndMathml', errorColor: '#b00020' };
  try {
    html.push(katex.renderToString(it.tex, Object.assign({ throwOnError: true }, base)));
  } catch (e) {
    errors.push({ i, msg: String(e.message) });
    html.push(katex.renderToString(it.tex, Object.assign({ throwOnError: false }, base)));
  }
});
process.stdout.write(JSON.stringify({ html, errors, warnings }));
"""


def ensure_katex(cache: Path, verbose: bool) -> Path:
    """KaTeX 패키지가 캐시에 있게 하고, 캐시 디렉토리를 돌려준다."""
    pkg = cache / "node_modules" / "katex" / "package.json"
    if pkg.exists():
        return cache
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        die(2, "npm을 찾지 못했다. Node.js를 설치하거나 --katex-dir 로 katex가 설치된 디렉토리를 주라.")
    cache.mkdir(parents=True, exist_ok=True)
    if not (cache / "package.json").exists():
        (cache / "package.json").write_text('{"name":"md2pdf-cache","private":true}\n', encoding="utf-8")
    log(verbose, f"KaTeX를 내려받는다: npm install {KATEX_SPEC} → {cache}")
    r = subprocess.run([npm, "install", "--silent", "--no-audit", "--no-fund", KATEX_SPEC],
                       cwd=str(cache), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 or not pkg.exists():
        die(2, "KaTeX 설치 실패:\n" + (r.stderr or r.stdout))
    return cache


def render_math(items: list[tuple[str, bool]], katex_dir: Path, verbose: bool) -> tuple[list[str], list[dict], dict]:
    if not items:
        return [], [], {}
    node = shutil.which("node")
    if not node:
        die(2, "node를 찾지 못했다. Node.js를 설치하라 (KaTeX 렌더링에 쓴다).")
    helper = katex_dir / "katex_render.js"
    if not helper.exists() or helper.read_text(encoding="utf-8") != KATEX_HELPER_JS:
        helper.write_text(KATEX_HELPER_JS, encoding="utf-8")
    payload = json.dumps({"katex": str(katex_dir), "items": [{"tex": t, "display": d} for t, d in items]}, ensure_ascii=False)
    r = subprocess.run([node, str(helper)], input=payload.encode("utf-8"), capture_output=True, timeout=600)
    if r.returncode != 0:
        die(1, "KaTeX 렌더링 실패:\n" + r.stderr.decode("utf-8", "replace"))
    out = json.loads(r.stdout.decode("utf-8"))
    return out["html"], out["errors"], out["warnings"]


# ──────────────────────────────────────────────────────────────────────────────
# 3. Markdown → HTML
# ──────────────────────────────────────────────────────────────────────────────

def build_markdown():
    try:
        from markdown_it import MarkdownIt
        from mdit_py_plugins.dollarmath import dollarmath_plugin
        from mdit_py_plugins.footnote import footnote_plugin
    except ImportError as e:
        die(2, f"Python 패키지가 없다({e.name}). 설치: pip install markdown-it-py mdit-py-plugins")
    md = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    # double_inline=True: 문단 한가운데(앞뒤 빈 줄 없이) 선 $$…$$도 디스플레이 수식으로 그린다.
    # 그래야 정리 진술 문단이 디스플레이 수식을 품은 채 한 블록으로 남는다.
    md.use(dollarmath_plugin, allow_space=True, allow_digits=True, double_inline=True)
    md.use(footnote_plugin)

    def math_inline(self, tokens, idx, options, env):
        env["math"].append((normalize_tex(tokens[idx].content), False))
        return f"\x00MATH{len(env['math']) - 1}\x00"

    def math_display(self, tokens, idx, options, env):
        env["math"].append((normalize_tex(tokens[idx].content.strip(), display=True), True))
        return f"\x00MATH{len(env['math']) - 1}\x00\n"

    md.add_render_rule("math_inline", math_inline)
    md.add_render_rule("math_inline_double", math_display)
    md.add_render_rule("math_block", math_display)
    return md


def plain_text(md, inline_token) -> tuple[str, str]:
    """인라인 토큰의 글자만 뽑는다(제목·차례용). 둘째 값은 PDF 본문 검색에 쓸 열쇠(첫 수식 앞까지)다."""
    parts, key, seen_math = [], [], False
    for c in inline_token.children or []:
        if c.type in ("text", "code_inline"):
            parts.append(c.content)
            if not seen_math:
                key.append(c.content)
        elif c.type == "math_inline":
            parts.append(c.content)
            seen_math = True
        elif c.type == "softbreak":
            parts.append(" ")
            if not seen_math:
                key.append(" ")
    text = re.sub(r"\s+", " ", "".join(parts)).strip()
    k = re.sub(r"\s+", " ", "".join(key)).strip()
    return text, (k if len(k) >= 4 else text)


def escape_intraword_asterisks(text: str) -> str:
    """글자 사이에 낀 별표 하나(`V*다`, `(V*)`)를 `\\*`로 바꾼다.

    CommonMark는 `*`의 글자 사이 강조를 허용하므로 `V*다 … (V*`가 <em>으로 묶여 그 사이 본문 전체에
    드러냄표가 붙는다. 수식(`$…$`, `$$…$$`)과 코드(`` `…` ``) 안은 건드리지 않는다. `**`는 대상이 아니다.
    """
    out, i, n = [], 0, len(text)
    pat = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$|`[^`\n]+`", re.S)
    for m in pat.finditer(text):
        seg = text[i:m.start()]
        out.append(re.sub(r"(?<=[^\s*])\*(?=[^\s*])", r"\\*", seg))
        out.append(m.group(0))
        i = m.end()
    out.append(re.sub(r"(?<=[^\s*])\*(?=[^\s*])", r"\\*", text[i:]))
    return "".join(out)


def convert_markdown(md, text: str, env: dict) -> tuple[str, str, list[dict]]:
    """본문 HTML, 제목, 차례 항목을 돌려준다."""
    tokens = md.parse(text, env)
    title = ""
    headings: list[dict] = []
    n = 0
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.type == "heading_open":
            inline = tokens[i + 1]
            level = int(t.tag[1])
            txt, key = plain_text(md, inline)
            if level == 1 and not title:
                title = txt
                # 제목은 머리 블록에서 따로 그리므로 본문에서 뺀다
                del tokens[i:i + 3]
                continue
            n += 1
            hid = f"sec-{n}"
            t.attrSet("id", hid)
            headings.append({"level": level, "text": txt, "key": key, "id": hid})
        elif t.type == "paragraph_open" and i + 1 < len(tokens) and tokens[i + 1].type == "inline":
            ch = [c for c in (tokens[i + 1].children or []) if not (c.type == "text" and c.content == "")]
            if len(ch) >= 2 and ch[0].type == "strong_open" and ch[1].type == "text":
                head = ch[1].content.strip()
                if STATEMENT_HEAD.match(head):
                    t.attrJoin("class", "thm")
                elif PROOF_HEAD.match(head):
                    t.attrJoin("class", "proof")
        i += 1
    body = md.renderer.render(tokens, md.options, env)
    return body, title, headings


def decorate(body: str) -> str:
    """정리 블록의 지위 표지 [..]를 꼬리표로, 문단 끝 ∎를 오른쪽 정렬로 바꾼다."""
    def tag_in_head(m):
        inner = re.sub(r"\[([^\]]+)\]", r'<span class="tag">[\1]</span>', m.group(2))
        return m.group(1) + inner + m.group(3)
    body = re.sub(r'(<p class="thm"><strong>)(.*?)(</strong>)', tag_in_head, body, flags=re.S)
    body = re.sub(r"\s*∎\s*</p>", '<span class="qed">∎</span></p>', body)

    def short_cell(m):
        # 수식 자리표시자가 없고 글자 수가 짧은 표 칸은 nowrap으로 둔다(식별자 r81e7051, 시각 11-05 15:55 등).
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "\x00MATH" in inner:
            return m.group(0)
        txt = re.sub(r"<[^>]+>", "", inner)
        txt = html.unescape(txt).strip()
        if 0 < len(txt) <= 12 and "\n" not in txt:
            return f'<{tag}{attrs} class="nw">{inner}</{tag}>'
        return m.group(0)
    body = re.sub(r"<(td|th)((?:\s[^>]*)?)>(.*?)</\1>", short_cell, body, flags=re.S)
    return body


# ──────────────────────────────────────────────────────────────────────────────
# 4. HTML 문서 조립
# ──────────────────────────────────────────────────────────────────────────────

CSS = r"""
:root {
  --body: ${font_body};
  --head: ${font_head};
  --mono: ${font_mono};
  --fs: ${font_size};
  --lh: ${line_height};
  --ink: #1a1a1a;
  --muted: #666;
  --rule: #999;
}
@page { size: ${paper}; }
html { font-size: var(--fs); }
body {
  margin: 0; color: var(--ink);
  font-family: var(--body); font-size: 1rem; line-height: var(--lh);
  word-break: keep-all; line-break: strict; overflow-wrap: anywhere;
  text-align: ${align}; hyphens: manual;
  font-kerning: normal; font-variant-ligatures: common-ligatures;
  text-rendering: optimizeLegibility;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
p { margin: 0 0 0.65em; orphans: 2; widows: 2; }
strong { font-weight: 700; }
em { font-style: normal; text-emphasis: filled dot; -webkit-text-emphasis: filled dot; }  /* 한글은 기울임 대신 드러냄표 */
em:lang(en) { font-style: italic; text-emphasis: none; -webkit-text-emphasis: none; }
code { font-family: var(--mono); font-size: 0.9em; background: #f4f4f4; padding: 0 0.2em; border-radius: 2px; }
pre { font-family: var(--mono); font-size: 0.85em; line-height: 1.5; background: #f6f6f6; padding: 0.7em 0.9em; overflow: hidden; white-space: pre-wrap; border-radius: 3px; break-inside: avoid; }
pre code { background: none; padding: 0; }
a { color: inherit; text-decoration: none; }
hr { border: 0; border-top: 1px solid var(--rule); margin: 1.5em 0; }
blockquote { margin: 0.8em 0 0.8em 1.2em; padding-left: 0.8em; border-left: 2px solid #bbb; color: #333; }
ul, ol { margin: 0.2em 0 0.7em; padding-left: 1.6em; }
li { margin: 0.15em 0; }
li > p { margin: 0 0 0.3em; }
sup, sub { line-height: 0; }

/* 제목 */
h1, h2, h3, h4, h5, h6 { font-family: var(--head); font-weight: 700; color: #111; line-height: 1.35; break-after: avoid; text-align: left; }
h2 { font-size: 1.55rem; margin: 0 0 1.1em; padding-bottom: 0.3em; border-bottom: 1.5px solid #222; ${h2_break} }
h3 { font-size: 1.2rem; margin: 1.6em 0 0.6em; }
h4 { font-size: 1.05rem; margin: 1.3em 0 0.45em; }
h5, h6 { font-size: 1rem; margin: 1.1em 0 0.4em; }
h2 + h3 { margin-top: 0.4em; }

/* 머리 블록과 차례 */
header.title-block { text-align: center; margin: 2.2em 0 2.4em; }
header.title-block h1 { font-size: 1.9rem; margin: 0 0 0.5em; line-height: 1.4; text-align: center; border: 0; }
header.title-block .subtitle { font-family: var(--head); font-size: 1.05rem; color: #333; margin: 0.2em 0; }
header.title-block .meta { font-family: var(--head); font-size: 0.9rem; color: var(--muted); margin-top: 0.8em; }
nav.toc { margin: 0 0 1em; ${toc_break} }
nav.toc h2.toc-title { font-size: 1.3rem; border: 0; margin: 0 0 0.8em; break-before: auto; }
nav.toc ol { list-style: none; margin: 0; padding: 0; }
nav.toc li { margin: 0; }
nav.toc li.lv3 { padding-left: 1.6em; }
nav.toc li.lv4 { padding-left: 3.2em; font-size: 0.92em; }
nav.toc a { display: flex; align-items: baseline; line-height: 1.75; font-family: var(--head); font-size: 0.95em; }
nav.toc li.lv2 a { font-weight: 700; margin-top: 0.35em; }
nav.toc .t { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
nav.toc .dots { flex: 1; border-bottom: 1px dotted #999; margin: 0 0.4em 0.35em; min-width: 1em; }
nav.toc .pg { font-variant-numeric: tabular-nums; }

/* 정리·증명 블록 */
p.thm { margin: 0.9em 0 0.9em; padding: 0.15em 0 0.15em 0.9em; border-left: 2.5px solid #333; break-inside: avoid; }
p.thm > strong:first-child { font-family: var(--head); font-weight: 700; }
p.thm .tag { font-family: var(--head); font-weight: 400; font-size: 0.82em; color: var(--muted); margin-left: 0.15em; }
p.proof { margin: 0.6em 0 0.9em; }
p.proof > strong:first-child { font-family: var(--head); font-weight: 700; }
.qed { margin-left: 0.45em; white-space: nowrap; }  /* 증명 끝 표시는 마지막 문장 바로 뒤에 둔다(오른쪽 끝으로 띄우지 않는다) */

/* 표 */
table { border-collapse: collapse; margin: 1em auto 1.3em; font-size: 0.9em; line-height: 1.5; max-width: 100%; }
thead { display: table-header-group; }
th, td { padding: 0.3em 0.6em; vertical-align: top; text-align: left; border: 0; overflow-wrap: normal; }  /* 본문의 anywhere를 끄면 끊을 수 없는 토큰(식별자 등)이 열의 최소 폭이 되어 글자 단위로 쪼개지지 않는다 */
td.nw, th.nw { white-space: nowrap; }  /* 짧은 칸(식별자·시각)은 칸 안에서 줄을 바꾸지 않는다 */
th { font-family: var(--head); font-weight: 700; border-top: 1.5px solid #222; border-bottom: 1px solid #222; }
tbody tr:last-child td { border-bottom: 1.5px solid #222; }
tr { break-inside: avoid; }
td code, th code { background: none; padding: 0; font-size: 0.95em; }

/* 수식 (KaTeX) */
.katex { font-size: ${math_scale}; white-space: normal; }  /* 인쇄 단계(FIT_JS)가 base 조각을 묶음(.vr-grp)으로 감싸 관계 기호 뒤에서만 줄바꿈되게 한다 */
.vr-grp { display: inline-block; white-space: nowrap; }
.katex-display { margin: 0.8em 0 1em; break-inside: avoid; }
.katex-display .katex { white-space: nowrap; }                /* 디스플레이 수식은 한 줄이 기본. 넘치면 인쇄 단계가 쉼표 뒤 줄바꿈·글자 크기 축소로 맞춘다 */
.katex-display > .katex > .katex-html > .tag { position: relative; float: right; margin-left: 0.5em; }
.katex .text, .katex .textrm, .katex .mord.text { font-family: var(--body); }
.katex .katex-mathml { display: none; }                   /* MathML은 복사·검색용으로만 둔다 */

/* 각주 */
.footnotes { font-size: 0.88em; margin-top: 2em; border-top: 1px solid #999; padding-top: 0.6em; }
.footnotes ol { padding-left: 1.4em; }
.footnote-backref { font-size: 0.85em; }
"""

FIT_JS = r"""
() => {
  // KaTeX는 최상위 관계·이항 기호(와 그 뒤 글루) 뒤에서 식을 .base 조각으로 나눈다. .base는 inline-block이라 .katex가
  // white-space: normal이면 조각 사이 어디서나 줄이 바뀐다(⌊v · / 2^128⌋ 같은 나쁜 자리 포함). 그래서 조각들을 묶음
  // (.vr-grp, inline-block·nowrap)으로 감싸고, 허용한 자리(관계 기호 뒤, 목록 쉼표 뒤) 뒤에서만 묶음을 끊는다.
  const isBase = n => n.nodeType === 1 && n.classList.contains('base');
  const atoms = b => Array.from(b.children).filter(c => !c.classList.contains('strut') && !c.classList.contains('mspace'));
  const endsWithRel = b => { const a = atoms(b); return a.length > 0 && a[a.length - 1].classList.contains('mrel'); };
  const regroup = (kh, breakAfter) => {
    for (const g of Array.from(kh.querySelectorAll(':scope > .vr-grp'))) { while (g.firstChild) kh.insertBefore(g.firstChild, g); g.remove(); }
    let grp = null;
    for (const node of Array.from(kh.childNodes)) {
      if (!isBase(node)) { grp = null; continue; }
      if (!grp) { grp = document.createElement('span'); grp.className = 'vr-grp'; kh.insertBefore(grp, node); }
      grp.appendChild(node);
      if (breakAfter(node)) grp = null;
    }
  };
  // 최상위 쉼표(목록 구분) 뒤에서 base를 둘로 갈라 그 자리를 끊을 수 있는 자리로 표시한다(.base는 nowrap·min-content라 안에서는 못 끊는다).
  const splitAtPunct = (kh) => {
    for (const base of Array.from(kh.children).filter(isBase)) {
      let cur = base;
      for (const p of Array.from(base.querySelectorAll(':scope > .mpunct'))) {
        let after = p.nextSibling;
        if (after && after.classList && after.classList.contains('mspace')) after = after.nextSibling;
        if (!after) continue;
        const nb = document.createElement('span'); nb.className = cur.className;
        const strut = cur.querySelector(':scope > .strut'); if (strut) nb.appendChild(strut.cloneNode(true));
        while (after) { const nx = after.nextSibling; nb.appendChild(after); after = nx; }
        cur.dataset.punctEnd = '1';
        cur.after(nb);
        cur = nb;
      }
    }
  };
  // 1) 인라인 수식: 관계 기호(=, ≤, ⇒ …) 뒤에서만 줄을 바꾼다 — TeX의 인라인 줄바꿈 자리 가운데 이항 기호 뒤는 뺀 것이다.
  for (const kh of document.querySelectorAll('.katex-html')) {
    if (kh.closest('.katex-display')) continue;
    regroup(kh, endsWithRel);
  }
  // 2) 디스플레이 수식은 한 줄이 기본이다(CSS nowrap). 넘치면 쉼표 뒤에서 줄을 바꾸고, 그래도 넘치면 글자 크기를 줄이고,
  //    그래도 넘치면 관계 기호 뒤도 연다. 넘친 채 두면 Chromium이 문서 전체를 쪽 폭에 맞춰 축소 인쇄한다.
  const still = [];
  for (const el of document.querySelectorAll('.katex-display')) {
    const k = el.querySelector(':scope > .katex');
    if (!k) continue;
    const kh = k.querySelector('.katex-html');
    const avail = el.clientWidth;
    const over = () => k.scrollWidth > avail + 1;
    if (over() && kh) {
      splitAtPunct(kh);
      regroup(kh, b => b.dataset.punctEnd === '1');
      k.style.whiteSpace = 'normal';
    }
    let em = parseFloat(getComputedStyle(k).fontSize) / parseFloat(getComputedStyle(el).fontSize);
    let guard = 0;
    while (over() && em > 0.72 && guard++ < 12) {
      em -= 0.05; k.style.fontSize = em.toFixed(2) + 'em';
    }
    if (over() && kh) regroup(kh, b => b.dataset.punctEnd === '1' || endsWithRel(b));
    if (over()) still.push((k.textContent || '').slice(0, 80));
  }
  // 3) 표 칸은 overflow-wrap: normal이라 끊을 수 없는 토큰이 열의 최소 폭이 된다. 그 때문에 표가 본문 폭을 넘치면
  //    글자 크기를 단계적으로 줄이고, 그래도 넘치면 그 표의 칸에만 anywhere를 되돌린다(최후 수단).
  for (const tb of document.querySelectorAll('table')) {
    const avail = tb.parentElement.clientWidth;
    let em = parseFloat(getComputedStyle(tb).fontSize) / parseFloat(getComputedStyle(tb.parentElement).fontSize);
    let guard = 0;
    while (tb.scrollWidth > avail + 1 && em > 0.72 && guard++ < 12) {
      em -= 0.03; tb.style.fontSize = em.toFixed(2) + 'em';
    }
    if (tb.scrollWidth > avail + 1) {
      for (const c of tb.querySelectorAll('td, th')) { c.style.overflowWrap = 'anywhere'; c.classList.remove('nw'); }
      still.push('table: ' + (tb.textContent || '').trim().slice(0, 60));
    }
  }
  return still;
}
"""


def build_html(body: str, title: str, headings: list[dict], katex_css: str, opts, toc_pages: dict | None) -> str:
    toc_html = ""
    if opts.toc and headings:
        items = []
        for h in headings:
            if h["level"] > opts.toc_depth:
                continue
            pg = (toc_pages or {}).get(h["id"], "")
            items.append(
                f'<li class="lv{h["level"]}"><a href="#{h["id"]}"><span class="t">{html.escape(h["text"])}</span>'
                f'<span class="dots"></span><span class="pg" data-for="{h["id"]}">{pg}</span></a></li>'
            )
        toc_html = f'<nav class="toc"><h2 class="toc-title">{html.escape(opts.toc_title)}</h2><ol>{"".join(items)}</ol></nav>'
    sub = f'<p class="subtitle">{html.escape(opts.subtitle)}</p>' if opts.subtitle else ""
    meta = f'<p class="meta">{html.escape(opts.meta)}</p>' if opts.meta else ""
    css = Template(CSS).substitute({
        "font_body": opts.font_body, "font_head": opts.font_head, "font_mono": FONT_MONO,
        "font_size": opts.font_size, "line_height": opts.line_height, "paper": opts.paper,
        "align": "left" if opts.ragged else "justify",
        "h2_break": "" if opts.no_section_break else "break-before: page;",
        "toc_break": "break-after: page;" if not opts.no_section_break else "",
        "math_scale": opts.math_scale,
    })
    return (
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{html.escape(title or opts.input.stem)}</title>\n"
        f'<link rel="stylesheet" href="{katex_css}">\n<style>{css}</style>\n</head>\n<body>\n'
        f'<header class="title-block"><h1>{html.escape(title or opts.input.stem)}</h1>{sub}{meta}</header>\n'
        f"{toc_html}\n<main>\n{body}\n</main>\n</body>\n</html>\n"
    )


# ──────────────────────────────────────────────────────────────────────────────
# 5. HTML → PDF (Playwright)
# ──────────────────────────────────────────────────────────────────────────────

def launch_browser(p, prefer: str, verbose: bool):
    order = {"auto": ["msedge", "chrome", None], "msedge": ["msedge"], "chrome": ["chrome"], "chromium": [None]}[prefer]
    last = None
    for ch in order:
        try:
            b = p.chromium.launch(channel=ch) if ch else p.chromium.launch()
            log(verbose, f"브라우저: {ch or 'playwright chromium'} {b.version}")
            return b
        except Exception as e:  # noqa: BLE001
            last = e
    die(2, f"브라우저를 띄우지 못했다: {last}\n  Edge/Chrome을 설치하거나 `python -m playwright install chromium`을 실행하라.")


_PAPER_MM = {"a3": 297.0, "a4": 210.0, "a5": 148.0, "b5": 176.0, "letter": 215.9, "legal": 215.9, "tabloid": 279.4}


def css_length_px(s: str) -> float:
    """CSS 길이(mm, cm, in, pt, px)를 CSS 픽셀(96dpi)로 바꾼다."""
    m = re.fullmatch(r"\s*([0-9.]+)\s*(mm|cm|in|pt|px)?\s*", s)
    if not m:
        raise ValueError(f"길이를 읽을 수 없다: {s!r}")
    v, u = float(m.group(1)), (m.group(2) or "px")
    return v * {"mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96.0, "pt": 96 / 72, "px": 1.0}[u]


def content_width_px(opts) -> int:
    """인쇄되는 본문 폭(쪽 폭 − 양쪽 여백)을 CSS 픽셀로 돌려준다. FIT_JS가 이 폭에서 재어야 인쇄 결과와 같다."""
    paper = opts.paper.strip()
    first = paper.split()[0]
    if first.lower() in _PAPER_MM:
        paper_px = _PAPER_MM[first.lower()] * 96 / 25.4
    else:
        paper_px = css_length_px(first)
    return max(200, int(paper_px - 2 * css_length_px(opts.margin_side)))


def print_pdf(page, html_path: Path, opts, verbose: bool, tagged: bool = False) -> tuple[bytes, list[str]]:
    # 뷰포트를 인쇄 본문 폭에 맞춘다. 기본 뷰포트(1280px)에서 재면 디스플레이 수식·표가 쪽에서는 넘치는데도
    # 맞는 것으로 측정되고, Chromium은 넘치는 문서 전체를 쪽 폭에 맞춰 축소 인쇄한다(글자가 작아지고 쪽수가 준다).
    page.set_viewport_size({"width": content_width_px(opts), "height": 1400})
    page.set_default_timeout(600000)
    page.goto(html_path.as_uri(), wait_until="load", timeout=600000)
    page.wait_for_function("document.fonts.status === 'loaded'", timeout=120000)
    page.emulate_media(media="print")
    still = page.evaluate(FIT_JS)
    footer = (
        '<div style="width:100%;font-size:9px;font-family:' + html.escape(opts.font_body, quote=True) +
        ';text-align:center;color:#555;"><span class="pageNumber"></span></div>'
    )
    header = (
        '<div style="width:100%;font-size:8px;font-family:' + html.escape(opts.font_head, quote=True) +
        f';color:#888;padding:0 {opts.margin_side};text-align:right;">{html.escape(opts.running_head)}</div>'
        if opts.running_head else "<div></div>"
    )
    pdf = page.pdf(
        prefer_css_page_size=True,
        print_background=True,
        margin={"top": opts.margin_top, "bottom": opts.margin_bottom, "left": opts.margin_side, "right": opts.margin_side},
        display_header_footer=not opts.no_page_numbers,
        header_template=header if not opts.no_page_numbers else "<div></div>",
        footer_template=footer if not opts.no_page_numbers else "<div></div>",
        tagged=tagged,   # Chromium은 tagged일 때만 제목 책갈피(outline)를 만든다
        outline=tagged,
    )
    return pdf, still


def toc_pages_from_pdf(pdf: bytes, headings: list[dict], verbose: bool, has_toc: bool = True) -> dict:
    """1차 PDF의 책갈피(outline)에서 제목별 쪽 번호를 읽는다. 없으면 본문 검색으로 대신한다."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        log(verbose, "PyMuPDF가 없어 차례에 쪽 번호를 넣지 않는다 (pip install pymupdf).")
        return {}
    doc = fitz.open(stream=pdf, filetype="pdf")
    pages: dict = {}
    outline = doc.get_toc(simple=True)
    norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731
    if outline:
        # 책갈피 제목은 수식이 든 제목에서 글자가 겹쳐 나올 수 있으므로 첫 수식 앞까지의 열쇠로 앞부분 일치를 본다
        j = 0
        for h in headings:
            want, key = norm(h["text"]), norm(h["key"])
            for k in range(j, len(outline)):
                cand = norm(outline[k][1])
                if cand == want or cand.startswith(key):
                    pages[h["id"]] = outline[k][2]
                    j = k + 1
                    break
    missing = [h for h in headings if h["id"] not in pages]
    if missing:
        # 차례 자체가 제목 글자를 품고 있으므로, 마지막 제목이 처음 나오는 쪽(차례의 끝)까지는 건너뛴다.
        start = 0
        if has_toc:
            last_key = headings[-1]["key"][:60]
            for pno in range(doc.page_count):
                if doc[pno].search_for(last_key):
                    start = pno + 1
                    break
        for h in missing:
            for pno in range(start, doc.page_count):
                if doc[pno].search_for(h["key"][:60]):
                    pages[h["id"]] = pno + 1
                    start = pno
                    break
    log(verbose, f"차례 쪽 번호: 책갈피 {len(outline)}개, 제목 {len(headings)}개 중 {len(pages)}개 확정")
    return pages


def finish_pdf(pdf: bytes, title: str, headings: list[dict], pages: dict, verbose: bool) -> tuple[bytes, int | None]:
    """제목 구조를 책갈피로 넣고 메타데이터를 채운다(PyMuPDF가 있을 때). 쪽 수를 함께 돌려준다."""
    try:
        import fitz
    except ImportError:
        return pdf, None
    doc = fitz.open(stream=pdf, filetype="pdf")
    n = doc.page_count
    if pages:
        toc = []
        base = min(h["level"] for h in headings)
        for h in headings:
            if h["id"] in pages:
                toc.append([h["level"] - base + 1, h["text"], pages[h["id"]]])
        # 책갈피 깊이는 한 번에 한 단계씩만 깊어질 수 있다
        fixed, prev = [], 0
        for lvl, txt, pg in toc:
            lvl = min(lvl, prev + 1)
            fixed.append([lvl, txt, pg])
            prev = lvl
        doc.set_toc(fixed)
        log(verbose, f"책갈피 {len(fixed)}개")
    doc.set_metadata({"title": title, "producer": "md2pdf (markdown-it-py · KaTeX · Chromium)", "creator": "md2pdf"})
    out = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return out, n


# ──────────────────────────────────────────────────────────────────────────────
# 6. 주 흐름
# ──────────────────────────────────────────────────────────────────────────────

def log(verbose: bool, msg: str):
    if verbose:
        print(msg, file=sys.stderr)


def die(code: int, msg: str):
    print(msg, file=sys.stderr)
    sys.exit(code)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description="수식이 있는 Markdown을 PDF로 조판한다.")
    ap.add_argument("input", type=Path, help="입력 Markdown 파일")
    ap.add_argument("-o", "--output", type=Path, help="출력 PDF (기본: 입력과 같은 이름 .pdf)")
    ap.add_argument("--html", type=Path, help="중간 HTML을 이 경로에 남긴다")
    ap.add_argument("--subtitle", default="", help="제목 아래 부제")
    ap.add_argument("--meta", default="", help="제목 블록의 메타 줄(저자·날짜 등)")
    ap.add_argument("--running-head", default="", help="머리글에 넣을 짧은 제목(기본 없음)")
    ap.add_argument("--paper", default="A4", help="쪽 크기(CSS size 값: A4, letter, '170mm 240mm' …)")
    ap.add_argument("--margin-top", default="22mm")
    ap.add_argument("--margin-bottom", default="24mm")
    ap.add_argument("--margin-side", default="24mm")
    ap.add_argument("--font-body", default=FONT_BODY, help="본문 글꼴 목록(CSS font-family)")
    ap.add_argument("--font-head", default=FONT_HEAD, help="제목 글꼴 목록")
    ap.add_argument("--font-size", default="10.5pt", help="본문 글자 크기")
    ap.add_argument("--line-height", default="1.8", help="행간(배수)")
    ap.add_argument("--math-scale", default="1.08em", help="KaTeX 글자 크기(본문 대비)")
    ap.add_argument("--ragged", action="store_true", help="양끝 맞춤 대신 왼쪽 맞춤")
    ap.add_argument("--star-emphasis", action="store_true", help="글자 사이의 별표 하나(V*다)를 강조로 두고 이스케이프하지 않는다")
    ap.add_argument("--no-toc", dest="toc", action="store_false", help="차례를 만들지 않는다")
    ap.add_argument("--toc-title", default="차례")
    ap.add_argument("--toc-depth", type=int, default=3, help="차례에 넣을 제목 깊이(2=절만, 3=절·소절)")
    ap.add_argument("--no-section-break", action="store_true", help="2단계 제목마다 새 쪽에서 시작하지 않는다")
    ap.add_argument("--no-page-numbers", action="store_true")
    ap.add_argument("--browser", choices=["auto", "msedge", "chrome", "chromium"], default="auto")
    ap.add_argument("--katex-dir", type=Path, default=DEFAULT_CACHE, help="katex가 node_modules 아래 설치된 디렉토리(없으면 받는다)")
    ap.add_argument("-q", "--quiet", action="store_true")
    return ap.parse_args(argv)


def main(argv=None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    opts = parse_args(argv)
    verbose = not opts.quiet
    if not opts.input.is_file():
        die(2, f"입력 파일이 없다: {opts.input}")
    out = opts.output or opts.input.with_suffix(".pdf")
    text = opts.input.read_text(encoding="utf-8")

    # Markdown → HTML(수식은 자리표)
    t0 = time.time()
    md = build_markdown()
    env = {"math": []}
    if not opts.star_emphasis:
        text = escape_intraword_asterisks(text)
    body, title, headings = convert_markdown(md, text, env)
    body = decorate(body)
    log(verbose, f"Markdown 해석 {time.time() - t0:.1f}초, 제목 {len(headings)}개")

    # 수식 렌더링
    t0 = time.time()
    katex_dir = ensure_katex(opts.katex_dir, verbose)
    rendered, errors, warnings = render_math(env["math"], katex_dir, verbose)
    body = re.sub(r"\x00MATH(\d+)\x00", lambda m: rendered[int(m.group(1))], body)
    katex_css = (katex_dir / "node_modules" / "katex" / "dist" / "katex.min.css").as_uri()
    log(verbose, f"수식 {len(env['math'])}개 렌더링 {time.time() - t0:.1f}초 (오류 {len(errors)}개, 경고 종류 {len(warnings)}개)")
    for e in errors[:20]:
        tex = env["math"][e["i"]][0]
        print(f"  [수식 오류] {e['msg']}\n      {tex[:120]}", file=sys.stderr)
    for k, v in list(warnings.items())[:20]:
        log(verbose, f"  [수식 경고 ×{v}] {k}")

    # HTML → PDF (차례 쪽 번호는 2차 렌더링에서 채운다)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        die(2, "playwright가 없다. 설치: pip install playwright  (브라우저는 Edge/Chrome을 쓰거나 `python -m playwright install chromium`)")

    with tempfile.TemporaryDirectory(prefix="md2pdf-") as tmp:
        html_path = Path(tmp) / "doc.html"
        with sync_playwright() as p:
            browser = launch_browser(p, opts.browser, verbose)
            page = browser.new_page()
            html_path.write_text(build_html(body, title, headings, katex_css, opts, None), encoding="utf-8")
            t0 = time.time()
            pdf, still = print_pdf(page, html_path, opts, verbose, tagged=True)
            log(verbose, f"1차 인쇄(tagged, 책갈피 수집) {time.time() - t0:.0f}초")
            pages = {}
            if headings:
                pages = toc_pages_from_pdf(pdf, headings, verbose, has_toc=opts.toc)
                if pages and opts.toc:
                    html_path.write_text(build_html(body, title, headings, katex_css, opts, pages), encoding="utf-8")
                    t0 = time.time()
                    pdf, still = print_pdf(page, html_path, opts, verbose)
                    log(verbose, f"2차 인쇄(차례 쪽 번호 반영) {time.time() - t0:.0f}초")
            browser.close()
        if opts.html:
            opts.html.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(html_path, opts.html)
            log(verbose, f"HTML: {opts.html}")

    out.parent.mkdir(parents=True, exist_ok=True)
    pdf, n_pages = finish_pdf(pdf, title or opts.input.stem, headings, pages if (opts.toc and headings) else {}, verbose)
    out.write_bytes(pdf)
    for s in still[:10]:
        print(f"  [넘침] 줄인 뒤에도 폭을 넘는 디스플레이 수식: {s}", file=sys.stderr)
    print(f"PDF: {out}" + (f" ({n_pages}쪽, {len(pdf) / 1024 / 1024:.1f} MB)" if n_pages else f" ({len(pdf) / 1024 / 1024:.1f} MB)"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

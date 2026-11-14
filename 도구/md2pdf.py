r"""md2pdf — 수식이 있는 Markdown 문서를 읽기 좋은 PDF로 조판한다.

경로: Markdown ─(markdown-it-py)→ HTML ─(KaTeX, Node)→ 수식 HTML ─(Playwright·Chromium 계열)→ PDF

    python 도구/md2pdf.py 입력.md [-o 출력.pdf] [옵션]

필요한 것
  - Python 패키지: markdown-it-py, mdit-py-plugins, playwright  (pip install markdown-it-py mdit-py-plugins playwright)
  - Node.js(npm 포함): KaTeX를 처음 한 번 %LOCALAPPDATA%/md2pdf 에 내려받는다 (npm install katex@0.16)
  - 브라우저: Edge·Chrome·Playwright chromium 중 하나
  - 선택: PyMuPDF(fitz). 있으면 차례에 쪽 번호를 넣고 책갈피를 만든다.

처리 요지
  - 수식 구간($…$, $$…$$)을 Markdown 해석에서 보호하고 KaTeX로 서버 쪽에서 렌더링한다.
    유니코드 위·아래 첨자(₀ ⁺ 등)와 프라임(′)은 KaTeX 글꼴에 없으므로 TeX 표기로 바꾼다.
    긴 숫자열(24자리 이상)에는 열 자리마다 줄바꿈 기회를 둔다.
  - 정리·정의·명제·보조정리·따름정리로 시작하는 문단과 「증명.」 문단을 알아보고 블록으로 꾸민다. 문단 끝의 ∎는 마지막 문장 뒤에 둔다.
    문단 한가운데의 디스플레이 수식은 문단을 쪼개 독립 블록으로 둔다(쪽 경계에서 수식 조각이 남지 않게).
  - 2단계 제목마다 새 쪽에서 시작하고(--no-section-break 로 끔), 차례를 만든다(--no-toc 로 끔).
    차례와 책갈피의 쪽 번호는 1차 인쇄의 책갈피(tagged PDF)에서 순서대로 읽는다. 제목 안 수식은 차례에서도 KaTeX로 그린다.
  - 본문은 명조(Noto Serif KR → MaruBuri → 나눔명조 → 바탕), 제목은 고딕 계열. 어절 단위 줄바꿈(keep-all)과 행두·행말 금칙(line-break: strict)을 켠다.
  - 인라인 수식은 관계 기호·목록 쉼표 뒤에서 줄을 바꾸고, 행 폭의 30%를 넘는 긴 수식은 이항 기호 뒤에서도 바꾼다(TeX의 규칙).
  - 디스플레이 수식이 행 폭을 넘치면 쉼표 → 관계 기호 → 이항 기호 순으로 줄을 바꾸고, 그래도 넘치면 그 수식만 글자를 줄인다(0.8배까지; 끊을 수 없는 덩어리가 남으면 0.6배까지).
  - 표가 행 폭을 넘치면 칸 안 수식의 줄바꿈 → 글자 줄임 → 긴 토큰의 글자 단위 줄바꿈 순으로 맞춘다.
  - 넘침이 남아도 문서 전체를 축소 인쇄하지 않는다. Chromium은 본문 폭을 넘는 요소가 하나라도 있으면 문서 전체를
    최대 1/1.5로 줄여 인쇄하므로, 본문을 감싼 상자에서 가로 넘침을 잘라(overflow-x: clip) 그 축소를 막고 넘친 요소를 보고한다.
  - 인쇄는 2단계 제목 경계의 장 조각 단위로 병렬로 하고(--jobs), PyMuPDF로 합쳐 쪽 번호·머리글을 찍고 제목 구조를 책갈피로 넣는다.
    차례는 본문 쪽 수가 정해진 뒤 따로 한 번 찍으므로 문서 전체를 두 번 인쇄하지 않는다.

종료 코드: 0 성공 / 1 변환 실패 / 2 사용·환경 오류
"""
from __future__ import annotations

import argparse
import asyncio
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
FONT_MONO = '"Cascadia Mono", "Consolas", "D2Coding", "NanumGothicCoding", "Malgun Gothic", monospace'

STATEMENT_HEAD = re.compile(r"^(정의|정리|명제|보조정리|따름정리|문제|추측|가설|관찰|예|예제|주의|참고|노트)\b")
PROOF_HEAD = re.compile(r"^(증명|.*의 증명|증명의 (요지|구조|개요))\b")

# 수식 자리표. 인라인과 디스플레이를 구별해 두어야 문단 쪼개기에서 디스플레이만 골라낼 수 있다.
PH_INLINE = "\x00MATH{}\x00"
PH_DISPLAY = "\x00DMATH{}\x00"
PH_RE = re.compile(r"\x00D?MATH(\d+)\x00")

# 유니코드 첨자·프라임 → TeX 표기 (KaTeX 글꼴에 없는 글자)
SUB_MAP = {c: str(i) for i, c in enumerate("₀₁₂₃₄₅₆₇₈₉")}
SUB_MAP.update({"₊": "+", "₋": "-", "₌": "=", "₍": "(", "₎": ")", "ₙ": "n", "ₖ": "k", "ₘ": "m", "ᵢ": "i", "ⱼ": "j"})
SUP_MAP = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
           "⁺": "+", "⁻": "-", "⁼": "=", "⁽": "(", "⁾": ")", "ⁿ": "n", "ⁱ": "i"}
SUB_RE = re.compile("[" + "".join(map(re.escape, SUB_MAP)) + "]+")
SUP_RE = re.compile("[" + "".join(map(re.escape, SUP_MAP)) + "]+")
LONG_DIGITS_RE = re.compile(r"\d{24,}")


def allow_breaks_at_commas(tex: str) -> str:
    """긴 인라인 수식에서 최상위(중괄호 밖, \\left…\\right 밖)의 「, 」 뒤에 줄바꿈 기회를 둔다.
    KaTeX는 \\allowbreak 자리에서 base 조각을 나누고, 인쇄 단계가 그 자리를 끊을 수 있는 자리로 쓴다."""
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
    """KaTeX가 그리지 못하는 유니코드 글자를 TeX 표기로 바꾸고, 긴 수식에 줄바꿈 기회를 둔다."""
    if not display and len(tex) >= 30 and "," in tex:
        tex = allow_breaks_at_commas(tex)
    tex = SUB_RE.sub(lambda m: "_{" + "".join(SUB_MAP[c] for c in m.group(0)) + "}", tex)
    tex = SUP_RE.sub(lambda m: "^{" + "".join(SUP_MAP[c] for c in m.group(0)) + "}", tex)
    tex = tex.replace("′", "'").replace("″", "''").replace("‴", "'''")
    tex = tex.replace("−", "-")  # U+2212 minus
    tex = tex.replace("–", r"\text{–}").replace("—", r"\text{—}")  # 줄표는 글자로 둔다
    # 24자리 이상의 숫자열(정확 정수 계산 결과)은 어디서도 끊을 수 없어 행을 넘친다. 열 자리마다 줄바꿈 기회를 둔다.
    tex = LONG_DIGITS_RE.sub(lambda m: "\\allowbreak ".join(m.group(0)[i:i + 10] for i in range(0, len(m.group(0)), 10)), tex)
    # \tag{...}의 인자는 글 모드다. 첨자·명령이 들어 있으면 수식 모드로 감싼다 (\tag{R_0} → \tag{$R_0$})
    tex = re.sub(r"\\tag\{((?:[^{}]|\{[^{}]*\})*)\}",
                 lambda m: m.group(0) if not re.search(r"[_^\\]", m.group(1)) or m.group(1).startswith("$")
                 else r"\tag{$" + m.group(1) + "$}", tex)
    return tex


# TeX → 읽을 수 있는 글자(차례의 검색 열쇠와 PDF 책갈피용. 정확한 조판이 아니라 알아볼 수 있는 근사다)
_TEX_SYMBOLS = {
    "le": "≤", "ge": "≥", "leq": "≤", "geq": "≥", "ne": "≠", "neq": "≠", "ll": "≪", "gg": "≫", "approx": "≈", "sim": "∼",
    "to": "→", "rightarrow": "→", "leftarrow": "←", "Rightarrow": "⇒", "Leftrightarrow": "⇔", "mapsto": "↦",
    "in": "∈", "notin": "∉", "subset": "⊂", "subseteq": "⊆", "cup": "∪", "cap": "∩", "setminus": "∖", "emptyset": "∅",
    "cdot": "·", "times": "×", "pm": "±", "mp": "∓", "ast": "∗", "star": "⋆", "circ": "∘", "infty": "∞", "partial": "∂",
    "sum": "∑", "prod": "∏", "int": "∫", "sqrt": "√", "ell": "ℓ", "hbar": "ℏ", "nabla": "∇", "forall": "∀", "exists": "∃",
    "sharp": "♯", "flat": "♭", "natural": "♮", "dagger": "†", "ddagger": "‡", "prime": "′", "lfloor": "⌊", "rfloor": "⌋",
    "lceil": "⌈", "rceil": "⌉", "langle": "⟨", "rangle": "⟩", "mid": "|", "vert": "|", "colon": ":", "ldots": "…", "cdots": "…", "dots": "…",
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ",
    "vartheta": "ϑ", "iota": "ι", "kappa": "κ", "varkappa": "ϰ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "varpi": "ϖ",
    "rho": "ρ", "varrho": "ϱ", "sigma": "σ", "varsigma": "ς", "tau": "τ", "upsilon": "υ", "phi": "φ", "varphi": "φ", "chi": "χ",
    "psi": "ψ", "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ", "Pi": "Π", "Sigma": "Σ",
    "Upsilon": "Υ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
_TEX_WRAPPERS = ("mathsf", "mathrm", "mathbf", "mathit", "mathcal", "mathfrak", "mathbb", "mathscr", "boldsymbol", "operatorname",
                 "text", "textrm", "textbf", "textit", "tilde", "hat", "bar", "vec", "dot", "overline", "underline", "widetilde", "widehat")


def tex_to_plain(tex: str) -> str:
    """수식 TeX를 알아볼 수 있는 글자열로 근사한다 (\\mathsf W^\\sharp → W♯, n\\le6 → n≤6)."""
    s = tex
    for _ in range(6):   # 중첩 인자를 안쪽부터 푼다
        new = re.sub(r"\\(" + "|".join(_TEX_WRAPPERS) + r")\s*\{([^{}]*)\}", r"\2", s)
        new = re.sub(r"\\(" + "|".join(_TEX_WRAPPERS) + r")\s+([A-Za-z0-9])", r"\2", new)
        if new == s:
            break
        s = new
    s = re.sub(r"\\([A-Za-z]+)", lambda m: _TEX_SYMBOLS.get(m.group(1), m.group(1)), s)
    s = re.sub(r"\\([,;:!]|quad|qquad)", " ", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"^\1", s)
    s = re.sub(r"_\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"_([A-Za-z0-9])", r"\1", s)
    s = s.replace("{", "").replace("}", "").replace("\\", "")
    return re.sub(r"\s+", " ", s).strip()


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
  const base = { displayMode: !!it.display, strict, trust: false, output: 'html', errorColor: '#b00020' };
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


# 인라인 수식과 그 양옆 글자의 결합. Chromium은 inline-block(수식 묶음 .vr-grp) 앞뒤에서는 이웃 글자가 쉼표·닫는 괄호·여는 괄호여도
# 줄을 바꾼다(글자 사이라면 금칙 규칙이 막는 자리다). 단어 결합자(U+2060)도, 바깥을 감싼 white-space: nowrap도 그 자리에는
# 듣지 않는다(묶음의 부모인 .katex가 normal이어서다). 그래서 「$x$, $y$」의 쉼표나 「…$x$」」의 닫는 따옴표, 「$x$이다」의 조사가
# 다음 줄 머리에 홀로 오고, 「($x$」의 여는 괄호가 줄 끝에 홀로 남는 일이 있었다.
# 여기서는 여는 괄호 + 수식 + 뒤에 붙은 한글·닫는 구두점을 .nb로 감싸 표시만 하고, 인쇄 단계(FIT_JS 6)가 그 글자들을
# 첫·마지막 묶음(.vr-grp, nowrap) 안으로 옮겨 붙인다. 묶음 사이의 줄바꿈 자리는 그대로 남는다.
_GLUE_RE = re.compile(r"([([「『{]?)\x00MATH(\d+)\x00([가-힣,.;:)\]」』?!%]*)")


_TEXT_SEG = re.compile(r"(<code>.*?</code>|<[^>]+>)|([^<]+)", re.S)


def tighten_quotes(body: str) -> str:
    """본문 글자의 전각 낫표 「『를 .qo로, 」』를 .qc로 감싼다(태그·코드 안은 건드리지 않는다)."""
    def seg(m):
        if m.group(1) is not None:
            return m.group(1)
        t = m.group(2)
        if "「" not in t and "」" not in t and "『" not in t and "』" not in t:
            return t
        t = re.sub(r"[「『]", lambda q: f'<span class="qo">{q.group(0)}</span>', t)
        return re.sub(r"[」』]", lambda q: f'<span class="qc">{q.group(0)}</span>', t)
    return _TEXT_SEG.sub(seg, body)


def substitute_math(s: str, rendered: list[str]) -> str:
    def glue(m):
        pre, idx, post = m.group(1), int(m.group(2)), m.group(3)
        out = rendered[idx]
        if pre or post:
            out = f'<span class="nb">{pre}{out}{post}</span>'
        return out
    s = _GLUE_RE.sub(glue, s)
    return PH_RE.sub(lambda m: rendered[int(m.group(1))], s)   # 남은 것(디스플레이 수식)


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
    # 그래야 정리 진술 문단이 디스플레이 수식을 품은 채 한 블록으로 남는다(블록 구조는 decorate가 다시 짠다).
    md.use(dollarmath_plugin, allow_space=True, allow_digits=True, double_inline=True)
    md.use(footnote_plugin)

    def math_inline(self, tokens, idx, options, env):
        env["math"].append((normalize_tex(tokens[idx].content), False))
        return PH_INLINE.format(len(env["math"]) - 1)

    def math_display(self, tokens, idx, options, env):
        env["math"].append((normalize_tex(tokens[idx].content.strip(), display=True), True))
        return PH_DISPLAY.format(len(env["math"]) - 1) + "\n"

    md.add_render_rule("math_inline", math_inline)
    md.add_render_rule("math_inline_double", math_display)
    md.add_render_rule("math_block", math_display)
    return md


def heading_parts(md, inline_token, env) -> tuple[str, str, str]:
    """제목 인라인 토큰에서 (읽을 글자, 검색 열쇠, HTML)을 뽑는다.
    읽을 글자는 책갈피·검색용으로 수식을 근사 글자로 바꾼 것이고, 열쇠는 첫 수식 앞까지의 글자다.
    HTML은 차례에 넣을 것으로, 수식 자리표를 그대로 품는다(수식 렌더링 뒤 본문과 함께 치환한다)."""
    parts, key, seen_math = [], [], False
    for c in inline_token.children or []:
        if c.type in ("text", "code_inline"):
            parts.append(c.content)
            if not seen_math:
                key.append(c.content)
        elif c.type == "math_inline":
            parts.append(tex_to_plain(c.content))
            seen_math = True
        elif c.type == "softbreak":
            parts.append(" ")
            if not seen_math:
                key.append(" ")
    text = re.sub(r"\s+", " ", "".join(parts)).strip()
    k = re.sub(r"\s+", " ", "".join(key)).strip()
    html_ = md.renderer.renderInline(inline_token.children or [], md.options, env)
    return text, (k if len(k) >= 4 else text), html_


def escape_stray_asterisks(text: str) -> str:
    """강조 쌍(`*제목*`)을 이루지 않는 별표 하나를 `\\*`로 바꾼다.

    CommonMark는 글자 사이의 `*`(`V*다`, `(V*)`, `H*)`)도 강조 여닫이로 보므로, 본문 전체가 <em>으로 묶이거나
    `*Analytic Combinatorics*,`처럼 올바른 강조가 깨진다. 문단마다 여는 별표(앞이 공백·여는 괄호)와 닫는 별표(뒤가
    공백·구두점·여는 괄호)를 순서대로 짝지어 쌍은 남기고, 짝이 없는 별표는 모두 이스케이프한다.
    수식(`$…$`, `$$…$$`)과 코드(`` `…` ``) 안은 건드리지 않는다. `**`는 대상이 아니다.
    """
    protected = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$|`[^`\n]+`", re.S)
    single = re.compile(r"(?<![\\*])\*(?!\*)")
    opener_prev = set(" \t\n([「『\"'“‘")
    closer_next = set(" \t\n,.;:)]」』\"'”’?!(")

    def fix_paragraph(par: str) -> str:
        # 보호 구간을 자리표로 바꾼 뒤 별표를 판정하고, 마지막에 되돌린다
        saved: list[str] = []
        def stash(m):
            saved.append(m.group(0)); return f"\x01{len(saved) - 1}\x01"
        s = protected.sub(stash, par)
        cands = [m.start() for m in single.finditer(s)]
        if not cands:
            return par
        escape: set[int] = set()
        open_at = None
        for i in cands:
            prev = s[i - 1] if i > 0 else "\n"
            nxt = s[i + 1] if i + 1 < len(s) else "\n"
            is_open = prev in opener_prev and not nxt.isspace() and nxt != "\x01"
            is_close = not prev.isspace() and prev != "\x01" and nxt in closer_next
            if open_at is None:
                if is_open:
                    open_at = i
                else:
                    escape.add(i)
            else:
                if is_close:
                    open_at = None
                elif is_open:
                    escape.add(open_at); open_at = i
                else:
                    escape.add(i)
        if open_at is not None:
            escape.add(open_at)
        if escape:
            s = "".join(("\\*" if j in escape else ch) for j, ch in enumerate(s))
        return re.sub(r"\x01(\d+)\x01", lambda m: saved[int(m.group(1))], s)

    return "\n\n".join(fix_paragraph(p) for p in text.split("\n\n"))


def escape_pipes_in_table_math(text: str) -> str:
    r"""표 행(`|`로 시작하는 줄)의 수식 안 `|`(절댓값 기호)를 `\|`로 바꾼다. 그대로 두면 표 파서가 칸 경계로 읽어
    수식이 갈라지고 TeX 원문이 그대로 찍힌다. markdown-it은 칸 안의 `\|`를 `|`로 되돌린다."""
    out = []
    for line in text.split('\n'):
        if line.startswith("|") and "$" in line:
            line = re.sub(r"\$[^$]+?\$", lambda m: m.group(0).replace('\\|', "|").replace("|", '\\|'), line)
        out.append(line)
    return '\n'.join(out)


def convert_markdown(md, text: str, env: dict) -> tuple[str, str, list[dict]]:
    """본문 HTML, 제목, 차례 항목을 돌려준다."""
    tokens = md.parse(text, env)
    title = ""
    headings: list[dict] = []
    thm_starts: list[int] = []
    n = 0
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.type == "heading_open":
            inline = tokens[i + 1]
            level = int(t.tag[1])
            txt, key, html_ = heading_parts(md, inline, env)
            if level == 1 and not title:
                title = txt
                # 제목은 머리 블록에서 따로 그리므로 본문에서 뺀다
                del tokens[i:i + 3]
                continue
            n += 1
            hid = f"sec-{n}"
            t.attrSet("id", hid)
            headings.append({"level": level, "text": txt, "key": key, "html": html_, "id": hid})
        elif t.type == "paragraph_open" and i + 1 < len(tokens) and tokens[i + 1].type == "inline":
            ch = [c for c in (tokens[i + 1].children or []) if not (c.type == "text" and c.content == "")]
            if len(ch) >= 2 and ch[0].type == "strong_open" and ch[1].type == "text":
                head = ch[1].content.strip()
                # 「정리 2.32의 증명.」은 증명이지 진술이 아니므로 증명 판정을 먼저 한다. 다만 지위 표지 [증명됨; …]가 붙은 머리는
                # 제목에 「…의 증명 구조」가 들어 있어도 진술이다.
                if PROOF_HEAD.match(head) and not (STATEMENT_HEAD.match(head) and "[" in head):
                    t.attrJoin("class", "proof")
                elif STATEMENT_HEAD.match(head):
                    t.attrJoin("class", "thm")
                    thm_starts.append(i)
        i += 1
    wrap_statement_blocks(tokens, thm_starts)
    body = md.renderer.render(tokens, md.options, env)
    return body, title, headings


# 진술 문단 뒤에 빈 줄로 떨어져 이어지는 항목 문단의 머리: (가)(나)…, (ㄱ)(ㄴ)…, (i)(ii)…, (a)(b)…, (1)(2)…, (A)(A⁺)…
ITEM_HEAD = re.compile(r"^\((?:[가-힣]|[ㄱ-ㅎ]|[ivx]+|[a-z]|\d+|[A-Z][′'⁺+*♯♭]*)\)")


def wrap_statement_blocks(tokens, thm_starts: list[int]) -> None:
    """진술 문단(paragraph_open에 class thm)에 이어지는 항목 문단과 디스플레이 수식을 <div class="thmblk">로 감싼다.
    원고는 긴 진술의 항목을 빈 줄로 나눈 별도 문단으로 적으므로, 문단마다 꾸미면 세로선이 머리 문단만 감싸고
    항목들은 선 밖의 보통 문단으로 보인다. 진술이 아닌 문단(증명, 설명)이 나오면 거기서 블록을 닫는다."""
    from markdown_it.token import Token

    def is_item_paragraph(j: int) -> bool:
        if tokens[j].type != "paragraph_open" or tokens[j].attrGet("class"):
            return False
        inline = tokens[j + 1]
        ch = [c for c in (inline.children or []) if not (c.type == "text" and c.content == "")]
        return bool(ch) and ch[0].type == "text" and bool(ITEM_HEAD.match(ch[0].content.lstrip()))

    inserts: list[tuple[int, str]] = []   # (토큰 위치, html)
    for start in thm_starts:
        j = start
        while tokens[j].type != "paragraph_close":
            j += 1
        end = j + 1                       # 블록 끝(배타). 진술 문단 바로 뒤부터 이어 붙일 수 있는 것을 센다
        k = end
        while k < len(tokens):
            if tokens[k].type == "math_block":
                k += 1
                end = k
                continue
            if is_item_paragraph(k):
                while tokens[k].type != "paragraph_close":
                    k += 1
                k += 1
                end = k
                continue
            break
        if end > j + 1:
            inserts.append((start, '<div class="thmblk">'))
            inserts.append((end, "</div>"))
    for pos, html_ in sorted(inserts, key=lambda t: t[0], reverse=True):
        tok = Token("html_block", "", 0)
        tok.content = html_ + "\n"
        tok.block = True
        tokens.insert(pos, tok)


def decorate(body: str) -> str:
    """정리 블록의 지위 표지 [..]를 꼬리표로, 문단 끝 ∎를 마지막 문장 뒤로 바꾸고,
    문단 한가운데의 디스플레이 수식을 독립 블록으로 떼어 낸다."""
    def tag_in_head(m):
        inner = re.sub(r"\[([^\]]+)\]", r'<span class="tag">[\1]</span>', m.group(2))
        return m.group(1) + inner + m.group(3)
    body = re.sub(r'(<p class="thm"><strong>)(.*?)(</strong>)', tag_in_head, body, flags=re.S)
    body = re.sub(r"\s*∎\s*</p>", '<span class="qed">∎</span></p>', body)
    # 강조: 한글이 든 강조는 드러냄표(점), 로마자뿐인 강조(서양 문헌 제목 등)는 기울임으로 그린다
    body = re.sub(r"<em>(.*?)</em>",
                  lambda m: m.group(0) if re.search(r"[가-힣]", m.group(1)) else f'<em class="lat">{m.group(1)}</em>', body, flags=re.S)

    def split_display(m):
        # <p>글 $$수식$$ 글</p> → <div class="para"><p>글</p><div class="dmath">수식</div><p>글</p></div>
        # 디스플레이 수식이 문단(인라인 서식 문맥) 안의 익명 블록으로 남으면 쪽 경계에서 Chromium이 수식 조각(첨자 글자,
        # 괄호)을 앞 쪽 아래 여백에 남기는 일이 있었다. 블록 구조로 바꾸면 수식 블록 전체가 함께 넘어간다.
        attrs, inner = m.group(1), m.group(2)
        if "\x00DMATH" not in inner:
            return m.group(0)
        cls = re.search(r'class="([^"]*)"', attrs)
        cls = (" " + cls.group(1)) if cls else ""
        pieces = re.split(r"(\x00DMATH\d+\x00)\n?", inner)
        out = [f'<div class="para{cls}">']
        for piece in pieces:
            if piece.startswith("\x00DMATH"):
                out.append(f'<div class="dmath">{piece}</div>')
            elif piece.strip():
                out.append(f"<p>{piece.strip()}</p>")
        out.append("</div>")
        return "".join(out)
    body = re.sub(r"<p((?:\s[^>]*)?)>(.*?)</p>", split_display, body, flags=re.S)

    # 코드 안의 긴 토큰(폴더 해시, 경로; 공백 없이 24자 이상)에는 20자마다 줄바꿈 기회(<wbr>)를 둔다. 표 칸이 좁을 때
    # 글자 단위(anywhere)로 쪼개지면 열이 한두 글자 폭으로 줄어 수십 줄이 되므로, 최소 폭을 20자로 잡아 두세 줄에서 끝나게 한다.
    def wbr_code(m):
        inner = re.sub(r"\S{24,}", lambda t: "<wbr>".join(t.group(0)[i:i + 20] for i in range(0, len(t.group(0)), 20)), m.group(2))
        return m.group(1) + inner + m.group(3)
    body = re.sub(r"(<code>)([^<]*)(</code>)", wbr_code, body)

    # 코드(경로·파일 이름)가 글자의 40%를 넘는 문단은 양끝 맞춤을 끈다. 끊을 수 없는 긴 토큰 사이가 크게 벌어지기 때문이다.
    def ragged_codey(m):
        attrs, inner = m.group(1), m.group(2)
        code_len = sum(len(re.sub(r"<[^>]+>", "", c)) for c in re.findall(r"<code>(.*?)</code>", inner, flags=re.S))
        text_len = len(re.sub(r"<[^>]+>", "", inner))
        if text_len and code_len / text_len > 0.4:
            attrs = re.sub(r'class="([^"]*)"', r'class=" ragged"', attrs) if 'class="' in attrs else attrs + ' class="ragged"'
        return f"<p{attrs}>{inner}</p>"
    body = re.sub(r"<p((?:\s[^>]*)?)>(.*?)</p>", ragged_codey, body, flags=re.S)

    def short_cell(m):
        # 수식 자리표시자가 없고 글자 수가 짧은 표 칸은 nowrap으로 둔다(식별자 r81e7051, 시각 11-05 15:55 등).
        tag, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "\x00" in inner:
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
/* 본문 글꼴에 없는 기호(위·아래 첨자 글자, ♭♯♮, ‴, ⋆, ∎, ⌈⌉, ⟺, ℓ, 수학 글자체)는 한 글꼴에서 가져온다.
   글꼴마다 다른 대체 글리프로 튀어 「P⁺ ⁺」처럼 벌어지거나 모양이 어긋나던 것을 막는다. */
@font-face { font-family: "md2pdf-sym"; src: local("Cambria Math"), local("CambriaMath"), local("Segoe UI Symbol");
  unicode-range: U+2070-209F, U+2034, U+2113, U+220E, U+22C6, U+2308-230B, U+27F5-27FF, U+1D400-1D7FF; }
@font-face { font-family: "md2pdf-sym"; src: local("Segoe UI Symbol"), local("SegoeUISymbol"), local("Cambria Math");
  unicode-range: U+266D-266F; }
html { font-size: var(--fs); }
body {
  margin: 0; color: var(--ink);
  font-family: var(--body); font-size: 1rem; line-height: var(--lh);
  word-break: ${word_break}; line-break: strict; overflow-wrap: anywhere;
  text-align: ${align}; hyphens: manual;
  font-kerning: normal; font-variant-ligatures: common-ligatures;
  text-rendering: optimizeLegibility;
  -webkit-print-color-adjust: exact; print-color-adjust: exact;
}
/* 본문 폭을 넘는 요소가 하나라도 있으면 Chromium은 문서 전체를 최대 1/1.5로 줄여 인쇄한다(글자가 작아지고 쪽수가 준다).
   가로 넘침을 여기서 잘라 그 축소를 막는다. 넘친 요소는 인쇄 단계가 따로 보고한다. */
#sheet { overflow-x: clip; overflow-clip-margin: 6px; }   /* 클립 여유: 줄 끝 이탤릭 글자의 삐침이 잘리지 않게 */
p { margin: 0 0 0.65em; orphans: 2; widows: 2; }
p.ragged { text-align: left; }   /* 코드(경로)가 대부분인 문단 */
strong { font-weight: 700; }
em { font-style: normal; text-emphasis: filled dot; -webkit-text-emphasis: filled dot; }  /* 한글은 기울임 대신 드러냄표 */
em.lat, em:lang(en) { font-style: italic; text-emphasis: none; -webkit-text-emphasis: none; font-family: "md2pdf-sym", "Times New Roman", "Noto Serif", var(--body); }  /* 로마자뿐인 강조(문헌 제목)는 기울임. 한글 글꼴에는 이탤릭이 없어 합성 기울임이 되므로 참 이탤릭이 있는 글꼴로 */
/* 전각 낫표 「」『』는 글리프의 안쪽 절반이 비어 「 순열 」처럼 보인다. text-spacing-trim은 이 글꼴(halt 특성 없음)에 듣지 않으므로 여백을 직접 줄인다 */
.qo { margin-right: -0.38em; }
.qc { margin-left: -0.38em; }
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
nav.toc .t { flex: 0 1 auto; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }  /* 긴 제목은 줄임표로 자른다 */
nav.toc .dots { flex: 1; border-bottom: 1px dotted #999; margin: 0 0.4em 0.35em; min-width: 1em; }
nav.toc .pg { flex: none; white-space: nowrap; font-variant-numeric: tabular-nums; }  /* 쪽 번호가 두 줄로 쪼개지지 않게 */
nav.toc .katex { font-size: 1em; white-space: nowrap; }
nav.toc .katex .vr-grp, nav.toc .base { white-space: nowrap; }

/* 정리·증명 블록. 문단 안 디스플레이 수식을 떼어 낸 뒤에는 div.para(.thm/.proof) 안에 p와 div.dmath가 이어진다 */
.para { margin: 0 0 0.65em; }
.para > p { margin: 0; }
.dmath { break-inside: avoid; }
.thm { margin: 0.9em 0 0.9em; padding: 0.15em 0 0.15em 0.9em; border-left: 2.5px solid #333; break-inside: avoid; }
/* 항목 문단·디스플레이 수식까지 이어지는 긴 진술은 .thmblk가 블록 전체를 감싸고 세로선을 그린다. 안의 .thm은 선을 다시 긋지 않는다 */
.thmblk { margin: 0.9em 0 0.9em; padding: 0.15em 0 0.15em 0.9em; border-left: 2.5px solid #333; break-inside: avoid; }
.thmblk .thm { margin: 0; padding: 0; border-left: 0; break-inside: auto; }
.thmblk > p, .thmblk > .para { margin: 0.35em 0 0; }
.thmblk > .katex-display { margin: 0.6em 0 0.6em; }
.thm > strong:first-child, .thm > p:first-child > strong:first-child { font-family: var(--head); font-weight: 700; }
.thm .tag { font-family: var(--head); font-weight: 400; font-size: 0.82em; color: var(--muted); margin-left: 0.15em; }
.proof { margin: 0.6em 0 0.9em; }
.proof > strong:first-child, .proof > p:first-child > strong:first-child { font-family: var(--head); font-weight: 700; }
.qed { margin-left: 0.45em; white-space: nowrap; }  /* 증명 끝 표시는 마지막 문장 바로 뒤에 둔다(오른쪽 끝으로 띄우지 않는다) */

/* 표 */
table { border-collapse: collapse; margin: 1em auto 1.3em; font-size: 0.9em; line-height: 1.5; max-width: 100%; }
thead { display: table-header-group; break-after: avoid; }   /* 머리행은 쪽마다 반복되고, 머리행만 앞 쪽에 남지 않는다 */
th, td { padding: 0.3em 0.6em; vertical-align: top; text-align: left; border: 0; overflow-wrap: normal; }  /* 본문의 anywhere를 끄면 끊을 수 없는 토큰(식별자 등)이 열의 최소 폭이 되어 글자 단위로 쪼개지지 않는다 */
td.nw, th.nw { white-space: nowrap; }  /* 짧은 칸(식별자·시각)은 칸 안에서 줄을 바꾸지 않는다 */
th { font-family: var(--head); font-weight: 700; border-top: 1.5px solid #222; border-bottom: 1px solid #222; }
tbody tr:last-child td { border-bottom: 1.5px solid #222; }
tr { break-inside: avoid; }
td code, th code { background: none; padding: 0; font-size: 0.95em; }

/* 수식 (KaTeX) */
.katex { font-size: ${math_scale}; white-space: normal; }  /* 인쇄 단계(FIT_JS)가 base 조각을 묶음(.vr-grp)으로 감싸 허용한 자리에서만 줄바꿈되게 한다 */
.vr-grp { display: inline-block; white-space: nowrap; }
.katex .glue { font-family: var(--body); font-size: ${glue_size}; }   /* 수식 묶음 안으로 옮겨 붙인 본문 글자(조사·구두점·여는 괄호) */
.katex-display { margin: 0.8em 0 1em; break-inside: avoid; }
.katex-display .katex { white-space: nowrap; }                /* 디스플레이 수식은 한 줄이 기본. 넘치면 인쇄 단계가 줄바꿈·글자 크기 축소로 맞춘다 */
.katex-display > .katex > .katex-html { display: flow-root; }                                    /* 식 번호 float를 식 블록 안에 가둔다(자리가 없어 아래로 내려가도 다음 문단과 겹치지 않게) */
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
  // KaTeX는 최상위 관계 기호(mrel)·이항 기호(mbin)·\allowbreak 뒤에서 식을 .base 조각으로 나눈다(TeXbook p.173의 규칙).
  // .base는 inline-block이라 .katex가 white-space: normal이면 조각 사이 어디서나 줄이 바뀐다. 그래서 조각들을 묶음
  // (.vr-grp, inline-block·nowrap)으로 감싸고, 허용한 종류의 자리 뒤에서만 묶음을 끊는다.
  const isBase = n => n.nodeType === 1 && n.classList.contains('base');
  // 이 base 뒤의 자리 종류: 'rel' | 'bin' | 'allow'(\allowbreak, 목록 쉼표·긴 숫자열) | 'punct'(splitAtPunct가 가른 쉼표) | null
  const kindAfter = b => {
    if (b.dataset.punctEnd === '1') return 'punct';
    if (b.dataset.relEnd === '1') return 'rel';
    const kids = Array.from(b.children);
    for (let i = kids.length - 1; i >= 0; i--) {
      const c = kids[i].classList;
      if (c.contains('strut') || c.contains('mspace')) continue;   // 연산자 뒤 글루는 같은 base에 붙는다
      if (c.contains('mrel')) return 'rel';
      if (c.contains('mbin')) return 'bin';
      if (c.contains('allowbreak')) return 'allow';
      return null;
    }
    return null;
  };
  // 괄호 깊이. 「Pr(β > j)」의 >나 「Lc(Y, r)」의 쉼표처럼 괄호 안의 자리에서는 줄을 바꾸지 않는다(TeX은 바꾸지만 읽기 나쁘다).
  // KaTeX의 ( ) [ ]는 base의 자식 mopen/mclose로 나란히 놓이고, \left…\right는 minner로 감싸여 자식에 안 보인다.
  // KaTeX는 이웃한 같은 종류의 기호를 한 span으로 합치므로("))" → mclose 하나) 괄호는 글자 수로 센다.
  const nBr = c => (c.textContent || '').replace(/\s/g, '').length || 1;
  const markDepth = kh => {
    let depth = 0;
    for (const b of Array.from(kh.children).filter(isBase)) {
      for (const c of b.children) {
        if (c.classList.contains('mopen')) depth += nBr(c);
        else if (c.classList.contains('mclose')) depth = Math.max(0, depth - nBr(c));
      }
      b.dataset.depth = String(depth);
    }
  };
  const regroup = (kh, allowed) => {
    for (const g of Array.from(kh.querySelectorAll(':scope > .vr-grp'))) { while (g.firstChild) kh.insertBefore(g.firstChild, g); g.remove(); }
    markDepth(kh);
    let grp = null;
    for (const node of Array.from(kh.childNodes)) {
      if (!isBase(node)) { grp = null; continue; }
      if (!grp) { grp = document.createElement('span'); grp.className = 'vr-grp'; kh.insertBefore(grp, node); }
      grp.appendChild(node);
      if (allowed.has('any') || ((allowed.has('deep') || node.dataset.depth === '0') && allowed.has(kindAfter(node)))) grp = null;
    }
  };
  const maxGroup = kh => Math.max(0, ...Array.from(kh.querySelectorAll(':scope > .vr-grp')).map(g => g.getBoundingClientRect().width));
  const totalWidth = kh => Array.from(kh.querySelectorAll(':scope > .vr-grp')).reduce((s, g) => s + g.getBoundingClientRect().width, 0);
  // 최상위 쉼표(목록 구분) 뒤에서 base를 둘로 갈라 끊을 수 있는 자리로 표시한다(.base는 nowrap·min-content라 안에서는 못 끊는다).
  const splitAtPunct = (kh, anyDepth) => {
    if (kh.dataset.punctSplit === (anyDepth ? '2' : '1') || kh.dataset.punctSplit === '2') return;
    kh.dataset.punctSplit = anyDepth ? '2' : '1';
    for (const g of Array.from(kh.querySelectorAll(':scope > .vr-grp'))) { while (g.firstChild) kh.insertBefore(g.firstChild, g); g.remove(); }
    for (const base of Array.from(kh.children).filter(isBase)) {
      let cur = base;
      // 괄호 밖(깊이 0)의 쉼표만 고른다
      const puncts = []; let depth = 0;
      for (const c of Array.from(base.children)) {
        if (c.classList.contains('mopen')) depth += nBr(c);
        else if (c.classList.contains('mclose')) depth = Math.max(0, depth - nBr(c));
        else if (c.classList.contains('mpunct') && (depth === 0 || anyDepth)) puncts.push(c);
      }
      for (const p of puncts) {
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
  // 디스플레이 수식: 줄을 바꿀 때 관계 기호(=, ≤)는 줄 끝이 아니라 다음 줄 머리에 둔다(amsmath의 관례). KaTeX의 base 조각은
  // 관계 기호로 끝나므로 그 기호(와 뒤 공백)를 다음 base 머리로 옮기고, 앞 base에 「관계 자리」 표지를 남긴다.
  const relToNextLine = kh => {
    if (kh.dataset.relMoved === '1') return;
    kh.dataset.relMoved = '1';
    const bases = Array.from(kh.children).filter(isBase);
    for (let i = 0; i < bases.length - 1; i++) {
      const kids = Array.from(bases[i].children);
      let j = kids.length - 1;
      while (j >= 0 && (kids[j].classList.contains('strut') || kids[j].classList.contains('mspace'))) j--;
      if (j < 0 || !kids[j].classList.contains('mrel')) continue;
      if (i === 0 && bases[i].getBoundingClientRect().width < 90) continue;   // 「k̄e :=」처럼 짧은 좌변은 관계 기호와 함께 첫 줄에 둔다
      const next = bases[i + 1];
      const strut = next.querySelector(':scope > .strut');
      const anchor = strut ? strut.nextSibling : next.firstChild;
      for (const m of kids.slice(j)) next.insertBefore(m, anchor);
      if (j > 0 && kids[j - 1].classList.contains('mspace')) kids[j - 1].remove();   // 관계 기호 앞 공백은 줄 끝에 남기지 않는다
      bases[i].dataset.relEnd = '1';
    }
  };
  const S = (...a) => new Set(a);
  const still = [];
  // 1) 인라인 수식. TeX은 관계 기호·이항 기호 뒤의 줄바꿈을 벌점으로 억제해, 식을 통째로 다음 줄로 옮겨도 행간 간격이 크게
  //    나빠지지 않으면 식 안에서 끊지 않는다. Chromium은 벌점이 없어 허용한 자리마다 낱말 사이와 같은 값으로 끊으므로,
  //    짧은 식까지 「d_i =」/「pos_i − a_i」로 갈라졌다. 그래서 행 폭의 1/5 이하인 식은 통째로 두고, 그보다 길면 관계 기호와
  //    \allowbreak(목록 쉼표, 긴 숫자열) 뒤를, 행 폭의 30%를 넘으면 이항 기호·쉼표 뒤도 연다. 한 묶음이 행 폭을 넘으면 어디서나 끊는다.
  for (const kh of document.querySelectorAll('.katex-html')) {
    if (kh.closest('.katex-display') || kh.closest('table')) continue;
    const box = kh.closest('p, li, dd, blockquote, div, h1, h2, h3, h4, h5, h6') || document.body;
    const avail = box.clientWidth;
    regroup(kh, S());
    const w = totalWidth(kh);
    if (w > avail * 0.2) regroup(kh, S('rel', 'allow'));
    if (w > avail * 0.3) { splitAtPunct(kh); regroup(kh, S('rel', 'allow', 'bin', 'punct')); }
    if (maxGroup(kh) > avail) regroup(kh, S('any'));
  }
  // 2) 디스플레이 수식은 한 줄이 기본이다(CSS nowrap). 넘치면 쉼표 → 관계 기호 → 이항 기호 순으로 줄을 열고,
  //    그래도 넘치면 글자 크기를 0.8배까지 줄이고, 그래도 넘치면 어디서나 끊는다.
  for (const el of document.querySelectorAll('.katex-display')) {
    const k = el.querySelector(':scope > .katex');
    if (!k) continue;
    const kh = k.querySelector('.katex-html');
    if (!kh) continue;
    // 식 번호(.tag)는 내용 뒤에서 오른쪽으로 띄운다(float). 줄이 바뀐 식에서는 마지막 줄 끝에, 자리가 없으면 그 아래 줄에 놓인다(amsmath와 같다).
    const avail = el.clientWidth;
    const over = () => k.scrollWidth > avail + 1;
    if (!over()) continue;
    k.style.whiteSpace = 'normal';
    relToNextLine(kh);
    splitAtPunct(kh);
    for (const lv of [S('punct', 'allow'), S('punct', 'allow', 'rel'), S('punct', 'allow', 'rel', 'bin')]) {
      regroup(kh, lv);
      if (!over()) break;
    }
    let em = parseFloat(getComputedStyle(k).fontSize) / parseFloat(getComputedStyle(el).fontSize);
    let guard = 0;
    while (over() && em > 0.8 && guard++ < 12) {
      em -= 0.04; k.style.fontSize = em.toFixed(2) + 'em';
    }
    if (over()) regroup(kh, S('deep', 'punct', 'allow', 'rel', 'bin'));   // 0.8배로도 안 맞으면 괄호 안의 자리도 연다(더 줄이는 것보다 낫다)
    guard = 0;
    while (over() && em > 0.6 && guard++ < 12) {   // 끊을 수 없는 한 덩어리가 행 폭을 넘으면 잘리느니 더 줄인다
      em -= 0.04; k.style.fontSize = em.toFixed(2) + 'em';
    }
    if (over()) regroup(kh, S('any'));
    if (over()) still.push('디스플레이 수식: ' + (k.textContent || '').replace(/\s+/g, ' ').slice(0, 80));
    // 여러 줄로 갈라진 식은 amsmath multline처럼 첫 줄을 왼쪽에, 마지막 줄을 오른쪽에 맞춘다(가운데 정렬된 조각이 떠 보이지 않게).
    // 오른쪽 맞춤은 scrollWidth를 한두 px 늘리므로 맞춤 판정이 끝난 뒤에 건다.
    const grps = kh.querySelectorAll(':scope > .vr-grp');
    if (grps.length > 1 && grps[0].getBoundingClientRect().top < grps[grps.length - 1].getBoundingClientRect().top) {
      kh.style.textAlign = 'left'; kh.style.textAlignLast = 'right';
    }
  }
  // 3) 표. 칸은 overflow-wrap: normal이라 끊을 수 없는 토큰이 열의 최소 폭이 된다. 표가 본문 폭을 넘치면
  //    칸 안 수식의 줄바꿈 → 글자 줄임(0.8배까지) → 코드 토큰의 글자 단위 줄바꿈 → 모든 칸의 글자 단위 줄바꿈 순으로 맞추고,
  //    그래도 넘치면 고정 배치(fixed)로 표 상자만이라도 폭 안에 둔다.
  for (const tb of document.querySelectorAll('table')) {
    const avail = tb.parentElement.clientWidth;
    const over = () => tb.getBoundingClientRect().width > avail + 1;
    for (const kh of tb.querySelectorAll('.katex-html')) regroup(kh, S());   // 표가 폭 안에 들면 칸 안 수식은 끊지 않는다
    if (!over()) continue;
    for (const kh of tb.querySelectorAll('.katex-html')) regroup(kh, S('rel', 'allow'));
    if (!over()) continue;
    for (const kh of tb.querySelectorAll('.katex-html')) { splitAtPunct(kh); regroup(kh, S('rel', 'allow', 'bin', 'punct')); }
    let em = parseFloat(getComputedStyle(tb).fontSize) / parseFloat(getComputedStyle(tb.parentElement).fontSize);
    let guard = 0;
    while (over() && em > 0.8 && guard++ < 12) {
      em -= 0.03; tb.style.fontSize = em.toFixed(2) + 'em';
    }
    if (over()) {
      for (const c of tb.querySelectorAll('td code, th code')) c.style.overflowWrap = 'anywhere';
      tb.style.width = '100%';
    }
    if (over()) {
      for (const c of tb.querySelectorAll('td, th')) { c.style.overflowWrap = 'anywhere'; c.classList.remove('nw'); }
      for (const kh of tb.querySelectorAll('.katex-html')) { splitAtPunct(kh, true); regroup(kh, S('any')); }   // 괄호 안 쉼표(「(450, 0.548)」)에서도 끊는다
    }
    if (over()) {
      tb.style.tableLayout = 'fixed';
      still.push('표: ' + (tb.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60));
    }
  }
  // 4) 정리·정의·명제 같은 진술 블록은 표와 같이 한 쪽에 들어가면(본문 높이의 95% 이하) 쪽 사이에서 끊지 않는다. 앞 쪽 아래가
  //    비더라도 진술이 두 쪽에 갈라지는 것보다 낫다. 한 쪽을 넘는 블록만 끊는다. 증명은 짧은 것(1/3 이하)만 통째로 둔다
  //    (디스플레이 수식 .dmath는 그대로 한 덩어리다).
  const pageH = document.documentElement.clientHeight;   // 뷰포트 높이는 인쇄 쪽 높이와 다르므로 인쇄 본문 높이를 따로 받는다
  const contentH = window.__md2pdfContentHeight || pageH;
  const limit = contentH * 0.95;
  for (const el of document.querySelectorAll('.proof')) {
    if (el.getBoundingClientRect().height <= contentH / 3) el.style.breakInside = 'avoid';
  }
  // 표: 한 쪽에 들어가는 표(본문 높이의 95% 이하)는 쪽 사이에서 끊지 않는다(LaTeX의 떠다니는 표와 같다. 앞 쪽 아래가 비더라도
  // 머리행과 몇 행만 앞 쪽에 남는 것보다 낫다). 한 쪽을 넘는 표만 쪽 사이에서 끊되 머리행이 쪽마다 반복되고(thead:
  // table-header-group) 행 안에서는 끊지 않는다.
  for (const tb of document.querySelectorAll('table')) {
    if (tb.getBoundingClientRect().height <= contentH * 0.95) tb.style.breakInside = 'avoid';
  }
  for (const el of document.querySelectorAll('.thm, .thmblk')) {
    if (el.getBoundingClientRect().height > limit) el.style.breakInside = 'auto';
  }
  // 5) 그 밖에 본문 폭을 넘는 요소(긴 코드, 이미지 등)를 보고한다. #sheet가 가로 넘침을 자르므로 문서 전체 축소는 일어나지 않는다.
  const w = document.documentElement.clientWidth;
  for (const el of document.querySelectorAll('main > *, main p, main li, main pre, main img')) {
    const r = el.getBoundingClientRect();
    if (r.right > w + 1 && !el.querySelector('table, .katex-display')) {
      still.push('요소 ' + el.tagName.toLowerCase() + ': ' + (el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60));
      if (still.length > 40) break;
    }
  }
  // 6) 수식 양옆에 붙은 글자(.nb 표지: 여는 괄호, 조사·어미, 닫는 구두점)를 첫·마지막 묶음 안으로 옮긴다. 묶음은 nowrap
  //    inline-block이라 그 안에서는 줄이 바뀌지 않는다. 묶음 밖에 두면 Chromium이 inline-block 경계에서 줄을 바꿔
  //    쉼표·조사가 다음 줄 머리에, 여는 괄호가 줄 끝에 홀로 남는다. 묶음 다시 짜기(regroup)가 모두 끝난 뒤에 해야 한다.
  for (const nb of document.querySelectorAll('.nb')) {
    const k = nb.querySelector(':scope > .katex');
    const kh = k && k.querySelector('.katex-html');
    const grps = kh ? kh.querySelectorAll(':scope > .vr-grp') : [];
    if (!grps.length) continue;
    const after = []; for (let t = k.nextSibling; t; t = t.nextSibling) after.push(t);
    const before = []; for (let t = k.previousSibling; t; t = t.previousSibling) before.unshift(t);
    if (after.length) { const sp = document.createElement('span'); sp.className = 'glue'; after.forEach(n => sp.appendChild(n)); grps[grps.length - 1].appendChild(sp); }
    if (before.length) { const sp = document.createElement('span'); sp.className = 'glue'; before.forEach(n => sp.appendChild(n)); grps[0].insertBefore(sp, grps[0].firstChild); }
  }
  return still;
}
"""


def glue_size(math_scale: str) -> str:
    """수식 글자 크기(본문 대비, 예 1.08em)의 역수. 수식 묶음 안으로 옮긴 본문 글자를 본문 크기로 되돌리는 데 쓴다."""
    m = re.fullmatch(r"\s*([0-9.]+)\s*em\s*", math_scale)
    return f"{1 / float(m.group(1)):.4f}em" if m and float(m.group(1)) > 0 else "1em"


def build_html(body: str, title: str, katex_css: str, opts, headings: list[dict] | None = None,
               toc_pages: dict | None = None, with_header: bool = False) -> str:
    """HTML 문서 하나를 조립한다. with_header면 제목 블록을, headings를 주면 차례를 body 앞에 둔다."""
    toc_html = ""
    if headings is not None and opts.toc and headings:
        items = []
        for h in headings:
            if h["level"] > opts.toc_depth:
                continue
            pg = (toc_pages or {}).get(h["id"], "")
            items.append(
                f'<li class="lv{h["level"]}"><a href="#{h["id"]}"><span class="t">{h["html"]}</span>'
                f'<span class="dots"></span><span class="pg" data-for="{h["id"]}">{pg}</span></a></li>'
            )
        toc_html = f'<nav class="toc"><h2 class="toc-title">{html.escape(opts.toc_title)}</h2><ol>{"".join(items)}</ol></nav>'
    head_html = ""
    if with_header:
        sub = f'<p class="subtitle">{html.escape(opts.subtitle)}</p>' if opts.subtitle else ""
        meta = f'<p class="meta">{html.escape(opts.meta)}</p>' if opts.meta else ""
        head_html = f'<header class="title-block"><h1>{html.escape(title or opts.input.stem)}</h1>{sub}{meta}</header>\n'
    css = Template(CSS).substitute({
        "font_body": '"md2pdf-sym", ' + opts.font_body, "font_head": '"md2pdf-sym", ' + opts.font_head, "font_mono": FONT_MONO,
        "font_size": opts.font_size, "line_height": opts.line_height, "paper": opts.paper,
        "align": "left" if opts.ragged else "justify",
        "h2_break": "" if opts.no_section_break else "break-before: page;",
        "toc_break": "break-after: page;" if body.strip() else "",   # 앞부분만 찍을 때는 차례 뒤 빈 쪽이 생기지 않게
        "math_scale": opts.math_scale,
        "glue_size": glue_size(opts.math_scale),
        "word_break": opts.word_break,
    })
    return (
        '<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
        f"<title>{html.escape(title or opts.input.stem)}</title>\n"
        f'<link rel="stylesheet" href="{katex_css}">\n<style>{css}</style>\n</head>\n<body>\n<div id="sheet">\n'
        f"{head_html}{toc_html}\n<main>\n{body}\n</main>\n</div>\n</body>\n</html>\n"
    )


def split_chunks(body: str, headings: list[dict], split: bool) -> list[tuple[str, list[dict]]]:
    """본문을 2단계 제목(새 쪽에서 시작) 경계에서 장 조각으로 나눈다. 각 조각에 든 제목 목록을 함께 돌려준다.
    split이 거짓이면(--no-section-break) 조각 하나다."""
    if not split:
        return [(body, list(headings))]
    starts = [m.start() for m in re.finditer(r"<h2[\s>]", body)]
    bounds = [0] + starts + [len(body)]
    chunks = []
    for a, b in zip(bounds, bounds[1:]):
        piece = body[a:b]
        if not piece.strip():
            continue
        ids = set(re.findall(r'<h[2-6] id="(sec-\d+)"', piece))
        chunks.append((piece, [h for h in headings if h["id"] in ids]))
    return chunks


# ──────────────────────────────────────────────────────────────────────────────
# 5. HTML → PDF (Playwright, 장 단위 병렬 인쇄)
# ──────────────────────────────────────────────────────────────────────────────

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


def content_height_px(opts) -> int:
    """인쇄되는 본문 높이(쪽 높이 − 위·아래 여백)를 CSS 픽셀로 돌려준다."""
    paper = opts.paper.strip().split()
    if paper[0].lower() in _PAPER_MM:
        h_mm = {"a3": 420.0, "a4": 297.0, "a5": 210.0, "b5": 250.0, "letter": 279.4, "legal": 355.6, "tabloid": 431.8}[paper[0].lower()]
        paper_px = h_mm * 96 / 25.4
    else:
        paper_px = css_length_px(paper[1] if len(paper) > 1 else paper[0])
    return max(200, int(paper_px - css_length_px(opts.margin_top) - css_length_px(opts.margin_bottom)))


async def _launch(p, prefer: str, verbose: bool):
    order = {"auto": [None, "msedge", "chrome"], "msedge": ["msedge"], "chrome": ["chrome"], "chromium": [None]}[prefer]   # 내장 chromium이 있으면 먼저(종료가 가장 빠르다)
    last = None
    for ch in order:
        try:
            b = await (p.chromium.launch(channel=ch) if ch else p.chromium.launch())
            log(verbose, f"브라우저: {ch or 'playwright chromium'} {b.version}")
            return b
        except Exception as e:  # noqa: BLE001
            last = e
    die(2, f"브라우저를 띄우지 못했다: {last}\n  Edge/Chrome을 설치하거나 `python -m playwright install chromium`을 실행하라.")


async def _print_one(browser, sem, html_path: Path, opts, tagged: bool) -> tuple[bytes, list[str]]:
    """HTML 파일 하나를 PDF로 인쇄한다. 머리글·꼬리글은 넣지 않는다(합친 뒤 PyMuPDF로 찍는다)."""
    async with sem:
        page = await browser.new_page()
        try:
            # 뷰포트를 인쇄 본문 폭에 맞춘다. 기본 뷰포트(1280px)에서 재면 디스플레이 수식·표가 쪽에서는 넘치는데도 맞는 것으로 측정된다.
            await page.set_viewport_size({"width": content_width_px(opts), "height": 1400})
            page.set_default_timeout(600000)
            await page.goto(html_path.as_uri(), wait_until="load", timeout=600000)
            await page.evaluate("document.fonts.ready.then(() => true)")   # 쓰이는 글꼴이 모두 내려올 때까지
            await page.emulate_media(media="print")
            await page.evaluate(f"window.__md2pdfContentHeight = {content_height_px(opts)}")
            t0 = time.time()
            still = await page.evaluate(FIT_JS)
            dt_fit = time.time() - t0
            t0 = time.time()
            pdf = await page.pdf(
                prefer_css_page_size=True, print_background=True,
                margin={"top": opts.margin_top, "bottom": opts.margin_bottom, "left": opts.margin_side, "right": opts.margin_side},
                display_header_footer=False, tagged=tagged, outline=tagged,
            )
            log(opts_verbose(opts), f"  {html_path.name}: 맞춤 {dt_fit:.1f}초, 인쇄 {time.time() - t0:.1f}초")
            return pdf, still
        finally:
            await page.close()


async def _close_quietly(browser):
    """Edge 채널은 닫는 데 수십 초가 걸린다. 잠깐 기다리고 넘어간다(드라이버가 끝나며 프로세스는 정리된다)."""
    try:
        await asyncio.wait_for(browser.close(), timeout=8)
    except Exception:  # noqa: BLE001
        pass


async def _render_all(chunk_paths: list[Path], chunks, front_html, tmpd: Path, opts, verbose: bool):
    """브라우저 하나로 본문 조각들을 병렬 인쇄하고, 그 쪽 수로 차례를 채워 앞부분을 찍는다."""
    import fitz
    from playwright.async_api import async_playwright
    workers = opts.jobs if opts.jobs > 0 else max(1, min(6, (os.cpu_count() or 2)))
    async with async_playwright() as p:
        browser = await _launch(p, opts.browser, verbose)
        sem = asyncio.Semaphore(workers)
        try:
            t0 = time.time()
            results = list(await asyncio.gather(*(_print_one(browser, sem, f, opts, True) for f in chunk_paths)))
            log(verbose, f"본문 {len(chunk_paths)}조각 인쇄 {time.time() - t0:.0f}초 (동시 {workers})")
            parts, still, local_pages, offset = [], [], {}, 0
            for (pdf, st), (_, chunk_headings) in zip(results, chunks):
                n = fitz.open(stream=pdf, filetype="pdf").page_count
                for hid, pg in heading_pages_in_chunk(pdf, chunk_headings, verbose).items():
                    local_pages[hid] = offset + pg
                parts.append(pdf); still.extend(st); offset += n
            # 제목 블록과 차례. 차례의 쪽 수가 본문 쪽 번호를 밀므로, 쪽 수를 재고 그 수로 번호를 채워 다시 찍는다.
            front, front_pages, pages, guess = b"", 0, {}, 0
            for _ in range(3):
                pages = {hid: pg + guess for hid, pg in local_pages.items()}
                f = tmpd / "front.html"
                f.write_text(front_html(pages), encoding="utf-8")
                front, st = await _print_one(browser, sem, f, opts, False)
                front_pages = fitz.open(stream=front, filetype="pdf").page_count
                if front_pages == guess:
                    break
                guess = front_pages
            still.extend(st)
            log(verbose, f"제목·차례 {front_pages}쪽, 제목 {len(local_pages)}개의 쪽 확정")
            return parts, still, pages, front, front_pages
        finally:
            await _close_quietly(browser)


def opts_verbose(opts) -> bool:
    return not opts.quiet


def heading_pages_in_chunk(pdf: bytes, chunk_headings: list[dict], verbose: bool) -> dict:
    """장 조각 PDF의 책갈피(tagged)에서 제목별 쪽 번호(조각 안 1부터)를 읽는다. 개수가 맞으면 순서대로, 아니면 글자 대조·본문 검색으로."""
    import fitz
    doc = fitz.open(stream=pdf, filetype="pdf")
    pages: dict = {}
    outline = doc.get_toc(simple=True)
    norm = lambda s: re.sub(r"\s+", " ", s).strip()  # noqa: E731
    if len(outline) == len(chunk_headings) and all(outline[i][2] <= outline[i + 1][2] for i in range(len(outline) - 1)):
        for h, e in zip(chunk_headings, outline):
            pages[h["id"]] = e[2]
        return pages
    j = 0
    for h in chunk_headings:
        want, key = norm(h["text"]), norm(h["key"])
        for k in range(j, len(outline)):
            cand = norm(outline[k][1])
            if cand == want or cand.startswith(key):
                pages[h["id"]] = outline[k][2]
                j = k + 1
                break
    start = 0
    for h in chunk_headings:
        if h["id"] in pages:
            continue
        for pno in range(start, doc.page_count):
            if doc[pno].search_for(h["key"][:60]):
                pages[h["id"]] = pno + 1
                start = pno
                break
    if len(pages) < len(chunk_headings):
        log(verbose, f"  조각의 제목 {len(chunk_headings)}개 중 {len(pages)}개만 쪽을 확정했다(책갈피 {len(outline)}개)")
    return pages


def find_font_file(families: str) -> str | None:
    """CSS font-family 목록에서 앞에서부터 설치된 글꼴 파일을 찾는다(PyMuPDF가 쪽 번호·머리글을 찍을 때 쓴다)."""
    candidates = {
        "noto serif kr": ["NotoSerifKR-Regular", "NotoSerifCJKkr-Regular"], "maruburi": ["MaruBuri-Regular"],
        "nanummyeongjo": ["NanumMyeongjo"], "batang": ["batang", "HANBatang"], "noto serif cjk kr": ["NotoSerifCJKkr-Regular"],
        "noto sans kr": ["NotoSansKR-Regular", "NotoSansCJKkr-Regular"], "nanumbarungothic": ["NanumBarunGothic"],
        "malgun gothic": ["malgun"], "noto sans cjk kr": ["NotoSansCJKkr-Regular"], "nanumgothic": ["NanumGothic"],
    }
    dirs = [Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Windows" / "Fonts",
            Path("/usr/share/fonts"), Path("/usr/local/share/fonts"), Path.home() / ".fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts")]
    files: dict[str, Path] = {}
    for d in dirs:
        if d.is_dir():
            for f in d.rglob("*"):
                if f.suffix.lower() in (".ttf", ".otf"):
                    files.setdefault(f.stem.lower(), f)
    for fam in re.findall(r'"([^"]+)"|([A-Za-z][\w -]*)', families):
        name = (fam[0] or fam[1]).strip().lower()
        for stem in candidates.get(name, [name.replace(" ", "")]):
            if stem.lower() in files:
                return str(files[stem.lower()])
    return None


def assemble_pdf(parts: list[bytes], title: str, headings: list[dict], pages: dict, opts, verbose: bool) -> tuple[bytes, int]:
    """조각 PDF들을 순서대로 합치고, 쪽 번호·머리글을 찍고, 책갈피와 메타데이터를 넣는다."""
    import fitz
    doc = fitz.open()
    for part in parts:
        doc.insert_pdf(fitz.open(stream=part, filetype="pdf"))
    n = doc.page_count
    if not opts.no_page_numbers:
        body_font = find_font_file(opts.font_body)
        head_font = find_font_file(opts.font_head) or body_font
        pt = 72 / 96
        side = css_length_px(opts.margin_side) * pt
        kw = {"fontfile": body_font, "fontname": "F0"} if body_font else {"fontname": "helv"}
        kw2 = {"fontfile": head_font, "fontname": "F1"} if head_font else {"fontname": "helv"}
        measure = fitz.Font(fontfile=body_font) if body_font else fitz.Font("helv")
        measure2 = fitz.Font(fontfile=head_font) if head_font else fitz.Font("helv")
        fs, fs2 = 9 * pt, 8 * pt
        for pno in range(n):
            pg = doc[pno]
            r = pg.rect
            # 꼬리글: 쪽 번호(9px, 가운데, #555). 아래 여백의 한가운데 높이에 둔다.
            txt = str(pno + 1)
            y = r.height - css_length_px(opts.margin_bottom) * pt / 2 + fs / 2
            w = measure.text_length(txt, fontsize=fs)
            pg.insert_text((r.width / 2 - w / 2, y), txt, fontsize=fs, color=(0.33, 0.33, 0.33), **kw)
            if opts.running_head:
                # 머리글: 짧은 제목(8px, 오른쪽, #888). 위 여백의 한가운데 높이에 둔다.
                y2 = css_length_px(opts.margin_top) * pt / 2 + fs2 / 2
                w2 = measure2.text_length(opts.running_head, fontsize=fs2)
                pg.insert_text((r.width - side - w2, y2), opts.running_head, fontsize=fs2, color=(0.53, 0.53, 0.53), **kw2)
    if pages:
        toc = []
        base = min(h["level"] for h in headings) if headings else 1
        for h in headings:
            if h["id"] in pages:
                toc.append([h["level"] - base + 1, h["text"], pages[h["id"]]])
        fixed, prev = [], 0
        for lvl, txt, pg_ in toc:
            lvl = min(lvl, prev + 1)   # 책갈피 깊이는 한 번에 한 단계씩만 깊어질 수 있다
            fixed.append([lvl, txt, pg_])
            prev = lvl
        doc.set_toc(fixed)
        log(verbose, f"책갈피 {len(fixed)}개")
    doc.set_metadata({"title": title, "producer": "md2pdf (markdown-it-py · KaTeX · Chromium)", "creator": "md2pdf"})
    out = doc.tobytes(garbage=4, deflate=True)   # garbage=4: 조각마다 겹치는 글꼴·글리프 스트림을 하나로 합친다
    doc.close()
    return out, n


def link_toc(pdf: bytes, headings: list[dict], pages: dict, toc_page_count: int) -> bytes:
    """차례 줄에서 제목 글자를 찾아 그 쪽으로 가는 링크를 단다(찾은 줄만)."""
    import fitz
    doc = fitz.open(stream=pdf, filetype="pdf")
    for pno in range(min(toc_page_count, doc.page_count)):
        pg = doc[pno]
        for h in headings:
            if h["id"] not in pages or len(h["key"]) < 4:
                continue
            for rect in pg.search_for(h["key"][:40])[:1]:
                rect.x1 = pg.rect.width - rect.x0
                pg.insert_link({"kind": fitz.LINK_GOTO, "from": rect, "page": pages[h["id"]] - 1, "to": fitz.Point(0, 0)})
    out = doc.tobytes(garbage=1, deflate=True)
    doc.close()
    return out


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
    ap.add_argument("--html", type=Path, help="중간 HTML(본문 전체 한 문서)을 이 경로에 남긴다")
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
    ap.add_argument("--word-break", choices=["keep-all", "normal"], default="keep-all",
                    help="한글 줄바꿈 단위. keep-all=어절(기본), normal=글자(인쇄 관행; 수식이 많은 문단의 벌어짐을 줄인다)")
    ap.add_argument("--star-emphasis", action="store_true", help="별표 하나를 CommonMark 규칙대로 두고 짝 없는 별표를 이스케이프하지 않는다")
    ap.add_argument("--no-toc", dest="toc", action="store_false", help="차례를 만들지 않는다")
    ap.add_argument("--toc-title", default="차례")
    ap.add_argument("--toc-depth", type=int, default=3, help="차례에 넣을 제목 깊이(2=절만, 3=절·소절)")
    ap.add_argument("--no-section-break", action="store_true", help="2단계 제목마다 새 쪽에서 시작하지 않는다(장 단위 병렬 인쇄도 끈다)")
    ap.add_argument("--no-page-numbers", action="store_true")
    ap.add_argument("--jobs", type=int, default=0, help="동시에 인쇄할 장 조각 수(0=CPU 수, 최대 6)")
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
        text = escape_stray_asterisks(text)
    text = escape_pipes_in_table_math(text)
    body, title, headings = convert_markdown(md, text, env)
    body = decorate(body)
    log(verbose, f"Markdown 해석 {time.time() - t0:.1f}초, 제목 {len(headings)}개")

    # 수식 렌더링
    t0 = time.time()
    katex_dir = ensure_katex(opts.katex_dir, verbose)
    rendered, errors, warnings = render_math(env["math"], katex_dir, verbose)
    body = tighten_quotes(substitute_math(body, rendered))
    for h in headings:
        h["html"] = substitute_math(h["html"], rendered)
    katex_css = (katex_dir / "node_modules" / "katex" / "dist" / "katex.min.css").as_uri()
    log(verbose, f"수식 {len(env['math'])}개 렌더링 {time.time() - t0:.1f}초 (오류 {len(errors)}개, 경고 종류 {len(warnings)}개)")
    for e in errors[:20]:
        tex = env["math"][e["i"]][0]
        print(f"  [수식 오류] {e['msg']}\n      {tex[:120]}", file=sys.stderr)
    for k, v in list(warnings.items())[:20]:
        log(verbose, f"  [수식 경고 ×{v}] {k}")

    try:
        from playwright.async_api import async_playwright  # noqa: F401
    except ImportError:
        die(2, "playwright가 없다. 설치: pip install playwright  (브라우저는 Edge/Chrome을 쓰거나 `python -m playwright install chromium`)")
    try:
        import fitz
    except ImportError:
        die(2, "PyMuPDF가 없다. 설치: pip install pymupdf  (조각 합치기·쪽 번호·책갈피에 쓴다)")

    with tempfile.TemporaryDirectory(prefix="md2pdf-") as tmp:
        tmpd = Path(tmp)
        if opts.html:
            opts.html.parent.mkdir(parents=True, exist_ok=True)
            opts.html.write_text(build_html(body, title, katex_css, opts, headings, None, with_header=True), encoding="utf-8")
            log(verbose, f"HTML: {opts.html}")

        # 장 조각(2단계 제목 경계)을 병렬로 인쇄하고, 조각 PDF의 책갈피에서 제목 쪽을 읽은 뒤 차례를 찍는다.
        chunks = split_chunks(body, headings, split=not opts.no_section_break)
        paths = []
        for i, (piece, _) in enumerate(chunks):
            f = tmpd / f"part{i:03d}.html"
            f.write_text(build_html(piece, title, katex_css, opts), encoding="utf-8")
            paths.append(f)
        front_html = lambda pages: build_html("", title, katex_css, opts, headings if opts.toc else None, pages, with_header=True)  # noqa: E731
        parts, still, pages, front, front_pages = asyncio.run(_render_all(paths, chunks, front_html, tmpd, opts, verbose))

    pdf, n_pages = assemble_pdf([front] + parts, title or opts.input.stem, headings, pages, opts, verbose)
    if opts.toc and pages:
        pdf = link_toc(pdf, headings, pages, front_pages)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(pdf)
    for s in still[:20]:
        print(f"  [넘침] 맞춘 뒤에도 본문 폭을 넘어 잘린 요소: {s}", file=sys.stderr)
    print(f"PDF: {out} ({n_pages}쪽, {len(pdf) / 1024 / 1024:.1f} MB)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

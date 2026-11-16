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
        "font_body": opts.font_body, "font_head": opts.font_head, "font_mono": FONT_MONO,
        "font_size": opts.font_size, "line_height": opts.line_height, "paper": opts.paper,
        "align": "left" if opts.ragged else "justify",
        "h2_break": "" if opts.no_section_break else "break-before: page;",
        "toc_break": "break-after: page;",
        "math_scale": opts.math_scale,
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


async def _launch(p, prefer: str, verbose: bool):
    order = {"auto": ["msedge", "chrome", None], "msedge": ["msedge"], "chrome": ["chrome"], "chromium": [None]}[prefer]
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
            await page.wait_for_function("document.fonts.status === 'loaded'", timeout=120000)
            await page.emulate_media(media="print")
            still = await page.evaluate(FIT_JS)
            pdf = await page.pdf(
                prefer_css_page_size=True, print_background=True,
                margin={"top": opts.margin_top, "bottom": opts.margin_bottom, "left": opts.margin_side, "right": opts.margin_side},
                display_header_footer=False, tagged=tagged, outline=tagged,
            )
            return pdf, still
        finally:
            await page.close()


async def _print_all(paths: list[Path], opts, verbose: bool, tagged: bool, workers: int) -> list[tuple[bytes, list[str]]]:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await _launch(p, opts.browser, verbose)
        sem = asyncio.Semaphore(max(1, workers))
        try:
            return list(await asyncio.gather(*(_print_one(browser, sem, f, opts, tagged) for f in paths)))
        finally:
            await browser.close()


def print_many(paths: list[Path], opts, verbose: bool, tagged: bool = False) -> list[tuple[bytes, list[str]]]:
    workers = opts.jobs if opts.jobs > 0 else max(1, min(6, (os.cpu_count() or 2)))
    return asyncio.run(_print_all(paths, opts, verbose, tagged, workers))


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
        fs, fs2 = 9 * pt, 8 * pt
        for pno in range(n):
            pg = doc[pno]
            r = pg.rect
            # 꼬리글: 쪽 번호(9px, 가운데, #555). 아래 여백의 한가운데 높이에 둔다.
            txt = str(pno + 1)
            y = r.height - css_length_px(opts.margin_bottom) * pt / 2 + fs / 2
            w = fitz.get_text_length(txt, fontsize=fs, **({"fontfile": body_font} if body_font else {"fontname": "helv"}))
            pg.insert_text((r.width / 2 - w / 2, y), txt, fontsize=fs, color=(0.33, 0.33, 0.33), **kw)
            if opts.running_head:
                # 머리글: 짧은 제목(8px, 오른쪽, #888). 위 여백의 한가운데 높이에 둔다.
                y2 = css_length_px(opts.margin_top) * pt / 2 + fs2 / 2
                w2 = fitz.get_text_length(opts.running_head, fontsize=fs2, **({"fontfile": head_font} if head_font else {"fontname": "helv"}))
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
    out = doc.tobytes(garbage=3, deflate=True)
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
    body, title, headings = convert_markdown(md, text, env)
    body = decorate(body)
    log(verbose, f"Markdown 해석 {time.time() - t0:.1f}초, 제목 {len(headings)}개")

    # 수식 렌더링
    t0 = time.time()
    katex_dir = ensure_katex(opts.katex_dir, verbose)
    rendered, errors, warnings = render_math(env["math"], katex_dir, verbose)
    body = substitute_math(body, rendered)
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

        # 1) 장 조각(2단계 제목 경계)을 병렬로 인쇄한다. 조각 PDF의 책갈피에서 제목 쪽을 읽는다.
        chunks = split_chunks(body, headings, split=not opts.no_section_break)
        paths = []
        for i, (piece, _) in enumerate(chunks):
            f = tmpd / f"part{i:03d}.html"
            f.write_text(build_html(piece, title, katex_css, opts), encoding="utf-8")
            paths.append(f)
        t0 = time.time()
        results = print_many(paths, opts, verbose, tagged=True)
        log(verbose, f"본문 {len(chunks)}조각 인쇄 {time.time() - t0:.0f}초")
        parts, still, local_pages = [], [], {}
        offset = 0
        for (pdf, st), (_, chunk_headings) in zip(results, chunks):
            n = fitz.open(stream=pdf, filetype="pdf").page_count
            for hid, pg in heading_pages_in_chunk(pdf, chunk_headings, verbose).items():
                local_pages[hid] = offset + pg
            parts.append(pdf); still.extend(st); offset += n

        # 2) 제목 블록과 차례. 차례의 쪽 수가 본문 쪽 번호를 밀므로, 먼저 쪽 수를 재고 그 수로 번호를 채워 다시 찍는다.
        front, front_pages, pages = b"", 0, {}
        guess = 0
        for _ in range(3):
            pages = {hid: pg + guess for hid, pg in local_pages.items()}
            f = tmpd / "front.html"
            f.write_text(build_html("", title, katex_css, opts, headings if opts.toc else None, pages, with_header=True), encoding="utf-8")
            (front, st), = print_many([f], opts, verbose, tagged=False)
            front_pages = fitz.open(stream=front, filetype="pdf").page_count
            if front_pages == guess:
                break
            guess = front_pages
        still.extend(st)
        log(verbose, f"제목·차례 {front_pages}쪽, 제목 {len(headings)}개 중 {len(local_pages)}개의 쪽 확정")

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

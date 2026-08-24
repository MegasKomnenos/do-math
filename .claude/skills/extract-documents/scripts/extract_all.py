import sys
import gc
import re
import shutil
import subprocess
import tempfile
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRATCH_DIR = Path(tempfile.mkdtemp(prefix="extract_"))

# OCR이 필요한 페이지·이미지는 Tesseract로 직접 판독하지 않고 PNG로 렌더해
# 이 디렉토리에 남긴다. 실제 판독은 메인 에이전트가 Read 도구로 그 PNG를 읽어
# 수행한다(stdout에 남기는 플레이스홀더 [[VISION ...]]의 경로). SCRATCH_DIR와
# 달리 실행 종료 시 삭제하지 않는다. --render-dir로 위치를 지정할 수 있고,
# 지정하지 않으면 삭제하지 않는 임시 디렉토리를 만든다.
RENDER_DIR = None

# 렌더 해상도(dpi). Read 도구가 이미지를 장변 기준으로 정규화(다운샘플)하므로
# Tesseract용 고해상도(600dpi)는 불필요하다. 작은 글씨가 밀집한 문서에서
# 다운샘플로 뭉개지면 이 값을 올리거나(--dpi) 페이지 분할 렌더를 검토한다.
RENDER_DPI = 200

whisper_model = None


def init_whisper():
    global whisper_model
    if whisper_model is None:
        from faster_whisper import WhisperModel
        print("[init] faster-whisper 로딩 중...")
        whisper_model = WhisperModel("base", device="cpu", compute_type="int8")
        print("[init] faster-whisper 준비 완료")
    return whisper_model


# ── Vision 렌더: OCR 대상 페이지·이미지를 PNG로 남기고 플레이스홀더를 방출 ──

def _ensure_render_dir():
    global RENDER_DIR
    if RENDER_DIR is None:
        RENDER_DIR = Path(tempfile.mkdtemp(prefix="extract_vision_"))
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    return RENDER_DIR


def _placeholder(label, tag, png_path, note=""):
    extra = f" | {note}" if note else ""
    return f"[[VISION {label} | {tag} | {png_path}{extra}]]"


def render_page(page, basename, page_no, tag, dpi=None, note=""):
    rd = _ensure_render_dir()
    pix = page.get_pixmap(dpi=dpi or RENDER_DPI)
    out = rd / f"{basename}_p{page_no}.png"
    pix.save(str(out))
    return _placeholder(f"페이지 {page_no}", tag, out, note)


# ── 방법 1: 직접 텍스트 읽기 ──

def extract_text_file(path):
    for enc in ["utf-8", "cp949", "euc-kr", "latin-1"]:
        try:
            return path.read_text(encoding=enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return ""


# ── 좌표 기반 텍스트 재조합 ──

def _dedup_shadow_spans(spans, y_tol=4.0):
    """그림자/볼드 효과로 중복 배치된 텍스트 span 제거.

    (1) 동일 텍스트·유사 위치의 단순 그림자 복사본 제거
    (2) 넓은 span에 포함되는 좁은 sub-span 제거 (멀티레이어 그림자)
    """
    if not spans:
        return spans
    wider_first = sorted(spans, key=lambda s: (s[0], -(s[2] - s[1])))
    kept = []
    for span in wider_first:
        y, x0, x1, sz, text = span
        is_covered = False
        for k in kept:
            ky, kx0, kx1, ksz, ktext = k
            if abs(y - ky) > y_tol or abs(sz - ksz) > 2.0:
                continue
            overlap_start = max(x0, kx0)
            overlap_end = min(x1, kx1)
            span_len = x1 - x0
            if overlap_end > overlap_start and span_len > 0:
                if (overlap_end - overlap_start) / span_len > 0.5:
                    is_covered = True
                    break
        if not is_covered:
            kept.append(span)
    kept.sort(key=lambda s: (s[0], s[1]))
    return kept


def extract_page_structured(page):
    Y_TOL = 4.0
    d = page.get_text("dict")
    spans_all = []
    for block in d["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"]
                if not text.strip():
                    continue
                y_mid = (span["bbox"][1] + span["bbox"][3]) / 2
                x0, x1 = span["bbox"][0], span["bbox"][2]
                sz = span["size"]
                spans_all.append((y_mid, x0, x1, sz, text.strip()))
    if not spans_all:
        return ""
    spans_all.sort(key=lambda t: (t[0], t[1]))
    spans_all = _dedup_shadow_spans(spans_all)

    result_lines = []
    cur_y = None
    cur_spans = []
    for y, x0, x1, sz, text in spans_all:
        if cur_y is None or abs(y - cur_y) > Y_TOL:
            if cur_spans:
                result_lines.append(_merge_spans(cur_spans))
            cur_y = y
            cur_spans = [(x0, x1, sz, text)]
        else:
            cur_spans.append((x0, x1, sz, text))
    if cur_spans:
        result_lines.append(_merge_spans(cur_spans))
    return "\n".join(result_lines)


def _merge_spans(spans):
    spans.sort(key=lambda t: t[0])
    parts = []
    prev_x1 = None
    for x0, x1, sz, text in spans:
        if prev_x1 is not None:
            gap = x0 - prev_x1
            if gap > sz * 0.3:
                parts.append(" ")
            elif gap < -sz * 0.5:
                pass
        parts.append(text)
        prev_x1 = max(prev_x1 or x1, x1)
    return "".join(parts)


def _postprocess_structured(text):
    text = re.sub(r"제조(\S+?)(\d+)\(", lambda m: f"제{m.group(2)}조({m.group(1)}", text)
    text = re.sub(r"대학원생 포함의\(\)", "대학원생 포함)의", text)
    text = re.sub(r"- \d+ -\n?", "", text)
    return text.strip()


# ── 방법 2 + 3: PDF 추출 (텍스트 레이어 + 페이지별 vision 렌더 판정) ──

def _has_supplement_chart(doc, page):
    """텍스트 레이어 페이지에 본문과 별개인 큰 차트·도표 이미지가 있는지.

    500K 픽셀을 넘고 페이지의 80% 미만을 덮는(배경 스캔이 아닌) 이미지가 대상.
    있으면 페이지를 렌더해 표·차트를 vision으로 보충 판독한다.
    """
    for img in page.get_images():
        try:
            bi = doc.extract_image(img[0])
            if bi["width"] * bi["height"] <= 500000:
                continue
            xref = img[0]
            img_rects = page.get_image_rects(xref)
            page_area = page.rect.width * page.rect.height
            if any((ir.width * ir.height) / page_area > 0.80 for ir in img_rects):
                continue
            return True
        except Exception:
            pass
    return False


def extract_pdf(path):
    import fitz
    doc = fitz.open(str(path))
    methods_used = set()
    all_text = []
    basename = path.stem

    for i, page in enumerate(doc):
        page_no = i + 1
        text = page.get_text().strip()
        images = page.get_images()
        drawings = page.get_drawings()

        if len(text) > 50:
            structured = extract_page_structured(page)
            all_text.append(structured if structured else text)
            methods_used.add("pdf_text")
            # 텍스트 레이어 페이지라도 별도 표·차트·도표 이미지가 있으면
            # 페이지를 렌더해 vision으로 보충 판독한다.
            if _has_supplement_chart(doc, page):
                all_text.append(render_page(
                    page, basename, page_no, "텍스트페이지 표/차트",
                    note="본문 텍스트는 위에 있으니 표·차트·도표만 판독"))
                methods_used.add("vision_supplement")
            continue

        has_content_img = False
        is_fullpage_scan = False
        for img in images:
            try:
                bi = doc.extract_image(img[0])
                if bi["width"] * bi["height"] > 160000:
                    has_content_img = True
                    xref = img[0]
                    img_rects = page.get_image_rects(xref)
                    page_area = page.rect.width * page.rect.height
                    if any((ir.width * ir.height) / page_area > 0.80 for ir in img_rects):
                        is_fullpage_scan = True
                    break
            except Exception:
                pass

        if is_fullpage_scan:
            all_text.append(render_page(page, basename, page_no, "전면 스캔"))
            methods_used.add("scan_vision")

        elif has_content_img:
            all_text.append(render_page(page, basename, page_no, "이미지 페이지"))
            methods_used.add("image_vision")
            if text:
                structured = extract_page_structured(page)
                all_text.append(structured if structured else text)
                methods_used.add("pdf_text")

        elif len(drawings) > 100:
            # 텍스트 레이어 없이 글자를 벡터 path로 그린 PDF(CaseNote 등 웹 출력물).
            # 텍스트가 거의 0이라 위 조건들을 통과하지 못하고 이 분기로 온다.
            # 페이지 전체를 렌더해 에이전트가 Read로 판독한다. Tesseract의 psm
            # 오분할 문제가 없어 판시 요약란 같은 다단·박스 레이아웃도 온전히 읽힌다.
            all_text.append(render_page(page, basename, page_no, "벡터 렌더"))
            methods_used.add("vector_vision")

        elif text:
            structured = extract_page_structured(page)
            all_text.append(structured if structured else text)
            methods_used.add("pdf_text")

    doc.close()
    return "\n\n".join(all_text), list(methods_used)


# ── 방법 4: HWP 변환 추출 ──

def extract_hwp(path):
    out_dir = SCRATCH_DIR / "hwp_out"
    if out_dir.exists():
        shutil.rmtree(out_dir)

    result = subprocess.run(
        ["hwp5html", str(path), "--output", str(out_dir)],
        capture_output=True, text=True, timeout=60,
    )

    xhtml_path = out_dir / "index.xhtml"
    if not xhtml_path.exists():
        for f in out_dir.rglob("*.xhtml"):
            xhtml_path = f
            break
        else:
            for f in out_dir.rglob("*.html"):
                xhtml_path = f
                break

    if not xhtml_path.exists():
        return ""

    content = xhtml_path.read_text(encoding="utf-8", errors="replace")
    content = re.sub(r"<style[^>]*>.*?</style>", "", content, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", content)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    text = re.sub(r"&#\d+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    shutil.rmtree(out_dir, ignore_errors=True)
    return text


# ── 방법 5: DOCX XML 추출 ──

def extract_docx(path):
    with zipfile.ZipFile(str(path)) as z:
        doc_xml = z.read("word/document.xml")
    tree = ET.fromstring(doc_xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for para in tree.findall(".//w:p", ns):
        texts = para.findall(".//w:t", ns)
        para_text = "".join(t.text or "" for t in texts)
        if para_text.strip():
            paragraphs.append(para_text)
    return "\n".join(paragraphs)


# ── 방법 6: 음성 텍스트 변환 ──

def extract_audio_stt(path):
    model = init_whisper()

    wav_path = SCRATCH_DIR / "audio_tmp.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(path), "-ar", "16000", "-ac", "1",
         "-f", "wav", str(wav_path)],
        capture_output=True, timeout=120,
    )

    if not wav_path.exists():
        return ""

    segments, info = model.transcribe(str(wav_path), language="ko")
    lines = []
    for seg in segments:
        ts = f"[{seg.start:.1f}s-{seg.end:.1f}s]"
        lines.append(f"{ts} {seg.text}")

    wav_path.unlink(missing_ok=True)
    return "\n".join(lines)


# ── 방법 7: 비디오 프레임 렌더(vision 판독 대상) ──

def extract_video_frames_render(path):
    rd = _ensure_render_dir()
    frame_dir = rd / f"{path.stem}_frames"
    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    frame_dir.mkdir(parents=True)

    subprocess.run(
        ["ffmpeg", "-y", "-i", str(path), "-vf", "fps=1", "-q:v", "2",
         str(frame_dir / "frame_%03d.png")],
        capture_output=True, timeout=120,
    )

    frames = sorted(frame_dir.glob("*.png"))
    if not frames:
        return ""

    parts = []
    for f in frames:
        idx = f.stem.split("_")[-1]
        parts.append(_placeholder(f"프레임 {idx}", "비디오 프레임", f))
    return "\n".join(parts)


# ── 추출 후 아티팩트 정리 ──

_CASENOTE_URL = re.compile(
    r"^https?[:/l]{2,}casenote[\s.].*$", re.MULTILINE | re.IGNORECASE
)
_CASENOTE_LABEL = re.compile(r"^CaseNote\s*$", re.MULTILINE)
_CASENOTE_TIMESTAMP = re.compile(
    r"^\d{2,4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*(?:오[전후우]|AM|PM)\s*\d{1,2}[.:]\d{2}\s*$",
    re.MULTILINE,
)
_PAGE_COUNTER = re.compile(r"^\d{1,3}\s*/\s*\d{1,3}\s*$", re.MULTILINE)
_LEGISLATION_HEADER = re.compile(
    r"^법제처\s+\d+\s+국가법령정보센터\s*$", re.MULTILINE
)
_CASENOTE_UI = re.compile(
    r"^(?:키워드[를틀]\s*입력하세요|업무\s*관리|이용\s*중인\s*플랜이|"
    r"Al\s*요약|메모|저장|다운로드|인쇄|공유|하이라이트|본문검색|"
    r"보기설정|오류\s*신고|관련\s*문서|확정)\s*$",
    re.MULTILINE,
)
_MULTI_BLANK = re.compile(r"\n{3,}")


def postprocess_text(text):
    for pat in (
        _CASENOTE_URL,
        _CASENOTE_LABEL,
        _CASENOTE_TIMESTAMP,
        _PAGE_COUNTER,
        _LEGISLATION_HEADER,
        _CASENOTE_UI,
    ):
        text = pat.sub("", text)
    text = _postprocess_structured(text)
    text = _MULTI_BLANK.sub("\n\n", text)
    return text.strip()


# ── 메인 로직 ──

def process_file(path):
    ext = path.suffix.lower()
    result = {"file": str(path), "methods": [], "text_length": 0, "error": None}

    try:
        if ext in (".txt", ".md"):
            text = extract_text_file(path)
            result["methods"].append("direct_read")
            result["text_length"] = len(text)
            return text, result

        elif ext == ".pdf":
            text, methods = extract_pdf(path)
            text = postprocess_text(text)
            result["methods"] = methods
            result["text_length"] = len(text)
            return text, result

        elif ext in (".png", ".jpg", ".jpeg"):
            # 이미지 파일은 원본을 그대로 Read로 판독한다(렌더 불요).
            text = _placeholder("이미지", "이미지 파일", path.resolve())
            result["methods"].append("image_vision")
            result["text_length"] = len(text)
            return text, result

        elif ext == ".hwp":
            text = extract_hwp(path)
            result["methods"].append("hwp_convert")
            result["text_length"] = len(text)
            return text, result

        elif ext == ".docx":
            text = extract_docx(path)
            result["methods"].append("docx_xml")
            result["text_length"] = len(text)
            return text, result

        elif ext == ".m4a":
            text = extract_audio_stt(path)
            result["methods"].append("stt")
            result["text_length"] = len(text)
            return text, result

        elif ext == ".mp4":
            parts = []

            stt_text = extract_audio_stt(path)
            if stt_text.strip():
                parts.append("=== 오디오 음성 인식 ===\n" + stt_text)
                result["methods"].append("stt")

            frame_text = extract_video_frames_render(path)
            if frame_text.strip():
                parts.append("=== 비디오 프레임(vision 판독 대상) ===\n" + frame_text)
                result["methods"].append("video_frame_vision")

            text = "\n\n".join(parts)
            result["text_length"] = len(text)
            return text, result

        else:
            result["error"] = f"지원하지 않는 확장자: {ext}"
            return "", result

    except Exception as e:
        result["error"] = str(e)
        return "", result


def _is_vision_method(m):
    return m.endswith("vision") or m == "vision_supplement"


def main():
    global RENDER_DIR, RENDER_DPI
    argv = sys.argv[1:]
    files = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--render-dir":
            i += 1
            if i < len(argv):
                RENDER_DIR = Path(argv[i]).resolve()
        elif a.startswith("--render-dir="):
            RENDER_DIR = Path(a.split("=", 1)[1]).resolve()
        elif a == "--dpi":
            i += 1
            if i < len(argv):
                RENDER_DPI = int(argv[i])
        elif a.startswith("--dpi="):
            RENDER_DPI = int(a.split("=", 1)[1])
        else:
            files.append(a)
        i += 1

    if not files:
        print("사용법: python extract_all.py [--render-dir DIR] [--dpi N] <파일1> [파일2] ...",
              file=sys.stderr)
        print("지정된 파일에서 텍스트를 추출하여 stdout에 출력합니다.", file=sys.stderr)
        print("이미지·스캔·벡터 PDF 페이지는 PNG로 렌더하고 그 자리에 [[VISION ...]]",
              file=sys.stderr)
        print("플레이스홀더를 남깁니다. 플레이스홀더의 PNG를 Read 도구로 판독하세요.",
              file=sys.stderr)
        sys.exit(1)

    paths = [Path(p).resolve() for p in files]
    any_vision = False

    for path in paths:
        if not path.exists():
            print(f"[오류] 파일 없음: {path}", file=sys.stderr)
            continue

        print(f"[추출] {path} ...", file=sys.stderr, flush=True)
        text, meta = process_file(path)

        if meta["error"]:
            print(f"[오류] {meta['error']}", file=sys.stderr)
        else:
            methods_str = ", ".join(meta["methods"])
            print(f"[완료] {meta['text_length']}자 [{methods_str}]", file=sys.stderr)
            if any(_is_vision_method(m) for m in meta["methods"]):
                any_vision = True

        if len(paths) > 1:
            print(f"\n{'='*60}")
            print(f"=== {path.name} ===")
            print(f"{'='*60}\n")

        print(text)

        gc.collect()

    if any_vision and RENDER_DIR is not None:
        print(f"[vision] OCR 대상 페이지를 {RENDER_DIR} 에 PNG로 렌더했습니다.",
              file=sys.stderr)
        print("[vision] stdout의 [[VISION ...]] 플레이스홀더에 적힌 PNG를 Read 도구로 "
              "판독해 그 자리를 채우세요.", file=sys.stderr)

    shutil.rmtree(SCRATCH_DIR, ignore_errors=True)


if __name__ == "__main__":
    main()

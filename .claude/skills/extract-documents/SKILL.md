---
name: extract-documents
description: PDF·HWP·DOCX·이미지·음성·영상의 내용을 텍스트로 추출하거나 전사할 때 사용한다. "PDF 전문 뽑아줘", "스캔본 OCR해줘", "녹음 전사해줘"라고 요청하거나 다른 작업에 앞서 바이너리 문서 전문을 읽어야 할 때 호출한다. 이미 텍스트인 Markdown·TXT 파일을 단순 열람하는 경우에는 사용하지 않는다.
argument-hint: <file paths to extract>
---

# Document extraction

`extract_all.py` extracts text from specified files and prints results to stdout. Text layers and non-image formats are extracted directly. Pages that need OCR (scans, vector-path PDFs, standalone images, charts inside text pages, video frames) are **not** OCR'd by the script. Instead the script renders them to PNG and emits a `[[VISION ...]]` placeholder in their place; the main agent then reads each rendered PNG with the Read tool (Claude vision) and replaces the placeholder with the transcribed text. This reading also serves as correction, so a separate OCR-correction pass is not needed for those pages.

## Usage

```bash
python .claude/skills/extract-documents/scripts/extract_all.py [--render-dir DIR] [--dpi N] <file1> [file2] ...
```

- `--render-dir DIR`: directory where OCR-needed pages are rendered as PNG. Pass the session scratchpad directory so the agent can read them afterward. If omitted, a non-deleted temp directory is created and its path is printed to stderr.
- `--dpi N`: render resolution (default 200). The Read tool downsamples images by long edge, so Tesseract-grade 600dpi is unnecessary; raise it only if dense small text blurs.

Extracted text goes to stdout, progress/errors to stderr. The exit code is 1 if any input file is missing, raises an extraction error (including HWP conversion that produces no output), or yields empty text; the other files are still processed and printed. A zero exit code does not certify completeness (see step 4 below).

### Agent workflow (vision reading)

1. Run the script, redirecting stdout to a draft `.txt`. Text-layer content is already filled in place.
2. For each `[[VISION 페이지 N | 유형 | <png경로>]]` placeholder, Read the PNG at that path, transcribe it, and replace the placeholder with the transcription. The transcription is the corrected text (preserve original wording; do not add or reconstruct content).
3. Leave only genuinely illegible tokens (blur, crop, ambiguous handwriting) as `[OCR 불확실]`.
4. **Numeric-critical legal originals** (case originals where amounts, article numbers, ratios, or periods decide the legal analysis): before adopting the extraction as the canonical transcription, render sample pages (all content pages if short) to PNG and compare against the text-layer output. A text layer can exist yet systematically drop digits, and the script emits **no warning** for this: adoption is judged only by character count (>50 chars/page), so the loss is silent. Judge per document, not per source (one PDF can drop digits while another from the same source is clean).

### Examples

```bash
# Single image (placeholder points at the original file; Read it directly)
python .claude/skills/extract-documents/scripts/extract_all.py --render-dir "$SCRATCH" "자료/스캔_문서.png"

# PDF: text-layer pages come out as text, OCR pages come out as [[VISION ...]] placeholders
python .claude/skills/extract-documents/scripts/extract_all.py --render-dir "$SCRATCH" "자료/문서.pdf" > draft.txt
```

## Methods

| # | Method | Tool | Targets |
|---|--------|------|---------|
| 1 | Direct text read | `open().read()` | `.txt`, `.md` |
| 2 | PDF text layer | PyMuPDF `page.get_text()` | `.pdf` with text layer |
| 3 | PNG render + agent Read | PyMuPDF `get_pixmap` renders the page (or the original image is pointed at directly); the agent reads it with the Read tool (Claude vision) | `.png`, `.jpg`, image-only PDF pages, vector-drawing PDF pages, full-page scans, chart/table/diagram images inside text-layer pages |
| 4 | HWP conversion | `hwp5html` → strip HTML tags | `.hwp` |
| 5 | DOCX XML parsing | `zipfile` → `w:t` tags | `.docx` |
| 6 | Speech-to-text | faster-whisper (`base`, `ko`) | `.m4a`, `.mp4` audio track |
| 7 | Video frame render | ffmpeg 1fps → PNG → agent Read | `.mp4` visual content |

## PDF page-level decision logic

Each PDF page is classified independently:

1. **Text > 50 chars** → use text layer. Additionally, any embedded image > 500K pixels that covers < 80% of page area triggers a full-page render placeholder for supplementary vision reading (catches charts/tables alongside text).
2. **Text ≤ 50 chars + image > 160K pixels** → render the page to PNG for vision reading (full-page scan or content image).
3. **Text ≤ 50 chars + drawings > 100** → render page to PNG for vision reading, for vector-path PDFs like Gmail/CaseNote printouts. Vision reads multi-column/box layouts intact, avoiding the column mis-segmentation that Tesseract's psm modes suffered on these captures.
4. **Otherwise** → empty page (section dividers, page numbers).

Text length is the sole discriminator for vector-path PDFs: drawings count alone cannot separate vector-glyph PDFs from legitimately drawing-heavy documents (a university regulation PDF had 210K chars of text with 290K drawings).

## Dependencies

- PyMuPDF (`fitz`) — PDF text/image extraction and page rendering to PNG
- Read tool (Claude vision) — transcribes the rendered PNGs. No OCR engine and no API key are required; the main agent reads the PNGs in-session
- pyhwp (`hwp5html`) — HWP to XHTML conversion
- faster-whisper — speech recognition
- ffmpeg — audio extraction, video frame extraction

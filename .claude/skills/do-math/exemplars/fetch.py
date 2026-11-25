#!/usr/bin/env python3
"""Fetch the exemplar papers from arXiv and rebuild each as one LaTeX file.

    python fetch.py                  every paper that is missing or differs
    python fetch.py --only <key>     one paper (the option may be repeated)
    python fetch.py --to <folder>    write the files into another folder

The script reads manifest.json, which stands beside it.  For each paper it
downloads the source of the recorded arXiv version, joins it into a single
file <key>.tex and compares the SHA-256 of that file with the manifest.  A
file is written only when the digest agrees.  The exit code is nonzero when a
paper could not be rebuilt as recorded.

How a source becomes one file:

  * the main file is the LaTeX file of the archive that has \\documentclass
    and \\begin{document};
  * every \\input and \\include that names a .tex file of the archive is
    replaced by the content of that file, recursively; commands inside
    comments are left alone;
  * where \\bibliography{...} stands and the archive has the .bbl file, the
    content of the .bbl replaces the command;
  * what the authors commented out is left out: every line whose first
    character that is not a blank is %, and every comment environment from
    \\begin{comment} to \\end{comment}; a % after text on a line stays, and
    so does everything inside verbatim, lstlisting and similar environments;
  * everything after \\end{document} is dropped;
  * nothing else is changed.  The text is written as UTF-8 with LF line ends.

An archive is untrusted data.  It is unpacked in memory only, member names
with an absolute path or a ".." are refused, and nothing from it is executed.
Only the standard library is used.
"""
import argparse
import gzip
import hashlib
import io
import json
import os
import posixpath
import re
import sys
import tarfile
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
USER_AGENT = "exemplar-fetch/1.0"
WAIT_SECONDS = 3.5
HOSTS = ("https://export.arxiv.org/e-print/", "https://arxiv.org/e-print/")
MAX_BYTES = 100 * 1024 * 1024
MAX_DEPTH = 12

_last_request = [0.0]


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- download

def _request(url):
    wait = WAIT_SECONDS - (time.time() - _last_request[0])
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.read(MAX_BYTES + 1)
    finally:
        _last_request[0] = time.time()


def download(arxiv_id):
    """Return the bytes of the e-print of arxiv_id (identifier with version)."""
    errors = []
    for host in HOSTS:
        url = host + arxiv_id
        for attempt in range(2):
            try:
                data = _request(url)
            except (urllib.error.URLError, OSError) as exc:
                errors.append("%s: %s" % (url, exc))
                continue
            if len(data) > MAX_BYTES:
                raise BuildError("source of %s is larger than %d bytes" % (arxiv_id, MAX_BYTES))
            return data
    raise BuildError("download failed: " + "; ".join(errors))


# ------------------------------------------------------------------ unpack

def _safe_name(name):
    if not name or name.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", name):
        return None
    parts = name.replace("\\", "/").split("/")
    if ".." in parts:
        return None
    return posixpath.normpath("/".join(parts))


def unpack(data):
    """Return {member name: bytes} for an arXiv e-print, read in memory."""
    if data[:4] == b"%PDF":
        raise BuildError("the e-print is a PDF, there is no LaTeX source")
    if data[:2] == b"\x1f\x8b":
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
            data = gz.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise BuildError("unpacked source is larger than %d bytes" % MAX_BYTES)
    files = {}
    try:
        tar = tarfile.open(fileobj=io.BytesIO(data), mode="r:")
    except tarfile.TarError:
        return {"main.tex": data}
    total = 0
    with tar:
        for member in tar.getmembers():
            name = _safe_name(member.name)
            if name is None:
                raise BuildError("archive member with an unsafe name: %r" % member.name)
            if not member.isfile():
                continue
            total += member.size
            if total > MAX_BYTES:
                raise BuildError("unpacked source is larger than %d bytes" % MAX_BYTES)
            handle = tar.extractfile(member)
            if handle is not None:
                files[name] = handle.read()
    return files


# ----------------------------------------------------------------- flatten

def decode(raw):
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def split_comment(line):
    """Split a line into the part TeX reads and the comment (from %)."""
    i = 0
    while True:
        i = line.find("%", i)
        if i < 0:
            return line, ""
        backslashes = 0
        j = i - 1
        while j >= 0 and line[j] == "\\":
            backslashes += 1
            j -= 1
        if backslashes % 2 == 0:
            return line[:i], line[i:]
        i += 1


def code_of(text):
    return "\n".join(split_comment(line)[0] for line in text.split("\n"))


INPUT_RE = re.compile(
    r"\\(?:input|include)\s*\{\s*([^{}]+?)\s*\}"      # \input{name}  \include{name}
    r"|\\input\s+([^\s{}\\%]+)"                        # \input name
)
JOIN_RE = re.compile(INPUT_RE.pattern + r"|(\\bibliography\s*\{[^{}]*\})")
CLASS_RE = re.compile(r"\\document(?:class|style)\s*[\[{]")
BEGIN_RE = re.compile(r"\\begin\s*\{document\}")
END_RE = re.compile(r"\\end\s*\{document\}")
TEX_EXT = (".tex", ".ltx")


def resolve(name, files, base_dir):
    name = name.strip().replace("\\", "/")
    if name.startswith("./"):
        name = name[2:]
    tries = []
    for folder in ("", base_dir):
        for candidate in (name + ".tex", name):
            path = posixpath.normpath(posixpath.join(folder, candidate))
            if path not in tries:
                tries.append(path)
    lower = {}
    for key in sorted(files):
        lower.setdefault(key.lower(), key)
    for path in tries:
        if not path.lower().endswith(TEX_EXT):
            continue
        if path in files:
            return path
        if path.lower() in lower:
            return lower[path.lower()]
    return None


def flatten(name, files, bbl, state, stack=()):
    if len(stack) > MAX_DEPTH:
        raise BuildError("\\input nested deeper than %d" % MAX_DEPTH)
    base_dir = posixpath.dirname(stack[0] if stack else name)
    out = []
    for line in decode(files[name]).split("\n"):
        code, comment = split_comment(line)

        def put(match):
            if match.group(3) is not None:          # \bibliography{...}
                if bbl is None or state["bbl_done"]:
                    return match.group(0)
                state["bbl_done"] = True
                return decode(files[bbl]).rstrip("\n") + "\n"
            target = resolve(match.group(1) or match.group(2), files, base_dir)
            if target is None or target == name or target in stack:
                return match.group(0)
            body = flatten(target, files, bbl, state, stack + (name,))
            return body.rstrip("\n") + "\n"

        # one pass, so that text put in place is not searched again
        new = JOIN_RE.sub(put, code)
        if new != code and new.endswith("\n") and not comment:
            new = new[:-1]
        out.append(new + comment)
    return "\n".join(out)


VERBATIM_RE = re.compile(
    r"\\begin\s*\{(verbatim\*?|Verbatim\*?|BVerbatim\*?|LVerbatim\*?|lstlisting|minted|alltt|filecontents\*?)\}")
COMMENT_BEGIN_RE = re.compile(r"\\begin\s*\{comment\}")
COMMENT_END_RE = re.compile(r"\\end\s*\{comment\}")
OWN_COMMENT_RE = re.compile(r"\\(?:newtheorem\*?|(?:re)?newenvironment)\s*\{comment\}")


def is_comment_line(line):
    return line.lstrip(" \t").startswith("%")


def drop_comments(text):
    """Leave out what the authors commented out.

    Dropped: every line whose first character that is not a blank is %, and
    every comment environment, from \\begin{comment} to \\end{comment}.  Kept:
    a % after text on a line, and everything inside verbatim, lstlisting and
    similar environments.  Text that stands on the line of \\begin{comment}
    before it, or on the line of \\end{comment} after it, is kept.  A paper
    that declares an environment of its own named comment keeps it.
    """
    own_comment = OWN_COMMENT_RE.search(code_of(text)) is not None
    out = []
    verbatim = None        # name of the verbatim-like environment we are in
    in_comment = False
    for line in text.split("\n"):
        if verbatim is not None:
            out.append(line)
            if ("\\end{%s}" % verbatim) in line:
                verbatim = None
            continue
        if in_comment:
            end = COMMENT_END_RE.search(line)
            if end:
                in_comment = False
                tail = line[end.end():]
                if tail.strip() and not is_comment_line(tail):
                    out.append(tail)
            continue
        if is_comment_line(line):
            continue
        code = split_comment(line)[0]
        begin = None if own_comment else COMMENT_BEGIN_RE.search(code)
        if begin:
            head = line[:begin.start()]
            end = COMMENT_END_RE.search(line, begin.end())
            if end:
                kept = head + line[end.end():]
            else:
                kept = head
                in_comment = True
            if kept.strip() and not is_comment_line(kept):
                out.append(kept)
            continue
        opened = VERBATIM_RE.search(code)
        if opened and ("\\end{%s}" % opened.group(1)) not in line[opened.end():]:
            verbatim = opened.group(1)
        out.append(line)
    return "\n".join(out)


def cut_after_end(text):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        code = split_comment(line)[0]
        match = END_RE.search(code)
        if match:
            lines[i] = line[:match.end()]
            return "\n".join(lines[:i + 1]) + "\n"
    return text if text.endswith("\n") else text + "\n"


def main_candidates(files):
    found = []
    for name in sorted(files):
        ext = posixpath.splitext(name)[1].lower()
        if ext not in TEX_EXT and ext != "":
            continue
        code = code_of(decode(files[name]))
        if CLASS_RE.search(code) and BEGIN_RE.search(code):
            found.append(name)
    return found


def pick_bbl(main, files):
    bbls = sorted(n for n in files if n.lower().endswith(".bbl"))
    own = posixpath.splitext(main)[0] + ".bbl"
    if own in files:
        return own
    if len(bbls) == 1:
        return bbls[0]
    return None


def build(data):
    """Return the single-file LaTeX text (bytes, UTF-8) for an e-print."""
    files = unpack(data)
    candidates = main_candidates(files)
    if not candidates:
        raise BuildError("no file with \\documentclass and \\begin{document}")
    built = []
    for main in candidates:
        state = {"bbl_done": False}
        text = cut_after_end(drop_comments(flatten(main, files, pick_bbl(main, files), state)))
        has_front = ("\\begin{abstract}" in text) or ("\\maketitle" in text)
        built.append((has_front, len(text), main, text))
    # the main file: one with a title or abstract, then the longest, then by name
    built.sort(key=lambda item: (not item[0], -item[1], item[2]))
    return built[0][3].encode("utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


# -------------------------------------------------------------------- main

def main(argv=None):
    parser = argparse.ArgumentParser(description="Fetch the exemplar papers from arXiv.")
    parser.add_argument("--only", action="append", metavar="KEY", help="rebuild this paper only")
    parser.add_argument("--to", metavar="FOLDER", default=HERE, help="folder for the .tex files")
    args = parser.parse_args(argv)

    with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as handle:
        manifest = json.load(handle)
    by_key = {entry["key"]: entry for entry in manifest}

    failed = []
    if args.only:
        entries = []
        for key in args.only:
            if key in by_key:
                entries.append(by_key[key])
            else:
                print("%s: no such key in manifest.json" % key)
                failed.append(key)
    else:
        entries = manifest

    os.makedirs(args.to, exist_ok=True)
    for entry in entries:
        key, arxiv_id, want = entry["key"], entry["arxiv"], entry["sha256"]
        path = os.path.join(args.to, key + ".tex")
        if os.path.isfile(path):
            with open(path, "rb") as handle:
                if sha256(handle.read()) == want:
                    print("%s: present and equal to the manifest, nothing to do" % key)
                    continue
            print("%s: present but different from the manifest, fetching arXiv:%s" % (key, arxiv_id))
        else:
            print("%s: missing, fetching arXiv:%s" % (key, arxiv_id))
        sys.stdout.flush()
        try:
            text = build(download(arxiv_id))
        except BuildError as exc:
            print("%s: FAILED, %s" % (key, exc))
            failed.append(key)
            continue
        got = sha256(text)
        if got != want:
            print("%s: FAILED, rebuilt file has SHA-256 %s, the manifest records %s; nothing written"
                  % (key, got, want))
            failed.append(key)
            continue
        with open(path, "wb") as handle:
            handle.write(text)
        print("%s: rebuilt, %d bytes, SHA-256 agrees" % (key, len(text)))

    if failed:
        print("%d paper(s) could not be rebuilt as recorded: %s" % (len(failed), ", ".join(failed)))
        return 1
    print("all %d paper(s) are as recorded" % len(entries))
    return 0


if __name__ == "__main__":
    sys.exit(main())

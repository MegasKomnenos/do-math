# -*- coding: utf-8 -*-
"""M11 검산 공용: 장 파일을 진술 블록으로 나누고 머리를 찾는다(자리 찾기용)."""
import re, glob, os

ROOT = r'C:\math\임시\주차함수_증명'
CH = os.path.join(ROOT, '장v2')

def load_chapters():
    out = {}
    for f in sorted(glob.glob(os.path.join(CH, '장*.md'))):
        out[os.path.basename(f)] = open(f, encoding='utf-8').read().split('\n')
    return out

HEAD_RE = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의) \{\{([^}]+)\}\}(.*?)\*\*')

def blocks(lines, fname):
    """각 블록: dict(kind,label,name,mark,sec,start,end,text). 머리 없는 문단은 '준비(절)' 블록."""
    res = []
    sec = None
    cur = None
    def close(i):
        nonlocal cur
        if cur is not None:
            cur['end'] = i
            cur['text'] = '\n'.join(lines[cur['start']:i])
            res.append(cur)
            cur = None
    for i, ln in enumerate(lines):
        m = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)', ln)
        if m:
            close(i)
            sec = m.group(2)
            cur = dict(kind='준비', label=None, name=None, mark=None, sec=sec, start=i, file=fname)
            continue
        h = HEAD_RE.match(ln)
        if h:
            close(i)
            rest = h.group(3)
            nm = re.match(r'\s*\(([^)]*(?:\([^)]*\)[^)]*)*)\)', rest)
            mk = re.search(r'\[([^\]]*)\]\.?\s*$', rest)
            cur = dict(kind=h.group(1), label=h.group(2), name=(nm.group(1) if nm else None),
                       mark=(mk.group(1) if mk else None), sec=sec, start=i, file=fname, headline=ln)
            continue
        if cur is None:
            cur = dict(kind='준비', label=None, name=None, mark=None, sec=sec, start=i, file=fname)
    close(len(lines))
    return res

def all_blocks():
    chs = load_chapters()
    out = []
    for fn, lines in chs.items():
        out.extend(blocks(lines, fn))
    return out

def head_index(bl):
    return {b['label']: b for b in bl if b['label']}

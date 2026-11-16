# -*- coding: utf-8 -*-
"""J14: 대응표(대조v2/라벨_번호_대응표_1114.md)와 의존지도 1절을 장 파일 진술 머리와 견준다.
- 현재 번호: 장마다 머리를 파일 순서로 센 번호(5A→5B, 7A→7B 이어 셈).
- 의존지도: 절·지위(';' 앞)·머리 줄이 인용한 라벨을 견준다.
usage: python -I 검토전체4_J14_map.py [table|dep]
"""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'C:\math\임시\주차함수_증명')
ORDER = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
HEAD = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|가설|관찰|주장|예|알고리즘)\s+\{\{([^}]+)\}\}(?!의 증명|\s*\(?[가-힣]*\)?의 증명)\s*(.*?)\*\*')
SEC = re.compile(r'^(#{2,4})\s+(\d+(?:\.\d+)*)')
heads = {}   # label -> dict
order_in_ch = {}
for f in ORDER:
    ch = int(re.sub(r'\D', '', f))
    sec = str(ch)
    lines = (ROOT/'장v2'/(f+'.md')).read_text(encoding='utf-8').splitlines()
    for i, L in enumerate(lines):
        m = SEC.match(L)
        if m: sec = m.group(2)
        m = HEAD.match(L)
        if not m: continue
        kind, lab, rest = m.groups()
        order_in_ch[ch] = order_in_ch.get(ch, 0) + 1
        num = f'{ch}.{order_in_ch[ch]}'
        mm = re.match(r'\s*\((.*?)\)\s*(\[(.*)\])?\s*\.?\s*$', rest)
        name = ''; status = ''
        if mm:
            name = mm.group(1); status = mm.group(3) or ''
        else:
            mm = re.match(r'\s*\[(.*)\]\s*\.?\s*$', rest)
            if mm: status = mm.group(1)
            else: name = rest
        cited = re.findall(r'\{\{([^}]+)\}\}', L)
        cited = [c for c in cited if c != lab]
        # 본문(다음 머리 전까지) 인용
        body = []
        j = i + 1
        while j < len(lines) and not HEAD.match(lines[j]):
            body += re.findall(r'\{\{([^}]+)\}\}', lines[j]); j += 1
        heads[lab] = dict(kind=kind, sec=sec, name=name, status=status, num=num, cited=cited,
                          body=set(body), where=f'{f}.md:{i+1}')
mode = sys.argv[1] if len(sys.argv) > 1 else 'table'
if mode == 'table':
    seen = set()
    for L in (ROOT/'대조v2'/'라벨_번호_대응표_1114.md').read_text(encoding='utf-8').splitlines():
        if not L.startswith('| `{{'): continue
        cols = [c.strip() for c in L.strip().strip('|').split('|')]
        lab = re.search(r'\{\{([^}]+)\}\}', cols[0]).group(1)
        kind, name, num, num1552, sec = cols[1], cols[2], cols[3], cols[4], cols[5]
        seen.add(lab)
        if lab not in heads:
            if num != '뺌' and '뺌' not in num:
                print(f'[머리 없음] {lab}: {kind} {name} 번호={num} 절={sec}')
            continue
        h = heads[lab]
        probs = []
        if h['kind'] != kind: probs.append(f"종류 표={kind} 머리={h['kind']}")
        if h['num'] != num: probs.append(f"번호 표={num} 머리={h['num']}")
        if sec and not (h['sec'] == sec or h['sec'].startswith(sec + '.')): probs.append(f"절 표={sec} 머리={h['sec']}")
        hname = h['name']
        if name != '—' and name != hname: probs.append(f"이름 표=「{name}」 머리=「{hname}」")
        if name == '—' and hname: probs.append(f"이름 표=— 머리=「{hname}」")
        if probs: print(f"[{lab}] @ {h['where']}: " + ' / '.join(probs))
    for lab, h in heads.items():
        if lab not in seen: print(f"[표 없음] {lab} ({h['kind']} {h['num']}) @ {h['where']}")
else:
    seen = set()
    for L in (ROOT/'의존지도_v2.md').read_text(encoding='utf-8').splitlines()[10:416]:
        if not L.startswith('| `{{'): continue
        cols = [c.strip() for c in L.strip().strip('|').split('|')]
        if len(cols) < 10: print(f'[열 수] {L[:60]}'); continue
        lab = re.search(r'\{\{([^}]+)\}\}', cols[0]).group(1)
        sec, old, gist, status, inputs, rec, lit, appD, note = cols[1:10]
        seen.add(lab)
        if lab not in heads:
            print(f'[머리 없음] {lab}: 절={sec} 요지={gist}'); continue
        h = heads[lab]
        probs = []
        if not (h['sec'] == sec or h['sec'].startswith(sec + '.')): probs.append(f"절 지도={sec} 머리={h['sec']}")
        hst = h['status'].split(';')[0].strip() if h['status'] else ''
        if h['kind'] == '정의': hst = '정의'
        if status != hst: probs.append(f"지위 지도=「{status}」 머리=「{hst}」")
        # 머리 줄 인용 라벨
        head_part = inputs.split('본문 인용:')[0]
        head_labels = [c for c in re.findall(r'\{\{([^}]+)\}\}', head_part)]
        if sorted(set(head_labels)) != sorted(set(h['cited'])):
            probs.append(f"머리 인용 지도={sorted(set(head_labels))} 머리={sorted(set(h['cited']))}")
        # 본문 인용 라벨
        body_part = inputs.split('본문 인용:')[1] if '본문 인용:' in inputs else ''
        body_labels = set(re.findall(r'\{\{([^}]+)\}\}', body_part))
        hb = {b for b in h['body'] if not b.startswith('D:') and b != lab and b not in set(h['cited'])}
        if hb - body_labels - set(head_labels):
            only_head = sorted(hb - body_labels - set(head_labels))
            probs.append(f"본문이 인용하나 지도에 없음={only_head}")
        # 기록 주장: 머리 ';' 뒤
        hrec = h['status'].split(';')[1].strip() if ';' in h['status'] else ''
        if hrec and rec == '—': probs.append(f"기록 지도=— 머리=「{hrec}」")
        if gist and h['name'] and gist.split(';')[0].strip() != h['name'].split(';')[0].strip():
            probs.append(f"요지 지도=「{gist[:40]}」 머리=「{h['name'][:40]}」")
        if probs: print(f"[{lab}] @ {h['where']}: " + ' / '.join(probs))
    for lab, h in heads.items():
        if lab not in seen: print(f"[지도 없음] {lab} ({h['kind']} {h['num']}, {h['sec']}) @ {h['where']}")

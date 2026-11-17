# 검토전체25 R9: 9장 진술마다 증명이 부르는 라벨 가운데 외부 입력(계산 증거·계산 보조·문헌 인용·…에 의존)을 가진 것과 머리의 의존 목록을 나란히 출력(판정은 사람이 한다)
import re, glob, io
heads = {}
for f in glob.glob('장v2/*.md'):
    for line in io.open(f, encoding='utf-8'):
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}', line)
        if m:
            h = line.split('.**')[0]
            g = re.findall(r'\[([^\[\]]*)\]$', h)
            heads[m.group(2)] = (m.group(1), g[0] if g else '')
def ext(st):
    return bool(re.search(r'계산 증거|계산 보조|문헌 인용|에 의존', st))
lines = io.open('장v2/장9.md', encoding='utf-8').read().split('\n')
idx = [i for i, l in enumerate(lines) if re.match(r'\*\*(정리|명제|보조정리|따름정리) \{\{9:', l)]
for a, i in enumerate(idx):
    lab = re.match(r'\*\*\S+ \{\{([^}]+)\}\}', lines[i]).group(1)
    # 증명 끝(∎)까지
    j = i
    while j < len(lines) and '∎' not in lines[j]: j += 1
    body = '\n'.join(lines[i:j+1])
    hd = heads.get(lab, ('?', '?'))[1]
    declared = set(re.findall(r'\{\{([^}]+)\}\}', hd))
    used = set(re.findall(r'\{\{([^}]+)\}\}', body)) - {lab}
    used_ext = {u for u in used if u in heads and ext(heads[u][1])}
    print('==', lab, '|', hd[:160])
    print('   부르는 외부 입력 진술:', sorted(used_ext))
    print('   머리에 있고 본문에 없음:', sorted(declared - used), '| 외부 입력인데 머리에 없음:', sorted(used_ext - declared), '| 머리에 있으나 외부 입력 아님:', sorted(d for d in declared if d in heads and not ext(heads[d][1])))

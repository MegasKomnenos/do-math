# 부록 B의 기록 가운데 본문(장1–장10)·부록 D가 인용하는 것의 수(7절 머리말의 72+3 주장 확인)
import io, re, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = open('장v2/부록B.md', encoding='utf-8').read().split('\n')
bids = [m.group(1) for l in B for m in [re.match(r'\| (r[0-9a-f]{7}) \|', l)] if m]
body = [f for f in glob.glob('장v2/장*.md')] + [f for f in glob.glob('장v2/부록D_*.md')]
cnt = {r: {} for r in bids}
allids = set()
for f in body:
    t = open(f, encoding='utf-8').read()
    for r in re.findall(r'r[0-9a-f]{7}(?![0-9a-f])', t):
        allids.add(r)
        if r in cnt:
            cnt[r][f] = cnt[r].get(f, 0) + 1
none = [r for r in bids if not cnt[r]]
print('본문·부록D가 인용하는 부록B 기록 수', len(bids) - len(none))
print('본문·부록D에 없는 부록B 기록', none)
print('본문·부록D에 있는데 부록B에 없는 r-식별자', sorted(allids - set(bids)))
for a in ['장v2/부록A.md', '장v2/부록C.md']:
    t = open(a, encoding='utf-8').read()
    ids = set(re.findall(r'r[0-9a-f]{7}(?![0-9a-f])', t))
    print(a, len(ids), '부록B 밖:', sorted(ids - set(bids)), '; 부록B에 있으나 이 파일에 없음:', sorted(set(bids) - ids))

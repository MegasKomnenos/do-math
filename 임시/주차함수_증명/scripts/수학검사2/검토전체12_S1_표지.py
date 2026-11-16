# 장1·장2: (1) 머리에 '작성자 판단'이 있는 진술의 증명에 †가 있는지, 거꾸로 †가 있는 진술의 머리에 '작성자 판단'이 있는지
# (2) 장2의 라벨이 다른 장에서 어디에 인용되는지 (첫째/둘째 증명 전용 주장 확인용)
import re, glob, os
root = r'C:\math\임시\주차함수_증명\장v2'
files = {os.path.basename(p): open(p, encoding='utf-8').read() for p in glob.glob(os.path.join(root, '*.md'))}
for target in ['장1.md', '장2.md']:
    txt = files[target]
    heads = [(m.start(), m.group(0)) for m in re.finditer(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{[^}]+\}\}[^\n]*?\*\*', txt)]
    print('====', target, len(heads), 'heads')
    for idx, (pos, head) in enumerate(heads):
        end = heads[idx+1][0] if idx+1 < len(heads) else len(txt)
        body = txt[pos:end]
        lab = re.search(r'\{\{([^}]+)\}\}', head).group(1)
        has_aj = '작성자 판단' in head
        n_dagger = body.count('†')
        if has_aj != (n_dagger > 0):
            print('불일치:', lab, '| 머리 작성자판단', has_aj, '| † 수', n_dagger)
    # 진술 밖 †(준비 문단)
    outside = []
    for m in re.finditer('†', txt):
        pass
print()
# 장2 라벨의 타 장 인용
labs2 = sorted(set(re.findall(r'\*\*(?:정리|명제|보조정리|따름정리|정의)\s+\{\{(2:[^}]+)\}\}', files['장2.md'])))
for lab in labs2:
    cited = {}
    for fn, txt in files.items():
        if fn in ('장2.md',): continue
        c = len(re.findall(re.escape('{{'+lab+'}}'), txt))
        if c: cited[fn] = c
    print(lab, cited)

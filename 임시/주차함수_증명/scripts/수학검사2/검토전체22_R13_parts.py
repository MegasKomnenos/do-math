# 라벨의 진술문(증명 전까지)에 부분 표지 (가)(나)…/(ㄱ)(ㄴ)…/(i)(ii)가 무엇이 있는지 보여 준다.
import re, sys, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r"C:/math/임시/주차함수_증명/"
heads = json.load(open(W+"scripts/수학검사2/검토전체22_R13_heads.json", encoding='utf-8'))
H = {o['label']: o for o in heads if not o['proof']}
def stmt(lab):
    o = H[lab]
    L = open(W+"장v2/"+o['file']+".md", encoding='utf-8').read().split('\n')
    i = o['line']-1; out=[]
    while i < len(L):
        if i > o['line']-1 and (L[i].startswith('**증명') or re.match(r'^\*\*\S+ \{\{', L[i]) or L[i].startswith('#')): break
        out.append(L[i]); i+=1
    return '\n'.join(out)
if __name__ == '__main__':
    for lab in sys.argv[1:]:
        if lab not in H: print(lab, 'DEAD'); continue
        s = stmt(lab)
        parts = []
        for m in re.finditer(r'(?:^|\s|\.)\((가|나|다|라|마|바|사|아|ㄱ|ㄴ|ㄷ|ㄹ|ㅁ|ㅂ|i|ii|iii|iv|a|b|c)\)', s):
            if m.group(1) not in parts: parts.append(m.group(1))
        o=H[lab]
        print(lab, o['kind'], o['num'], o['file'], o['line'], 'parts:', ' '.join(parts), '| name:', o['name'], '| len', len(s))

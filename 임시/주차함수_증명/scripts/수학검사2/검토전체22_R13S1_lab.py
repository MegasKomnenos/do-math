# S1 검산 도구: 라벨의 현행 머리(종류·절·파일·행)를 heads.json에서 찾아 보이고, 장 파일에서 그 라벨의 머리 행도 직접 찾는다.
# 사용: python -I 검토전체22_R13S1_lab.py 2:old-2-3 7:old-6-8 ...
import sys, io, os, json, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
H = json.load(io.open(os.path.join(here, '검토전체22_R13_heads.json'), encoding='utf-8'))
base = os.path.join(here, '..', '..', '장v2')
for lab in sys.argv[1:]:
    hs = [h for h in H if h['label'] == lab]
    if hs:
        for h in hs:
            print('%s: %s %s절 %s:%d (%s)%s' % (lab, h['kind'], h['sec'], h['file'], h['line'], h['name'], ' [증명 머리]' if h.get('proof') else ''))
    else:
        n = 0
        for p in sorted(glob.glob(os.path.join(base, '*.md'))):
            for i, line in enumerate(io.open(p, encoding='utf-8'), 1):
                if '{{' + lab + '}}' in line: n += 1
        print('%s: 머리 없음(heads.json); 장 파일 인용 %d건' % (lab, n))

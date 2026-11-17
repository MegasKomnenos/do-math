# 기록의 exposition.md(또는 지정 파일)에서 지정한 행을 보여 준다. 부록 A·C가 행 번호로 가리킨 자리의 대조용.
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
rec = 'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
folders = {d[:8]: d for d in os.listdir(rec)}
for spec in sys.argv[1:]:
    parts = spec.split(':')
    rid = parts[0]; nums = parts[1]; fn = parts[2] if len(parts) > 2 else 'exposition.md'
    w = int(parts[3]) if len(parts) > 3 else 300
    p = rec + folders[rid] + '/' + fn
    L = open(p, encoding='utf-8').read().split('\n')
    for n in nums.split(','):
        if '-' in n: a, b = map(int, n.split('-'))
        else: a = b = int(n)
        for k in range(a, b+1):
            print(f'[{rid} {fn} L{k}] {L[k-1][:w]}')

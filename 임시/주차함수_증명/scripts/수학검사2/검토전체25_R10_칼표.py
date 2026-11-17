# 「작성자 판단」 표지와 칼표 †의 대응을 훑는다(10.1절·1.5절의 규칙). 진술 머리에서 다음 머리까지를 한 구간으로 본다. 어긋나 보이는 구간은 원문을 읽는다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
names = ['1','2','3','4','5A','5B','6','7A','7B','8','9']
for c in names:
    L = open(base + f'장{c}.md', encoding='utf-8').read().split('\n')
    heads = []
    for i, ln in enumerate(L):
        m = re.match(r'\*\*((정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}.*?)\.\*\*', ln)
        if m and '[' in m.group(1): heads.append((i, m.group(3), m.group(1)))
    # 머리 앞의 문단(준비 문단) †: 앞 구간에 속함
    for idx, (i, lab, h) in enumerate(heads):
        j = heads[idx+1][0] if idx+1 < len(heads) else len(L)
        span = '\n'.join(L[i:j])
        nd = span.count('†')
        aj = '작성자 판단' in h
        if aj and nd == 0:
            # 앞 구간 끝(이 머리 바로 앞 준비 문단)에 †가 있는지
            pi = heads[idx-1][0] if idx > 0 else 0
            prev = '\n'.join(L[pi:i])
            # 앞 구간에서 마지막 ∎ 뒤의 †
            tail = prev.split('∎')[-1]
            print(f'장{c}:{i+1} {lab}: 작성자 판단인데 구간 안 † 0개; 머리 앞 준비 문단의 † {tail.count("†")}개')
        if (not aj) and nd > 0:
            # †가 증명 끝(∎) 뒤 준비 문단에 있으면 다음 진술의 것일 수 있음
            parts = span.split('∎')
            inproof = sum(p.count('†') for p in parts[:-1]) if len(parts) > 1 else nd
            after = parts[-1].count('†') if len(parts) > 1 else 0
            nxt = heads[idx+1][2] if idx+1 < len(heads) else ''
            print(f'장{c}:{i+1} {lab}: 작성자 판단 없음인데 † 증명 안 {inproof}개·∎ 뒤 {after}개 (다음 머리 작성자 판단: {"작성자 판단" in nxt})')

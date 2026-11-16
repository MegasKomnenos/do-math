import io
p = '작업_장부.md'
t = io.open(p, encoding='utf-8').read()
item = io.open('대조v2/수학검사2/_장부_항목_전체검토2수리회수.txt', encoding='utf-8').read().rstrip('\n') + '\n'
key = item.split('**')[1]
if key in t:
    print('항목 이미 있음')
else:
    marker = '\n## 재개 기록\n'
    i = t.index(marker)
    t = t[:i].rstrip('\n') + '\n\n' + item + marker + t[i + len(marker):]
    print('항목 삽입')
lines = t.split('\n')
for j, l in enumerate(lines):
    if l.startswith('- 갱신 시각:'):
        lines[j] = ('- 갱신 시각: 2026-11-15 08:2x (전체 독립 검토 2차의 수리 열셋(S1·S3–S12·SD·S11·SL) 회수·파생물 재생성 완료; '
                    '조립본 08:23 2,342,807바이트·11,217행, 진술 410·부록 D 43, 불변식·괄호·지위 서식·조사 0, 자리표시자 51; '
                    '3차 전체 독립 검토 열다섯(I1–I14, I7a·I7b; 이력 비공개) 진행 중, 장부 1.2 「쓰이는 장」 전수(SM) 병행; '
                    '결정 105·번역 측 전달은 3차 결과 뒤; 남은 자리표시자 D.15 10종·D.5 3종; 계산: D.5·D.34·D.15 H2 재실행 계속; PDF는 자리표시자 채운 뒤 재렌더)')
        print('현재 상태 갱신')
        break
io.open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))

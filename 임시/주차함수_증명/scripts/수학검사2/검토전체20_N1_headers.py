# 장1·장2 진술 머리 표지 검사: 쌍반점 하나, 식별자 꼴, 부록B 등재, 작성자 판단<->칼표 대응, 제타상수 사용처
import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
B=open('장v2/부록B.md',encoding='utf-8').read()
for f in ['장v2/장1.md','장v2/장2.md']:
    lines=open(f,encoding='utf-8').read().split('\n')
    i=0
    while i<len(lines):
        l=lines[i]
        m=re.match(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\w+):([^}]+)\}\}(.*?)\*\*',l)
        if m:
            kind,lab,rest=m.group(1),m.group(3),m.group(4)
            br=re.search(r'\[([^\]]*)\]\.?\s*$',rest.strip())
            tag=br.group(1) if br else None
            # 블록: 다음 진술 머리 또는 ### 전까지
            j=i+1; blk=[]
            while j<len(lines) and not re.match(r'\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{',lines[j]) and not lines[j].startswith('###'):
                blk.append(lines[j]); j+=1
            blk='\n'.join(blk)
            dag='†' in blk
            if tag is None:
                if kind!='정의': print(f'{f}:{i+1} {kind} {lab}: 표지 없음')
            else:
                if tag.count(';')!=1: print(f'{f}:{i+1} {lab}: 쌍반점 수 {tag.count(";")} -> [{tag}]')
                ids=re.findall(r'r[0-9a-f]{7}',tag.split(';')[-1]) if ';' in tag else []
                for r in ids:
                    if r not in B: print(f'{f}:{i+1} {lab}: 부록B에 없는 식별자 {r}')
                tail=tag.split(';')[-1].strip()
                if tail and tail!='표준' and not re.fullmatch(r'(r[0-9a-f]{7})(,\s*r[0-9a-f]{7})*',tail): print(f'{f}:{i+1} {lab}: 식별자 꼴 이상 [{tail}]')
                aj='작성자 판단' in tag
                if aj and not dag: print(f'{f}:{i+1} {lab}: 머리에 작성자 판단, 본문에 † 없음')
                if dag and not aj: print(f'{f}:{i+1} {lab}: 본문에 †, 머리에 작성자 판단 없음')
            i=j
        else:
            i+=1
print('done')

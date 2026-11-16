import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
p=r"C:\math\임시\주차함수_증명\장v2\장11.md"
lines=open(p,encoding='utf-8').read().split('\n')
want=sys.argv[1:] 
for ln in lines[20:42]:
    cells=[c.strip() for c in ln.strip().strip('|').split(' | ')]
    if want and not any(w in cells[0] for w in want): continue
    print('='*20)
    for i,c in enumerate(cells):
        print(f'[{i}] {c}\n')

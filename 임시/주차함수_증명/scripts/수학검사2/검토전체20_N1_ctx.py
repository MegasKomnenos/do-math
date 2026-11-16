# 고정 문자열 문맥 추출: python ctx.py 파일 '문자열' [앞뒤 글자수] [최대 건수]
import sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
f,s=sys.argv[1],sys.argv[2]; w=int(sys.argv[3]) if len(sys.argv)>3 else 150; mx=int(sys.argv[4]) if len(sys.argv)>4 else 5
n=0
for i,l in enumerate(open(f,encoding='utf-8'),1):
    j=l.find(s)
    while j>=0 and n<mx:
        print(f'[{i}] …{l[max(0,j-w):j+len(s)+w].strip()}…'); n+=1
        j=l.find(s,j+1)
print(f'(total shown {n})')

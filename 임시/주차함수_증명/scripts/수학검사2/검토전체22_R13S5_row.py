import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
n = int(sys.argv[1]); a = int(sys.argv[2]) if len(sys.argv)>2 else 0; b = int(sys.argv[3]) if len(sys.argv)>3 else 10**9
L = open('장부_v2.md', encoding='utf-8').read().split('\n')[n-1]
print(len(L)); print(L[a:b])

# 생성기 함수(build_A, build_C)를 메모리에서만 불러 현행 부록 A·C와 맞대어 본다(파일을 쓰지 않는다)
import io, sys, importlib.util, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
spec = importlib.util.spec_from_file_location('gen', 'scripts/부록_v2.py')
gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
ledger = io.open('장부_v2.md', encoding='utf-8').read()
C = gen.build_C(ledger)
curC = io.open('장v2/부록C.md', encoding='utf-8').read()
print('부록C 같음?', C == curC, len(C), len(curC))
if C != curC:
    a, b = curC.split('\n'), C.split('\n')
    for l in difflib.unified_diff(a, b, '현행 부록C', '재생성', lineterm='', n=0):
        print(l[:700])
texts = gen.chapter_texts()
body = '\n'.join(texts.values())
A, missing = gen.build_A(ledger, body, prune=False)
curA = io.open('장v2/부록A.md', encoding='utf-8').read()
print('부록A 같음?', A == curA, len(A), len(curA), 'missing', missing)
if A != curA:
    a, b = curA.split('\n'), A.split('\n')
    for l in difflib.unified_diff(a, b, '현행 부록A', '재생성', lineterm='', n=0):
        print(l[:500])

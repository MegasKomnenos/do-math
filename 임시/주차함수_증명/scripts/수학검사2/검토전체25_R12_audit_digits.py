# -*- coding: utf-8 -*-
"""R12: 부록 D.band102-integer (가)의 결과 줄에 적힌 하계의 표시 자리가 감사의 정확한 값을 넘지 않는지 본다.

기록의 감사 스크립트(원고_자료/r475ada3, r6b37c7e 사본)를 임시 폴더에 원래 배치(work/hermite, work/audit)로 복사해
그대로 돌리고, 스크립트가 저장하는 JSON의 final_k52_margin(정확 유리수의 float 변환)을 읽는다.
원고_자료/ 에는 쓰지 않는다.  사용: python -I 검토전체25_R12_audit_digits.py
"""
import os, sys, shutil, subprocess, tempfile, json, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = r'C:\math\임시\주차함수_증명\원고_자료'
A = os.path.join(B, 'r475ada3'); S = os.path.join(B, 'r6b37c7e', 'evidence', 'producer', 'audit')
T = tempfile.mkdtemp(prefix='r12audit_')
os.makedirs(os.path.join(T, 'work', 'hermite')); os.makedirs(os.path.join(T, 'work', 'audit'))
for f in ('audit_diag.py', 'audit_band.py', 'audit_param.py'): shutil.copy(os.path.join(A, f), T)
shutil.copy(os.path.join(S, 'audit_param_ext2.py'), T)
shutil.copy(os.path.join(A, 'hermite_exact.py'), os.path.join(T, 'work', 'hermite'))
shutil.copy(os.path.join(A, 'uv_5_19.json'), os.path.join(T, 'work', 'hermite'))
for f in ('uv_general_m1_120.json', 'uv_general_m1_600.json'): shutil.copy(os.path.join(S, 'work', 'hermite', f), os.path.join(T, 'work', 'hermite'))
def run(script, args, outjson):
    subprocess.run([sys.executable, '-I', script] + [str(a) for a in args], cwd=T, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    d = json.load(open(os.path.join(T, 'work', 'audit', outjson)))
    return {int(k[len('assembly_nu'):]): v['final_k52_margin'] for k, v in d.items() if k.startswith('assembly_nu')}
def trunc(x, nd): 
    import math
    return math.floor(x * 10 ** nd) / 10 ** nd
m = {}
m.update(run('audit_diag.py', [], 'audit_diag_out.json'))
m.update(run('audit_band.py', [], 'audit_band_out.json'))
text = dict(zip(range(1, 20), [0.2048,0.1938,0.1827,0.1717,0.1607,0.1496,0.1386,0.1275,0.1165,0.1054,0.0944,0.0833,0.0723,0.0613,0.0502,0.0392,0.0281,0.0170,0.0060]))
print('K1=10000 (본문 명제 4:analytic-transfer (가)와 부록 D 결과 줄의 열아홉 값):')
for nu in range(1, 20):
    flag = '' if m[nu] > text[nu] else '   <-- 하계가 적힌 값보다 작다'
    print('  nu=%2d  하계=%.10f  적힌 값=%.4f  넷째 자리 내림=%.4f%s' % (nu, m[nu], text[nu], trunc(m[nu], 4), flag))
m2 = run('audit_param.py', [11100] + list(range(20, 41)), 'audit_param_K11100_out.json')
text2 = {20:0.2173,22:0.1976,24:0.1779,26:0.1582,28:0.1300,30:0.1103,32:0.0906,34:0.0709,36:0.0511,38:0.0313,39:0.0130,40:0.0032}
print('K1=11100 (부록 D 결과 줄):')
for nu, t in text2.items():
    flag = '' if m2[nu] >= t else '   <-- 하계가 적힌 값보다 작다'
    print('  nu=%2d  하계=%.10f  적힌 값=%.4f%s' % (nu, m2[nu], t, flag))
m3 = run('audit_param_ext2.py', [14000, 96, 97, 98, 99, 100], 'audit_param_K14000_out.json')
text3 = {96:0.0244,97:0.0167,98:0.0090,99:0.0013}
print('K1=14000 (부록 D 결과 줄):')
for nu, t in text3.items():
    flag = '' if m3[nu] >= t else '   <-- 하계가 적힌 값보다 작다'
    print('  nu=%2d  하계=%.10f  적힌 값=%.4f%s' % (nu, m3[nu], t, flag))
print('  nu=100 하계=%.10f (적힌 값 -0.0063)' % m3[100])
shutil.rmtree(T, ignore_errors=True)

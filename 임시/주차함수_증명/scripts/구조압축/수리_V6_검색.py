# -*- coding: utf-8 -*-
# 수리 V6 — 다섯 파일의 토큰 전수 검색과 CR·바이트·줄 수. 토큰은 raw 문자열로 적는다(백슬래시 안전).
import io, os, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
files = ['장부_v2.md', '장v2/부록A.md', '장v2/부록B.md', '장v2/부록C.md', '구조표_v2.md']
toks = [r'9장', r'{{9:', r'`9:', r'첫째 증명', r'둘째 증명', r'두 증명', r'두 길', r'두 마무리', r'LRP', r'regen', r'FS(', r'lk_', r'P◇', r'P\Diamond', r'공유 입력', r'고유 입력', r'실질 잔여', r'둘째 층 한 칸', r'재생 원천', r'3132', r'3.6k', r'1.05', r'11.3', r'11.4', r'머리 합', r'출발 빚', r'무게 증분', r'감소율', r'평평한', r'D_k', r'varrho', r'dec_N', r'Upsilon', r'varphi^\flat', r'D-bound', r'increment-bounds', r'pair-rearrange', r'regen-vs-ledger', r'old-6-22', r'old-2-39', r'old-2-41', r'r5909c9e', r'r2fe0259', r'rc391829', r'r29b01e8', r'SRC', r'깊은 낙하', r'H_{\mathrm B}', r'lp_k', r'lpr_k', r'(6.37)', r'(6.38)', r'(6.27)', r'(4.14)', r'(4.13)', r'(4.10)', r'vartheta_\xi', r'P_t(k)', r'Pi^{\mathrm{up}}', r'mathfrak l_m', r'mathfrak k', r'mathfrak l(', r'둘째 문턱', r'1.009', r'BV_n\ge\Theta_n']
for f in files:
    t = io.open(os.path.join(ROOT, f), encoding='utf-8', newline='').read()
    print(f'== {f}: bytes {len(t.encode("utf-8"))}, CR {t.count(chr(13))}, lines {t.count(chr(10))+1}, 끝 개행 {t.endswith(chr(10))}')
    for tk in toks:
        n = t.count(tk)
        if n: print(f'   {tk!r}: {n}')
u = shutil.disk_usage('C:/'); print(f'== 디스크 C: 남은 {u.free/2**30:.1f} GiB / {u.total/2**30:.1f} GiB')

# -*- coding: utf-8 -*-
"""ZV5: scripts/_patch_README_세션파일.py 의 PARAS 가운데 window_mass_env 문단이 원고_자료/README.md 의 문단과 글자까지 같은지 확인한다(읽기만)."""
import ast, re, os
ROOT = r"C:\math\임시\주차함수_증명"
s = open(os.path.join(ROOT, 'scripts', '_patch_README_세션파일.py'), encoding='utf-8').read()
r = open(os.path.join(ROOT, '원고_자료', 'README.md'), encoding='utf-8').read()
m = re.search(r'("`세션_재계산/window_mass_env/`는 .*?")\),', s, re.S)
para = ast.literal_eval(m.group(1))
print('PARAS window_mass_env 문단 길이', len(para))
print('README에 같은 문단 있음:', para in r)
print('README에 제타 상수 절 있음:', 'zeta_constants/zeta_iv_out.txt`의 인증 구간을 바깥쪽으로 넓혀 넣는다' in r)

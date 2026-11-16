# -*- coding: utf-8 -*-
"""ZV5: 원고_자료/README.md 의 SHA-256 표에서 window_mass_env/ 의 행 일곱 개가 현행 파일의 해시와 같은지 확인한다(읽기만)."""
import hashlib, re, os
ROOT = r"C:\math\임시\주차함수_증명"
r = open(os.path.join(ROOT, '원고_자료', 'README.md'), encoding='utf-8').read()
ok = True
for rel in ['ia.py', 'check_table_iv_out.txt', 'cert_interval_iv_out.txt', 'cert_interval_iv_result.json', 'summarize_out.txt',
            'cert_interval_iv.py', 'check_table_iv.py', 'cert_Cb_iv.py', 'summarize.py', 'test_ia.py']:
    key = '세션_재계산/window_mass_env/' + rel
    h = hashlib.sha256(open(os.path.join(ROOT, '원고_자료', key), 'rb').read()).hexdigest()
    m = re.search(r'\| `' + re.escape(key) + r'` \| `([0-9a-f]{64})` \|', r)
    same = bool(m) and m.group(1) == h
    print(f"{rel:<32} README 행 {'있음' if m else '없음'}; 해시 일치: {same}")
    ok &= same
print('모두 일치:', ok)

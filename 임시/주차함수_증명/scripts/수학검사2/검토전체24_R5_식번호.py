# 검토전체24 R5: 장6 의 식 번호 태그와 참조 맞춤
import re
import io
import sys

s = io.open(sys.argv[1], encoding='utf-8').read()
tags = [int(x) for x in re.findall(r'\\tag\{6\.(\d+)\}', s)]
print('tags', len(tags), 'sequential', tags == list(range(1, len(tags) + 1)), tags[-1] if tags else None)
refs = sorted(set(int(x) for x in re.findall(r'\(6\.(\d+)\)', s)))
print('refs without tag', [r for r in refs if r not in tags])
print('tags never referenced', [t for t in tags if s.count('(6.%d)' % t) == 0])
print('other-chapter eq refs', sorted(set(re.findall(r'\((?:[1-57-9]|10)\.\d+\)', s))))
print('section refs', sorted(set(re.findall(r'(\d+\.\d+(?:\.\d+)?)절', s))))
print('CR present', '\r' in io.open(sys.argv[1], 'rb').read().decode('utf-8'))

# -*- coding: utf-8 -*-
"""중복 가족(F5·F6이 든 것 + X6 추가)의 분량 합산: 구성원 증명 행 수·본문 글자 수, 가장 긴 하나를 남긴 나머지 = 중복 추정."""
import json, os
ROOT = r"C:\math\임시\주차함수_증명"
g = json.load(open(os.path.join(ROOT,'scripts/구조압축/심사_X6_graph.json'),encoding='utf-8'))
bc = json.load(open(os.path.join(ROOT,'scripts/구조압축/심사_X6_bodychars.json'),encoding='utf-8'))
num2lab = {}; cnt = {}
for s in g['statements']:
    ch = s['label'].split(':')[0]
    if ch == 'D': continue
    cnt[ch] = cnt.get(ch,0)+1; num2lab[f"{ch}.{cnt[ch]}"] = s['label']
by = {s['label']: s for s in g['statements']}
FAM = {
 'F5-1 섬유 부호식(둘째 차분 한 식)': ['2.15','2.27','2.29','2.36','5.44','7.2','7.5','7.39','9.4','10.22','6.22'],
 'F5-2 사슬 통과 확률 θ(포개진 사슬 기대 개수)': ['2.37','2.38','2.47','2.48','2.49','2.52','5.45','6.51','8.25','9.5','9.40','10.3'],
 'F5-3 첫 층 생존 상계·Jensen 하계': ['6.1','8.10','10.11','10.21','8.7','10.26'],
 'F5-4 수준 질량 상하계': ['5.52','5.59','6.48','6.52','8.23','9.6','9.7','10.27','10.28'],
 'F5-5a 한 나무 재귀': ['5.2','6.14','8.1','9.22'],
 'F5-5b 사슬 공식 2.14 = 병합 항등식': ['2.14','9.14','9.15'],
 'F5-5c 다섯 몫 2.43 = 재생 항등식 9.25': ['2.43','9.25'],
 'F5-6 4.3절 = 7.4절(4.9·4.14 vs 7.50·7.51); 5.5.3절=2.9절': ['4.9','4.14','7.50','7.51'],
 'F5-7 갱신 인증서 셋': ['7.27','7.32','7.33'],
 'F5-8 Borel·Stirling 상계': ['2.38','5.47','7.69','8.6','9.8','9.43'],
 'F6-3 선형화 4.6(1–3단계) = 5.5(가)': ['4.6','5.5'],
 'F6-4 대각 비 5.50·6.21·9.2(+9.4)': ['5.50','6.21','9.2','9.4'],
 'F6-(가) 가중 최댓값 자르기 재귀': ['2.6','2.10','2.18','2.30','4.6','7.8','7.22','7.36','2.8','7.11','5.5'],
 'X6 나무 곡률 x_t(y) 표현(5.5.1절·5.49·6.20·6.34·6.35)': ['5.49','6.20','6.34','6.35'],
 'X6 최댓값 자리 분해(2.18·2.30·4.5·7.18·7.36·7.40)': ['2.18','2.30','7.18','7.36','7.40'],
}
out = []
tot_dup_lines = 0; tot_dup_chars = 0
for name, mem in FAM.items():
    rows = []
    for n in mem:
        lab = num2lab.get(n)
        if not lab: rows.append((n,'?',0,0)); continue
        s = by[lab]; rows.append((n, lab, s['proof_lines'], bc[lab]))
    pl = sorted(r[2] for r in rows); ch = sorted(r[3] for r in rows)
    dup_l = sum(pl) - (max(pl) if pl else 0); dup_c = sum(ch) - (max(ch) if ch else 0)
    tot_dup_lines += dup_l; tot_dup_chars += dup_c
    out.append(f"## {name}\n  구성원(번호 라벨 증명행 본문글자): " + '; '.join(f"{r[0]} {r[1].split(':')[1] if ':' in r[1] else r[1]} {r[2]} {r[3]}" for r in rows))
    out.append(f"  증명행 합 {sum(pl)} / 최장 제외 {dup_l};  본문글자 합 {sum(ch)} / 최장 제외 {dup_c}")
out.append(f"\n가족 합(겹침 미제거): 최장 제외 증명행 {tot_dup_lines}, 본문글자 {tot_dup_chars}")
open(os.path.join(ROOT,'scripts/구조압축/심사_X6_dupfam.txt'),'w',encoding='utf-8').write('\n'.join(out))
print('\n'.join(out))

# -*- coding: utf-8 -*-
"""ZV11 — 외부 피드백 넷째 묶음(묶음 C, 장6) 검토의 자리 확인 스크립트.

첫째 단계: 바꾸기로 한 여섯 자리의 「전」 문자열이 장v2/장6.md에 꼭 한 번씩 있는지,
「후」 문자열은 아직 없는지, 그리고 2장 라벨(2.11·2.25·2.38)의 출현 수를 센다.
둘째 단계 뒤: --after 를 주면 「후」 문자열이 한 번씩 있고 「전」은 없음을 확인한다.
파일은 읽기만 한다. 실행: python -I scripts/수학검사2/검토_외부피드백_1116_ZV11_자리확인.py [--after]
"""
import sys, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATH = os.path.join(ROOT, '장v2', '장6.md')

# (항목, 전, 후) — 전·후 모두 고정 문자열(정규식 아님).
CHANGES = [
    ('C4-240 (6.9 증명; 2.25(가)·(다), 출처를 (6.16)의 증명으로 적음)',
     r"$g$가 증가하고 $N+1>k$이므로 $\epsilon_N\ge0$이고, $g<1$에서 $\epsilon_N\le1-g(k)$이며, (6.16)의 증명에서 본 $g(k)\ge1-3/(2k)+1/(2k^2)$에서 $1-g(k)\le3/(2k)$다.",
     r"보조정리 {{2:old-2-26}}(가)에 따라 $g$가 증가하고 $N+1>k$이므로 $\epsilon_N\ge0$이고, 같은 보조정리 (다)의 $g<1$에서 $\epsilon_N\le1-g(k)$이며, 그 하계 $g(k)\ge1-3/(2k)+1/(2k^2)$에서 $1-g(k)\le3/(2k)$다."),
    ('C4-280 (6.11 (가) 증명; 2.25(가))',
     r"한편 $t-1\ge k$와 $g$의 증가에서 $k(1-g(t-1))\le k(1-g(k))$이고,",
     r"한편 $t-1\ge k$와 $g$의 증가(보조정리 {{2:old-2-26}}(가))에서 $k(1-g(t-1))\le k(1-g(k))$이고,"),
    ('C5-435 (6.12 미룬 증명 d=2; 2.25(나)·(다))',
     r"$\pi_{y+1}(y+1)=\mathrm{Bor}(1)\mathrm{Bor}(y+1)/\mathrm{Bor}(y+2)=e^{-g(y+1)}\ge e^{-1}$이므로 $c_{y+1}(y)\ge e^{-1}/(y+1)$이다.",
     r"$\pi_{y+1}(y+1)=\mathrm{Bor}(1)\mathrm{Bor}(y+1)/\mathrm{Bor}(y+2)=e^{-g(y+1)}\ge e^{-1}$이므로(보조정리 {{2:old-2-26}}(나)·(다)) $c_{y+1}(y)\ge e^{-1}/(y+1)$이다."),
    ('C6-764 (6.37 (가) 증명; 2.11)',
     r"사슬 밖의 꼭짓점은 변위가 $y-1$ 이하이므로 최대 변위가 $y$ 이상일 조건부 확률은 $1-\prod_{i\le L}y/(y+q_i)$이고,",
     r"사슬 밖의 꼭짓점은 변위가 $y-1$ 이하이므로, 정리 {{2:old-2-11}}에 따라 최대 변위가 $y$ 이상일 조건부 확률은 $1-\prod_{i\le L}y/(y+q_i)$이고,"),
    ('C6-986 (6.47 (가) 증명; 2.11)',
     r"사슬이 주어지면 크기 $k-1$ 이하의 꼭짓점은 변위가 $k-2$ 이하이므로, 최대 변위가 $k-1$일 조건부 확률은",
     r"사슬이 주어지면 크기 $k-1$ 이하의 꼭짓점은 변위가 $k-2$ 이하이므로, 정리 {{2:old-2-11}}에 따라 최대 변위가 $k-1$일 조건부 확률은"),
    ('C7-1065 (6.49 (다) 증명; 2.38(라))',
     r"(Robbins)과 $\Psi(d)\le0.7979\sqrt d$에서 $\mathrm{Ren}(d+1)/\Psi(d)\ge1/(5d)$다.",
     r"(Robbins)과 $\Psi(d)\le0.7979\sqrt d$(보조정리 {{2:old-2-37}}(라))에서 $\mathrm{Ren}(d+1)/\Psi(d)\ge1/(5d)$다."),
]

LABELS = ['{{2:old-2-11}}', '{{2:old-2-26}}', '{{2:old-2-37}}', '{{2:old-2-45}}', '{{2:old-2-31}}', '{{2:old-2-6}}']


def main():
    after = '--after' in sys.argv
    raw = open(PATH, 'rb').read()
    print('파일', PATH, '바이트', len(raw), 'CRLF', raw.count(b'\r\n'), 'LF', raw.count(b'\n'))
    text = raw.decode('utf-8')
    lines = text.split('\n')
    ok = True
    for name, before, after_s in CHANGES:
        nb = text.count(before)
        na = text.count(after_s)
        where_b = [i + 1 for i, l in enumerate(lines) if before in l]
        where_a = [i + 1 for i, l in enumerate(lines) if after_s in l]
        if not after:
            good = (nb == 1 and na == 0)
        else:
            good = (nb == 0 and na == 1)
        ok &= good
        print(('OK ' if good else 'NG ') + name, '| 전', nb, where_b, '| 후', na, where_a)
    print('--- 2장 라벨 출현 수(장6 전체)')
    for lab in LABELS:
        rows = [i + 1 for i, l in enumerate(lines) if lab in l]
        print(lab, len(rows), rows)
    print('결과:', '모두 맞음' if ok else '어긋난 자리 있음')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.exit(main())

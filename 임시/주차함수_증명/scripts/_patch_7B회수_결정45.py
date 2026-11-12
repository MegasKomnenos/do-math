# -*- coding: utf-8 -*-
"""7B 2차 대조 회수: 세션 결정 45(4장 보조정리 gauss-contraction)를 적고, 작업 장부에 회수·재개·4장 파견 항목과 집필자 ID 표를 더한다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


D45 = (
    "45. **4장의 수축 부등식·Hermite 하계를 진술로(2026-11-12 밤; 7B 2차 대조 #2·#3·#6).** 7B의 `{{7:hermite-nu}}`가 `{{4:gauss-coeff}}` 증명 안의 단계(3차 보정 근사 $\\hat\\upsilon$에 대한 수축 부등식, Hermite 하계 $\\mathcal H_0=4$)를 가리켰다. 증명 안 단계는 다른 장이 가리킬 수 없으므로(지침 4.2) 4장이 보조정리 `{{4:gauss-contraction}}`로 그 사실을 조건과 함께 진술하고(증명은 옮김; gauss-coeff의 증명은 그것을 가리킴), "
    "7B는 4장의 글자($\\upsilon^\\circ$, $\\hat\\upsilon$, $\\mathfrak a$, $\\mathfrak x$, $\\vartheta$, $\\kappa$, $\\mathfrak g$)로 진술을 고쳐 쓰며 범위를 증명이 받치는 것으로 줄인다. 4장 집필자(a7848940efd5605cc)를 재개해 보조정리를 쓰게 하고, 7B는 2차 재개 때 그 진술에 맞춘다.\n"
)


def patch_decisions(s):
    if "45. **4장의 수축 부등식" in s:
        return s
    assert "44. **Lagrange 역변환의 음의 거듭제곱" in s
    return s.rstrip("\n") + "\n" + D45


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


ENTRY = (
    "- 2026-11-12 23:4x **7B 2차 대조 회수, 7B 집필자 1차 재개, 4장 보조정리 파견**: 7B 2차 대조(fable-high, 49분; `대조v2/장7B_2차대조.md`; 세션 결정 42·43을 받아 「다른 장과 맞추어야 할 결정」에 ⇐ 방향의 입력 다섯 범위를 기록 원문으로 판정해 적음) — 상 9(841–2000 열별 인증 진술 부재→7A의 theorem-G-prime, hermite-nu의 $\\hat\\upsilon$ 정의·범위·글자 오류 셋, qstar-implies-wlflat (가) 불완전·394행 old-6-9 오인용, explicit-bounds (다) 전개 슬립, 등급 이름, 부록 D band102 식 누락, 7A 부록 D 미확인), 중 27, 하 10; 증명 46개 재유도(전 단계 확인 41; 작성자 판단 셋 성립; 정정값 셋 일치; 넓힌 6.17(가) 증명됨). "
    "세션 결정 45(4장 `{{4:gauss-contraction}}` 보조정리). 7B 집필자(ac658a988f71a1f55) 1차 재개: 7A에 기대지 않는 결함 전부 + 결정 42·43·45·38 + 세션 발견(등급 머리 넷, 예약 글자 9곳, 부록 D 2곳) + 7A와 공유하는 글자는 표로만; 2차 재개(7A 최종 글자·새 라벨·4장 보조정리 진술 맞춤)는 7A·4장 회수 뒤. 4장 집필자(a7848940efd5605cc) 재개: 7B가 필요로 하는 사실을 확인해 `{{4:gauss-contraction}}`로 진술·증명 옮김, 장4_집필대조에 「후속 수정」 절. "
    "사전 최종 정리에 더할 것(7B 2차 대조): $E^\\sharp(\\cdot;z)$·$E^\\sharp_n$ 이중 배정, 7.4 묶음 $\\mathfrak r_t$ 대 전역 $\\mathfrak r_N$, 뿌리 자리 법칙 정의 절 7.5→7.4, 낱말 껍질·삼중·쌍별 도달·Green 원자 등록, 「줄기」 두 뜻 해소. "
    "집필자 ID 표(재개용): 1장 ad205791a711110e9, 2장 a8f572e5f436cfa00, 3장 a5e246a599cd7e563, 4장 a7848940efd5605cc, 5A a25a6ba133fe1200a, 5B a553851903def48b5, 6장 acafd99850c74a3fb, 7A a1148e6467d84da2c, 7B ac658a988f71a1f55, 8장 a1d56e4463a4a1ac1, 9장 aec18314f7f006454, 10장 a35b8fce3db7355bd; 설계 a31b878fbba25e2de; 2차 대조 6장 a034b02a01474e198(재개 중), 5B a21bcc1a60b141225, 5A adcb51b174b33000a."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "7B 2차 대조 회수, 7B 집필자 1차 재개" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("1·2·3·4·8·9·10장 완료, 7A 수정 중, 6·5B·7B·5A 2차 대조 중)", "1·2·3·8·9·10장 완료, 4장 보조정리 추가 중, 7A·7B 수정 중, 6·5B·5A 2차 대조 중)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)

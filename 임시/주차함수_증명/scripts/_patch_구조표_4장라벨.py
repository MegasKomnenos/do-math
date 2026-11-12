# -*- coding: utf-8 -*-
"""구조표 4.3 셀에 새 보조정리 라벨 둘(gauss-contraction·borel-tail-arc; 세션 결정 45·46)을 적어 라벨 등록부 재생성이 집어 가게 하고,
작업 장부에 4장 둘째 회수 항목을 더한다."""
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


def patch_struct(s):
    a = "Gauss 계수 단계와 두 보정의 수직선 적분을 보조정리 `{{4:gauss-coeff}}`·`{{4:two-corrections}}`로 조직"
    assert s.count(a) == 1, s.count(a)
    if "{{4:gauss-contraction}}" in s:
        return s
    return s.replace(a, a + ", 그 증명 안 단계 가운데 다른 장이 쓰는 것은 보조정리 `{{4:gauss-contraction}}`(Hermite 비의 수축 부등식과 Hermite 수의 하계; 7.4의 hermite-nu가 쓴다; 세션 결정 45)·`{{4:borel-tail-arc}}`(Borel 꼬리의 전개와 호 위 상계; 5.6이 쓴다; 세션 결정 46)로 진술")


rw(os.path.join(ROOT, "구조표_v2.md"), patch_struct)


ENTRY = (
    "- 2026-11-12 23:5x 4장 집필자 둘째 회수(결정 46, 5분): `{{4:two-corrections}}` 바로 앞에 보조정리 `{{4:borel-tail-arc}}`(Borel 꼬리의 전개와 호 위 상계; [rce3dc75] 보조정리 V의 (V6)·§7.1 꼬리 상계; 「비형식 증명, 작성자 판단」) — (가) 옛 (4.13) 전개와 오차 $(2\\pi)^{-1/2}\\varepsilon^3e^{-\\operatorname{Re}w}[\\frac59+\\frac23|w|+\\frac{13}{12}|w|^2]$, (나) $|\\mathrm{Bor}^{\\mathrm{tail}}_k(\\varsigma)|\\le(1+e^{1+|\\varsigma|})\\exp(k(\\log|\\varsigma|+1-\\operatorname{Re}\\varsigma)_+)$, $|\\varsigma|\\le1.079$에서 상수 9. two-corrections 증명은 그것을 가리킴; 4장 식 번호 이동(새 (4.11); 옛 (4.11)→(4.12), (4.12)→(4.13)). 4장 라벨 순서 14개. 5B 집필자에게 즉시 전달(5.6의 $\\mathfrak w_j\\to W_j$, $h(w)\\to\\Omega(w)$, $\\mathfrak S_k\\to S_k$, (4.13) 참조→보조정리 (가), 식 번호 직접 인용 금지). 구조표 4.3 셀에 두 라벨 등록(라벨 등록부 재생성용). **4장 완료**(세션 일관성 검토 대기)."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "4장 집필자 둘째 회수(결정 46" in s:
        return s
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
    s = s.replace("1·2·3·8·9·10장 완료, 4장 보조정리 추가 중, 7A·7B·5B 수정 중, 6·5A 2차 대조 중)", "1·2·3·4·8·9·10장 완료, 7A·7B·5B 수정 중, 6·5A 2차 대조 중)")
    return s


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)

# -*- coding: utf-8 -*-
"""작업 장부: 4장 두 보조정리의 글자 교체 회수, 7A의 7B 요구 셋 반영 회수, 후속 재개(4장 e-integral, 7B 맞춤)."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()

ENTRY = (
    "- 2026-11-13 00:5x 4장 글자 교체 회수(결정 53, 8분): `{{4:gauss-contraction}}`·`{{4:borel-tail-arc}}`와 gauss-coeff·two-corrections·old-4-7·e-integral 증명·부록D_장4에서 일괄 치환 — $\\mathfrak a\\to\\mathfrak N$, $\\mathfrak u,\\mathfrak v\\to\\mathfrak U,\\mathfrak W$, $\\xi_j\\to\\mathfrak x_j$, 인수 $\\xi\\to\\iota$, $\\gamma(\\xi)\\to2\\upsilon^\\circ-1$, $\\mathfrak k_i\\to\\mathfrak C_i$, 생성 변수 $\\tau\\to\\mathfrak Y$, $\\varepsilon\\to k^{-1/2}$(풀어 씀), $S_k(w)\\to\\mathrm{Bor}^{\\mathrm{sum}}_k(\\phi)$, $w\\to\\phi$, $\\Omega\\to\\mathrm{Bor}^{\\mathrm{ld}}$, 점 $\\varsigma\\to\\mathfrak Z$, 적분 변수 $\\eta\\to\\iota$, $\\mathfrak b_j(\\varsigma)\\to\\mathrm{Bor}(j;\\varsigma)$(4.3 국소; 5A의 unit-circle·hat-normalization이 쓰므로 5A도 맞춰야 함); gauss-coeff 둘째 단계·(4.8)의 $\\kappa^2$ 계수를 일반식 $506+97\\nu+5\\nu^2+\\cdots$로. 남은 주의: e-integral 진술의 $\\tau$·$\\varsigma$·$\\Lambda$ → 같은 방식으로 교체 지시($\\Lambda$는 1.2의 4.3 전역이면 유지). "
    "7A 소수정 회수(9분): flat-threshold $\\upsilon,\\upsilon'\\to f,f^\\ast$(10곳); xcert-partAB 「결과」에 층별 $\\varsigma$ 하계(B층 $k=2002$에서 5.31467 최소; 전 층 $\\ge5.3146$; 자료 세 파일 추가); $\\mathfrak m_\\Pi=k\\rho_k$를 pole-unique (나) 진술로(7.3 본문 714행 참조 수정). **7A 완료.** "
    "7B 집필자에게 마무리 지시(gauss-contraction 새 글자로 hermite-nu 맞춤; polar-PD의 5.31468→5.31467; 𝔪_Π 참조를 pole-unique (나)로). 5A·5B 글자 맞춤(Bor(j;ς)·e-integral 새 글자·borel-tail-arc 새 글자)은 4장 e-integral 회수 뒤 한 번에."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "4장 글자 교체 회수(결정 53" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
s = s.replace("1·2·3·6·8·9·10장 완료, 4장 보조정리 글자 교체 중, 7A 소수정 중, 5A 수정 중, 5B·7B는 4장 글자 맞춤 대기)", "1·2·3·6·7A·8·9·10장 완료, 4장 e-integral 글자 교체 중, 5A 수정 중, 7B 마무리 중, 5B는 4장 글자 맞춤 대기)")
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md (4장 글자 교체·7A 소수정)")

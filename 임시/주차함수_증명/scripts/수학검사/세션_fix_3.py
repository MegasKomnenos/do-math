# -*- coding: utf-8 -*-
"""10.7절 둘째 고리 「(V) ⇒ V*」 제거(사용자 확인 뒤). 근거: 셋째 고리(명제 old-6-20)는 머리·증명 모두 정리 V-all(판정 V)에 기대고,
V*는 장10 815행 밖 어디에도 쓰이지 않으며(7A·7B·9·11장 0), 명제 old-6-18(사다리)도 장10에서 815행과 도입 9행에서만 언급된다.
따라 고치는 것: 고리 번호(셋째→둘째 … 여섯째→다섯째, 「여섯 고리」→「다섯 고리」), 장10 도입의 넷→셋, 장11 11.3 표의 사다리 행 제거와 「셋째 고리」 참조, 장6 도입의 사용처 문장. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def apply(path, edits):
    p = os.path.join(ROOT, path)
    s = io.open(p, encoding="utf-8").read(); n = 0
    for old, new in edits:
        c = s.count(old)
        if c == 1:
            s = s.replace(old, new); n += 1
        elif new and new in s:
            pass
        elif c == 0 and not new:
            pass
        else:
            print("앵커 수", c, ":", path, old[:50])
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print(path, "고침", n)


apply("장v2/장10.md", [
    ("둘째 고리는 (V) ⇒ $\\mathsf V^\\ast$다. (V)는 정리 {{6:V-all}}으로 모든 $m\\in[k,2k]$에서 성립하고, 명제 {{6:old-6-18}}의 사다리에 따라 확률 무게의 꼬리합의 부호가 임계 기울임 무게의 꼬리합 $\\mathsf V^\\ast$의 부호로 옮겨 간다.\n\n",
     ""),
    ("셋째 고리는 원천 쪽 ∧ $\\mathsf V$ ∧ $\\mathsf Q^\\star_2$ ⇒ 열 $3131$ 이상의 $\\mathsf Q^\\star$다.",
     "둘째 고리는 원천 쪽 ∧ $\\mathsf V$ ∧ $\\mathsf Q^\\star_2$ ⇒ 열 $3131$ 이상의 $\\mathsf Q^\\star$다. (V)는 정리 {{6:V-all}}으로 모든 $m\\in[k,2k]$에서 성립한다."),
    ("넷째 고리는 열 $2001$에서 $3130$까지의", "셋째 고리는 열 $2001$에서 $3130$까지의"),
    ("다섯째 고리는 $\\mathsf Q^\\star$ ⇒ $\\mathsf W_L^\\flat$", "넷째 고리는 $\\mathsf Q^\\star$ ⇒ $\\mathsf W_L^\\flat$"),
    ("여섯째 고리는 $\\mathsf W_L^\\flat$ ⇒", "다섯째 고리는 $\\mathsf W_L^\\flat$ ⇒"),
    ("위에 적은 여섯 고리를 차례로 이으면 된다.", "위에 적은 다섯 고리를 차례로 이으면 된다."),
    ("그 추정은 넷이다. 첫 층의 확률 꼬리합이 음이 아니라는 판정 $\\mathsf V$, 그 판정을 다른 무게로 잰 꼬리합의 판정으로 옮기는 사다리, 크기가 하나 늘 때 최대 변위가 같은 수준에 머무는 몫을 수준 질량으로 누르는 머묾 법칙, 벌크 수준 질량의 상계다(정리 {{6:V-all}}, 명제 {{6:old-6-18}}, 정리 {{6:old-8-13}}·{{6:old-8-12}}).",
     "그 추정은 셋이다. 첫 층의 확률 꼬리합이 음이 아니라는 판정 $\\mathsf V$, 크기가 하나 늘 때 최대 변위가 같은 수준에 머무는 몫을 수준 질량으로 누르는 머묾 법칙, 벌크 수준 질량의 상계다(정리 {{6:V-all}}, 정리 {{6:old-8-13}}·{{6:old-8-12}})."),
])
apply("장v2/장11.md", [
    ("| 사다리: 명제 {{6:old-6-18}} | 없음 | 10.7절 둘째 고리 |\n", ""),
    ("10.7절 셋째 고리(직접)", "10.7절 둘째 고리(직접)"),
])
apply("장v2/장6.md", [
    ("명제 {{6:old-6-18}}, 정리 {{6:old-8-13}}·{{6:old-8-12}}, 따름정리 {{6:V-core-identity}}·{{6:DD-lower-bound}} 등은 둘째 증명(10장)만 쓴다.",
     "정리 {{6:old-8-13}}·{{6:old-8-12}}, 따름정리 {{6:V-core-identity}}·{{6:DD-lower-bound}} 등은 둘째 증명(10장)만 쓴다. 사다리(명제 {{6:old-6-18}})는 어느 증명의 입력도 아니며, 6.6절의 논법을 미리 보이는 구실만 한다."),
])

# -*- coding: utf-8 -*-
"""둘째 판 장(조각)의 2차 대조 파견문 생성.

사용: python _gen_2차대조v2_파견문.py 5A [--out 파견/2차대조v2_5A_파견문.md]
입력: 공통 계약 파견/집필_2차대조_공통_v2.md, 장 파견문 파견/장v2_<태그>_파견문.md, 장 파일 장v2/장<태그>.md,
      부록 D 조각 장v2/부록D_장<태그>.md(있으면), 집필 대조 대조v2/장<태그>_집필대조.md.
"""
import argparse
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COMMON = r"C:\math\임시\주차함수_증명\파견\집필_2차대조_공통_v2.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tag", help="장 번호 또는 조각 태그(예 6, 5A)")
    ap.add_argument("--out")
    args = ap.parse_args()
    tag = args.tag
    brief = os.path.join(ROOT, "파견", f"장v2_{tag}_파견문.md")
    chapter = os.path.join(ROOT, "장v2", f"장{tag}.md")
    dpart = os.path.join(ROOT, "장v2", f"부록D_장{tag}.md")
    compare = os.path.join(ROOT, "대조v2", f"장{tag}_집필대조.md")
    for p in (brief, chapter, compare):
        if not os.path.exists(p):
            raise SystemExit(f"없음: {p}")
    size = os.path.getsize(chapter)
    n_heads = sum(1 for ln in io.open(chapter, encoding="utf-8") if ln.startswith("**") and "{{" in ln.split("**")[1] if ln.count("**") >= 2)
    out_path = args.out or os.path.join(ROOT, "파견", f"2차대조v2_{tag}_파견문.md")
    L = []
    L.append(f"# 파견문: 둘째 판 장{tag}의 2차 대조\n")
    L.append("## 임무와 목적\n")
    L.append(f"다른 에이전트가 쓴 `{chapter}`({size:,}바이트, 진술 머리 약 {n_heads}개)를 공통 계약 `{COMMON}`의 일곱 축(가 단계별 재유도, 나 기록 대조, 다 충실성, 라 언급 금지·사족, 마 사전·라벨·표지, 바 부록 D·자리 표시자, 사 작문·구조)으로 대조하고 보고서 `C:\\math\\임시\\주차함수_증명\\대조v2\\장{tag}_2차대조.md`를 쓴다. 공통 계약을 먼저 전문으로 읽는다. 이 장의 범위·출처·특별 지시는 집필자가 받은 파견문 `{brief}`에 있고(축자 발췌 포함), 집필자가 적은 대조 기록은 `{compare}`에 있다. 집필자의 대조 기록은 검사 대상이지 근거가 아니다. 기록 원문을 직접 연다.\n")
    L.append("## 수신 컨텍스트\n")
    L.append("파견문 밖의 대화는 전달되지 않는다. 읽을 파일: 위 넷, 그리고 공통 계약 2절이 드는 입력(장부 v2, 구조표 v2, 의존지도 v2, 라벨 등록부 v2, 집필 공통 지침 v2, 기록 원문). `C:\\math\\CLAUDE.md`, `C:\\math\\.claude\\`, `C:\\math\\.agents\\`를 열지 않는다. 연구 인스턴스는 읽기만 한다. 장 파일을 고치지 않는다(지적만 적는다).\n")
    if os.path.exists(dpart):
        L.append(f"부록 D 조각 `{dpart}`도 대조 대상이다(축 바).\n")
    else:
        L.append("이 장(조각)에는 부록 D 조각이 없다. 장 파견문의 「부록 D 항목」 표에 항목이 있는데 조각이 없으면 축 바의 지적으로 적는다.\n")
    L.append("## 완료 조건과 반환\n")
    L.append("보고서가 공통 계약의 서식(축별 표, 「증명별 재유도 표」, 중대 사항, 통계)을 따르고, 전개 대상 증명마다 재유도 표에 행이 있으며, 반환이 공통 계약의 반환 서식을 따른다.\n")
    io.open(out_path, "w", encoding="utf-8", newline="\n").write("\n".join(L))
    print("written", out_path)


if __name__ == "__main__":
    sys.exit(main())

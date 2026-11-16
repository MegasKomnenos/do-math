# -*- coding: utf-8 -*-
"""부록 생성기(부록_v2.py)에 두 손질을 넣는다. 멱등.
(1) clean(): 첫 판의 절·행 위치 표지 「(3.3·937)」, 설계 질문 번호 「Qnn」, 대조 확인 표지 「(확인)」을 걷어 낸다.
(2) build_C(): 기록 이름 ↔ 진술 표의 같은 행 중복을 한 번만 적는다."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "scripts", "부록_v2.py")

PRE = '''def preclean(text):
    """첫 판의 절·행 위치 표지 「(3.3·937)」·「(7·8장)」, 설계 질문 번호 「Qnn」, 대조 확인 표지 「(확인)」을 걷어 낸다."""
    text = re.sub(r"\\((?:[\\d.]+·)+[\\d.]+장?(?:,\\s*(?:[\\d.]+·)+[\\d.]+장?)*\\)", "", text)
    text = re.sub(r"\\(Q\\d+\\)", "", text)
    text = re.sub(r";\\s*Q\\d+(?=[;)])", "", text)
    text = re.sub(r"\\(확인;\\s*", "(", text)
    text = text.replace("(확인)", "")
    return text


def clean(text):
'''
OLD_DEF = "def clean(text):\n"
OLD_DOC = '    """사전의 뜻·비고 열에서 작업 메모(첫 판 참조, 세션 결정, 대조·회수 기록)를 걷어 낸다. 괄호 단위와 쌍반점 조각 단위로."""\n'
NEW_DOC = OLD_DOC + "    text = preclean(text)\n"
OLD_ROW = '        out.append(f"| {recname} | {kind} {label} | {name} |")\n'
NEW_ROW = ('        line = f"| {recname} | {kind} {label} | {name} |"\n'
           '        if line in out:\n'
           '            continue\n'
           '        out.append(line)\n')


def main():
    s = io.open(P, encoding="utf-8").read()
    changed = False
    if "def preclean(text):" not in s:
        assert s.count(OLD_DEF) == 1 and s.count(OLD_DOC) == 1
        s = s.replace(OLD_DEF, PRE, 1).replace(OLD_DOC, NEW_DOC, 1)
        changed = True
        print("clean(): preclean 추가")
    if OLD_ROW in s:
        s = s.replace(OLD_ROW, NEW_ROW, 1)
        changed = True
        print("build_C(): 중복 행 제거")
    if changed and "--dry" not in sys.argv:
        io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    elif not changed:
        print("이미 반영")


if __name__ == "__main__":
    main()

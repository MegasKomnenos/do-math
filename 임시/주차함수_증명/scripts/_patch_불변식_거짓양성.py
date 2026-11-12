# -*- coding: utf-8 -*-
"""시험 조립(23:2x)에서 드러난 불변식 v2의 거짓 양성 셋을 좁히고, 2장 부록 D의 코드 변수 문장을 결정 40의 꼴로 고치며,
장부 v2 재생성이 세션 패치를 덮어쓴 사실을 작업 장부에 적는다."""
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


def patch_checker(s):
    a = 'r"사슬 밖", '
    assert s.count(a) == 1
    s = s.replace(a, 'r"사슬 밖(?!의 (?:꼭짓점|점|자리|나무|부분|성분))", ')
    b = 'DISTINCTION = [r"다른 (?:양|기호|함수|대상|수|뜻|명제|결과|분해|자름|말)(?:이다|이고|이며|이라|과|와|로)", '
    assert s.count(b) == 1
    s = s.replace(b, 'DISTINCTION = [r"(?:[와과은는]|서로) 다른 (?:양|기호|함수|대상|수|뜻|명제|결과|분해|자름|말)(?:이다|이고|이며|이라|과|와|로)", ')
    c = '            extra = re.sub(r"[,，·\\s은는이가의와과에서도만\\(\\)]+|항등식'
    assert s.count(c) == 1, s.count(c)
    s = s.replace(c, '            extra = re.sub(r"의존(?:하는)?|(?:\\([가-힣]\\))+", "", extra)\n' + c)
    return s


rw(os.path.join(ROOT, "scripts", "불변식_v2.py"), patch_checker)


def patch_d2(s):
    a = "기록의 $B$는 이 글의 $\\mathfrak b-1$이다."
    if s.count(a) == 1:
        s = s.replace(a, "코드의 변수 `B`는 이 글의 $\\mathfrak b-1$이다.")
    return s


rw(os.path.join(ROOT, "장v2", "부록D_장2.md"), patch_d2)


ENTRY = (
    "- 2026-11-12 23:2x 세션 몫 처리: 짧은 식별자 전 파일 치환(`scripts/_sweep_식별자.py`: rba2ecf→rba2ecf4, ra7615a→ra7615a0, r9e782→r9e782f5; 장v2·구조표·의존지도·장부·명세 JSON·출처목록·명세v2_수정·META), 8장 `{{8:explicit-bounds}}` 머리 「표준(Robbins, Euler–Maclaurin)」→「표준」, "
    "2장 부록 D 「기록의 $B$는 …」→「코드의 변수 `B`는 이 글의 $\\mathfrak b-1$이다」(결정 40), 불변식 v2 거짓 양성 셋 좁힘(「사슬 밖의 꼭짓점」 제외, 구별 문장은 와·과·은·는·서로 뒤의 「다른 …」만, 「…에 의존」 절을 낯선 낱말에서 제거). "
    "**발견**: 설계 에이전트는 `장부_v2.md`를 자기 자료에서 재생성해 통째로 쓰므로 세션이 1·2·3·5·6·7절에 직접 넣은 패치가 덮인다 — `_patch_9장_2차대조.py`의 3절 두 행(조건부 수준 질량 $c_N(k-1)/s_N(k)$·7.5, 증가 시작점 9.1)과 5절 여유의 예약 $h$ 제거가 23:0x 재생성에서 사라짐(그 전의 패치 — 띠·절반·첫 층·상자·무거운은 둘째 반영에 흡수되어 남음). "
    "방침: 사전의 세션 몫은 설계 에이전트의 최종 정리 지시에 넣어 그 자료에 반영시키고, 최종 정리 뒤 `_patch_9장_2차대조.py`를 다시 돌려 검산한다(멱등). 그 뒤로는 설계 에이전트를 재개하지 않는다."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "짧은 식별자 전 파일 치환" in s:
        return s
    return s.replace(old, "\n" + ENTRY + "\n" + old)


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)

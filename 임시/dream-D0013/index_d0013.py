P="기억/색인.md"; A="기억/색인_아카이브.md"
t=open(P,encoding="utf-8",newline="").read(); nl="\r\n" if "\r\n" in t else "\n"
assert t.count("반영 수위: M-0657 · D-0012")==1
t=t.replace("반영 수위: M-0657 · D-0012","반영 수위: M-0657 · D-0013")
L={
"L-0006":"[기억 하네스 운영] -- 통제 경계, 세 층의 역할, 읽기 경로, 유지와 삭제, 세션 경계(병행 세션의 스테이징 혼입과 대상 지정 커밋, 공유 색인의 한계)와 근거 경로의 추적 상태, 저장소를 줄이는 삭제와 기억의 근거(회수 커밋 dbde17f4·90478bc0^, 중첩 무시 규칙, 지운 개념의 정의)",
"L-0016":"[위임 파이프라인 운영] -- 상태의 정본, 분해·병렬화(공유 파생물의 단일 소유, 공유 수정 지점별 묶음, do-dag 회수 좌표), 파견 계약(의무 수행 위치를 포함한 쓰기 범위, 확인된 공백의 수리 권한, 품는 절차의 자리 배정, 같은 답으로 수렴한 판단, 진행 중 공백의 상신), 병렬 구현 파견(가지 충돌을 푸는 장소)과 시험 실행 규율, 통신과 재개(같은 식별자 재기동은 재실행, 이관 성과), 긴 다단계 작업의 완료 경로(교정의 재발, 커밋 보류와 인도), 회수 검증, 외부 한도 대체, 모델과 비용; verify-rounds는 L-0022",
"L-0020":"[do-math 구현과 운영] -- 현행 셋째 세대 기준: 설계 기록 가운데 설치 뒤 바뀐 절(11개 주제 묶음), 재구축의 결정과 근거, 사용자 요구와 AI 자율, 간소화가 걸러 낸 판단 기준, 설계 판단의 기준, 판단 규칙이 행동이 되는 경로, 섹션·노드 lease(게시까지 점유하는 이유)와 증명된 조각의 두 형태, 지식 모형(절 단위 전파, contested 격리, concern 주석, root 경로 형식화, 형식 수준의 비전파, 상한 없는 형식화, 기록 불변성과 도출된 보기), 출시와 미착수 종결(출시 순서와 탐구 한 사이클의 이유), 종료 재판단, 검토 독립성, 실행 중 인스턴스에 변경 적용, 실행기·브로커·Windows, 검증 기록, 잔여",
"L-0022":"[verify-rounds 검증 라운드 운영] -- 독해 범위와 실제 입력, 분담 축과 크기, 동결문 진술과 판정 단계, 기각·무처분의 재검토와 직접 처리, 적용 뒤 결과, 상한 종료, 라운드 커밋 범위와 결합 불변식의 문면 공백, 런 사이 실제 실행 관찰; D-0011 보강 넷과 D-0009 판독 보강은 SKILL.md·파견문.md에 승격",
}
for k,v in L.items():
    ls=[l for l in t.split(nl) if l.startswith(f"- {k} ")]; assert len(ls)==1,k
    t=t.replace(ls[0],f"- {k} {v}")
open(P,"w",encoding="utf-8",newline="").write(t)
a=open(A,encoding="utf-8",newline="").read(); anl="\r\n" if "\r\n" in a else "\n"
fm=open("기억/layer2/D-0013.md",encoding="utf-8").read().split("basis: [")[1].split("]")[0]
title=open("기억/layer2/D-0013.md",encoding="utf-8").read().split("title: ")[1].split("\n")[0]
d=f"- D-0013 [{title}] -- basis: {fm} -- do-dag 기록 재독(D-0004가 이미 읽음): 기준선 커밋 자리에 0단계 시점의 주체가 없어 검증 행 23개가 대행 커밋, 같은 답으로 수렴한 판단은 빠진 조항, 후보 지목만으로는 진행 중 교정 없음; 설계 기록의 대체 29단위를 L-0020에 11개 묶음으로; 스테이징 직후 확인의 창과 대상 지정 커밋(공유 색인 한계); 제안 2건(verify-rounds 라운드 커밋 범위, commit-harness 경로 지정); 자율 실익 소진으로 루프 종료"
ls=[l for l in a.split(anl) if l.startswith("- D-0012 ")]; assert len(ls)==1
a=a.replace(ls[0],ls[0]+anl+d); open(A,"w",encoding="utf-8",newline="").write(a)
line=[l for l in a.splitlines() if l.startswith("- D-0013 ")][0]
print("basis match:", line.split("basis: ")[1].split(" -- ")[0].split(", ")==fm.split(", "), len(fm.split(", ")))

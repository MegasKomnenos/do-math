import re
P="기억/색인.md"; A="기억/색인_아카이브.md"
t=open(P,encoding="utf-8",newline="").read()
nl="\r\n" if "\r\n" in t else "\n"
def sub1(old,new,s):
    assert s.count(old)==1,(old[:40],s.count(old)); return s.replace(old,new)
t=sub1("반영 수위: M-0653 · D-0011","반영 수위: M-0657 · D-0012",t)
L={
"L-0001":"[검증 설계 원리] -- 통과가 증언하는 대상·판본·경계, 검증 장치의 가치와 대리 측정의 짝, 검증 사각의 세 축, 거짓 GREEN의 일반 목록, 검증 계약(전건의 모집단·정체·깊이, 검수하는 쪽 임시 검산의 실패, 같은 바이트·해시 차용과 소유, 한 판본의 완결 실행, 수리 전 red의 기준선 재관찰), 현재 실패의 관찰, 검색의 모집단; 시험 설계 세부는 L-0023",
"L-0015":"[컨텍스트를 읽는 범위와 비용] -- 현재 원문 재사용·압축 뒤 재확보·합산 출력 한도·중간 생략 절단과 끝 표지의 한계, 계속 커지는 파일, 압축 없이 끝나는 작업 단위, 측정(실제 입력, 전달 경로별 읽기 한도, 토큰 환산)",
"L-0016":"[위임 파이프라인 운영] -- 상태의 정본, 분해·병렬화(공유 파생물의 단일 소유, 공유 수정 지점별 묶음, do-dag 회수 좌표), 파견 계약(의무 수행 위치를 포함한 쓰기 범위, 확인된 공백의 수리 권한), 병렬 구현 파견과 시험 실행 규율, 통신과 재개(같은 식별자 재기동은 재실행, 이관 성과), 긴 다단계 작업의 완료 경로(교정의 재발, 커밋 보류와 인도), 회수 검증, 외부 한도 대체, 모델과 비용; verify-rounds는 L-0022",
"L-0020":"[do-math 구현과 운영] -- 현행 셋째 세대 기준: 재구축의 결정과 근거, 사용자 요구와 AI 자율, 간소화가 걸러 낸 판단 기준, 설계 판단의 기준(단순 의미론으로 기계를 걷어 냄), 판단 규칙이 행동이 되는 경로, 섹션·노드 lease와 증명된 조각의 두 형태, 지식 모형(명제 논리 절 단위 전파, contested 격리, concern 주석, root 경로 형식화), 출시와 미착수 종결, 종료 재판단, 검토 독립성(peer·review Opus 우선 기본값), 실행 중 인스턴스에 변경 적용, 실행기·브로커·Windows, 검증 기록, 잔여",
"L-0022":"[verify-rounds 검증 라운드 운영] -- 독해 범위와 실제 입력, 분담 축과 크기, 동결문 진술과 판정 단계, 기각·무처분의 재검토와 직접 처리, 적용 뒤 결과, 상한 종료, 런 사이 실제 실행 관찰; D-0011 보강 넷과 D-0009 판독 보강은 SKILL.md·파견문.md에 승격",
"L-0023":"[시험 스위트 설계] -- 대역·fixture의 실제 계약 결속, 음성 시험과 검사기 강도(성공 분기 상실, 생산값 계약 위반을 놓치는 비교), 문서 필드의 실제 결과, 이름 패치, 과거 상태에 묶인 시험, 수집과 결과 판정, 시간 예산, 판본과 완결 실행(하위 성질 승계, 생성 전후 트리, 기준 판본 동시 실패의 해석과 fixture 우선순위), 두 트리 통합, 사건 시험의 범위, 원인별 발동 호출 수, 이름 이동 뒤 소비자 검색",
}
for k,v in L.items():
    lines=[l for l in t.split(nl) if l.startswith(f"- {k} ")]
    assert len(lines)==1,k
    t=t.replace(lines[0],f"- {k} {v}")
m=re.search(r"## layer-1"+re.escape(nl)+re.escape(nl)+r"(.*?)"+re.escape(nl)+re.escape(nl)+"## layer-2",t,re.S)
moved=m.group(1).split(nl); assert [l[2:8] for l in moved]==["M-0657","M-0656","M-0655","M-0654"],moved
t=t.replace(m.group(1),"(없음)")
open(P,"w",encoding="utf-8",newline="").write(t)
a=open(A,encoding="utf-8",newline="").read()
anl="\r\n" if "\r\n" in a else "\n"
anchor=[l for l in a.split(anl) if l.startswith("- M-0653 ")]; assert len(anchor)==1
a=a.replace(anchor[0],anchor[0]+anl+anl.join(reversed(moved)))
d="- D-0012 [위임 작업의 결함은 검수 도구와 배정 범위에서도 나오고, 되풀이된 교정은 단위 규칙 대신 구조를 바꿨으며, 처분 범위 없는 확인 규칙이 되돌리기로 넓혀 읽힌 사례가 있었다] -- basis: D-0011, M-0423, M-0550~M-0584, M-0593, M-0642, M-0643, M-0654, M-0655, M-0656, M-0657 -- G09 확정(검수 쪽 검사 도구 실패 34개 중 10개 노드, 통과가 증언하지 못한 세 형태, partial 6 중 3은 배정 공백), 완료 경로·지식 모형에서 되풀이된 교정과 구조 변경(효과 미판정), 앵커 단언의 첫 효과와 넓혀 읽힌 확인 규칙, 기준 판본 동시 실패는 변경 탓이 아님만 증언; 세칙 v29(보류 주제군 패킷의 기준선 재작성); 다음 dream은 사용자 호출(do-dag 기록, 셋째 세대 설계 공백)"
d11=[l for l in a.split(anl) if l.startswith("- D-0011 ")]; assert len(d11)==1
a=a.replace(d11[0],d11[0]+anl+d)
open(A,"w",encoding="utf-8",newline="").write(a)
print("ok")

# phase 012 커밋 행정 마감

첫 finalize.py는 기억/인계 검사와 manager.json 게시 뒤 Git 공백 검사에서 멈췄다. 원 출력은 staged-diff-check.json의 exit2로 보존한다. 지적286건은 양쪽 corpus/manifest.json의 새 항목 구간에만 있으며 모두 원바이트의 CRLF 또는 기존 두 칸 JSON 들여쓰기다. 각 해당 줄을 Git index blob에서 직접 읽어 CRLF 앞의 실제 공백/탭이 없고 들여쓰기가 짝수 칸임을 확인했다. 두 manifest는 기존 -text 속성대로 작업트리 원바이트와 index가 같고 이전18항목도 유지한다.

제품·속성·원보고를 수정하지 않았다. 두 원바이트 manifest 외 전체 stage에는 일반 diff --check를 그대로 적용해 통과했다. 이 제한된 형식 판정은 task 성공을 새로 만드는 시험 변경이 아니다. stage-whitespace-audit.json과 초기 검사 출력, resume_commit.py가 판단/후속 마감 근거다. 보존 목록에 행정 근거를 더한 뒤 manager.json을 candidate로 handoff를 다시 검사하고 정확 stage/바이트 대조 후 커밋한다. 원 task와 공용 요구·다음 배정은 바뀌지 않았다.

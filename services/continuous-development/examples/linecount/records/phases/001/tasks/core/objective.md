## 목적과 역할

사용자가 실행할 줄 집계 CLI의 실제 처리 함수를 제공한다.
CLI task가 의존하는 S1을 구현한다. CLI 작업과 병렬로 진행하므로
CLI의 작업 파일이나 진행 상태를 읽거나 기다릴 필요가 없어야 한다.

## 완료 조건

### A1 S1 구현
count_lines가 공용 LineCounter의 호출 형식과 LineCounts 반환 타입을 사용하고
S1의 입력·출력·줄 경계·동일성·부수 효과 계약을 만족한다.
빈 입력, 세 종류 줄 경계, 공백 줄, 대소문자, U+2028을 검증한다.

### A2 자체 검증
tests/test_core.py가 실제 core 구현에 대해 위 사례를 확인한다.
검사 명령과 결과를 evidence에 보존한다. CLI 연결은 이 task의 완료 조건이 아니다.

## 판단과 경계

수정 범위는 phase.json의 core 배정이다. 내부 알고리즘은 자유롭게 정한다.
공용 seam이나 CLI 구현을 수정하지 않는다. S1의 모순을 발견하면
해당 입력과 기대 동작의 충돌을 findings로 보고한다.

## 검증 방법

프로젝트 루트에서 PYTHONPATH=src로 설정하고
python -m unittest discover -s tests -p test_core.py를 실행한다.
이어서 python -m contract_checks.s1을 실행해 실제 함수의 호출·반환 호환성을 확인한다.
두 검사 성공과 S1의 각 사례 대응을 확인하고 출력은
자기 evidence/core-tests.txt에 보존한다.
자기 테스트만 실행하므로 동시에 수정 중인 CLI 테스트를 불러오지 않는다.

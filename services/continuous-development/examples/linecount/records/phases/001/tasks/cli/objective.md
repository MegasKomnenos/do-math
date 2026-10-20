## 목적과 역할

사용자가 파일 경로 하나로 집계 결과를 얻는 실행 진입점을 만든다.
파일·인수·오류·JSON 출력은 이 task의 책임이고 집계는 S1에 맡긴다.
같은 phase의 core 구현이 아직 없거나 수정 중일 수 있다.

## 완료 조건

### A1 정상 경로
파일을 UTF-8로 읽고 S1에 문자열을 전달한다.
반환된 dict를 G2의 형식으로 출력하고 종료 코드 0을 낸다.

### A2 오류 경로
G3의 인수 오류·읽기 오류·해독 오류에서 stdout은 비고
stderr에는 오류 한 줄이 있으며 종료 코드는 2다.

### A3 자체 검증과 경계 유지
자기 테스트에서 contract_checks.s1.make_consumer_stub으로 LineCounter 정의에
맞는 S1 대역을 만들어 A1·A2를 검증한다.
제품 코드는 실제 linecount.core.count_lines를 호출한다.
실제 core와의 연결은 미검증으로 보고하고 제품 안에 대역을 넣지 않는다.

## 판단과 경계

수정 범위는 phase.json의 cli 배정이다. 오류 문구는 자유롭게 정한다.
집계·정규화·정렬 기준을 바꾸거나 core.py를 만들지 않는다.
테스트 대역은 CLI를 불러오기 전에 테스트 프로세스 안에서 주입한다.
테스트가 실행 중인 core.py를 import하지 않게 하여 독립성을 유지한다.

## 검증 방법

프로젝트 루트에서 PYTHONPATH=src로 설정하고
python -m unittest discover -s tests -p test_cli.py를 실행한다.
assert_consumed_text로 대역이 받은 문자열을 확인하고, 반환 dict의 JSON 출력과
stdout·stderr·종료 코드를 확인한다. 잘못된 인자 이름은 공용 정의를 사용하는 대역이 거부한다.
출력을 자기 evidence/cli-tests.txt에 보존한다.
실제 `python -m linecount FILE` 실행은 제공자 구현 종료 후 후속 task가 확인한다.

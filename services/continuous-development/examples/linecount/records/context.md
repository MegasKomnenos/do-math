# 줄별 출현 횟수 CLI의 현재 맥락

## C1 목적과 완료 기준

사용자는 텍스트 파일에서 정확히 같은 줄이 몇 번 나오는지 확인하려 한다.
터미널에서 `python -m linecount FILE`을 실행하고 stdout을 다른 도구의
JSON 입력으로 사용할 수 있어야 한다. 설명 문구가 stdout에 섞이면 안 된다.
요구의 원문은 sources/request.md다.

### G1 집계 동작
LF, CRLF, CR로 구분한 줄을 센다. 길이 0인 줄만 제외한다.
공백·대소문자를 보존한다. 유니코드 정규화는 하지 않는다.
예를 들어 `A\r\nA\n a \r\n\n`은 A가 2회, ' a '가 1회다.
빈 파일은 빈 객체다. U+2028은 이번 요구에서 정한 줄 경계가 아니므로 보존한다.

### G2 정상 실행
파일 하나를 UTF-8로 읽고 결과를 JSON 객체로 출력한다.
키는 Python 문자열 비교 순서로 정렬하고 비ASCII 문자를 그대로 쓴다.
구분자 주변 공백은 생략한다. JSON 뒤에 LF 하나를 붙인다.
stdout에는 이 결과만, stderr에는 아무것도 쓰지 않고 종료 코드 0을 낸다.

### G3 오류 실행
파일 경로 인수가 정확히 하나가 아니거나 파일 읽기·UTF-8 해독에 실패하면
stdout을 비우고 stderr에 한 줄 오류를 쓴 뒤 종료 코드 2를 낸다.
오류 문구의 구체적인 표현은 구현자가 정한다.

### G4 실제 연결과 검토
처리 함수와 CLI의 실제 구현을 함께 실행해 G1~G3을 확인한다.
최종 제품은 review phase의 검토를 거쳐야 한다.

## C2 구성과 책임

src/linecount/core.py의 count_lines가 문자열을 집계한다.
src/linecount/__main__.py가 인수·파일 읽기·JSON 출력·오류 표시를 담당한다.
CLI는 집계를 직접 다시 구현하지 않고 S1을 호출한다.
core는 파일·표준 입출력에 접근하지 않는다.
두 구현이 공유하는 seam은 seams.md의 S1이다. 호출과 타입의 정본은
src/linecount/contracts.py이며, contract_checks/s1.py가 실제 호환성을 검사한다.

## C3 현재 환경과 상태

준비 세션이 pyproject.toml, src/linecount/__init__.py, 공용 타입 정의
src/linecount/contracts.py와 공유 검사 contract_checks/s1.py를 만들었다.
검사 환경은 Python 3.11 이상이며 실행 시 PYTHONPATH=src를 사용한다.
PowerShell에서는 `$env:PYTHONPATH = 'src'`를 설정한 뒤 Python 명령을 실행한다.
POSIX 셸에서는 `PYTHONPATH=src python ...` 형식으로 실행한다.
아직 core.py와 __main__.py는 없다. 구현이 있다고 가정해 import하지 않는다.
phase 001은 두 구현을 만든다. 실제 연결은 두 task가 끝난 뒤 검증한다.

## C4 위임된 결정과 남은 불확실성

오류 문구와 함수 내부 자료구조는 task가 정할 수 있다.
집계 의미·출력 의미·종료 코드를 바꾸는 재량은 없다.
UTF-8 BOM은 별도로 제거하지 않고 디코딩된 U+FEFF 문자로 보존한다.
이 결정은 UTF-8 해독 이외의 문자 변환을 하지 않는다는 적용 범위에서 나온다.
현재 알려진 제품 요구의 미결정은 없다.
테스트 대역을 사용한 CLI 검증으로 실제 core와의 연결까지 입증할 수는 없다.

# 경계 계약

## S1 줄 집계 함수

위치: src/linecount/core.py
호출: from linecount.core import count_lines
호출·타입 정본: src/linecount/contracts.py의 LineCounter, LineCounts
실제 구현의 모듈·심볼: 같은 파일의 IMPLEMENTATION_MODULE, IMPLEMENTATION_SYMBOL
시그니처: count_lines(text: str) -> LineCounts
위치 인자와 text= 키워드 인자를 모두 지원한다.
반환값은 dict[str, int] 자체이며 counts 같은 필드로 감싸지 않는다.
공유 검사 정본: contract_checks/s1.py
제공 구성 요소: core
사용 구성 요소: CLI
현재 상태: 구현 예정. phase 001/core가 제공한다.

입력은 이미 UTF-8에서 해독된 Python str이다.
함수는 str 전체를 받고 str 이외 입력의 처리는 계약 범위 밖이다.
문자열의 CRLF를 LF로 바꾼 뒤 남은 CR을 LF로 바꾸고 LF로 나눈 것과
같은 줄 경계를 사용한다. 다른 문자를 줄 경계로 취급하지 않는다.
길이 0인 줄은 제외한다. 공백만 있는 줄은 센다.
대소문자·앞뒤 공백·유니코드 문자 표현을 변경하지 않는다.

출력 키는 남은 각 줄이고 값은 1 이상의 Python int 출현 횟수다.
빈 입력이나 줄 경계만 있는 입력은 빈 dict를 반환한다.
dict의 순회 순서는 계약하지 않는다. 출력 정렬은 CLI의 책임이다.
함수는 파일과 표준 입출력에 접근하지 않고 외부 상태를 변경하지 않는다.
계약 범위의 입력에 정상 결과를 반환한다. 자원 고갈까지 처리하는 약속은 없다.

공유 사례:
- 빈 문자열 -> {}
- "A\r\nA\n a \r\n\n" -> {"A": 2, " a ": 1}
- " \n \n" -> {" ": 2}
- "A\ra\r" -> {"A": 1, "a": 1}
- "x\u2028y" -> {"x\u2028y": 1}

제공자는 자료구조와 알고리즘을 자유롭게 정한다.
소비자는 S1의 구현을 제품에 재작성하지 않는다.
phase 001/cli는 자기 테스트 내부 대역으로 위 입출력 계약을 검증할 수 있다.
그 결과는 실제 core 구현과의 연결 검증을 대신하지 않는다.

제공자는 LineCounts 타입을 사용하고, 실제 구현을 import하는 공유 검사를 실행한다.
프로젝트 루트에서 PYTHONPATH=src로 설정한 뒤 python -m contract_checks.s1을 실행한다.
이 검사는 import 위치·함수 이름·text 인자·타입 선언·반환 구조·공유 사례를 확인한다.
소비자의 자체 검사에서는 make_consumer_stub으로 같은 LineCounter 정의에서 대역을 만들고
assert_consumed_text로 전달한 문자열을 확인한다. 독자적으로 다른 호출 규격의 대역을 만들지 않는다.
공유 검사는 실제 제공자와 실제 소비자의 결합 검증까지 대신하지 않는다.

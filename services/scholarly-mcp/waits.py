"""대기 시간의 단일 출처.

자료원이 느리다는 이유로 작업을 포기하지 않는다. 자료원 응답을 기다리는 모든 대기는 SOURCE_WAIT_MS를 쓴다.
있으면 처리하고 없으면 넘어가는 탐색(쿠키 배너, 선택적 요소)만 PROBE_WAIT_MS를 쓴다. 두 값 모두 환경변수로 조정한다.

  SCHOLARLY_SOURCE_WAIT_MS  자료원 응답 대기(기본 300000, 5분)
  SCHOLARLY_PROBE_WAIT_MS   선택적 요소 탐색(기본 5000)
  SCHOLARLY_LOCAL_TOOL_S    로컬 변환 도구 실행(기본 300초)
  SCHOLARLY_BROWSER_START_S 소유 브라우저 기동(기본 60초)
  SCHOLARLY_CONNECT_WAIT_S  TCP 연결 수립(기본 30초)
  SCHOLARLY_TRANSIENT_ATTEMPTS 제공자의 일시 오류에 같은 요청을 시도하는 총 횟수(기본 5)
  SCHOLARLY_TRANSIENT_PAUSE_MS 일시 오류 뒤 첫 재시도까지 쉬는 시간(기본 2000). 시도마다 두 배가 된다
"""
import os


def wait_ms(name, default, environment=None):
    """환경변수의 정수 밀리초 값을 읽는다. 값이 없거나 정수가 아니면 기본값을 쓴다."""
    value = (environment if environment is not None else os.environ).get(name)
    if value is None:
        return default
    value = value.strip()
    return int(value) if value.isdigit() and int(value) > 0 else default


SOURCE_WAIT_MS = wait_ms("SCHOLARLY_SOURCE_WAIT_MS", 300000)
PROBE_WAIT_MS = wait_ms("SCHOLARLY_PROBE_WAIT_MS", 5000)
LOCAL_TOOL_S = wait_ms("SCHOLARLY_LOCAL_TOOL_S", 300)
BROWSER_START_S = wait_ms("SCHOLARLY_BROWSER_START_S", 60)
PROCESS_EXIT_S = wait_ms("SCHOLARLY_PROCESS_EXIT_S", 15)
CONNECT_WAIT_S = wait_ms("SCHOLARLY_CONNECT_WAIT_S", 30)
# 실측한 WoS의 일시 오류율은 절반 안팎이었다. 다섯 번이면 연속 실패 확률이 3% 남짓으로 내려간다.
TRANSIENT_ATTEMPTS = wait_ms("SCHOLARLY_TRANSIENT_ATTEMPTS", 5)
# 실측한 일시 오류는 몇 초씩 몰려서 왔다. 쉬지 않고 다시 시도하면 같은 몰림 안에서 전부 실패한다.
TRANSIENT_PAUSE_MS = wait_ms("SCHOLARLY_TRANSIENT_PAUSE_MS", 2000)

SOURCE_WAIT_S = SOURCE_WAIT_MS // 1000
PROBE_WAIT_S = PROBE_WAIT_MS // 1000

from work import *
def edit(relative, transform):
    path = REPO / relative
    path.write_bytes(transform(path.read_bytes().decode('utf-8')).encode('utf-8'))
root = '.claude/skills/do-math/references/'
edit(root+'초기화-운전.md', lambda t: t.replace(
    'Lean 관련 검색 경로 환경 변수는 호스트에서 상속하지 않는다.',
    'Lake 프로젝트를 쓰지 않는 명령의 `toolchain.project`는 `null`이다. Lean 관련 검색 경로 환경 변수는 호스트에서 상속하지 않는다.'))
edit(root+'초기화-효율과-정비.md', lambda t: t.replace(
    '형식 검사는 달라진 파일 목록(`environment_check.changed_files`)을 보존하고 `formal_environment` 대기로 멈춘다.',
    '형식 검사는 달라진 파일 목록(`environment_check.changed_files`)의 앞 50개와 전체 변화 개수(`changed_file_count`)를 보존하고 `formal_environment` 대기로 멈춘다. 이 목록은 지문 불일치 분기에만 있다. 성공과 재결박, 기록 부재·파손이나 판본 식별 오류로 먼저 반려된 검사에는 목록과 개수 필드가 없고, 각 반려 사유는 `errors`에 남는다.').replace(
    '검색 경로는 Lean 설치와 Lake 프로젝트 안에 있어야 한다. 판본 식별 다이제스트는',
    '프로젝트 소스 식별에는 추적된 트리와 diff의 해시, 추적되지 않은 입력의 개수와 이름·내용 해시의 다이제스트가 들어간다. `.lake`의 소스와 빌드 산출물은 이 입력에서 제외한다. Lake 프로젝트를 쓰지 않으면 프로젝트 값은 `null`이다. 검색 경로는 Lean 설치와 Lake 프로젝트 안에 있어야 한다. 판본 식별 다이제스트는'))
print('Clarified conditional fields and compact source identity without changing authority')

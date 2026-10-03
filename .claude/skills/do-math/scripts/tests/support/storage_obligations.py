"""저장 의무의 유한 입력 축과 비용 계약. 실행 성적이나 제품 registry가 아니다.

중앙 비용 목록은 없으므로 결함-범주 5.10의 다섯 기록을 선언한다.
N은 시간 실측이 아니라 원문 규모다. 모든 계수는 준비 이후 새 reader의
명시 snapshot 호출에서 시작하며 기존 관찰 기록을 지우지 않는다.
"""
from hypothesis import strategies as st

from do_math.payloads import LIMIT


COST_CASES = {
    'B-27': {'sizes': (3, 64, 65, 1043), 'source': '조사/결함-B.md:610-618',
             'path': 'repository.export', 'bound': 'ceil(N/64)+2 Git 연산; 파일 쓰기 N'},
    'D-10': {'sizes': (3, 16, 17, 200), 'source': '조사/결함-범주.md:1664-1677',
             'path': 'repository.query', 'bound': 'ceil(N/16)+1 Git 연산; 일치 항목 해시 N'},
    'A-18': {'sizes': (1, 10), 'source': '조사/결함-범주.md:1019; k=10은 유한 회귀 상한',
             'path': 'scheduler._run_parallel', 'bound': '안정 idle k회 commit 0'},
    'B-03': {'sizes': (6, 56230), 'source': 'domain-prep-storage.md C5',
             'path': 'trust_inventory.content_hashes/identity_errors',
             'bound': '내용 읽기 N; 구조 검사 open/hash/resolve 0'},
    'D-08': {'sizes': (2, 100), 'source': '조사/결함-범주.md:1632-1646',
             'path': 'lifecycle_engine._refresh_readiness',
             'bound': '상태 전체 deepcopy 0; 평가 결과 deepcopy N'},
}

SAFE_TEXT = st.text(alphabet=st.characters(blacklist_categories=('Cs',)), max_size=24)
JSON_VALUES = st.recursive(
    st.none() | st.booleans() | st.integers(-(2**53 - 1), 2**53 - 1) | SAFE_TEXT,
    lambda child: st.lists(child, max_size=4) | st.dictionaries(SAFE_TEXT, child, max_size=4),
    max_leaves=12,
)


@st.composite
def payload_records(draw):
    """큰 값 둘을 반드시 포함하고 최상위/중첩 키 순서를 각각 섞는다."""
    suffix = draw(SAFE_TEXT)
    first = 'A' * (LIMIT + draw(st.integers(0, 128))) + suffix
    second = 'B' * (LIMIT + draw(st.integers(0, 128))) + suffix
    nested = dict(draw(st.permutations((('z', first), ('a', second)))))
    pairs = (('z', first), ('a', second), ('nested', [nested, draw(JSON_VALUES)]))
    return dict(draw(st.permutations(pairs)))


@st.composite
def title_sequences(draw):
    """두 재등장 형태를 모든 예에 포함하고 추가 값도 생성한다(길이 7~9)."""
    suffix = draw(SAFE_TEXT)
    first, second = 'A' * LIMIT + suffix, 'B' * LIMIT + suffix
    middle = draw(st.lists(SAFE_TEXT, max_size=2))
    return [first, 'short', first, second, *middle, first, second, first]

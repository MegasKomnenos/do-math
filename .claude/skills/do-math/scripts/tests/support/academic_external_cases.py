"""실제 권한 결정·요청 생산자와 저장 레코드 검증을 쓰는 외부 작업 입력."""
from copy import deepcopy

from do_math import governance
from do_math.external import prepare_operation, execute_operation
from do_math.record_schemas import RECORD_RULES
from do_math.state_contract import default_state_contract, validate_record
from support.fakes.clock import FakeClock
from support.fakes.http import make_fake
from support.state_builders import governance_start

ORIGIN = 'https://academic.example.test'


class AcademicExternalCase:
    def __init__(self):
        self.clock = FakeClock()
        self.instance = governance_start({'id': 'I', 'governance_sources': {
            'user': governance.preserve_source('user', '합성 HTTP 권한 승인', origin='user')}})
        self.instance, _, _ = governance.apply_decision(self.instance, {}, {'kind': 'grant', 'grant': {
            'id': 'G', 'kind': 'http', 'reuse': 'reusable', 'allowed_origins': [ORIGIN],
            'allowed_methods': ['POST'], 'allowed_path_prefixes': ['/submit'], 'credential_env': {}}},
            source_ref='user', clock=self.clock)
        self.grant = self.instance['grants']['G']
        self.operation = prepare_operation({'method': 'POST', 'url': ORIGIN + '/submit', 'body': '합성 본문'},
                                           'G', 'user', 'OP-academic')
        RECORD_RULES['external_operations'](self.operation)
        self.http = make_fake({'/submit': (201, b'accepted', None)})
        self.saved = []

    def persist(self, row):
        validate_record(default_state_contract().family('runtime', 'external_operations').checker,
                        row, 'external operation')
        RECORD_RULES['external_operations'](row)
        self.saved.append(deepcopy(row))
        return True

    def send(self, operation=None, **options):
        arguments = {'persist': self.persist, 'transport': self.http.request, 'clock': self.clock,
                     'environment': {}, 'runtime': {}}
        arguments.update(options)
        return execute_operation(self.operation if operation is None else operation, self.grant, **arguments)

    def unknown(self):
        self.http.table['/submit'] = (503, b'unknown', None)
        return self.send()

    def evidence(self, operation, fact='succeeded'):
        return {'operation_id': operation['id'], 'request_sha256': operation['request_sha256'],
                'idempotency_key': operation['idempotency_key'], 'fact': fact,
                'evidence_ref': 'remote:synthetic-receipt', 'observed_at': self.clock.now()}

    def retry_evidence(self, operation):
        return {'kind': 'verified_idempotency', 'request_sha256': operation['request_sha256'],
                'idempotency_key': operation['idempotency_key'], 'evidence_ref': 'remote:synthetic-contract',
                'valid_until': '2199-01-01T00:00:00Z'}

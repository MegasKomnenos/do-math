"""실제 탐침 프롬프트를 읽는 외부 CLI 입력 생산자. 러너나 수집기를 대체하지 않는다."""
from copy import deepcopy
import json
from pathlib import Path

from support.operator_finish_scene import OperatorCLI
from support.provider_runs import CLAUDE_INIT, claude_result, codex_stream


class ProbeCLI(OperatorCLI):
    def __init__(self, *, case, events=(), file_value='nonce', checkpoint=True, models=None):
        super().__init__()
        self.case, self.events = case, deepcopy(list(events))
        self.file_value, self.checkpoint, self.models = file_value, checkpoint, models
        self.on_input = self.produce

    def produce(self, call):
        output = call['output']
        nonce = call['schema']['properties']['nonce']['const']
        workspace = Path(call['cwd'])
        if self.case == 'files':
            if self.file_value is not None:
                (workspace / 'probe-evidence.txt').write_text(
                    nonce if self.file_value == 'nonce' else self.file_value, encoding='utf-8')
            if self.checkpoint:
                # 제품이 프롬프트에 보낸 체크포인트를 그대로 사용한다.
                raw = call['prompt'].split('then write checkpoint.json as ', 1)[1]
                value, _ = json.JSONDecoder().raw_decode(raw)
                (workspace / 'checkpoint.json').write_text(json.dumps(value), encoding='utf-8')
        if self.case == 'background' and self.file_value is not None:
            (workspace / 'completed.txt').write_text(
                nonce if self.file_value == 'nonce' else self.file_value, encoding='utf-8')
        final = json.dumps(output).encode('utf-8')
        if '--print' in call['command']:
            fields = {} if self.models is None else {'modelUsage': {name: {'inputTokens': 1} for name in self.models}}
            rows = [CLAUDE_INIT, *self.events, claude_result(final, **fields)]
        else:
            rows = [json.loads(row) for row in codex_stream(final).splitlines()]
            rows[2:2] = self.events
        self.stdout = b''.join(json.dumps(row).encode('utf-8') + b'\n' for row in rows)

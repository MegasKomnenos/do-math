"""제품 코드를 교체하지 않고 지정 함수의 실제 실행 행을 관찰한다."""
import inspect
import sys
from support.monitoring_slots import reserve_tool


class ExecutedLines:
    def __init__(self, function):
        self.code = inspect.unwrap(getattr(function, '__func__', function)).__code__
        self.lines = []

    def __enter__(self):
        self.tool = reserve_tool('planning producer paths')
        sys.monitoring.register_callback(self.tool, sys.monitoring.events.LINE,
            lambda code, line: self.lines.append(line))
        sys.monitoring.set_local_events(self.tool, self.code, sys.monitoring.events.LINE)
        return self

    def __exit__(self, *error):
        sys.monitoring.set_local_events(self.tool, self.code, 0)
        sys.monitoring.register_callback(self.tool, sys.monitoring.events.LINE, None)
        sys.monitoring.free_tool_id(self.tool)

    def crossed(self, first, second):
        return (first, second) in zip(self.lines, self.lines[1:])

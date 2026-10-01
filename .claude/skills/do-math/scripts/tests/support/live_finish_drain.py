"""An already admitted calculation on the real calls implementation, ready to drain.

Unlike the old autospec, collect is the product's and resolves its Future and
resumes its generator. The scheduler must collect once before the calculation
gets its deterministic turn and once after. No engine callback is replaced.
"""
from support.fakes.calls import DeterministicCallsPort


class ExistingCalculation(DeterministicCallsPort):
    def __init__(self, clock):
        super().__init__(clock)
        self.returned = []

    def new(self, **callbacks):
        calls = super().new(**callbacks)

        def continuation():
            result = yield {}
            self.returned.append(result)

        generator = continuation()
        arguments = next(generator)
        calls.start_call(generator, lambda: {'status': 'completed', 'output': None, 'usage': {}}, arguments)
        return calls

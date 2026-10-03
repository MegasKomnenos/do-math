"""Deterministic calls port: the owner and the calls take turns, switching only at stated points.

``DeterministicCalls`` is the product ``ModelCalls`` with its thread steps
replaced, so stop judgment, observation queues and collection are the
product's own code. Each call's calculation runs on its own thread, but only
while the owner has handed it the turn in ``wait``; the owner waits until the
call returns or hands the turn back. A call hands the turn back at two points:

- a start callback, which the owner runs on its own thread and answers, as the
  product queues it to the owner;
- ``owner_turn()``, which a calculation calls while it waits for the owner (a
  worker waiting for its control receipt). The call is ready again at the
  owner's next ``wait``, so one owner pass runs in between.

``wait`` gives the turn to the ready call ``choose`` picks (default: the
earliest); with none ready it advances the clock by the timeout. For one set
of choices a scenario therefore runs in one order.
"""
import threading

from do_math.parallel import ModelCalls

_current = threading.local()
_STOP = object()


def owner_turn():
    """A calculation waits for the owner: hand the turn back until the owner's next ``wait``."""
    if _current.turn.hand_back(('yield',)) is _STOP:
        raise RuntimeError("executor is shutting down")


class _Turn:
    """One call's thread and its two-way hand-off with the owner."""

    def __init__(self, run):
        self.run, self.thread, self.ready = run, None, True
        self.to_call, self.to_owner = threading.Semaphore(0), threading.Semaphore(0)
        self.value = self.message = None

    def _body(self):
        _current.turn = self
        self.to_call.acquire()
        try:
            self.run()
        finally:
            self.message = ('done',)
            self.to_owner.release()

    def give(self, value):
        """Owner: hand the call ``value`` and the turn; return what the call hands back."""
        self.value = value
        if self.thread is None:
            self.thread = threading.Thread(target=self._body, name="do-math-fake-call", daemon=True)
            self.thread.start()
        self.to_call.release()
        self.to_owner.acquire()
        return self.message

    def hand_back(self, message):
        """Call: hand the owner ``message`` and the turn; return what the owner hands back."""
        self.message = message
        self.to_owner.release()
        self.to_call.acquire()
        return self.value


class DeterministicCalls(ModelCalls):
    def __init__(self, *, clock=None, choose=None, **callbacks):
        super().__init__(**callbacks)
        self.turns, self.clock = [], clock
        self.choose = choose or (lambda ready: 0)

    def _spawn(self, run):
        self.turns.append(_Turn(run))

    def _owner_call(self, function, args):
        if self.stopping:
            raise RuntimeError("executor is shutting down")
        outcome, value = _current.turn.hand_back(('owner_call', function, args))
        if outcome == 'error':
            raise value
        return value

    def wait(self, timeout):
        ready = [turn for turn in self.turns if turn.ready]
        if ready:
            turn = ready[self.choose(ready)]
            turn.ready = False
            message = turn.give(None)
            while message[0] == 'owner_call':
                _, function, args = message
                try:
                    answer = ('ok', function(*args))
                except BaseException as error:
                    answer = ('error', error)
                message = turn.give(answer)
            if message[0] == 'yield':
                turn.ready = True
            else:
                turn.thread.join()
                self.turns.remove(turn)
        elif self.clock is not None:
            self.clock.sleep(timeout)
        self.wake.clear()

    def close(self):
        super().close()
        # Cooperative close runs even unstarted calculations to their actual outcome.
        self._finish_turns(self.turns)
        self.turns.clear()

    def abandon_owner(self):
        """Sim-only process loss: clean up started calls without launching lost work."""
        super().close()  # Set stops and reject queued callbacks before local cleanup.
        self._finish_turns(turn for turn in self.turns if turn.thread is not None)
        # ModelCalls' original closures have completed every started calculation.
        # Only unstarted calculations remain pending; no turn/Future pairing is needed.
        for future in self.futures:
            future.cancel()
        self.futures.clear()
        self.turns.clear()

    def _finish_turns(self, turns):
        for turn in list(turns):
            # ModelCalls.close has set stops and rejected queued callbacks.
            # Only the original closure completes the Future with a result/exception.
            message = turn.message
            while message is None or message[0] != 'done':
                if message is None:
                    answer = None
                elif message[0] == 'owner_call':
                    answer = ('error', RuntimeError("executor is shutting down"))
                else:
                    answer = _STOP
                message = turn.give(answer)
            turn.thread.join()


class DeterministicCallsPort:
    def __init__(self, clock=None, choose=None):
        self.clock, self.choose = clock, choose
        self.created = []

    def new(self, *, on_returned=None, on_observation_error=None):
        calls = DeterministicCalls(clock=self.clock, choose=self.choose, on_returned=on_returned,
                                   on_observation_error=on_observation_error)
        self.created.append(calls)
        return calls


def make_fake(clock=None):
    return DeterministicCallsPort(clock)

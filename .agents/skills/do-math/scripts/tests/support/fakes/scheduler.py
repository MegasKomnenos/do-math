"""Fake scheduler port: an in-memory task table with the adapter's three task views.

Views carry the adapter's keys. The operator and engine views after ``install``
and the wake view after ``schedule-wake`` are this fake's model of the real
adapter; the real registering actions are checked only in the smoke tier (T5).
Every call is recorded in ``calls`` as ``(action, arguments)``.
"""
from datetime import datetime, timezone


def _view(name, *, action='', interval=None, execution_limit='', next_run=None, description=''):
    return {'name': name, 'state': 'Ready', 'action': action, 'interval': interval, 'multiple_instances': 'IgnoreNew',
            'execution_limit': execution_limit, 'next_run': next_run, 'last_result': 267011, 'description': description}


class FakeScheduler:
    def __init__(self):
        self.tasks, self.calls = {}, []

    def run(self, action, arguments):
        self.calls.append((action, dict(arguments)))
        operator, engine, wake = arguments['OperatorTask'], arguments['EngineTask'], arguments['WakeTask']
        if action == 'install':
            seconds = int(arguments['IntervalSeconds'])
            self.tasks[operator] = _view(operator, action=arguments['Python'] + ' operator', interval=f'PT{seconds}S',
                                         execution_limit=f"PT{int(arguments['OperatorTimeoutSeconds']) + 300}S")
            self.tasks[engine] = _view(engine, action=arguments['Python'] + ' run-engine', execution_limit='PT0S')
        elif action == 'uninstall':
            for name in (operator, engine, wake):
                self.tasks.pop(name, None)
        elif action == 'schedule-wake':
            utc = datetime.fromisoformat(arguments['WakeAt']).astimezone(timezone.utc)
            self.tasks[wake] = _view(wake, action=arguments['Python'] + ' wake', execution_limit='PT2M',
                                     next_run=utc.strftime('%Y-%m-%dT%H:%M:%S.0000000Z'), description=arguments['WakeKey'])
        elif action == 'cancel-wake':
            self.tasks.pop(wake, None)
        elif action in ('start-engine', 'start-operator'):
            task = self.tasks.get(engine if action == 'start-engine' else operator)
            if task is None:
                raise RuntimeError('The system cannot find the file specified.')
            task['state'] = 'Running'
        elif action != 'status':
            raise RuntimeError('unknown scheduler action: ' + action)
        return {'operator': self.tasks.get(operator), 'engine': self.tasks.get(engine), 'wake': self.tasks.get(wake)}


def make_fake():
    return FakeScheduler()

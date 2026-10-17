"""Isolation labels for do-math tests.

``test_group('lean')`` and ``test_group('resource')`` mark tests that call the
real Lean toolchain or manage real process lifetimes and resources; the runner
runs them per class in an owned Windows Job, waiting for the root and all owned
children without an elapsed deadline. A label goes on
the class when every test in it needs isolation, otherwise on each such method;
a method's label overrides its class's.
"""
LABELS = ('lean', 'resource')


def test_group(label):
    if label not in LABELS:
        raise ValueError('unknown test label: ' + str(label))
    def decorate(target):
        target.do_math_test_group = label
        return target
    return decorate


def isolation_for(test):
    """'lean' or 'resource' when the test must run isolated, else None; a method label overrides its class."""
    method = getattr(test, getattr(test, '_testMethodName', ''), None)
    return getattr(method, 'do_math_test_group', None) or getattr(type(test), 'do_math_test_group', None)

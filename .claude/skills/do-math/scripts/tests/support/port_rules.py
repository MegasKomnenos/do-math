"""Port completeness: the real implementation and the fake carry every protocol operation with one signature."""
import inspect


def _operations(protocol):
    return [name for name, value in vars(protocol).items()
            if not name.startswith('_') and callable(value)]


def signature_issues(protocol, real, fake):
    issues = []
    for side, implementation in (('real', real), ('fake', fake)):
        for name in _operations(protocol):
            method = getattr(implementation, name, None)
            if method is None:
                issues.append((side, name, 'missing'))
            elif inspect.signature(method) != inspect.signature(getattr(protocol, name)).replace(
                    parameters=list(inspect.signature(getattr(protocol, name)).parameters.values())[1:]):
                issues.append((side, name, 'signature'))
    return issues

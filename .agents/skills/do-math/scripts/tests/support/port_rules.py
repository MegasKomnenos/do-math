"""Port completeness: the real implementation and the fake carry every protocol operation, callable alike.

"Alike" means the same parameter names, kinds and defaults; annotations are
documentation and are not compared.
"""
import inspect


def _operations(protocol):
    return [name for name, value in vars(protocol).items()
            if not name.startswith('_') and callable(value)]


def _shape(function, *, drop_self):
    parameters = list(inspect.signature(function).parameters.values())
    if drop_self:
        parameters = parameters[1:]
    return [(p.name, p.kind, p.default) for p in parameters]


def signature_issues(protocol, real, fake):
    issues = []
    for side, implementation in (('real', real), ('fake', fake)):
        for name in _operations(protocol):
            method = getattr(implementation, name, None)
            if method is None:
                issues.append((side, name, 'missing'))
            elif _shape(method, drop_self=False) != _shape(getattr(protocol, name), drop_self=True):
                issues.append((side, name, 'signature'))
    return issues

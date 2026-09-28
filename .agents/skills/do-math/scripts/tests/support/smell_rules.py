"""Test-smell rules of docs/do-math/시험-재편-2026-09-29/설계.md 6.2, judged by AST.

They apply to new-system test files (tests/<tier folder>/test_*.py):
* no_assertion: a test method calls no assert*/fail/skipTest, no raises helper,
  and no helper listed in ASSERTION_HELPERS;
* unpinned_rejection: assertRaises(Type) whose exception is never inspected; use
  assertRaisesRegex with a distinctive phrase or compare an issue code;
* product_patch: patch/patch.object aimed at a do_math name; put doubles in a port;
* fixed_sleep: time.sleep; poll a condition with a bound or advance virtual time;
* unreasoned_skip: skip/skipIf/skipUnless/skipTest without a reason text;
* broad_except: a bare except or except Exception/BaseException in a test.
``pragma_issues`` checks product code: a coverage exclusion states its reason.
"""
import ast

# Helpers that assert internally; a test calling one of them has an assertion.
ASSERTION_HELPERS = {'assert_reaches'}
_SKIPS = {'skip': 0, 'skipIf': 1, 'skipUnless': 1, 'skipTest': 0}


def _name(node):
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def _product_names(tree):
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.module.split('.')[0] == 'do_math':
            names |= {alias.asname or alias.name for alias in node.names}
        elif isinstance(node, ast.Import):
            names |= {(alias.asname or alias.name).split('.')[0] for alias in node.names
                      if alias.name.split('.')[0] == 'do_math'}
    return names


def _reason_given(call, position):
    arguments = list(call.args[position:position + 1]) + [k.value for k in call.keywords if k.arg == 'reason']
    return any(isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value.strip() for a in arguments) \
        or any(not isinstance(a, ast.Constant) for a in arguments)


def _test_issues(method, path, product):
    issues = []
    asserted = False
    raises_as = {}
    for node in ast.walk(method):
        if isinstance(node, ast.Call):
            called = _name(node.func)
            if called and (called.startswith('assert') or called in ('fail', 'skipTest') or called in ASSERTION_HELPERS):
                asserted = True
            if called == 'sleep' and isinstance(node.func, ast.Attribute) and _name(node.func.value) == 'time':
                issues.append('fixed_sleep')
            if called in ('patch', 'object') and node.args:
                target = node.args[0]
                if isinstance(target, ast.Constant) and isinstance(target.value, str) and target.value.startswith('do_math'):
                    issues.append('product_patch')
                elif called == 'object' and _name(node.func.value) == 'patch':
                    root = target
                    while isinstance(root, ast.Attribute):
                        root = root.value
                    if isinstance(root, ast.Name) and root.id in product:
                        issues.append('product_patch')
            if called == 'skipTest' and not _reason_given(node, 0):
                issues.append('unreasoned_skip')
        if isinstance(node, ast.withitem) and isinstance(node.context_expr, ast.Call) \
                and _name(node.context_expr.func) == 'assertRaises':
            name = node.optional_vars.id if isinstance(node.optional_vars, ast.Name) else None
            raises_as[id(node)] = name
        if isinstance(node, ast.ExceptHandler) and (node.type is None or _name(node.type) in ('Exception', 'BaseException')):
            issues.append('broad_except')
    inspected = {n.value.id for n in ast.walk(method)
                 if isinstance(n, ast.Attribute) and n.attr == 'exception' and isinstance(n.value, ast.Name)}
    issues += ['unpinned_rejection' for name in raises_as.values() if name is None or name not in inspected]
    for node in ast.walk(method):
        if isinstance(node, ast.Call) and _name(node.func) == 'assertRaises' and len(node.args) > 1:
            issues.append('unpinned_rejection')
    for decorator in method.decorator_list:
        if isinstance(decorator, ast.Call) and _name(decorator.func) in _SKIPS \
                and not _reason_given(decorator, _SKIPS[_name(decorator.func)]):
            issues.append('unreasoned_skip')
    if not asserted:
        issues.append('no_assertion')
    return [{'file': path, 'test': method.name, 'rule': rule, 'line': method.lineno} for rule in issues]


def smell_issues(source, path):
    tree = ast.parse(source)
    product = _product_names(tree)
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith('test'):
                    issues += _test_issues(method, path, product)
    return issues


def pragma_issues(source, path):
    issues = []
    for number, line in enumerate(source.splitlines(), 1):
        marker = line.find('# pragma: no cover')
        if marker >= 0 and not line[marker + len('# pragma: no cover'):].strip(' -:'):
            issues.append({'file': path, 'rule': 'unreasoned_exclusion', 'line': number})
    return issues

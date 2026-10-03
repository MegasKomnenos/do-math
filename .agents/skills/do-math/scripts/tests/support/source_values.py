"""Finite producer values from current source; unknown dynamic expressions fail."""
import ast


def assignments_in(function):
    result = {}
    for node in ast.walk(function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    result.setdefault(target.id, []).append(node.value)
    return result


def result_values(node, assignments, functions=None, visiting=()):
    functions = functions or {}
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.IfExp):
        return result_values(node.body, assignments, functions, visiting) | result_values(node.orelse, assignments, functions, visiting)
    if isinstance(node, ast.Name) and node.id in assignments and node.id not in visiting:
        values = set()
        for expression in assignments[node.id]:
            values |= result_values(expression, assignments, functions, (*visiting, node.id))
        return values
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'get' \
            and isinstance(node.func.value, ast.Dict) and len(node.args) == 2:
        values = result_values(node.args[1], assignments, functions, visiting)
        for expression in node.func.value.values:
            values |= result_values(expression, assignments, functions, visiting)
        return values
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in functions \
            and 'call:' + node.func.id not in visiting:
        function = functions[node.func.id]
        values = set()
        for returned in (value for value in ast.walk(function) if isinstance(value, ast.Return)):
            calls = tuple(name for name in visiting if name.startswith('call:'))
            values |= result_values(returned.value, assignments_in(function), functions, (*calls, 'call:' + node.func.id))
        return values
    raise AssertionError('producer needs an explicit finite declaration: ' + ast.dump(node))

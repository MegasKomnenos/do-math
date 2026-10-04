"""13-C static bindings: command flags belong to their actual parser.

The document population includes operating guides, the glossary and role
contracts. Code examples, rather than unrelated prose on the same line,
determine command/option associations. Bare flag mentions retain the existing
tool-vocabulary check; they are not evidence for a command-specific binding.

Dotted fields use their actual schema or an explicitly selected producer. A
prose variable with different owners, such as record or result, can declare
its owner on the same line: <!-- do-math fields: record=governance_record -->.
These bindings never leak to later lines or override canonical namespaces.
Unknown namespaces are coverage gaps, not evidence of a valid field.
"""
import ast
import inspect
import importlib
import textwrap
from pathlib import Path
import re
import shlex

ENTRY = re.compile(r'(?:do_math\.py|\$dmCli)\s+([a-z][a-z-]*)\b')
SPAN = re.compile(r'(?<!`)`([^`\n]+)`(?!`)')
FLAG = re.compile(r'^--[a-z][a-z-]*(?:=.*)?$')


def documents(skill):
    skill = Path(skill)
    return [skill / name for name in ('SKILL.md', 'README.md', 'GLOSSARY.md')] + \
        sorted((skill / 'references').glob('*.md')) + sorted((skill / '계약').glob('*.md'))


def parser_options(parser):
    from do_math.cli_contract import _command_parsers
    return {name: {flag for action in command._actions for flag in action.option_strings}
            for name, command in _command_parsers(parser).items()}


def tool_options(scripts):
    flags = set()
    for path in [*Path(scripts).joinpath('do_math').rglob('*.py'), *Path(scripts).glob('*.py')]:
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                    and re.fullmatch(r'--[a-z][a-z-]*', node.value):
                flags.add(node.value)
    return flags


def code_examples(text):
    """Keep shell continuations inside their code block; do not attach prose flags."""
    blocks = re.findall(r'```[^\n]*\n(.*?)```', text, flags=re.S)
    for block in blocks:
        joined = re.sub(r'(?:`|\\)\s*\n\s*', ' ', block)
        yield from joined.splitlines()
    yield from SPAN.findall(text)


def command_issues(text, options, flags):
    issues = {('command', name) for name in ENTRY.findall(text) if name not in options}
    issues |= {('option', name) for name in re.findall(r'`(--[a-z][a-z-]*)', text) if name not in flags}
    for example in code_examples(text):
        matches = list(ENTRY.finditer(example))
        if not matches:
            try:
                tokens = shlex.split(example, posix=False)
            except ValueError:
                continue  # Partial prose notation is not a command example.
            if len(tokens) > 1 and tokens[0] in options and any(token.startswith('--') for token in tokens[1:]):
                matches = [re.match(r'\s*' + re.escape(tokens[0]), example)]
                short_name = tokens[0]
            else:
                continue
        else:
            short_name = None
        for index, match in enumerate(matches):
            name = short_name or match.group(1)
            if name not in options:
                continue
            tail = example[match.end():matches[index + 1].start() if index + 1 < len(matches) else None]
            try:
                arguments = shlex.split(tail, posix=False)
            except ValueError:
                issues.add(('unparseable command example', name))
                continue
            for argument in arguments:
                if FLAG.fullmatch(argument):
                    flag = argument.split('=', 1)[0]
                    if flag not in options[name]:
                        issues.add(('command option', name, flag))
    return sorted(issues)


def producer_nodes(function, scope=None, branch=None):
    tree = ast.parse(textwrap.dedent(inspect.getsource(inspect.unwrap(function))))
    function_node = tree.body[0]
    if scope is not None:
        matches = [node for node in ast.walk(function_node)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == scope]
        if len(matches) != 1:
            raise ValueError(f'Review nested producer scope {function.__qualname__}: {scope}')
        function_node = matches[0]
    pending, nodes = list(function_node.body), []
    while pending:
        node = pending.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        nodes.append(node)
        pending.extend(ast.iter_child_nodes(node))
    if branch is not None:
        expected = ast.unparse(ast.parse(branch, mode='eval').body)
        matches = [node for node in nodes if isinstance(node, ast.If) and ast.unparse(node.test) == expected]
        if len(matches) != 1:
            raise ValueError(f'Review producer branch {function.__qualname__}: {branch}')
        pending, nodes = list(matches[0].body), []
        while pending:
            node = pending.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue
            nodes.append(node)
            pending.extend(ast.iter_child_nodes(node))
    return nodes


def produced_object_schema(function, target=None, *, bindings=None, variants=False, keyword=None, scope=None, branch=None, return_item=None):
    """Read explicitly selected producer objects; unknown fields require review."""
    nodes = producer_nodes(function, scope, branch)
    if keyword is not None:
        expected = ast.unparse(ast.parse(target, mode='eval').body)
        values = [item.value for node in nodes if isinstance(node, ast.Call) and ast.unparse(node.func) == expected
                  for item in node.keywords if item.arg == keyword]
    elif target is None:
        values = [node.value for node in nodes if isinstance(node, ast.Return)]
    else:
        expected = ast.unparse(ast.parse(target, mode='eval').body)
        values = [node.value for node in nodes if isinstance(node, ast.Assign)
                  and any(ast.unparse(item) == expected for item in node.targets)]
    if return_item is not None:
        if any(not isinstance(value, ast.Tuple) or return_item >= len(value.elts) for value in values):
            raise ValueError(f'Review producer result tuple {function.__qualname__}')
        values = [value.elts[return_item] for value in values]
    if not values or (not variants and len(values) != 1) or any(not isinstance(value, ast.Dict) for value in values):
        raise ValueError(f'Review document field producer {function.__qualname__}: {target or "return"}')
    bindings, used = bindings or {}, set()
    def shape(node):
        expression = ast.unparse(node)
        if expression in bindings:
            used.add(expression)
            return bindings[expression]
        if not isinstance(node, ast.Dict):
            return {}
        properties = {}
        for key, value in zip(node.keys, node.values):
            if key is None:
                expanded = shape(value)
                if 'properties' not in expanded:
                    raise ValueError(f'Unresolved object keys in document field producer {function.__qualname__}')
                properties.update(expanded['properties'])
            elif isinstance(key, ast.Constant) and isinstance(key.value, str):
                properties[key.value] = shape(value)
            else:
                raise ValueError(f'Unresolved object keys in document field producer {function.__qualname__}')
        return {'type': 'object', 'properties': properties, 'additionalProperties': False}
    shapes = [shape(value) for value in values]
    if used != set(bindings):
        raise ValueError(f'Unused producer bindings in {function.__qualname__}: {sorted(set(bindings) - used)}')
    return {'anyOf': shapes} if variants else shapes[0]


def written_object_schema(function, target, *, branch=None):
    """Fixed subscript/keyword additions to one selected object, not other CLI branches."""
    expected = ast.unparse(ast.parse(target, mode='eval').body)
    properties = {}
    for node in producer_nodes(function, branch=branch):
        if isinstance(node, ast.Assign):
            for destination in node.targets:
                if isinstance(destination, ast.Subscript) and ast.unparse(destination.value) == expected:
                    if not isinstance(destination.slice, ast.Constant) or not isinstance(destination.slice.value, str):
                        raise ValueError(f'Unresolved written field in {function.__qualname__}: {target}')
                    properties[destination.slice.value] = {}
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'update' \
                and ast.unparse(node.func.value) == expected:
            if node.args or any(item.arg is None for item in node.keywords):
                raise ValueError(f'Unresolved object update in {function.__qualname__}: {target}')
            properties.update({item.arg: {} for item in node.keywords})
    if not properties:
        raise ValueError(f'No written fields in {function.__qualname__}: {target}')
    return {'type': 'object', 'properties': properties}


def field_schemas():
    """Bind stored records separately from the role-input objects built from them."""
    from do_math import academic, context_store, governance, reporting, submission, supervision, trace_report
    from do_math.contracts import PLAN_DISPOSITION
    from do_math.core_engine import CoreEngineMixin
    from do_math.record_schemas import config_schema
    from do_math.record_schemas.schemas import RECORDS, RESEARCH_FIELDS
    from do_math.state_contract import default_state_contract
    roots = {name: {'type': 'object', 'properties': {}} for name in ('research', 'runtime')}
    for family in default_state_contract().families():
        value = family.schema
        if family.shape == 'map':
            value = {'type': 'object', 'additionalProperties': value}
        elif family.shape == 'list':
            value = {'type': 'array', 'items': value}
        roots[family.root]['properties'][family.name] = value
    schemas = {'config': config_schema(), 'action': RECORDS['queue'], 'task': RECORDS['tasks'],
               'execution': RECORDS['executions'], 'profile': RECORDS['execution_profiles'],
               'lifecycle': RESEARCH_FIELDS['lifecycle'],
               'runtime': roots['runtime'], 'instance': roots['research'],
               'formal_result': RECORDS['formal_results'], 'execution_to_review': RECORDS['executions']}
    for name, parent, key in (
            ('ai', 'profile', 'ai'), ('assessment', 'task', 'assessment'),
            ('scope', 'task', 'scope'), ('expected', 'task', 'expected'),
            ('immutable_input', 'lifecycle', 'immutable_input'),
            ('maintenance_fence', 'runtime', 'maintenance_fence'),
            ('session_limits', 'config', 'session_limits')):
        schemas[name] = schemas[parent]['properties'][key]
    schemas['revisit'] = PLAN_DISPOSITION['properties']['revisit']
    from do_math import contracts, knowledge_io, model_policy, repair_execution
    schemas['activation'] = RESEARCH_FIELDS['lifecycle']['properties']['activation']
    schemas['disposition'] = contracts.disposition_schema()
    schemas['observation'] = RECORDS['execution_profiles']['properties']['observation']
    schemas['role_tiers'] = {'properties': {key: {} for key in model_policy.ROLE_TIERS}}
    schemas['user_request'] = RECORDS['inputs']
    schemas['governance_record'] = RECORDS['governance']
    schemas['governance_content'] = RECORDS['governance']['properties']['content']
    schemas['candidate_record'] = {'properties': {key: {} for key in knowledge_io._KNOWLEDGE_FIELDS}}
    schemas['repair'] = produced_object_schema(repair_execution.RepairExecutionMixin.route_submission_return, 'retry',
        bindings={'deepcopy(action)': RECORDS['queue']})['properties']['repair']
    schemas['checkpoint_source'] = produced_object_schema(CoreEngineMixin._context, 'evidence.update', keyword='checkpoint_source')
    schemas['result_source'] = produced_object_schema(context_store.restore_continuation, "stage['result_source']")
    schemas['rejected_response'] = produced_object_schema(context_store.restore_continuation, "history[-1]['rejected_response']")
    schemas['recovery_source'] = produced_object_schema(CoreEngineMixin._context, scope='recover', variants=True)
    from do_math import cli, core_engine
    schemas['query_record'] = written_object_schema(core_engine._query_record, 'record')
    schemas['input_manifest'] = produced_object_schema(context_store.build_role_manifest)
    schemas['input_manifest']['properties'].update(written_object_schema(
        context_store.prepare_role_input, 'manifest')['properties'])
    schemas['prompt'] = produced_object_schema(context_store.prepare_role_input, 'manifest.update', keyword='prompt')
    schemas['prompt']['properties'].update(written_object_schema(
        context_store.prepare_role_input, "manifest['prompt']")['properties'])
    schemas['input_manifest']['properties']['prompt'] = schemas['prompt']
    schemas['init_result'] = produced_object_schema(core_engine.initialize_instance)
    schemas['scheduling_result'] = written_object_schema(cli.execute, 'result', branch="command == 'init'")
    schemas['init_result']['properties'].update(schemas['scheduling_result']['properties'])
    schemas['selection_result'] = produced_object_schema(cli.execute, branch="command == 'select-profile'", return_item=0,
        bindings={'selected': RECORDS['executions']['properties']['model_selection']})
    for name in ('execution_window', 'scholarly', 'formal_verifier'):
        schemas[name] = produced_object_schema(CoreEngineMixin._context, f'context[{name!r}]')
    schemas['preview'] = produced_object_schema(submission.install_tools, 'context["formal_verifier"]["preview"]')
    schemas['formal_verifier']['properties']['preview'] = schemas['preview']
    schemas['record_map'] = produced_object_schema(context_store.record_map)
    schemas['record_map']['properties']['read_tool'] = produced_object_schema(
        submission.install_tools, 'context["record_map"]["read_tool"]')
    schemas['submission_contract'] = produced_object_schema(submission.install_tools, 'contract')
    schemas['profile_selection'] = produced_object_schema(context_store.prepare_role_input, "value['profile_selection']")
    schemas['operating_summary'] = produced_object_schema(reporting.operating_summary)
    schemas['governance'] = produced_object_schema(governance.governance_view)
    schemas['academic_validation'] = produced_object_schema(academic.academic_status, variants=True)
    schemas['operation_progress'] = produced_object_schema(trace_report.progress)
    schemas['status'] = produced_object_schema(reporting.status_report, bindings={
        'supervision_facts(instance, runtime)': produced_object_schema(supervision.supervision_facts),
        'operating_summary(instance, runtime)': schemas['operating_summary'],
        'observed': {'type': 'object', 'properties': {name: {} for name in reporting.OBSERVED_FIELDS}}})
    schemas['operational_evidence'] = produced_object_schema(CoreEngineMixin._context, 'evidence')
    schemas['operational_evidence']['properties']['activity_continuations'] = produced_object_schema(
        CoreEngineMixin._context, "evidence['activity_continuations']")
    return schemas


def property_variants(schema, name):
    """Properties in a closed shape or one of its actual schema alternatives."""
    variants = []
    if not isinstance(schema, dict):
        return variants
    if name in schema.get('properties', {}):
        variants.append(schema['properties'][name])
    for keyword in ('allOf', 'anyOf', 'oneOf'):
        for child in schema.get(keyword, []):
            variants.extend(property_variants(child, name))
    for keyword in ('then', 'else'):
        if keyword in schema:
            variants.extend(property_variants(schema[keyword], name))
    return variants


def field_bindings(line, schemas):
    """Line-local prose variables may name owners; canonical namespaces cannot be rebound."""
    local, issues, aliases = dict(schemas), [], set()
    directive = re.search(r'<!-- do-math fields: (.*?) -->', line)
    if directive:
        for binding in directive.group(1).split(','):
            alias, separator, owner = binding.strip().partition('=')
            if (not separator or not re.fullmatch(r'[a-z][a-z0-9_]*', alias) or owner not in schemas
                    or alias in schemas and alias != owner or alias in aliases):
                issues.append(('field binding', binding.strip()))
            else:
                local[alias] = schemas[owner]
                aliases.add(alias)
        used = {span.split('.')[0] for span in SPAN.findall(line)
                if re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+', span)}
        issues.extend(('unused field binding', alias) for alias in sorted(aliases - used))
    return local, issues


def scoped_field_issues(text, schemas):
    """Check owned dotted fields; unresolved namespaces remain a separate coverage obligation."""
    issues = []
    for line in text.splitlines():
        local, binding_issues = field_bindings(line, schemas)
        issues.extend(binding_issues)
        for span in SPAN.findall(line):
            if not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+', span):
                continue
            root, *parts = span.split('.')
            if root not in local:
                continue
            candidates = [local[root]]
            for part in parts:
                candidates = [child for schema in candidates for child in property_variants(schema, part)]
                if not candidates:
                    issues.append(('scoped field', span))
                    break
    return sorted(set(issues))


def declared_policy_names(scripts):
    """Named policy fields/choices come from schemas; code owners come from real modules."""
    from do_math import contracts, control_contracts
    from do_math.record_schemas import config_schema
    from do_math.record_schemas.schemas import RECORDS, RESEARCH_FIELDS, RUNTIME_FIELDS
    names = set()

    def visit(value):
        if isinstance(value, dict):
            names.update(value.get('properties', {}))
            names.update(item for item in value.get('enum', []) if isinstance(item, str))
            if isinstance(value.get('const'), str):
                names.add(value['const'])
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for schema in (RECORDS, RESEARCH_FIELDS, RUNTIME_FIELDS, config_schema(), contracts.SCHEMAS,
                   control_contracts.PAYLOADS, control_contracts.DECISION):
        visit(schema)
    names.update(path.stem for path in Path(scripts).joinpath('do_math').rglob('*_policy.py'))
    return names


def policy_issues(text, names):
    return sorted(('policy name', name) for name in documented_policies(text) if name not in names)


def documented_policies(text):
    return {name for span in SPAN.findall(text)
            for name in re.findall(r'\b[a-z][a-z0-9_]*policy\b', span)}


def function_reference_issues(text):
    """Explicit module.function(...) notation names a callable, never a state field."""
    issues = []
    for token in SPAN.findall(text):
        if not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\(\.\.\.\)', token):
            continue
        root, *attributes = token[:-5].split('.')
        try:
            value = importlib.import_module(root if root == 'os' else 'do_math.' + root)
            for attribute in attributes:
                value = getattr(value, attribute)
        except (ImportError, AttributeError):
            issues.append(('function reference', token))
        else:
            if not callable(value):
                issues.append(('function reference', token))
    return sorted(set(issues))


def diagnostic_names(scripts):
    """Qualified check codes belong to their actual emitting/checking modules."""
    owners = {'contract_check': 'submission.py', 'integration': 'integration.py'}
    return {prefix: {node.value for node in ast.walk(ast.parse(
                (Path(scripts) / 'do_math' / filename).read_text(encoding='utf-8')))
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and re.fullmatch(re.escape(prefix) + r'\.[a-z][a-z0-9_]*', node.value)}
            for prefix, filename in owners.items()}


def diagnostic_reference_issues(text, names):
    return sorted({('diagnostic code', token) for token in SPAN.findall(text)
                   if re.fullmatch(r'[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*', token)
                   and not token.endswith('.py') and token.split('.')[0] in names
                   and token not in names[token.split('.')[0]]})

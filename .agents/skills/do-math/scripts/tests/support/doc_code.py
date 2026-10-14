"""13-C static bindings: command flags belong to their actual parser.

The document population includes operating guides, the glossary and role
contracts. Code examples, rather than unrelated prose on the same line,
determine command/option associations. Bare flag mentions retain the existing
tool-vocabulary check; they are not evidence for a command-specific binding.

Dotted fields use their actual schema or an explicitly selected producer. A
prose variable with different owners, such as record or result, can declare
its owner on the same line: <!-- do-math fields: record=governance_record -->.
These bindings never leak to later lines or override canonical namespaces.
The document test rejects unknown namespaces. Array suffixes traverse item
shapes; an index proves field ownership, not that a runtime array has that index.
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
FIELD = re.compile(r'[a-z][a-z0-9_]*(?:\[\d*\])?(?:\.[a-z][a-z0-9_]*(?:\[\d*\])?)+')
# These owners are checked at their existing repository/file-return boundaries,
# not schemas that could validate fields without the actual responses.
STATUS_REPORT_BOUNDARY = object()
OPERATION_PROGRESS_BOUNDARY = object()
QUERY_RECORD_BOUNDARY = object()
QUERY_RESULT_BOUNDARY = object()
CLI_RESULT_BOUNDARIES = {owner: object() for owner in
                         ('init_result', 'scheduling_result', 'selection_result')}
ROLE_INPUT_BOUNDARIES = {owner: object() for owner in
                         ('input_manifest', 'prompt', 'documents', 'profile_selection')}
CONTINUATION_BOUNDARIES = {owner: object() for owner in
                           ('result_source', 'rejected_response', 'previous_output_files')}
OPERATIONAL_INPUT_BOUNDARIES = {owner: object() for owner in
                              ('operational_evidence', 'recovery_materials')}
RESULT_INPUT_BOUNDARIES = {owner: object() for owner in
                         ('source_ref', 'materialized_output_files', 'research_sources', 'results')}
TOOL_INPUT_BOUNDARIES = {owner: object() for owner in
                        ('execution_window', 'scholarly', 'formal_verifier', 'preview',
                         'record_map.read_tool', 'submission_contract')}
REVIEW_INPUT_BOUNDARIES = {owner: object() for owner in
                          ('role_review', 'pending_findings', 'review_research', 'review_sources')}
DELIVERY_INPUT_BOUNDARIES = {owner: object() for owner in ('submission_check', 'repair')}


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
            if len(tokens) > 1 and tokens[0] in options and any(token.strip('[]').startswith('--') for token in tokens[1:]):
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
                argument = argument.strip('[]')  # Optional arguments in command synopses.
                if FLAG.fullmatch(argument):
                    flag = argument.split('=', 1)[0]
                    if flag not in options[name]:
                        issues.add(('command option', name, flag))
    return sorted(issues)


def producer_nodes(function, scope=None, branch=None, iteration=None):
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
    if branch is not None or iteration is not None:
        expression = branch if branch is not None else iteration
        expected = ast.unparse(ast.parse(expression, mode='eval').body)
        matches = [node for node in nodes if
                   (isinstance(node, ast.If) and branch is not None and ast.unparse(node.test) == expected) or
                   (isinstance(node, ast.For) and iteration is not None and ast.unparse(node.iter) == expected)]
        if len(matches) != 1:
            raise ValueError(f'Review producer branch {function.__qualname__}: {expression}')
        pending, nodes = list(matches[0].body), []
        while pending:
            node = pending.pop()
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
                continue
            nodes.append(node)
            pending.extend(ast.iter_child_nodes(node))
    return nodes


def produced_object_schema(function, target=None, *, bindings=None, variants=False, keyword=None, scope=None, branch=None, return_item=None, argument=None, list_item=False):
    """Read explicitly selected producer objects; unknown fields require review."""
    nodes = producer_nodes(function, scope, branch)
    if keyword is not None or argument is not None:
        expected = ast.unparse(ast.parse(target, mode='eval').body)
        calls = [node for node in nodes if isinstance(node, ast.Call) and ast.unparse(node.func) == expected]
        if argument is not None:
            if any(argument >= len(node.args) for node in calls):
                raise ValueError(f'Review producer call argument {function.__qualname__}')
            values = [node.args[argument] for node in calls]
        else:
            values = [item.value for node in calls for item in node.keywords if item.arg == keyword]
    elif target is None:
        values = [node.value for node in nodes if isinstance(node, ast.Return)]
    else:
        expected = ast.unparse(ast.parse(target, mode='eval').body)
        values = [node.value for node in nodes if isinstance(node, ast.Assign)
                  and any(ast.unparse(item) == expected for item in node.targets)]
    if list_item:
        if any(not isinstance(value, ast.ListComp) for value in values):
            raise ValueError(f'Review producer list item {function.__qualname__}')
        values = [value.elt for value in values]
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
        if isinstance(node, ast.IfExp) and isinstance(node.body, ast.Dict) and isinstance(node.orelse, ast.Dict):
            return {'anyOf': [shape(node.body), shape(node.orelse)]}
        if not isinstance(node, ast.Dict):
            return {}
        properties, compositions = {}, []
        for key, value in zip(node.keys, node.values):
            if key is None:
                expanded = shape(value)
                if 'properties' in expanded:
                    properties.update(expanded['properties'])
                elif 'anyOf' in expanded or 'allOf' in expanded:
                    compositions.append(expanded)
                else:
                    raise ValueError(f'Unresolved object keys in document field producer {function.__qualname__}')
            elif isinstance(key, ast.Constant) and isinstance(key.value, str):
                properties[key.value] = shape(value)
            else:
                raise ValueError(f'Unresolved object keys in document field producer {function.__qualname__}')
        own = {'type': 'object', 'properties': properties, 'additionalProperties': False}
        return {'allOf': [own, *compositions]} if compositions else own
    shapes = [shape(value) for value in values]
    if used != set(bindings):
        raise ValueError(f'Unused producer bindings in {function.__qualname__}: {sorted(set(bindings) - used)}')
    return {'anyOf': shapes} if variants else shapes[0]


def written_object_schema(function, target, *, branch=None, iteration=None):
    """Fixed subscript/keyword additions to one selected object, not other CLI branches."""
    expected = ast.unparse(ast.parse(target, mode='eval').body)
    properties = {}
    for node in producer_nodes(function, branch=branch, iteration=iteration):
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



def consumed_object_schema(function, target, *, scope=None):
    """Fixed keys explicitly read from an open object; this is not a closed schema."""
    expected = ast.unparse(ast.parse(target, mode='eval').body)
    properties = {}
    for node in producer_nodes(function, scope=scope):
        key = None
        if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load) and ast.unparse(node.value) == expected:
            key = node.slice
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr == 'get' and ast.unparse(node.func.value) == expected and node.args:
            key = node.args[0]
        if isinstance(key, ast.Constant) and isinstance(key.value, str):
            properties[key.value] = {}
    if not properties:
        raise ValueError(f'No fixed read fields in {function.__qualname__}: {target}')
    return {'type': 'object', 'properties': properties}


def field_schemas():
    """Bind stored records separately from the role-input objects built from them."""
    from do_math import academic, context_store, governance, reporting, submission
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
    from do_math import contracts, knowledge_io, model_policy
    schemas['activation'] = RESEARCH_FIELDS['lifecycle']['properties']['activation']
    schemas['disposition'] = contracts.disposition_schema()
    schemas['observation'] = RECORDS['execution_profiles']['properties']['observation']
    schemas['role_tiers'] = {'properties': {key: {} for key in model_policy.ROLE_TIERS}}
    schemas['user_request'] = RECORDS['inputs']
    schemas['governance_record'] = RECORDS['governance']
    schemas['governance_content'] = RECORDS['governance']['properties']['content']
    schemas['candidate_record'] = {'properties': {key: {} for key in knowledge_io._KNOWLEDGE_FIELDS}}
    schemas.update(DELIVERY_INPUT_BOUNDARIES)
    schemas.update(CONTINUATION_BOUNDARIES)
    schemas['query_record'] = QUERY_RECORD_BOUNDARY
    schemas.update(ROLE_INPUT_BOUNDARIES)
    schemas.update(CLI_RESULT_BOUNDARIES)
    from do_math import formal, observations, planning, trust_validation
    from do_math.dispatch_engine import DispatchEngineMixin
    schemas['plan_settle_wait'] = produced_object_schema(DispatchEngineMixin._plan_settle_waits, "action['dispatch_wait']")
    schemas.update(RESULT_INPUT_BOUNDARIES)
    schemas.update(REVIEW_INPUT_BOUNDARIES)
    schemas['subject'] = RECORDS['executions']['properties']['observation_rules']['items']['properties']['subject']
    schemas['source_range'] = governance.interpretation_schema('interpret')['properties']['import_units']['items']['properties']['source_range']
    schemas['import_payload'] = consumed_object_schema(governance.validate_import_units, 'payload')
    schemas['change'] = consumed_object_schema(planning.evaluate_condition, "decision.get('change', {})", scope='visit')
    schemas['worker_feedback'] = {'properties': {key: {} for key in observations.WORKER_FEEDBACK_FIELDS}}
    schemas['import_check'] = produced_object_schema(governance.check_import, 'check',
        bindings={'deepcopy(output)': governance.interpretation_schema('check')})
    schemas['import_check']['properties'].update(written_object_schema(governance.check_import, 'check')['properties'])
    schemas['query_result'] = QUERY_RESULT_BOUNDARY
    schemas['project'] = produced_object_schema(formal._project_identity, 'identity')
    schemas['project']['properties'].update(written_object_schema(formal._project_identity, 'identity')['properties'])
    schemas['toolchain'] = produced_object_schema(formal.inspect_toolchain, 'result', bindings={
        '_project_identity(command, should_stop, workspace=workspace, jobs=jobs, clock=clock, environment=environment, git_backend=git_backend)': schemas['project']})
    environment_base = produced_object_schema(trust_validation.check_environment, 'result')
    environment_base['properties'].update(written_object_schema(trust_validation.check_environment, 'result')['properties'])
    schemas['environment_check'] = produced_object_schema(trust_validation.check_environment, variants=True,
        bindings={'result': environment_base})
    def array(item):
        return {'type': 'array', 'items': item}
    schemas['candidates'] = contracts.schema_for('research_preparation')['properties']['candidates']
    schemas['task_assessments'] = contracts.schema_for('research_plan')['properties']['task_assessments']
    schemas['item_dispositions'] = schemas['task_assessments']['items']['properties']['item_dispositions']
    extensions = submission.extension_schema({'role': 'research_preparation'})['properties']
    for name in ('task_conditions', 'knowledge_changes', 'revision_resolutions', 'contract_checks'):
        schemas[name] = extensions[name]
    schemas['question_details'] = governance.interpretation_schema('interpret')['properties']['question_details']
    schemas['external_rejections'] = array(RECORDS['external_rejections'])
    schemas.update({name: boundary for name, boundary in TOOL_INPUT_BOUNDARIES.items()
                    if name != 'record_map.read_tool'})
    schemas['record_map'] = {'type': 'object', 'properties': {
        name: {} for name in context_store.record_map({}, 'research_work', 'fixed')}, 'additionalProperties': False}
    schemas['record_map']['properties']['read_tool'] = TOOL_INPUT_BOUNDARIES['record_map.read_tool']
    from support.state_builders import current_state
    instance, runtime = current_state()
    summary = reporting.operating_summary(instance, runtime)
    schemas['operating_summary'] = {'type': 'object', 'properties': {
        name: {} for name in summary}, 'additionalProperties': False}
    # Only the fixed supervision object is traversed. This initializing result
    # does not establish other blocker variants or items in its empty grants.
    schemas['operating_summary']['properties']['supervision'] = {
        'type': 'object', 'properties': {name: {} for name in summary['supervision']},
        'additionalProperties': False}
    schemas['governance'] = produced_object_schema(governance.governance_view)
    schemas['academic_validation'] = produced_object_schema(academic.academic_status, variants=True)
    schemas['operation_progress'] = OPERATION_PROGRESS_BOUNDARY
    schemas['status'] = STATUS_REPORT_BOUNDARY
    schemas.update(OPERATIONAL_INPUT_BOUNDARIES)
    return schemas


def status_field_schema(report):
    """Bind status fields from a final repository response, never its producers.

    Keep the fixed nested objects previously covered by the document binding;
    a sample does not establish blocker variants or items in empty arrays.
    """
    schema = {'type': 'object', 'properties': {name: {} for name in report},
              'additionalProperties': False}
    for name in ('submission_checks', 'knowledge', 'execution_attempts', 'operating_summary'):
        if isinstance(report.get(name), dict):
            schema['properties'][name] = {'type': 'object',
                'properties': {key: {} for key in report[name]}, 'additionalProperties': False}
    summary = report.get('operating_summary', {})
    if isinstance(summary, dict) and isinstance(summary.get('supervision'), dict):
        schema['properties']['operating_summary']['properties']['supervision'] = {
            'type': 'object', 'properties': {name: {} for name in summary['supervision']},
            'additionalProperties': False}
    return schema


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



def item_variants(schema):
    """Array notation traverses declared items, never an arbitrary object map."""
    variants = []
    if not isinstance(schema, dict):
        return variants
    if isinstance(schema.get('items'), dict):
        variants.append(schema['items'])
    for keyword in ('allOf', 'anyOf', 'oneOf'):
        for child in schema.get(keyword, []):
            variants.extend(item_variants(child))
    for keyword in ('then', 'else'):
        if keyword in schema:
            variants.extend(item_variants(schema[keyword]))
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
        used = {re.split(r'[.\[]', span)[0] for span in SPAN.findall(line)
                if FIELD.fullmatch(span)}
        issues.extend(('unused field binding', alias) for alias in sorted(aliases - used))
    return local, issues



def unowned_field_references(text, schemas):
    """Unbound dotted names, including array items, cannot silently escape the population."""
    pending = set()
    for line in text.splitlines():
        local, _ = field_bindings(line, schemas)
        for token in SPAN.findall(line):
            if not FIELD.fullmatch(token):
                continue
            if '[' not in token and token.endswith(('.py', '.json', '.md', '.txt', '.jsonl', '.exe')):
                continue  # Filename classification does not prove file existence.
            root = re.split(r'[.\[]', token)[0]
            diagnostic = '[' not in token and root in {'contract_check', 'integration'}
            if root not in local and not diagnostic:
                pending.add(token)
    return sorted(pending)


def scoped_field_issues(text, schemas, *, defer_status=False, defer_operation_progress=False,
                        defer_query_record=False, defer_query_result=False, defer_cli_results=(),
                        defer_role_inputs=(), defer_continuations=(), defer_operational_inputs=(),
                        defer_result_inputs=(), defer_tool_inputs=(), defer_review_inputs=(),
                        defer_delivery_inputs=()):
    """Check owned dotted fields; unresolved namespaces remain a separate coverage obligation."""
    unknown = set(defer_cli_results) - CLI_RESULT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred CLI result owners: {sorted(unknown)}')
    unknown = set(defer_role_inputs) - ROLE_INPUT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred role input owners: {sorted(unknown)}')
    unknown = set(defer_continuations) - CONTINUATION_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred continuation owners: {sorted(unknown)}')
    unknown = set(defer_operational_inputs) - OPERATIONAL_INPUT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred operational input owners: {sorted(unknown)}')
    unknown = set(defer_result_inputs) - RESULT_INPUT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred result input owners: {sorted(unknown)}')
    unknown = set(defer_tool_inputs) - TOOL_INPUT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred tool input owners: {sorted(unknown)}')
    unknown = set(defer_review_inputs) - REVIEW_INPUT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred review input owners: {sorted(unknown)}')
    issues = []
    unknown = set(defer_delivery_inputs) - DELIVERY_INPUT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred delivery input owners: {sorted(unknown)}')
    for line in text.splitlines():
        local, binding_issues = field_bindings(line, schemas)
        issues.extend(binding_issues)
        for span in SPAN.findall(line):
            if not FIELD.fullmatch(span):
                continue
            root, *parts = re.findall(r'[a-z][a-z0-9_]*|\[\d*\]', span)
            if root not in local:
                continue
            owner = next((name for name, boundary in DELIVERY_INPUT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_delivery_inputs:
                    continue
                raise ValueError(owner + ' fields require the actual delivery input')
            owner = next((name for name, boundary in REVIEW_INPUT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_review_inputs:
                    continue
                raise ValueError(owner + ' fields require the actual review input')
            owner = next((name for name, boundary in TOOL_INPUT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if (owner is None and parts and parts[0] == 'read_tool'
                    and isinstance(local[root], dict)
                    and local[root].get('properties', {}).get('read_tool')
                    is TOOL_INPUT_BOUNDARIES['record_map.read_tool']):
                owner = 'record_map.read_tool'
            if owner is not None:
                if owner in defer_tool_inputs:
                    continue
                raise ValueError(owner + ' fields require the actual tool input')
            if local[root] is STATUS_REPORT_BOUNDARY:
                if defer_status:
                    continue
                raise ValueError('status fields require the actual repository report')
            if local[root] is OPERATION_PROGRESS_BOUNDARY:
                if defer_operation_progress:
                    continue
                raise ValueError('operation_progress fields require the actual file report')
            if local[root] is QUERY_RECORD_BOUNDARY:
                if defer_query_record:
                    continue
                raise ValueError('query_record fields require the actual query record')
            if local[root] is QUERY_RESULT_BOUNDARY:
                if defer_query_result:
                    continue
                raise ValueError('query_result fields require the actual query --files response')
            owner = next((name for name, boundary in CLI_RESULT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_cli_results:
                    continue
                raise ValueError(owner + ' fields require the actual CLI result')
            owner = next((name for name, boundary in ROLE_INPUT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_role_inputs:
                    continue
                raise ValueError(owner + ' fields require the actual role input')
            owner = next((name for name, boundary in CONTINUATION_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_continuations:
                    continue
                raise ValueError(owner + ' fields require the actual continuation result')
            candidates = [local[root]]
            owner = next((name for name, boundary in OPERATIONAL_INPUT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_operational_inputs:
                    continue
                raise ValueError(owner + ' fields require the actual operational input')
            owner = next((name for name, boundary in RESULT_INPUT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_result_inputs:
                    continue
                raise ValueError(owner + ' fields require the actual result input')
            for part in parts:
                candidates = [child for schema in candidates for child in
                              (item_variants(schema) if part.startswith('[') else property_variants(schema, part))]
                if not candidates:
                    issues.append(('scoped field', span))
                    break
    return sorted(set(issues))


def delivery_field_issues(text, owner, value):
    """Check one actual check or routed repair, including its line-local alias."""
    if owner not in DELIVERY_INPUT_BOUNDARIES:
        raise ValueError('Unknown delivery input owner: ' + owner)
    issues = []
    for line in text.splitlines():
        local, _ = field_bindings(line, DELIVERY_INPUT_BOUNDARIES)
        for token in SPAN.findall(line):
            if not FIELD.fullmatch(token):
                continue
            root, *parts = token.split('.')
            if local.get(root) is not DELIVERY_INPUT_BOUNDARIES[owner]:
                continue
            node = value
            for part in parts:
                if not isinstance(node, dict) or part not in node:
                    issues.append(('actual field', token))
                    break
                node = node[part]
    return sorted(set(issues))


def review_field_issues(text, owner, value):
    """Traverse a real seat or fixed investigation value, with line-local aliases.

    An empty list cannot establish an item field. Stage-specific empty cases
    are tested separately; the document owner must have a populated sample.
    """
    if owner not in REVIEW_INPUT_BOUNDARIES:
        raise ValueError('Unknown review input owner: ' + owner)
    def visit(node, parts):
        if not parts:
            return True
        part, *tail = parts
        if part.startswith('['):
            if not isinstance(node, list) or not node:
                return False
            index = part[1:-1]
            items = node if not index else node[int(index):int(index) + 1]
            return bool(items) and all(visit(item, tail) for item in items)
        return isinstance(node, dict) and part in node and visit(node[part], tail)
    issues = []
    for line in text.splitlines():
        local, _ = field_bindings(line, REVIEW_INPUT_BOUNDARIES)
        for token in SPAN.findall(line):
            if FIELD.fullmatch(token):
                root, *parts = re.findall(r'[a-z][a-z0-9_]*|\[\d*\]', token)
                if local.get(root) is REVIEW_INPUT_BOUNDARIES[owner] and not visit(value, parts):
                    issues.append(('actual field', token))
    return sorted(set(issues))


def tool_field_issues(text, owner, value):
    """Traverse one installed input value; preview is the verifier's child.

    No installation, missing field or another tool's command can establish
    a positive sample. File/command identity is checked by engine_context.
    """
    if owner not in TOOL_INPUT_BOUNDARIES:
        raise ValueError('Unknown tool input owner: ' + owner)
    bindings = {key: boundary for key, boundary in TOOL_INPUT_BOUNDARIES.items()
                if key != 'record_map.read_tool'}
    bindings['record_map'] = {'properties': {'read_tool': TOOL_INPUT_BOUNDARIES['record_map.read_tool']}}
    def visit(node, parts):
        for part in parts:
            if not isinstance(node, dict) or part not in node:
                return False
            node = node[part]
        return True
    issues = []
    for line in text.splitlines():
        local, _ = field_bindings(line, bindings)
        for token in SPAN.findall(line):
            if not FIELD.fullmatch(token):
                continue
            root, *parts = token.split('.')
            selected = local.get(root) is TOOL_INPUT_BOUNDARIES[owner]
            if owner == 'record_map.read_tool' and local.get(root) is bindings['record_map']:
                selected = bool(parts and parts.pop(0) == 'read_tool')
            if selected and not visit(value, parts):
                issues.append(('actual field', token))
    return sorted(set(issues))


def result_field_issues(text, owner, value):
    """Read fields of one actual catalog/restoration result, including line aliases.

    Empty arrays establish only the empty case. Populated producer tests own
    item fields; an index requires that actual item. Other owners remain under
    their own checks and cannot lend their fields to this value.
    """
    if owner not in RESULT_INPUT_BOUNDARIES:
        raise ValueError('Unknown result input owner: ' + owner)
    def visit(node, parts):
        if not parts:
            return True
        part, *tail = parts
        if part.startswith('['):
            if not isinstance(node, list):
                return False
            index = part[1:-1]
            items = node if not index else node[int(index):int(index) + 1]
            return (not index or bool(items)) and all(visit(item, tail) for item in items)
        return isinstance(node, dict) and part in node and visit(node[part], tail)
    issues = []
    for line in text.splitlines():
        local, _ = field_bindings(line, RESULT_INPUT_BOUNDARIES)
        for token in SPAN.findall(line):
            if not FIELD.fullmatch(token):
                continue
            root, *parts = re.findall(r'[a-z][a-z0-9_]*|\[\d*\]', token)
            if local.get(root) is RESULT_INPUT_BOUNDARIES[owner] and not visit(value, parts):
                issues.append(('actual field', token))
    return sorted(set(issues))


def operational_field_issues(text, owner, value):
    """Traverse one actual input, preserving each item and its conditional branch.

    Null checkpoint sources and restoration errors are explicit document reading
    conditions. Empty arrays do not establish an item shape; populated real
    producer tests check those paths separately. No union of sample keys is used.
    """
    if owner not in OPERATIONAL_INPUT_BOUNDARIES:
        raise ValueError('Unknown operational input owner: ' + owner)
    issues = []
    def visit(node, parts, path):
        if not parts:
            return True
        if node is None and path == owner + '.checkpoint_source':
            return True
        part, *remaining = parts
        if part.startswith('['):
            if not isinstance(node, list):
                return False
            index = part[1:-1]
            items = node if not index else node[int(index):int(index) + 1]
            return (not index or bool(items)) and all(visit(item, remaining, path + part) for item in items)
        if not isinstance(node, dict):
            return False
        if part == 'restoration_error' and part not in node:
            return True  # Successful source; the error-only reading instruction does not apply.
        if part == 'local_path' and 'restoration_error' in node:
            return True  # Error sources must never be materialized; checked at the file boundary.
        return part in node and visit(node[part], remaining, path + '.' + part)
    for token in SPAN.findall(text):
        if FIELD.fullmatch(token) and re.split(r'[.\[]', token)[0] == owner:
            parts = re.findall(r'[a-z][a-z0-9_]*|\[\d*\]', token)[1:]
            if not visit(value, parts, owner):
                issues.append(('actual field', token))
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


def constant_reference_issues(text):
    issues = []
    for token in SPAN.findall(text):
        if not re.fullmatch(r'[a-z][a-z0-9_]*\.[A-Z][A-Z0-9_]*', token):
            continue
        module, name = token.split('.')
        try:
            value = getattr(importlib.import_module('do_math.' + module), name)
        except (ImportError, AttributeError):
            issues.append(('constant reference', token))
        else:
            if callable(value):
                issues.append(('constant reference', token))
    return sorted(set(issues))

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
import json
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
                         ('source_ref', 'materialized_output_files', 'research_sources', 'results', 'call_result')}
TOOL_INPUT_BOUNDARIES = {owner: object() for owner in
                        ('execution_window', 'scholarly', 'formal_verifier', 'preview',
                         'record_map.read_tool', 'submission_contract')}
REVIEW_INPUT_BOUNDARIES = {owner: object() for owner in
                          ('role_review', 'pending_findings', 'review_research', 'review_sources')}
DELIVERY_INPUT_BOUNDARIES = {owner: object() for owner in ('submission_check', 'repair')}
GOVERNANCE_BOUNDARIES = {owner: object() for owner in
                         ('import_payload', 'import_check', 'governance', 'academic_validation')}
WAIT_BOUNDARIES = {owner: object() for owner in ('change', 'plan_settle_wait')}
TRUST_BOUNDARIES = {owner: object() for owner in ('project', 'toolchain', 'environment_check')}


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
            if len(tokens) > 1 and tokens[0] in options and (tokens[0] == 'operator' or
                    any(token.strip('[]').startswith('--') for token in tokens[1:])):
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
            if name == 'operator' and arguments:
                from do_math.cli_contract import build_parser, _command_parsers
                parser = _command_parsers(build_parser())['operator']
                choices = next(action.choices for action in parser._actions if action.dest == 'mode')
                mode = arguments[0].strip('[]')
                if not mode.startswith('--'):
                    for alternative in mode.split('|'):
                        if alternative not in choices:
                            issues.add(('command mode', name, alternative))
            for argument in arguments:
                argument = argument.strip('[]')  # Optional arguments in command synopses.
                if FLAG.fullmatch(argument):
                    flag = argument.split('=', 1)[0]
                    if flag not in options[name]:
                        issues.add(('command option', name, flag))
    issues.update(tool_command_issues(text))
    return sorted(issues)


def tool_command_issues(text):
    """Parse only setup/probe command examples, using the same entry as main."""
    from contextlib import redirect_stderr
    import io
    import setup_lean
    import probe_cli
    parsers = {'setup_lean.py': setup_lean.parse_arguments,
               'probe_cli.py': probe_cli.parse_arguments}
    issues = set()
    for example in code_examples(text):
        match = re.search(r'\b(setup_lean\.py|probe_cli\.py)\b', example)
        if match is None:
            continue
        owner = match.group(1)
        try:
            tail = re.sub(r'<[^<>]+>', lambda value: value.group().replace(' ', '_'), example[match.end():])
            argv = [part.strip('"\'') for part in shlex.split(tail, posix=False)]
        except ValueError:
            issues.add(('tool arguments', owner, 'unparseable command example'))
            continue
        if '|' in argv:
            argv = argv[:argv.index('|')]  # A shell pipeline is outside this tool's argv.
        if not argv:
            continue  # A bare filename is also used as a file reference in prose.
        error = io.StringIO()
        try:
            with redirect_stderr(error):
                parsers[owner](argv)
        except SystemExit as exit:
            if exit.code != 0:
                issues.add(('tool arguments', owner, error.getvalue().split('error: ', 1)[-1].strip()))
    return sorted(issues)


def _document_section(text, heading):
    """An explicit document coordinate, not inferred ownership of arbitrary prose."""
    headings = list(re.finditer(r'^(#{2,4}) (.+)$', text, flags=re.M))
    selected = [i for i, match in enumerate(headings) if match.group(2) == heading]
    if len(selected) != 1:
        raise ValueError('expected one document section: ' + heading)
    index = selected[0]
    start = headings[index]
    end = next((match.start() for match in headings[index + 1:]
                if len(match.group(1)) <= len(start.group(1))), len(text))
    return text[start.end():end].strip()


def _schema_path(schema, path):
    variants = [schema]
    for part in path.split('.'):
        name = part.removesuffix('[]')
        variants = [child for value in variants for child in property_variants(value, name)]
        if part.endswith('[]'):
            variants = [child for value in variants for child in item_variants(value)]
    return variants


def review_output_issues(text):
    """Only the initial declaration and organize output paragraphs have these owners.

    initial.id is the explicitly described finding's ID; organize's two bare
    names are issues item fields. pending_findings is supplied input. Other
    paragraphs, enum examples and unrelated backticks are not output claims.
    """
    from do_math.review_cycle import stage_schema
    issues = []
    coordinates = (
        ('initial', '초기 검토에서는 전체 판단과 발견을 반환한다',
         ('decision', 'findings', 'scope_complete'), {'id': 'findings[].id'}),
        ('organize', '쟁점 정리에서는 발견과 답변 담당을 연결한다',
         ('finding_refs', 'answer_role_slot_id'),
         {'finding_refs': 'issues[].finding_refs', 'answer_role_slot_id': 'issues[].answer_role_slot_id'}))
    for stage, heading, declarations, aliases in coordinates:
        try:
            section = _document_section(text, heading)
        except ValueError as error:
            issues.append(('review output section', stage, str(error)))
            continue
        paragraphs = section.split('\n\n')
        chosen = paragraphs[:1] if stage == 'initial' else paragraphs[:2]
        if not chosen[0].startswith('`' + stage + '`에서는') or (stage == 'organize' and
                (len(chosen) != 2 or not chosen[1].startswith('반환의 '))):
            issues.append(('review output declaration', stage))
            continue
        names = set(SPAN.findall('\n\n'.join(chosen))) - {stage}
        if stage == 'organize':
            names -= {'pending_findings', 'pending_findings[].ref'}
        for name in declarations:
            if name not in names:
                issues.append(('review output missing field', stage, aliases.get(name, name)))
        schema = stage_schema(stage)
        for name in sorted(names):
            path = aliases.get(name, name)
            if not _schema_path(schema, path):
                issues.append(('review output field', stage, path))
    return issues


def preparation_example_issues(text):
    """Two required partial JSON examples, each bound to its actual extension owner."""
    import jsonschema
    from do_math.submission import extension_schema
    ordinary = extension_schema({'role': 'research_preparation'})
    sibling = _schema_path(ordinary, 'contract_checks[].sibling_boundaries[]')[0]
    supplemental = extension_schema({'role': 'research_preparation', 'assessment_targets': []})
    coordinates = (
        ('sibling_boundaries[]', '5. 제출 전에 계약을 스스로 점검한다', sibling),
        ('assessment_targets', '기존 과제의 평가와 관찰 규칙을 보충하는 실행', supplemental))
    issues = []
    for owner, heading, schema in coordinates:
        try:
            section = _document_section(text, heading)
        except ValueError as error:
            issues.append(('preparation example section', owner, str(error)))
            continue
        fences = re.findall(r'^```json\n(.*?)\n```', section, flags=re.M | re.S)
        if len(fences) != 1:
            issues.append(('preparation example count', owner, len(fences)))
            continue
        try:
            value = json.loads(fences[0])
        except ValueError as error:
            issues.append(('preparation example JSON', owner, str(error)))
            continue
        if owner == 'assessment_targets' and isinstance(value, dict):
            for field in ('model_assessments', 'model_assessment_deferrals'):
                if not value.get(field):
                    issues.append(('preparation example missing family', owner, field))
        for error in sorted(jsonschema.Draft202012Validator(schema).iter_errors(value),
                            key=lambda error: (str(list(error.absolute_path)), error.validator, error.message)):
            path = '/'.join(map(str, error.absolute_path))
            issues.append(('preparation example schema', owner, path, error.validator, error.message))
    return issues


def _required_section(text, heading, owner, issues):
    try:
        return _document_section(text, heading)
    except ValueError as error:
        issues.append(('document section', owner, str(error)))
        return None


def _json_examples(section, owner, count, issues):
    if section is None:
        return []
    fences = re.findall(r'^```json\n(.*?)\n```', section, flags=re.M | re.S)
    if len(fences) != count:
        issues.append(('document JSON count', owner, len(fences), count))
        return []
    values = []
    for fence in fences:
        try:
            values.append(json.loads(fence))
        except ValueError as error:
            issues.append(('document JSON', owner, str(error)))
    return values


def _schema_issues(value, schema, owner):
    import jsonschema
    return [('document schema', owner, '/'.join(map(str, error.absolute_path)),
             error.validator, error.message)
            for error in sorted(jsonschema.Draft202012Validator(schema).iter_errors(value),
                                key=lambda error: (str(list(error.absolute_path)), error.validator, error.message))]


def initialization_example_issues(text, document):
    """The README setting and the two grant requests; placeholders stay symbolic."""
    from do_math.configuration import validate_config
    from do_math.control_contracts import DECISION, GRANT
    issues = []
    if document == 'README.md':
        section = _required_section(text, '모델과 동시실행 예산 설정', 'config', issues)
        for value in _json_examples(section, 'config', 1, issues):
            if not isinstance(value, dict):
                issues.append(('document config', 'config must be an object'))
                continue
            # This setting example promises both model mapping and slot mapping;
            # other configuration fields intentionally use product defaults.
            for field in ('tier_models', 'session_limits'):
                if field not in value:
                    issues.append(('document config missing field', field))
            try:
                validate_config(value, host_id='document-example')
            except ValueError as error:
                issues.append(('document config', str(error)))
    elif document == 'references/초기화-운전.md':
        section = _required_section(text, '3. 초기화 권한과 연구 권한을 나눈다', 'grant', issues)
        for value in _json_examples(section, 'grant', 2, issues):
            issues.extend(_schema_issues(value, DECISION, 'decision'))
            if not isinstance(value, dict) or value.get('kind') != 'grant' or not isinstance(value.get('grant'), dict):
                issues.append(('document grant request', 'expected kind=grant and grant object'))
                continue
            grant = value['grant']
            issues.extend(_schema_issues(grant, GRANT, 'grant'))
            # Required declarations in these complete request examples, not a
            # stronger grant schema or an authorization/expiry-time check.
            for field in ('id', 'kind', 'roles', 'task_ids', 'reuse', 'expires_at'):
                if field not in grant:
                    issues.append(('document grant missing field', field))
    return issues


def identity_module_issues(text):
    """Bind this one enumerating sentence to the actual adapter declarations."""
    from do_math.codex_adapter import CodexExecAdapter
    from do_math.claude_adapter import ClaudePrintAdapter
    issues = []
    section = _required_section(text, '4. 현행 프로필의 능력을 관측하고 채택한다', 'identity_modules', issues)
    if section is None:
        return issues
    match = re.search(r'Codex 어댑터의 식별 모듈은 (.*?)이고, Claude 어댑터는 여기에 (.*?)을 더한다\.', section)
    if match is None:
        return issues + [('identity modules declaration', 'missing')]
    codex = SPAN.findall(match.group(1))
    extra = SPAN.findall(match.group(2))
    for owner, names, adapter in (
            ('CodexExecAdapter', codex, CodexExecAdapter),
            ('ClaudePrintAdapter', codex + extra, ClaudePrintAdapter)):
        expected = set(adapter.identity_modules)
        actual = set(names)
        if actual != expected or len(names) != len(actual):
            issues.append(('identity modules', owner, tuple(sorted(expected - actual)),
                           tuple(sorted(actual - expected)), len(names) != len(actual)))
    return issues


def cli_table_issues(text):
    from do_math.configuration import DEFAULT_CONFIG
    from do_math.record_schemas import config_schema
    from do_math.record_schemas.schemas import RUNTIME_FIELDS
    issues = []
    section = _required_section(text, '인스턴스 실행 루프 `runtime.status`', 'runtime.status', issues)
    if section is not None:
        names = re.findall(r'^\| `([a-z_]+)` \|', section, flags=re.M)
        expected = set(RUNTIME_FIELDS['status']['enum'])
        if set(names) != expected or len(names) != len(set(names)):
            issues.append(('document state table', 'runtime.status', tuple(sorted(expected - set(names))),
                           tuple(sorted(set(names) - expected))))
    section = _required_section(text, '설정 계약', 'config', issues)
    if section is None:
        return issues
    schema = config_schema()['properties']
    seen = []
    for line in section.splitlines():
        if not line.startswith('| `'):
            continue
        cells = line.strip('|').split('|')
        if len(cells) != 3:
            issues.append(('document config row', line))
            continue
        key_cell, default, allowed = (cell.strip() for cell in cells)
        keys = SPAN.findall(key_cell)
        seen.extend(keys)
        for key in keys:
            if key not in schema:
                issues.append(('document config key', key))
        if len(keys) != 1 or keys[0] not in schema:
            continue
        key = keys[0]
        if default.startswith('없음'):
            if key in DEFAULT_CONFIG:
                issues.append(('document config absent default', key))
        elif schema[key].get('type') != 'object':
            literal = default.strip('`')
            try:
                value = json.loads(literal)
            except ValueError:
                value = literal
            if key not in DEFAULT_CONFIG or value != DEFAULT_CONFIG[key] or type(value) is not type(DEFAULT_CONFIG[key]):
                issues.append(('document config default', key, default, repr(DEFAULT_CONFIG.get(key))))
        if 'enum' in schema[key]:
            names = set(SPAN.findall(allowed))
            if key == 'operator_effort' and 'effort' in names:
                names.remove('effort')
                names.update(schema['effort']['enum'])
            if names != set(schema[key]['enum']):
                issues.append(('document config enum', key, tuple(sorted(names)), tuple(sorted(schema[key]['enum']))))
    if set(seen) != set(schema) or len(seen) != len(set(seen)):
        issues.append(('document config table coverage', tuple(sorted(set(schema) - set(seen))),
                       tuple(sorted(set(seen) - set(schema)))))
    return issues


def cli_query_issues(text):
    from do_math.cli_contract import build_parser, _command_parsers
    issues = []
    section = _required_section(text, 'record `query`', 'query', issues)
    if section is None:
        return issues
    synopsis = re.findall(r'^```text\n(.*?)\n```', section, flags=re.M | re.S)
    if len(synopsis) != 1:
        return issues + [('query synopsis count', len(synopsis))]
    match = re.search(r'\[--direction ([a-z|]+)\]', synopsis[0])
    parser = _command_parsers(build_parser())['query']
    expected = next(action.choices for action in parser._actions if action.dest == 'direction')
    if match is None or set(match.group(1).split('|')) != set(expected):
        issues.append(('query direction choices', match.group(1) if match else 'missing', tuple(expected)))
    return issues


def cli_knowledge_example_issues(text):
    from do_math.control_contracts import validate_control_payload
    from do_math.knowledge_io import candidate_shape_errors
    issues = []
    coordinates = (('candidate 수입', 2), ('종류 정의 등록', 1), ('관계 수입', 1), ('기존 지식 개정·무효화', 2))
    for heading, count in coordinates:
        section = _required_section(text, heading, 'knowledge', issues)
        values = _json_examples(section, 'knowledge/' + heading, count, issues)
        # The second candidate fence is explicitly a partial relation_claim.
        complete = values[:1] if heading == 'candidate 수입' else values
        for value in complete:
            try:
                validate_control_payload('knowledge', '', value)
            except ValueError as error:
                issues.append(('document knowledge control', str(error)))
            if heading == 'candidate 수입':
                if not isinstance(value, dict) or not isinstance(value.get('candidate'), dict):
                    issues.append(('document knowledge candidate', 'missing candidate object'))
                else:
                    issues.extend(('document knowledge candidate', error)
                                  for error in candidate_shape_errors(value['candidate']))
    return issues


def _declared_fields_issues(sentence, schema, owner):
    """Explicit backtick output declarations only; enum values keep their owner."""
    issues = []
    names = set()
    for token in SPAN.findall(sentence):
        name, equals, alternatives = token.partition('=')
        name = name.removesuffix('[]')
        names.add(name)
        variants = property_variants(schema, name)
        if not variants:
            issues.append(('CLI stage field', owner, name))
        elif equals and not any(set(alternatives.split('|')) == set(value.get('enum', [])) for value in variants):
            issues.append(('CLI stage enum', owner, name, alternatives))
    for name in sorted(set(schema.get('required', [])) - names):
        issues.append(('CLI stage missing field', owner, name))
    return issues


def cli_stage_issues(text):
    from do_math.review_cycle import stage_schema
    issues = []
    section = _required_section(text, '동일성 검토 계보의 동적 JSON', 'stage common', issues)
    if section is None:
        return issues
    preamble = section.split('###', 1)[0]
    common = set(SPAN.findall(preamble))
    # Root schemas define the common fields; the preamble must name them.
    baseline = set(stage_schema('initial')['properties']) & set(stage_schema('organize')['properties'])
    if common != baseline:
        issues.append(('CLI stage common declaration', tuple(sorted(common)), tuple(sorted(baseline))))
    item_coordinates = {
        'initial': (('각 finding은 ', 'findings[]'),),
        'organize': (('각 issue는 ', 'issues[]'), ('finding ref는 ', 'issues[].finding_refs[]')),
        'answer': (('answer는 ', 'answers[]'), ('new finding은 ', 'new_findings[]')),
        'judge': (('issue verdict는 ', 'issue_verdicts[]'),)}
    for stage in item_coordinates:
        part = _required_section(section, '`' + stage + '`', stage, issues)
        if part is None:
            continue
        schema = stage_schema(stage)
        sentence = part.split('. ', 1)[0]
        root_schema = {**schema, 'required': sorted(set(schema['required']) - baseline)}
        issues.extend(_declared_fields_issues(sentence, root_schema, stage))
        for prefix, path in item_coordinates[stage]:
            match = re.search(re.escape(prefix) + r'(.*?)(?:\. |\.$)', part)
            if match is None:
                issues.append(('CLI stage item declaration', stage, path))
                continue
            item = _schema_path(schema, path)[0]
            issues.extend(_declared_fields_issues(match.group(1), item, stage + '/' + path))
    return issues


def cli_checkpoint_issues(text):
    from do_math.observations import checkpoint_value
    from jsonschema import ValidationError
    issues = []
    section = _required_section(text, '`checkpoint.json`', 'checkpoint', issues)
    for value in _json_examples(section, 'checkpoint', 1, issues):
        try:
            checkpoint_value(json.dumps(value, ensure_ascii=False).encode('utf-8'))
        except (ValueError, ValidationError) as error:
            issues.append(('document checkpoint', str(error)))
    return issues


def named_document_issues(text, document):
    """Mandatory coordinates in three documents, never inferred from arbitrary words."""
    issues = initialization_example_issues(text, document)
    if document == 'references/초기화-운전.md':
        issues.extend(identity_module_issues(text))
    if document == 'references/CLI-실행-계약.md':
        for check in (cli_table_issues, cli_query_issues, cli_knowledge_example_issues,
                      cli_stage_issues, cli_checkpoint_issues):
            issues.extend(check(text))
    return issues


def field_schemas():
    """Bind stored records separately from the role-input objects built from them."""
    from do_math import context_store, governance, reporting, submission
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
    from do_math import observations
    schemas.update(WAIT_BOUNDARIES)
    schemas.update(RESULT_INPUT_BOUNDARIES)
    schemas.update(REVIEW_INPUT_BOUNDARIES)
    schemas['subject'] = RECORDS['executions']['properties']['observation_rules']['items']['properties']['subject']
    schemas['source_range'] = governance.interpretation_schema('interpret')['properties']['import_units']['items']['properties']['source_range']
    schemas.update(GOVERNANCE_BOUNDARIES)
    schemas['worker_feedback'] = {'properties': {key: {} for key in observations.WORKER_FEEDBACK_FIELDS}}
    schemas['query_result'] = QUERY_RESULT_BOUNDARY
    schemas.update(TRUST_BOUNDARIES)
    def array(item):
        return {'type': 'array', 'items': item}
    schemas['candidates'] = contracts.schema_for('research_preparation')['properties']['candidates']
    schemas['task_assessments'] = contracts.schema_for('research_plan')['properties']['task_assessments']
    schemas['item_dispositions'] = schemas['task_assessments']['items']['properties']['item_dispositions']
    extensions = submission.extension_schema({'role': 'research_preparation'})['properties']
    for name in ('task_conditions', 'knowledge_changes', 'revision_resolutions', 'contract_checks', 'question_routes'):
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
    schemas['operation_progress'] = OPERATION_PROGRESS_BOUNDARY
    schemas['status'] = STATUS_REPORT_BOUNDARY
    schemas.update(OPERATIONAL_INPUT_BOUNDARIES)
    return schemas


def status_field_schema(report, *, task_report=None):
    """Bind status fields from a final repository response, never its producers.

    Keep the fixed nested objects previously covered by the document binding;
    a sample does not establish blocker variants or items in empty arrays.
    An optional second repository response can supply nonempty task rows;
    it never supplies top-level fields missing from the primary response.
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
    task_rows = (task_report if task_report is not None else report).get('tasks', [])
    if 'tasks' in report and task_rows:
        schema['properties']['tasks'] = {'type': 'array', 'items': {
            'type': 'object', 'properties': {name: {} for row in task_rows for name in row},
            'additionalProperties': False}}
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
                        defer_delivery_inputs=(), defer_governance=(), defer_waits=(), defer_trust=()):
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
    unknown = set(defer_governance) - GOVERNANCE_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred governance owners: {sorted(unknown)}')
    unknown = set(defer_waits) - WAIT_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred wait owners: {sorted(unknown)}')
    unknown = set(defer_trust) - TRUST_BOUNDARIES.keys()
    if unknown:
        raise ValueError(f'Unknown deferred trust owners: {sorted(unknown)}')
    for line in text.splitlines():
        local, binding_issues = field_bindings(line, schemas)
        issues.extend(binding_issues)
        for span in SPAN.findall(line):
            if not FIELD.fullmatch(span):
                continue
            root, *parts = re.findall(r'[a-z][a-z0-9_]*|\[\d*\]', span)
            if root not in local:
                continue
            owner = next((name for name, boundary in TRUST_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_trust:
                    continue
                raise ValueError(owner + ' fields require the actual trust boundary')
            owner = next((name for name, boundary in WAIT_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_waits:
                    continue
                raise ValueError(owner + ' fields require the actual wait boundary')
            owner = next((name for name, boundary in GOVERNANCE_BOUNDARIES.items()
                          if local[root] is boundary), None)
            if owner is not None:
                if owner in defer_governance:
                    continue
                raise ValueError(owner + ' fields require the actual governance value')
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


def trust_field_issues(text, owner, value):
    """Read actual trust returns, retaining the documented conditional absences.

    Non-Lake project is null. changed_files exists only for a fingerprint
    mismatch, not for verified/rebind or an earlier record/identity error.
    Positive Lake and mismatch scenes separately check these spellings.
    """
    if owner not in TRUST_BOUNDARIES:
        raise ValueError('Unknown trust owner: ' + owner)
    issues = []
    for line in text.splitlines():
        local, _ = field_bindings(line, TRUST_BOUNDARIES)
        for token in SPAN.findall(line):
            if not FIELD.fullmatch(token):
                continue
            root, *parts = token.split('.')
            if local.get(root) is not TRUST_BOUNDARIES[owner]:
                continue
            if owner == 'project' and value is None and parts == ['source_identity']:
                continue
            if (owner == 'toolchain' and isinstance(value, dict) and 'project' in value
                    and value['project'] is None and parts == ['project', 'search_paths']):
                continue
            if (owner == 'environment_check' and isinstance(value, dict)
                    and parts == ['changed_files'] and 'changed_files' not in value
                    and (value.get('status') == 'verified' or value.get('status') == 'invalid'
                         and value.get('errors') and not any(
                             error.startswith('olean fingerprint differs') for error in value['errors']))):
                continue
            node = value
            for part in parts:
                if not isinstance(node, dict) or part not in node:
                    issues.append(('actual field', token))
                    break
                node = node[part]
    return sorted(set(issues))


def wait_field_issues(text, owner, value):
    """Check fields against a real positive input/wait sample, not required outputs.

    Missing change.value is independently tested as a whole-change comparison;
    the positive sample here validates its documented spelling only.
    """
    if owner not in WAIT_BOUNDARIES:
        raise ValueError('Unknown wait owner: ' + owner)
    issues = []
    for line in text.splitlines():
        local, _ = field_bindings(line, WAIT_BOUNDARIES)
        for token in SPAN.findall(line):
            if not FIELD.fullmatch(token):
                continue
            root, *parts = token.split('.')
            if local.get(root) is not WAIT_BOUNDARIES[owner]:
                continue
            node = value
            for part in parts:
                if not isinstance(node, dict) or part not in node:
                    issues.append(('actual field', token))
                    break
                node = node[part]
    return sorted(set(issues))


def governance_field_issues(text, owner, value):
    """Read one real import input/check or current query, retaining its owner.

    Only payload.kind is conditional on a nonempty payload, as the document
    explicitly states. A valid no-change payload does not establish any other
    field. Query failures do not provide a positive document sample.
    """
    if owner not in GOVERNANCE_BOUNDARIES:
        raise ValueError('Unknown governance owner: ' + owner)
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
        local, _ = field_bindings(line, GOVERNANCE_BOUNDARIES)
        for token in SPAN.findall(line):
            if not FIELD.fullmatch(token):
                continue
            root, *parts = re.findall(r'[a-z][a-z0-9_]*|\[\d*\]', token)
            if local.get(root) is not GOVERNANCE_BOUNDARIES[owner]:
                continue
            if owner == 'import_payload' and value == {} and parts == ['kind']:
                continue
            if not visit(value, parts):
                issues.append(('actual field', token))
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
    """Read fields of one actual catalog, restoration or call result, including line aliases.

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


def _is_callable_reference(name):
    root, *attributes = name.split('.')
    try:
        value = importlib.import_module(root if root == 'os' else 'do_math.' + root)
        for attribute in attributes:
            value = getattr(value, attribute)
    except (ImportError, AttributeError):
        return False
    return callable(value)


def function_reference_issues(text):
    """Explicit module.function(...) notation names a callable, never a state field."""
    issues = []
    for token in SPAN.findall(text):
        if not re.fullmatch(r'[a-z][a-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\(\.\.\.\)', token):
            continue
        if not _is_callable_reference(token[:-5]):
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

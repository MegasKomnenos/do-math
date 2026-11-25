"""Assemble and retain the exact context delivered to one worker."""
from pathlib import Path
import json
import os
import re
import shutil
import sys
from urllib.parse import quote, unquote

from canon import Canon, declaration_text
from runtime_support import read_json, write_json, write_text


RESEARCH_CONTEXT = ['what-research-is-for.md', 'user-writing-preferences.md']
# Every role states mathematics in Lean and reads the canon, so each receives the canon and Lean guides.
# A guide that only some roles act on goes to those roles: sections.md to the roles that register sections,
# records.md to the roles that write or judge the written texts of the canon.
ROLE_REFERENCES = {
    'attempt': RESEARCH_CONTEXT + ['literature.md', 'sections.md', 'retained-work.md'],
    'explore': RESEARCH_CONTEXT + ['literature.md', 'retained-work.md'],
    'formalizer': ['retained-work.md'],
    'peer': RESEARCH_CONTEXT + ['literature.md', 'sections.md', 'retained-work.md', 'records.md', 'change-format.md'],
    'review': RESEARCH_CONTEXT + ['literature.md', 'records.md', 'change-format.md', 'review-output.md'],
    'organizer': RESEARCH_CONTEXT + ['records.md', 'change-format.md', 'organizer-output.md'],
}


def root_in_lean(instance):
    """The root as it is fixed in Lean: its declaration and the file it stands in."""
    canon = Canon(instance)
    meta = read_json(Path(instance) / 'instance.json')
    entry = canon.load_index()['entries'][meta['root']]
    source = (canon.lean / entry['file']).read_text(encoding='utf-8').replace('\r\n', '\n')
    return (f"The root is the declaration `{meta['root']}` of the library `{meta['library']}`, in "
            f"`canon/lean/{entry['file']}`. Its statement is fixed for the life of the instance.\n\n"
            '```lean\n' + declaration_text(source, entry['span']) + '\n```\n\n'
            f"As Lean prints it: `{entry['statement']}`\n")


def rebase_links(body, source, session, scope):
    """Keep local links usable when a source is embedded in the launch pack."""
    def link(match):
        target = match[1]
        if target.startswith(('#', 'http:', 'https:', 'mailto:')):
            return match[0]
        path, separator, fragment = target.partition('#')
        resolved = (source.parent / unquote(path)).resolve()
        if not resolved.is_relative_to(scope.resolve()):
            raise ValueError('context reference escapes its source area: ' + target)
        relative = Path(os.path.relpath(resolved, session)).as_posix()
        return '](' + quote(relative, safe='/') + (separator + fragment if separator else '') + ')'
    return re.sub(r'\]\(([^)]+)\)', link, body)


def assemble(skill, instance, session, role, task, pipeline, revision, settings):
    skill, instance, session = map(Path, (skill, instance, session))
    context = session / 'context'
    (context / 'reference').mkdir(parents=True)
    (context / 'roles').mkdir()
    # References are snapshots too: editing installed guidance does not change a
    # running session's instructions when it follows a reference later.
    for source in (skill / 'reference').glob('*.md'):
        shutil.copyfile(source, context / 'reference' / source.name)
    shutil.copyfile(skill / 'roles' / (role + '.md'), context / 'roles' / (role + '.md'))
    # reference/operations.md links to ../SKILL.md; this copy keeps that link inside the snapshot.
    shutil.copyfile(skill / 'SKILL.md', context / 'SKILL.md')
    inputs = []
    for path in sorted((instance / 'control/inputs').glob('*.txt')):
        inputs.append({'id': path.name, 'text': path.read_text(encoding='utf-8-sig')})
    runtime = skill / 'runtime'
    commands = {
        'updates': [sys.executable, str(runtime / 'coordination.py'), 'updates', str(session)],
        'canon': [sys.executable, str(runtime / 'canon_tool.py'), '<command>', str(session)],
        'prepare': [sys.executable, str(runtime / 'canon_tool.py'), 'prepare', str(session)],
        'verify': [sys.executable, str(runtime / 'canon_tool.py'), 'verify', str(session)],
        'lease': [sys.executable, str(runtime / 'coordination.py'), 'lease', str(session), '<element>'],
        'wait': [sys.executable, str(runtime / 'coordination.py'), 'wait', str(session), '<element>', '--timeout', '50'],
        'section': [sys.executable, str(runtime / 'coordination.py'), 'section', str(session), '<element>', '--file', '<file>'],
        'release': [sys.executable, str(runtime / 'coordination.py'), 'release', str(session), '<element>'],
        'question_lease': [sys.executable, str(runtime / 'coordination.py'), 'question-lease', str(session), '<question>'],
        'question_wait': [sys.executable, str(runtime / 'coordination.py'), 'question-wait', str(session), '<question>', '--timeout', '50'],
        'question_take': [sys.executable, str(runtime / 'coordination.py'), 'question-take', str(session), '<question>'],
        'question_release': [sys.executable, str(runtime / 'coordination.py'), 'question-release', str(session), '<question>'],
        'message': [sys.executable, str(runtime / 'coordination.py'), 'message', str(session), '<recipient>', '--file', '<file>'],
        'check': [sys.executable, str(runtime / 'check.py'), str(session)],
        'lean': [sys.executable, str(runtime / 'lean_broker.py'), '<command>', str(instance)],
    }
    documents = ['reference/common.md', 'roles/' + role + '.md', 'reference/writing.md', 'reference/canon.md',
                 'reference/lean.md', 'reference/tools.md']
    documents += ['reference/' + name for name in ROLE_REFERENCES[role]]
    inp = {'schema': 1, 'instance': str(instance), 'session': session.name, 'role': role,
           'pipeline': pipeline, 'task': task, 'revision': revision,
           'references': str(context / 'reference'), 'documents': documents,
           'user_inputs': inputs, 'settings': settings, 'commands': commands}
    write_json(session / 'input.json', inp)

    def view(name, path, text=None):
        # Preserve mathematical text verbatim. Its relative references retain the
        # original source base, rather than rewriting arbitrary mathematical prose.
        return ['# ' + name, '', 'Source: ' + str(path),
                'Relative references in this research view use ' + str(path.parent) + ' as their base.',
                '', text if text is not None else path.read_text(encoding='utf-8-sig'), '']

    # The proposition and the assignment come before the guides, so that the guides are read with both in mind.
    parts = ['# Your do-math session', '',
             f'Role: {role}. Session: {session.name}. Instance: {instance}.', '',
             'Read this complete context before working. It begins with the proposition this instance exists to settle '
             'and with your assignment. The guides that explain your role follow; copies of their references are under '
             'context/reference/ in your session folder. After the guides come the research as it stood at your launch, '
             'the user conditions and the commands.', '']
    parts += view('Root statement', instance / 'root.md')
    # instance.json names the root and its library, and its folder, the instance, is the base of the path
    # that root_in_lean gives for the root's file.
    parts += view('The root in Lean', instance / 'instance.json', root_in_lean(instance))
    parts += ['# Your assignment', '',
              'This is `task` from input.json. Your role guide explains its fields. Where it names no work, your role '
              'chooses its own.', '',
              '```json', json.dumps({'task': task}, ensure_ascii=False, indent=2), '```', '']
    for name in documents:
        source = context / name
        body = source.read_text(encoding='utf-8-sig')
        body = rebase_links(body, source, session, context)
        parts += [f'<!-- begin {name} -->', body, f'<!-- end {name} -->', '']
    understanding = instance / 'canon/questions/q0.md'
    parts += view('Frontier at launch', instance / 'knowledge/frontier.md')
    parts += view('Understanding so far of the root problem as a whole (question q0)', understanding,
                  None if understanding.is_file() else 'No exploration has written it yet.\n')
    parts += view('Board at launch', instance / 'knowledge/board.md')
    parts += ['# User conditions supplied at launch', '',
              'The following inputs apply in listed order. Later conditions override earlier conditions on the same matter. '
              'Mathematical suggestions remain suggestions; they do not certify claims.']
    for item in inputs:
        parts += ['', '## ' + item['id'], '', item['text']]
    parts += ['', '# Executable commands', '',
              'These are `commands` from input.json; that file also holds your session identity, settings and '
              'user-condition snapshot.', '',
              '```json', json.dumps({'commands': commands}, ensure_ascii=False, indent=2), '```', '']
    pack = '\n'.join(parts)
    write_text(session / 'pack.md', pack)
    # A pack holds hundreds of thousands of bytes, more than the reading tool of a CLI returns in one call.
    # The prompt gives the size, so that a session reads the pack in ranges from its first call.
    lines, size = pack.count('\n'), len(pack.encode('utf-8'))
    write_text(session / 'prompt.txt',
               f'You are a do-math {role} session. Your working directory is {session}.\n'
               f'Read {session / "pack.md"} in full, then carry out the role it describes. The file has {lines} '
               f'lines in {size} bytes, more than a reading tool returns in one call, so read it in consecutive '
               'ranges of lines until its last line.\n'
               f'Your exact assignment, user conditions, settings and tool argv are in {session / "input.json"}.\n')
    return inp

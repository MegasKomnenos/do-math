"""Assemble and retain the exact context delivered to one worker."""
from pathlib import Path
import json
import os
import re
import shutil
import sys
from urllib.parse import quote, unquote

from runtime_support import write_json, write_text


RESEARCH_CONTEXT = ['what-research-is-for.md', 'user-writing-preferences.md']
ROLE_REFERENCES = {
    'attempt': RESEARCH_CONTEXT + ['retained-work.md'],
    'explore': RESEARCH_CONTEXT + ['retained-work.md'],
    'formalizer': ['retained-work.md', 'lean.md'],
    'peer': RESEARCH_CONTEXT + ['record-format.md', 'retained-work.md'],
    'review': RESEARCH_CONTEXT + ['record-format.md', 'review-output.md'],
    'organizer': RESEARCH_CONTEXT + ['organizer-output.md'],
}


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
        'lease': [sys.executable, str(runtime / 'coordination.py'), 'lease', str(session), '<node>'],
        'wait': [sys.executable, str(runtime / 'coordination.py'), 'wait', str(session), '<node>', '--timeout', '50'],
        'section': [sys.executable, str(runtime / 'coordination.py'), 'section', str(session), '<node>', '--file', '<file>'],
        'release': [sys.executable, str(runtime / 'coordination.py'), 'release', str(session), '<node>'],
        'question_lease': [sys.executable, str(runtime / 'coordination.py'), 'question-lease', str(session), '<question>'],
        'question_wait': [sys.executable, str(runtime / 'coordination.py'), 'question-wait', str(session), '<question>', '--timeout', '50'],
        'question_take': [sys.executable, str(runtime / 'coordination.py'), 'question-take', str(session), '<question>'],
        'question_release': [sys.executable, str(runtime / 'coordination.py'), 'question-release', str(session), '<question>'],
        'message': [sys.executable, str(runtime / 'coordination.py'), 'message', str(session), '<recipient>', '--file', '<file>'],
        'check': [sys.executable, str(runtime / 'check.py'), str(session)],
        'lean': [sys.executable, str(runtime / 'lean_broker.py'), '<command>', str(instance)],
    }
    documents = ['reference/common.md', 'roles/' + role + '.md', 'reference/writing.md', 'reference/tools.md']
    documents += ['reference/' + name for name in ROLE_REFERENCES[role]]
    inp = {'schema': 1, 'instance': str(instance), 'session': session.name, 'role': role,
           'pipeline': pipeline, 'task': task, 'revision': revision,
           'references': str(context / 'reference'), 'documents': documents,
           'user_inputs': inputs, 'settings': settings, 'commands': commands}
    write_json(session / 'input.json', inp)
    parts = ['# Your do-math session', '',
             f'Role: {role}. Session: {session.name}. Instance: {instance}.', '',
             'Read this complete context before working. The instruction sections below explain your role and the supplied research. '
             'Copies of their references are under context/reference/ in your session folder.', '']
    for name in documents:
        source = context / name
        body = source.read_text(encoding='utf-8-sig')
        body = rebase_links(body, source, session, context)
        parts += [f'<!-- begin {name} -->', body, f'<!-- end {name} -->', '']
    for name, path in [('Root statement', instance / 'root.md'), ('Full current global glossary', instance / 'knowledge/glossary.md'),
                       ('Frontier at launch', instance / 'knowledge/frontier.md'), ('Board at launch', instance / 'knowledge/board.md'),
                       ('General index at launch', instance / 'knowledge/index.md')]:
        # Preserve mathematical text verbatim. Its relative references retain the
        # original source base, rather than rewriting arbitrary mathematical prose.
        parts += ['# ' + name, '', 'Source: ' + str(path),
                  'Relative references in this research view use ' + str(path.parent) + ' as their base.',
                  '', path.read_text(encoding='utf-8-sig'), '']
    parts += ['# User conditions supplied at launch', '',
              'The following inputs apply in listed order. Later conditions override earlier conditions on the same matter. '
              'Mathematical suggestions remain suggestions; they do not certify claims.']
    for item in inputs:
        parts += ['', '## ' + item['id'], '', item['text']]
    parts += ['', '# Assignment and executable commands', '',
              'This is the task-and-commands excerpt from input.json; that file also holds your session identity, settings and user-condition snapshot.', '',
              '```json', json.dumps({'task': task, 'commands': commands}, ensure_ascii=False, indent=2), '```', '']
    write_text(session / 'pack.md', '\n'.join(parts))
    write_text(session / 'prompt.txt',
               f'You are a do-math {role} session. Your working directory is {session}.\n'
               f'Read {session / "pack.md"} in full, then carry out the role it describes.\n'
               f'Your exact assignment, user conditions, settings and tool argv are in {session / "input.json"}.\n')
    return inp

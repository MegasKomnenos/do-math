"""A stand-in for `lean` that reads a small subset of Lean, for tests of the canon; no Lean is involved.

It accepts what the broker passes (`-R root`, `-o file`, `--threads=N`, the source last) and
`--version`. A module is "compiled" by parsing its declarations and writing the four files Lean
4.32 emits; the public file depends on names and statements only, so a changed proof leaves it
unchanged, as the real compiler does when the auxiliary declarations stay the same. The source
`DoMathExtract.lean` is answered with the rows canon.extraction_source asks for, computed from the
sources under the root instead of from a compiled environment.

The subset: `namespace`/`end`, an optional `/-- … -/` doc comment, then `theorem`, `def`, `axiom`,
`structure` or `inductive` (optionally `private`) with a name, a statement up to the first `:=`
and a body. A declaration ends where the next one begins. What a declaration uses is every known
declaration name that occurs in it; a body containing `sorry` depends on `sorryAx`. A line
`-- fail: <message>` makes the compile fail with that message.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sys

KEYWORDS = ('theorem', 'def', 'axiom', 'structure', 'inductive')
START = re.compile(r'^(private\s+)?(theorem|def|axiom|structure|inductive)\s+([^\s(:{\[]+)')
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_'.]*")
IMPORT = re.compile(r'^(?:public\s+)?(?:meta\s+)?import\s+(?:all\s+)?(\S+)')
SUFFIXES = ('.olean', '.olean.private', '.olean.server', '.ir')


def module_of(root, path):
    return '.'.join(Path(path).resolve().relative_to(Path(root).resolve()).with_suffix('').parts)


def parse(module, text):
    """The declarations of one module: name, kind, span, statement, body."""
    lines = text.replace('\r\n', '\n').split('\n')
    namespaces, declarations, current, doc = [], [], None, None

    def close(last):
        nonlocal current
        if current is None:
            return
        while last > current['start'] and not lines[last - 1].strip():
            last -= 1
        body = '\n'.join(lines[current['line'] - 1:last])
        head, separator, value = body.partition(':=')
        statement = ' '.join(head.split())
        statement = statement[statement.index(current['short']) + len(current['short']):].strip()
        current.update(span=[current['start'], 0, last, len(lines[last - 1])], statement=statement,
                       body=value if separator else '', text=body)
        declarations.append(current)
        current = None

    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if line.startswith('namespace '):
            close(number - 1)
            namespaces.append(stripped.split()[1])
        elif line.startswith('end ') or stripped == 'end':
            close(number - 1)
            if namespaces:
                namespaces.pop()
        elif line.startswith('/--'):
            close(number - 1)
            doc = number
        elif (match := START.match(line)):
            close((doc or number) - 1)
            short = match[3]
            name = '.'.join(namespaces + [short])
            private = bool(match[1])
            current = {'name': f'_private.{module}.0.{name}' if private else name, 'user': name, 'short': short,
                       'kind': 'inductive' if match[2] in ('structure', 'inductive') else match[2],
                       'private': private, 'module': module, 'start': doc or number, 'line': number,
                       'namespaces': list(namespaces)}
            doc = None
        elif line.startswith(('@[', 'instance', 'section', 'public section', 'open ', 'module', 'import ',
                              'public import ')) and current is not None and not line.startswith('@['):
            close(number - 1)
    close(len(lines))
    return declarations


def library(root):
    declarations = []
    for path in sorted(Path(root).rglob('*.lean')):
        module = module_of(root, path)
        if module != 'DoMathExtract':
            declarations += parse(module, path.read_text(encoding='utf-8'))
    return declarations


def uses(text, declaration, names):
    found = []
    for token in IDENT.findall(text):
        candidates = [token] + ['.'.join(declaration['namespaces'][:i] + [token])
                                for i in range(len(declaration['namespaces']), 0, -1)]
        for candidate in candidates:
            target = names.get(candidate)
            if target and target != declaration['name'] and target not in found:
                found.append(target)
                break
    return found


def statement_hash(statement):
    return hashlib.sha256(' '.join(statement.split()).encode('utf-8')).hexdigest()[:24]


def bare(statement):
    """A statement without binders' spacing and outer parentheses, to compare one with a negation of another."""
    text = ''.join(statement.split())
    text = text[1:] if text.startswith(':') else text
    while text.startswith('(') and text.endswith(')'):
        text = text[1:-1]
    return text


def extract(root, source):
    text = Path(source).read_text(encoding='utf-8')
    targets = re.search(r'def targets : Array Name := #\[(.*?)\]', text)[1]
    targets = [name.strip().lstrip('`') for name in targets.split(',') if name.strip()]
    pairs = re.findall(r'\("(\w+)", `([^,\s]+), `([^)\s]+)\)', re.search(r'def pairs .*? := #\[(.*)\]', text)[1])
    declarations = library(root)
    names = {d['user']: d['name'] for d in declarations}
    by_name = {d['name']: d for d in declarations}
    for declaration in declarations:
        if declaration['module'] not in targets:
            continue
        row = {'name': declaration['name'], 'kind': declaration['kind'], 'module': declaration['module'],
               'private': declaration['private'], 'internal': False, 'user': declaration['user'],
               'span': declaration['span'], 'sig': (declaration['user'] + ' ' + declaration['statement']).strip(),
               'prop': declaration['kind'] in ('theorem', 'axiom'),
               'statement': statement_hash(declaration['statement']),
               'type_uses': uses(declaration['statement'], declaration, names),
               'value_uses': uses(declaration['body'], declaration, names),
               'library': [], 'axioms': ['sorryAx'] if re.search(r'\bsorry\b', declaration['body']) else []}
        print('@@canon ' + json.dumps(row))
    for kind, a, b in pairs:
        left, right = by_name.get(a), by_name.get(b)
        if left is None or right is None:
            holds = False
        elif kind == 'same':
            holds = statement_hash(left['statement']) == statement_hash(right['statement'])
        else:
            negated = bare(left['statement'])
            holds = negated.startswith('¬') and bare(negated[1:]) == bare(right['statement'])
        print('@@canon ' + json.dumps({'pair': kind, 'a': a, 'b': b, 'holds': holds}))
    print('@@canon ' + json.dumps({'done': True}))
    return 0


def main(argv):
    if '--version' in argv:
        print('Lean (canon test stand-in)')
        return 0
    source = argv[-1]
    root = next((argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == '-R'), str(Path(source).parent))
    olean = next((argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == '-o'), None)
    text = Path(source).read_text(encoding='utf-8')
    search = [p for p in os.environ.get('LEAN_PATH', '').split(os.pathsep) if p]
    for line in text.splitlines():
        match = IMPORT.match(line.strip())
        if not match or match[1].split('.')[0] in ('Lean', 'Init', 'Std', 'Mathlib'):
            continue
        if not any(all(os.path.isfile(os.path.join(entry, *match[1].split('.')) + suffix) for suffix in SUFFIXES)
                   for entry in search):
            print(f"{source}:1:0: error: unknown module '{match[1]}'")
            return 1
    failure = re.search(r'^-- fail: (.*)$', text, re.MULTILINE)
    if failure:
        print(f'{source}:1:0: error: {failure[1]}')
        return 1
    if Path(source).name == 'DoMathExtract.lean':
        code = extract(root, source)
    else:
        declarations = parse(module_of(root, source), text)
        known = {d['user'] for d in library(root)}
        for declaration in declarations:
            if declaration['kind'] == 'theorem' and ':=' not in declaration['text']:
                print(f"{source}:{declaration['line']}:0: error: theorem {declaration['user']} has no proof term")
                return 1
            for token in re.findall(r'have\s+\w+\s*:=\s*([A-Za-z_][A-Za-z0-9_.\']*)', declaration['body']):
                qualified = [token] + ['.'.join(declaration['namespaces'][:i] + [token])
                                       for i in range(len(declaration['namespaces']), 0, -1)]
                if not any(q in known for q in qualified):
                    print(f"{source}:{declaration['line']}:0: error: unknown identifier '{token}'")
                    return 1
            if re.search(r'\bsorry\b', declaration['body']):
                print(f"{source}:{declaration['line']}:8: warning: declaration uses `sorry`")
        code = 0
    if olean and code == 0:
        public = json.dumps([[d['user'], d['kind'], d['statement']] + ([d['body']] if d['kind'] == 'def' else [])
                             for d in parse(module_of(root, source), text) if not d['private']])
        stem = olean[:-len('.olean')] if olean.endswith('.olean') else os.path.splitext(olean)[0]
        Path(stem).parent.mkdir(parents=True, exist_ok=True)
        for suffix, content in (('.olean', public), ('.ir', public), ('.olean.private', text), ('.olean.server', text)):
            with open(stem + suffix, 'w', encoding='utf-8') as stream:
                stream.write(content)
    sys.stdout.flush()
    return code


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

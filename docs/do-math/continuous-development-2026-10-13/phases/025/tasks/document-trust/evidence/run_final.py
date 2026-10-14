from work import *
tree, name = sys.argv[1:]
scripts = REPO / tree / 'skills/do-math/scripts'
os.environ.update(TRUST_OBSERVER_OUTPUT=str(E/('observations-'+name)),
    TRUST_OBSERVER_SCRIPTS=str(scripts),
    PYTHONPATH=str(E/'observer')+os.pathsep+os.environ.get('PYTHONPATH', ''))
ids = json.loads((E/'related-selection.json').read_text())
code = command(name, [PY, '-u', '-B', str(scripts/'run_tests.py'), *ids,
                      '--jobs', '1', '--output', str(E/name)])
sys.exit(code)

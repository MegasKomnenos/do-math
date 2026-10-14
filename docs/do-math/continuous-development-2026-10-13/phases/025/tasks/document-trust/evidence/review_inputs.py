from work import *
import ast, re, zipfile
prior=json.loads((RUN/'phases/024/tasks/document-waits/evidence/history-verification.json').read_text(encoding='utf-8-sig'))
rows=[]
for item in prior['ast_history']:
    argv=['git','show','--format=fuller',item['commit'],'--','.claude/skills/do-math/scripts/tests/support/doc_code.py']
    p=subprocess.run(argv,cwd=REPO,capture_output=True)
    assert p.returncode==0
    (E/(item['id']+'-doc-code.diff')).write_bytes(p.stdout)
    lines=p.stdout.decode('utf-8').splitlines()
    excerpts=['\n'.join(lines[max(0,n-3):n+5]) for n,line in enumerate(lines)
              if any(x in line for x in ("schemas['project']", "schemas['toolchain']", "environment_base", "schemas['environment_check']"))]
    for report in item['reports']:
        assert digest(REPO/report['path'])['sha256']==report['sha256']
        json.loads((REPO/report['path']).read_text(encoding='utf-8-sig'))
    rows.append({**item,'argv':argv,'exit_code':p.returncode,'relevant_excerpts':excerpts,
        'decision':'Replace P08 AST assembled project/toolchain/environment shapes with current actual returns; retain lexical owners, aliases, shared schemas and existing P01-P07/P09-P11/PURE checks. Remove inference helpers only after their last product consumer disappears. No historic counts are added to current results.'})
packets=json.loads((RUN/'phases/001/tasks/document-closeout/evidence/followup-packets.json').read_text(encoding='utf-8-sig'))['packets']
packet=next(p for p in packets if p['id']=='P08')
coordinates=[]
for old in packet['original_document_locations']:
    relative=old['path'].split(':',1)[1]
    path=REPO/relative
    lines=path.read_text(encoding='utf-8').splitlines()
    needle = '등록은 툴체인 기록 파일을 읽는다.' if '운전.md' in relative else (
        '현재 지문이 결박한 기준과 다르면' if old['line']==34 else '**판본 식별**은')
    n,line=next((n,l) for n,l in enumerate(lines,1) if l.startswith(needle))
    heading=next(l for l in reversed(lines[:n-1]) if l.startswith('#'))
    coordinates.append({'historical':old,'current_line':n,'heading':heading,'text':line,
                        'path_sha256':digest(path)['sha256']})
sections=[]
for item in next(p for p in packets if p['id']=='N01')['required_slices']:
    if item['id'] in ('N01-274','N01-279','N01-281'):
        sections.append(item)
prior_review=json.loads((RUN/'phases/001/tasks/closure-map/evidence/prior-review-state.json').read_text(encoding='utf-8-sig'))
pr24=next(u for u in prior_review['review_units'] if u['id']=='PR24')
save('history-verification.json',{'ast_history':rows,'pure_history_retained':prior['pure_history_retained'],
    'reuse_formal_Git':'B38/8afa57c7 retained at 012 and fixture producer fix at 016; actual current function hashes match unchanged runtime baseline. Earlier missing 10 raw reports remain missing and counts are not combined.',
    'PR24':pr24,'scope':'Only P08 trust and exact N01-274/279/281 sentences; other PR24 hunks and policy/N/L01 meaning are not closed.'})
save('change-coordinates.json',{'P08':coordinates,'N01_slices':sections})
start=json.loads((E/'start.json').read_text())
manager=json.loads((RUN/'phases/024/manager-evidence/preservation.json').read_text(encoding='utf-8-sig'))
with zipfile.ZipFile(REPO/manager['archive']) as z:
    summaries=[]
    for relative in ('.claude/skills/do-math/scripts/tests/support/doc_code.py',
                     '.claude/skills/do-math/scripts/tests/support/engine_context.py'):
        raw=z.read(relative)
        assert hashlib.sha256(raw).hexdigest()==start[relative]['sha256']
        (E/(Path(relative).stem+'-start.py')).write_bytes(raw)
        def functions(raw):
            text=raw.decode('utf-8'); lines=text.splitlines(keepends=True)
            return {n.name:''.join(lines[n.lineno-1:n.end_lineno]) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
        before=functions(raw); after=functions((REPO/relative).read_bytes())
        changed=sorted(n for n in before if before[n]!=after.get(n))
        expected={'producer_nodes','produced_object_schema','written_object_schema','consumed_object_schema',
                  'field_schemas','scoped_field_issues'} if relative.endswith('doc_code.py') else set()
        assert set(changed)==expected,(relative,changed)
        summaries.append({'path':relative,'changed_existing_functions':changed,
                          'unchanged_existing_functions':sorted(set(before)-expected),
                          'added_functions':sorted(set(after)-set(before))})
save('helper-preservation.json',summaries)
temp=Path('C:/t/p025'); temp.mkdir(parents=True,exist_ok=True)
p=subprocess.run(['git','rev-parse','--show-toplevel'],cwd=temp,capture_output=True)
assert p.returncode!=0
save('temp-parent-git.json',{'argv':['git','rev-parse','--show-toplevel'],'cwd':str(temp),
    'exit_code':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
print('P08 history',[(r['id'],len(r['relevant_excerpts']),len(r['reports'])) for r in rows])
print('Mapped P08 texts and N slices', [(s['id'],s['heading']) for s in sections])
print('Retained all other helper functions; parent TEMP has no Git repository')

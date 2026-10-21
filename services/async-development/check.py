"""Small session-invoked checks; the dispatcher does not import this module."""
import json
from pathlib import Path
import re
import sys

from workspaces import changes, files, read_json, safe


def need(value,message):
    if not value:raise ValueError(message)


def report(records, task_id):
    home=safe(records,'tasks/'+task_id);r=read_json(home/'report.json')
    need(r.get('status') in ('complete','partial','blocked'),'Unknown report status')
    for key in ('summary','verification'):need(isinstance(r.get(key),str) and r[key].strip(),f'{key} required')
    for key in ('changes','findings'):need(isinstance(r.get(key),list) and all(isinstance(x,str) for x in r[key]),f'{key} must be strings')
    if (home/'baseline.json').exists():
        _,delta=changes(records,task_id)
        need(set(r['changes'])==set(delta),'Report changes must match actual workspace changes')
    return r


def queue(records, queue_file=None):
    records=Path(records).resolve();q=read_json(queue_file or records/'queue.json')
    need(q.get('status') in ('active','blocked','complete'),'Unknown queue status')
    tasks=q.get('tasks');accepted=q.get('accepted');cancelled=q.get('cancelled',[])
    need(isinstance(tasks,list) and isinstance(accepted,list) and isinstance(cancelled,list),'Invalid task/accepted/cancelled lists')
    ids=[t['id'] for t in tasks];need(len(ids)==len(set(ids)),'Duplicate task IDs')
    need(all(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',i) for i in ids),'Unsafe task ID')
    need(set(accepted+cancelled)<=set(ids),'Unknown accepted/cancelled ID')
    need(not set(accepted)&set(cancelled),'Accepted and cancelled overlap')
    by_id={t['id']:t for t in tasks}
    state=read_json(records/'state.json') if (records/'state.json').exists() else {'tasks':{}}
    for t in tasks:
        need(t.get('kind') in ('work','review'),'Unknown task kind')
        need(isinstance(t.get('depends_on'),list) and set(t['depends_on'])<=set(ids),'Unknown dependencies')
        need(isinstance(t.get('writes'),list) and isinstance(t.get('inputs'),list),'writes/inputs required')
        need(t['kind']!='review' or not t['writes'],'Review cannot modify product')
        for p in t['writes']:safe(Path.cwd(),p)
        if t['id'] not in cancelled:
            need((records/'tasks'/t['id']/'objective.md').is_file(),'Missing objective: '+t['id'])
            need(not set(t['depends_on'])&set(cancelled),'Dependency was cancelled')
        prior=state['tasks'].get(t['id'],{})
        if 'spec' in prior:need(prior['spec']==t,'Launched task assignment changed: '+t['id'])
    visiting=set();visited=set()
    def visit(i):
        need(i not in visiting,'Dependency cycle')
        if i in visited:return
        visiting.add(i)
        for d in by_id[i]['depends_on']:visit(d)
        visiting.remove(i);visited.add(i)
    for i in ids:visit(i)
    for i in accepted:
        report(records,i)
        need((records/'tasks'/i/'integration.json').is_file(),'Integrate before acceptance: '+i)
    if q['status']=='complete':
        need(not any(e['status']=='running' for e in state['tasks'].values()),'Tasks still running')
        need(set(ids)<=set(accepted+cancelled),'Unresolved tasks remain')
        reviews=[t for t in tasks if t['kind']=='review' and t['id'] in accepted]
        need(reviews,'Final review is required')
        work={t['id'] for t in tasks if t['kind']=='work' and t['id'] in accepted}
        def ancestors(i):
            result=set(by_id[i]['depends_on'])
            for d in list(result):result.update(ancestors(d))
            return result
        need(any(report(records,t['id'])['status']=='complete' and work<=ancestors(t['id']) for t in reviews),
             'Final review must follow the accepted work')
        need(bool(q.get('reason','').strip()),'Explain completion')
    if q['status']=='blocked':need(bool(q.get('reason','').strip()),'Explain external blocker')
    return q


if __name__=='__main__':
    try:
        mode=sys.argv[1];records=Path(sys.argv[2])
        if mode=='queue':queue(records,Path(sys.argv[3]) if len(sys.argv)>3 else None)
        elif mode=='report':report(records,sys.argv[3])
        else:raise ValueError('Use queue RECORDS or report RECORDS TASK')
        print('PASS',mode)
    except (ValueError,OSError,KeyError,TypeError,json.JSONDecodeError) as exc:
        print('FAIL',exc);raise SystemExit(1)

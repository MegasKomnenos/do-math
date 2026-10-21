"""Diagnostic inspection only: never accepts/replays historical submissions."""
import collections
import json
import hashlib
from pathlib import Path
import re
from analyze_records import git_bytes, git_json
from collect_evidence import ROOT, BASE, save, SNAPSHOT

def main():
    rows=json.loads((ROOT/'evidence/execution.json').read_text(encoding='utf-8'))['records']
    audits=[]
    for num, ex in enumerate(rows,1):
        if ex['role'] in ['formal_check','trust_activate']: continue
        if ex['role']=='recovery':
            directory=BASE/'work/operator/recovery'/ex['id']/'evidence'
            raw=(directory/'stdout.jsonl').read_bytes()
            provenance=str(directory/'stdout.jsonl')
        else:
            provenance=str(Path(ex['result_ref']).parent/'provider-evidence/stdout.jsonl').replace('\\','/')
            raw=git_bytes(provenance)
        counts=collections.Counter();tool_counts=collections.Counter();failures=[];duplicates=[];terminal=[];commands=[];messages=[]
        offset=0;final=None
        for line_no, line in enumerate(raw.splitlines(keepends=True),1):
            dup=[]
            def pairs(values):
                d={}
                for k,v in values:
                    if k in d: dup.append({'key':k,'first':d[k],'second':v})
                    d[k]=v
                return d
            try: ev=json.loads(line,object_pairs_hook=pairs)
            except Exception as err:
                failures.append({'line':line_no,'offset':offset,'parse_error':str(err)});offset+=len(line);continue
            typ=ev.get('type');counts[typ]+=1
            item=ev.get('item') or {}
            if dup:duplicates.append({'line':line_no,'offset':offset,'bytes':len(line),'event':typ,'item_type':item.get('type'),'duplicates':dup})
            if typ in ['turn.completed','turn.failed','error']:terminal.append({'line':line_no,'offset':offset,'event':ev})
            if typ=='item.completed':
                tool_counts[item.get('type')]+=1
                if item.get('type')=='command_execution':
                    command=item.get('command','')
                    command=re.sub(r'(--capability[= ]+)[^\s"\']+',r'\1[REDACTED]',command)
                    rec={'line':line_no,'id':item.get('id'),'command':command,'exit_code':item.get('exit_code'),'status':item.get('status')}
                    commands.append(rec)
                    if item.get('exit_code') not in (0,None):failures.append({**rec,'output_excerpt':str(item.get('aggregated_output',''))[:1800]})
                if item.get('type')=='mcp_tool_call' and (item.get('error') or item.get('status')=='failed'):
                    failures.append({'line':line_no,'type':'mcp','server':item.get('server'),'tool':item.get('tool'),'error':item.get('error')})
                if item.get('type')=='agent_message':
                    final=item.get('text');messages.append({'line':line_no,'text':final})
        
            offset+=len(line)
        audit={'number':num,'execution_id':ex['id'],'role':ex['role'],'provenance':provenance,
               'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'event_counts':dict(counts),
               'completed_item_types':dict(tool_counts),'duplicates':duplicates,'terminal':terminal,
               'command_failures':failures,'commands':commands,'agent_messages':messages}
        save(ROOT/'evidence/logs'/f'{num:02d}-{ex["id"]}.json',audit)
        audits.append({k:v for k,v in audit.items() if k not in ['commands','agent_messages']})
        if num==10 and final:
            try: save(ROOT/'evidence/literature-unaccepted-final.json',json.loads(final))
            except ValueError:pass
    save(ROOT/'evidence/log-inspection.json',audits)
    print(json.dumps([{'number':a['number'],'bytes':a['bytes'],'duplicates':len(a['duplicates']),'command_failures':len(a['command_failures']), 'terminal':[x['event']['type'] for x in a['terminal']]} for a in audits]))

if __name__=='__main__':main()

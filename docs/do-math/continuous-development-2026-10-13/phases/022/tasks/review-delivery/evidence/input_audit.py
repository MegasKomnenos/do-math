from work import *
import re
assignment = json.loads((RUN/'phases/022/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]
audit = []
for ref in assignment['inputs']:
    scope, name = ref.split(':',1)
    path = (RUN if scope=='run' else REPO)/name
    raw = path.read_bytes()
    text = raw.decode('utf-8-sig')
    value = json.loads(text) if path.suffix == '.json' else text
    audit.append({'reference':ref, **digest(path), 'type':type(value).__name__,
                  'lines':len(text.splitlines())})
save('input-audit.json',audit)
packet = json.loads((RUN/'phases/001/tasks/document-closeout/evidence/followup-packets.json').read_text(encoding='utf-8-sig'))
save('p07-packet.json',[p for p in packet['packets'] if p['id'] in ('P07','N01','N02')])
binding = json.loads((RUN/'phases/001/tasks/document-closeout/evidence/binding-inventory.json').read_text(encoding='utf-8-sig'))
save('p07-bindings.json',[b for b in binding['bindings'] if any(o in json.dumps(b) for o in ('submission_check','repair'))])
prior = json.loads((RUN/'phases/001/tasks/closure-map/evidence/prior-review-state.json').read_text(encoding='utf-8-sig'))
save('pr24.json',[p for p in prior['review_units'] if 'PR24' in json.dumps(p)])
sections=[]
for filename, title, identifier in [('CLI-실행-계약.md','입력 크기 조정','N01-237'),
    ('CLI-실행-계약.md','제출, 보존과 편입','N01-260'),
    ('공통-실행.md','시작할 때 입력을 확인한다','N02-002'),
    ('공통-실행.md','최종 응답을 전달하고 필요한 오류를 수리한다','N02-014')]:
    path=REPO/'.claude/skills/do-math/references'/filename
    lines=path.read_text(encoding='utf-8').splitlines()
    start=next(i for i,line in enumerate(lines) if re.fullmatch(r'#{2,3} '+re.escape(title),line))
    level=len(lines[start])-len(lines[start].lstrip('#'))
    end=next((i for i in range(start+1,len(lines)) if re.match(r'^#{1,'+str(level)+r'} ',lines[i])),len(lines))
    body='\n'.join(lines[start:end])
    tokens=sorted(set(re.findall(r'(?<!`)`([^`\n]+)`(?!`)',body)))
    sections.append({'id':identifier,'path':path.relative_to(REPO).as_posix(),'title':title,
        'start_line':start+1,'end_line':end,'body':body,'tokens':tokens})
save('current-sections.json',sections)
for s in sections:
    print(s['id'],s['title'],s['start_line'],s['end_line'])
    print(json.dumps(s['tokens'],ensure_ascii=False))

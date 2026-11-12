import json, sys, os, glob
K = sys.argv[1]
spec = json.loads(sys.argv[2])
for pre, ids in spec.items():
    ds = [d for d in os.listdir(os.path.join(K,'records')) if d.startswith(pre)]
    for d in ds:
        base = os.path.join(K,'records',d)
        r = json.load(open(os.path.join(base,'record.json'),encoding='utf-8'))
        try:
            a = json.load(open(os.path.join(base,'review','assessment.json'),encoding='utf-8'))
        except Exception as e:
            a = {'claims':[]}
        st = {x['claim']:(x['status'],x.get('reason','')) for x in a.get('claims',[])}
        allids = [c['id'] for c in r['claims']]
        print('=====', d, '| title:', r.get('title','')[:120])
        print('  ALL IDS:', allids)
        print('  relations:', [(x['id'], x.get('claim')) for x in r.get('relations',[])])
        print('  solutions:', [(x.get('node'), x.get('claim')) for x in r.get('solutions',[])])
        for c in r['claims']:
            if c['id'] in ids:
                s = st.get(c['id'],('?',''))
                print('  ---', c['id'], '| review:', s[0])
                print('     STMT:', c['statement'][:int(sys.argv[3]) if len(sys.argv)>3 else 700].replace('\n',' '))
                print('     REV:', s[1][:300].replace('\n',' '))
        for i in ids:
            if i not in allids: print('  !!! MISSING', i)

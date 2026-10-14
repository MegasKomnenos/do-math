from work import *
sys.path.insert(0,str(REPO/'.claude/skills/do-math/scripts'))
from do_math.file_io import read_bytes_shared
from collections import Counter
for path in sorted((E/sys.argv[1]).rglob('result.json')):
    try:data=json.loads(read_bytes_shared(path))
    except (OSError,ValueError):continue
    print(path.relative_to(E), data.get('complete'), Counter(r.get('outcome') for r in data.get('rows',[])))

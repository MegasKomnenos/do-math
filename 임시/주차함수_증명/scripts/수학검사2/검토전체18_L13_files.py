# check existence of 세션_재계산 paths mentioned in appendix D chapters 7A/7B/8/9/10
import re, os, glob
root = r"C:\math\임시\주차함수_증명"
files = ["장v2/부록D_장7A.md","장v2/부록D_장7B.md","장v2/부록D_장8.md","장v2/부록D_장9.md","장v2/부록D_장10.md"]
for f in files:
    txt = open(os.path.join(root,f),encoding="utf-8").read()
    # split by item header
    items = re.split(r"\n### ", txt)
    for it in items:
        head = it.split("\n",1)[0][:60]
        m = re.search(r"\*\*자료\.\*\*(.*?)\n", it, re.S)
        if not m: continue
        mat = m.group(1)
        paths = re.findall(r"`([^`]+)`", mat)
        # find folders 원고_자료/세션_재계산/<name>/
        folders = re.findall(r"원고_자료/세션_재계산/([^/`]+)/", mat)
        missing = []
        for p in paths:
            if p.startswith("원고_자료/"):
                full = os.path.join(root, p.replace("/",os.sep))
                if not os.path.exists(full) and not glob.glob(full):
                    missing.append(p)
        # bare filenames: check within listed folders
        bare = [p for p in paths if "/" not in p and not p.startswith("python") and not p.startswith("--") and re.search(r"\.(py|txt|json|jsonl|log|npy|out|md|c|sh|tsv|bat|gz|diff)$", p)]
        found_bare = {}
        for b in bare:
            ok = False
            for fo in set(folders):
                if glob.glob(os.path.join(root,"원고_자료","세션_재계산",fo,"**",b.replace("*","*")), recursive=True):
                    ok = True; break
            if not ok:
                # maybe in record folder copies
                if glob.glob(os.path.join(root,"원고_자료","r*",b), recursive=False) or glob.glob(os.path.join(root,"원고_자료","r*","**",b), recursive=True):
                    ok = True
            found_bare[b]=ok
        nb = [b for b,ok in found_bare.items() if not ok]
        print("==", f, head)
        print("   folders:", sorted(set(folders)), " missing full paths:", missing)
        print("   bare names not found anywhere under 원고_자료:", nb)

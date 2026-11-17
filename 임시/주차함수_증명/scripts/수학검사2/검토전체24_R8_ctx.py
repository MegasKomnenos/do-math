# R8 (review 24): print contexts of a fixed string in a file (no regex).
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
path, needle = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 70
for no, line in enumerate(open(path, encoding="utf-8"), 1):
    i = line.find(needle)
    while i >= 0:
        print(no, "…" + line[max(0, i - w): i + len(needle) + w].replace("\n", " ") + "…")
        i = line.find(needle, i + len(needle))

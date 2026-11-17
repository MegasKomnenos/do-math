# -*- coding: utf-8 -*-
"""고아 기록 사본 폴더 23개를 원고_자료/ 에서 대조v2/보관_자료_1117/ 로 옮기고 README를 쓴다. 2026-11-17 13:4x 세션(V7 몫).

- 고아 판정의 근거: 현행 부록 D 「자료」 줄(자료묶음_v2.py --dry: 항목 320·복사 614)과 V7a가 그에 맞춰 다시 쓴
  원고_자료/README.md 「파일 목록」(614행)이 가리키는 기록 폴더는 18개이고, 디스크의 기록 폴더는 41개다. 나머지 23개는
  어느 항목도 가리키지 않는다(V7a 인계 세션 절 4항; 세션이 경로 꼴 참조를 장v2·README·scripts에서 다시 검색해 0 확인).
- 옛 항목과의 대응은 커밋 fbf8a575의 README 「파일 목록」(1,265행; 열 「부록 D 항목」)에서 뽑는다.
- 지우지 않고 옮긴다(결정 130 선례, 보관_재계산_옛판_1117의 V7a 선례). git 추적 밖.
"""
import io, os, re, shutil, subprocess, sys

ROOT = r"C:\math\임시\주차함수_증명"
SRC = os.path.join(ROOT, "원고_자료")
DST = os.path.join(ROOT, "대조v2", "보관_자료_1117")
ORPHANS = """r051bfe1 r059f11e r0dc57fa r207f124 r29c10cd r2ec875c r33475a7 r5909c9e r5bbc534 r656206c r690be93 r708d99c
r7798355 r845b205 r88bed8a r89eb039 r9e782f5 rad00a59 rae1f209 rb6a2cd0 rbeae3a3 re79cb4d rf451d83""".split()
assert len(ORPHANS) == 23 and len(set(ORPHANS)) == 23

# 1. 현행 README 「파일 목록」이 가리키는 폴더 = 남는 폴더. 고아와 겹치면 중단.
readme_now = io.open(os.path.join(SRC, "README.md"), encoding="utf-8").read()
keep = set(re.findall(r"`(r[0-9a-f]{7})/", readme_now))
assert not (keep & set(ORPHANS)), keep & set(ORPHANS)
on_disk = sorted(n for n in os.listdir(SRC) if re.fullmatch(r"r[0-9a-f]{7}", n) and os.path.isdir(os.path.join(SRC, n)))
assert set(on_disk) == keep | set(ORPHANS), (set(on_disk) - keep - set(ORPHANS), keep - set(on_disk))
print("남는 폴더", len(keep), "고아", len(ORPHANS), "디스크", len(on_disk))

# 2. 옛 README(fbf8a575)에서 폴더별 옛 항목을 뽑는다.
old = subprocess.run(["git", "show", "fbf8a575:임시/주차함수_증명/원고_자료/README.md"], cwd=r"C:\math",
                     capture_output=True).stdout.decode("utf-8")
items = {}
for line in old.splitlines():
    m = re.match(r"\| `(r[0-9a-f]{7})/[^`]*` \| [^|]* \| ([^|]*) \|", line)
    if m:
        items.setdefault(m.group(1), set()).update(x.strip() for x in m.group(2).split("·") if x.strip())
print("옛 README에서 항목을 읽은 폴더", len(items))

# 3. 옮기기.
os.makedirs(DST, exist_ok=True)
rows = []
tot_f = tot_b = 0
for r in ORPHANS:
    s = os.path.join(SRC, r); d = os.path.join(DST, r)
    assert os.path.isdir(s) and not os.path.exists(d), (s, d)
    nf = nb = 0
    for dp, dn, fn in os.walk(s):
        for f in fn:
            nf += 1; nb += os.path.getsize(os.path.join(dp, f))
    shutil.move(s, d)
    tot_f += nf; tot_b += nb
    rows.append((r, nf, nb, "·".join(sorted(items.get(r, []))) or "(옛 README 파일 목록에 없던 폴더)"))
    print(r, nf, nb)
print("합", tot_f, tot_b)

# 4. README.
md = ["# 보관 — 고아가 된 기록 사본 폴더(2026-11-17, 세션 V7)", "",
      "9장 제거 물결(V1–V5)과 그 앞 물결들이 부록 D 항목을 지운 뒤, 현행 부록 D(항목 16)의 「자료」 줄과 `원고_자료/README.md` 「파일 목록」(614행)이 더 가리키지 않게 된 "
      "`원고_자료/<기록 식별자>/` 폴더 23개를 지우지 않고 여기로 옮긴 것이다(결정 130 (ㄴ)의 선례; `보관_재계산_옛판_1117/`과 같은 처리; 이 폴더는 git 추적 밖이다). "
      "옮긴 날짜·단위: 2026-11-17 13시대, 세션. 「옛 항목」은 커밋 `fbf8a575`의 README 「파일 목록」(1,265행)에서 그 폴더의 파일을 「자료」로 들던 부록 D 항목의 라벨이다(지금은 모두 지워진 라벨이거나, 남은 항목이 더는 그 파일을 들지 않는다). "
      "남은 기록 폴더 18개(`r030ffae`·`r10ff8c2`·`r13b0b8f`·`r15524fd`·`r15df76b`·`r19de912`·`r475ada3`·`r59c82d7`·`r6373c70`·`r6b37c7e`·`r81e7051`·`r8a9b11e`·`ra4c01fc`·`rb7effe0`·`rc9aee43`·`rce3dc75`·`re71a735`·`rfc69320`)는 그대로 `원고_자료/`에 있다. "
      "기록의 식별자 `[r…]`는 글(장·부록 B·C·장부)에 인용으로 남을 수 있다 — 그것은 연구 기록을 가리키는 것이고 이 사본 폴더를 가리키는 것이 아니다.", "",
      "| 폴더 | 파일 수 | 바이트 | 옛 항목(fbf8a575 README 기준) |", "|---|---|---|---|"]
for r, nf, nb, it in rows:
    md.append(f"| `{r}/` | {nf} | {nb:,} | {it} |")
md.append(f"| **합** | **{tot_f}** | **{tot_b:,}** | |")
md.append("")
io.open(os.path.join(DST, "README.md"), "w", encoding="utf-8", newline="\n").write("\n".join(md) + "\n")
print("README", os.path.getsize(os.path.join(DST, "README.md")))
left = sorted(n for n in os.listdir(SRC) if re.fullmatch(r"r[0-9a-f]{7}", n))
print("원고_자료에 남은 기록 폴더", len(left))

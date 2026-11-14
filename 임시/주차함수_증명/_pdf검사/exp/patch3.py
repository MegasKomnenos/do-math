"""md2pdf.py 수리 패치 3: 이항 기호 문턱 30%, 짧은 표는 쪽 안에, 머리행 뒤 끊김 금지, 디스플레이 정렬은 맞춤이 끝난 뒤에."""
import ast, subprocess
p = r"C:\math\도구\md2pdf.py"
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)


rep(r"""    if (w > avail * 0.45) { splitAtPunct(kh); regroup(kh, S('rel', 'allow', 'bin', 'punct')); }""",
    r"""    if (w > avail * 0.3) { splitAtPunct(kh); regroup(kh, S('rel', 'allow', 'bin', 'punct')); }""")
rep(r"""  //    \allowbreak(목록 쉼표, 긴 숫자열) 뒤를, 행 폭의 45%를 넘으면 이항 기호·쉼표 뒤도 연다. 한 묶음이 행 폭을 넘으면 어디서나 끊는다.""",
    r"""  //    \allowbreak(목록 쉼표, 긴 숫자열) 뒤를, 행 폭의 30%를 넘으면 이항 기호·쉼표 뒤도 연다. 한 묶음이 행 폭을 넘으면 어디서나 끊는다.""")
# 디스플레이: 정렬(text-align-last: right)은 scrollWidth를 2px 늘려 맞춤 판정을 흐리므로 맞춤이 끝난 뒤에 건다
rep(r"""    relToNextLine(kh);
    // 여러 줄로 갈라진 식은 amsmath multline처럼 첫 줄을 왼쪽에, 마지막 줄을 오른쪽에 맞춘다(가운데 정렬된 조각이 떠 보이지 않게).
    kh.style.textAlign = 'left'; kh.style.textAlignLast = 'right';
    splitAtPunct(kh);""",
    r"""    relToNextLine(kh);
    splitAtPunct(kh);""")
rep(r"""    if (over()) regroup(kh, S('any'));
    if (over()) still.push('디스플레이 수식: ' + (k.textContent || '').replace(/\s+/g, ' ').slice(0, 80));
  }""",
    r"""    if (over()) regroup(kh, S('any'));
    if (over()) still.push('디스플레이 수식: ' + (k.textContent || '').replace(/\s+/g, ' ').slice(0, 80));
    // 여러 줄로 갈라진 식은 amsmath multline처럼 첫 줄을 왼쪽에, 마지막 줄을 오른쪽에 맞춘다(가운데 정렬된 조각이 떠 보이지 않게).
    // 오른쪽 맞춤은 scrollWidth를 한두 px 늘리므로 맞춤 판정이 끝난 뒤에 건다.
    const grps = kh.querySelectorAll(':scope > .vr-grp');
    if (grps.length > 1 && grps[0].getBoundingClientRect().top < grps[grps.length - 1].getBoundingClientRect().top) {
      kh.style.textAlign = 'left'; kh.style.textAlignLast = 'right';
    }
  }""")
# 표: 쪽 높이의 60% 이하인 표는 통째로 둔다
rep(r"""  const pageH = document.documentElement.clientHeight;   // 뷰포트 높이는 인쇄 쪽 높이와 다르므로 인쇄 본문 높이를 따로 받는다
  const limit = (window.__md2pdfContentHeight || pageH) * 0.25;""",
    r"""  const pageH = document.documentElement.clientHeight;   // 뷰포트 높이는 인쇄 쪽 높이와 다르므로 인쇄 본문 높이를 따로 받는다
  const contentH = window.__md2pdfContentHeight || pageH;
  const limit = contentH * 0.25;
  // 표: 쪽 높이의 60% 이하인 표는 통째로 둔다(머리행과 한두 행만 앞 쪽에 남고 나머지가 다음 쪽으로 가는 것을 막는다).
  // 그보다 긴 표는 쪽 사이에서 끊되 머리행이 쪽마다 반복되고(thead: table-header-group) 행 안에서는 끊지 않는다.
  for (const tb of document.querySelectorAll('table')) {
    if (tb.getBoundingClientRect().height <= contentH * 0.6) tb.style.breakInside = 'avoid';
  }""")
rep(r"""thead { display: table-header-group; }""",
    r"""thead { display: table-header-group; break-after: avoid; }   /* 머리행은 쪽마다 반복되고, 머리행만 앞 쪽에 남지 않는다 */""")

open(p, "w", encoding="utf-8", newline="\n").write(s)
ast.parse(s)
fit = s[s.index('FIT_JS = r"""') + len('FIT_JS = r"""'):]
fit = fit[:fit.index('"""')]
r = subprocess.run(["node", "-e", "new Function('return ('+process.argv[1]+')'); console.log('js ok')", fit], capture_output=True, text=True)
print(r.stdout.strip(), r.stderr[:300])
print("patched")

# -*- coding: utf-8 -*-
"""외부 피드백 넷째 묶음의 오류가 연구 기록 원문(exposition·review·코드)에 있는지 찾는다(읽기만)."""
import io
import os
import re

R = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"


def folder(short):
    for d in os.listdir(R):
        if d.startswith(short):
            return os.path.join(R, d)


def grep(short, pats, exts=(".md", ".txt"), maxhits=3, w=110):
    f = folder(short)
    hits = 0
    for root, _, files in os.walk(f):
        for fn in files:
            if not fn.endswith(exts):
                continue
            p = os.path.join(root, fn)
            try:
                s = io.open(p, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            for pat in pats:
                for m in re.finditer(pat, s):
                    if hits >= maxhits:
                        return
                    rel = os.path.relpath(p, f)
                    print(f"  [{short} {rel}] …{s[max(0, m.start()-w):m.end()+w]}…".replace("\n", " "))
                    hits += 1
    if hits == 0:
        print(f"  [{short}] 없음")


print("### 3.1 r13b0b8f: Z_1 / zC 3/4")
grep("r13b0b8f", [r"Z\^\{\(2\)\}_1", r"zC\s*\\preceq", r"\\frac\{?3\}?\{?4\}?\s*\(1-z\)\^\{-1/2\}", r"3/4\)\s*\(1-z\)"])
print("### 3.2 r6b37c7e: hat n < 1 가정 / M^{3/2} < K")
grep("r6b37c7e", [r"\\hat\{?\\mathfrak\s*n\}?_q\s*<\s*1", r"M\^\{3/2\}\s*<\s*K", r"<\s*1\b.{0,40}(분모|denominator)", r"(분모|denominator).{0,80}<\s*1\b"])
print("### 3.3 r8a9b11e: C_I 정의 적분 범위")
grep("r8a9b11e", [r"C_\{?\\mathrm\{?I\}?\}?\s*[:=].{0,120}\\int_0\^\{?\\infty", r"C_I\s*[:=].{0,80}int_0\^\{?\\infty", r"\\theta\s*\\in\s*\[0,\s*40\]"])
print("### 3.4b r8a9b11e: 7.7148 / 6.0961")
grep("r8a9b11e", [r"7\.7148", r"6\.0961[^0-9]", r"0\.1153[^0-9]"], maxhits=5)
print("### 3.4c r845b205: 14.652 / 50.600")
grep("r845b205", [r"14\.652", r"50\.600", r"35\.948"])
print("### 3.4d r7e03176: 0.395")
grep("r7e03176", [r"0\.395[^0-9]", r"8\.5714"])
print("### 3.4e re71a735: 0.708345 / 2.528570")
grep("re71a735", [r"0\.708345", r"2\.528570"])
print("### 3.4f r10ff8c2: 1.0091")
grep("r10ff8c2", [r"1\.0091", r"0\.0046"])
print("### 3.5a r5f5cf73: 무게 e^{-varrho^2/2}(1+eps)")
grep("r5f5cf73", [r"e\^\{-\\varrho\^2/2\}\s*\(1\s*\+\s*\\epsilon", r"(weight|무게).{0,150}e\^\{-\\varrho\^2/2\}"])
print("### 3.6a r5909c9e: vartheta in (0,1]")
grep("r5909c9e", [r"\\vartheta\s*\\in\s*\(0,\s*1\]", r"\\theta\s*\\in\s*\(0,\s*1\]", r"\(0,\s*1\]"])
print("### 3.6b r030ffae: 12926 / C^1")
grep("r030ffae", [r"12926", r"C\^1.{0,80}Hermite|Hermite.{0,80}C\^1"])
print("### 3.7 r2… 수준 위험률 쓰는 기록(r317d678·r3d0856b): conditional / 조건부")
for sid in ("r317d678", "r3d0856b", "r79ee9e0"):
    grep(sid, [r"조건부.{0,30}(질량|확률)", r"conditional.{0,40}(mass|probab)"], maxhits=2)

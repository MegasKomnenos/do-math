# -*- coding: utf-8 -*-
"""8장 집필 회수 뒤 장부·구조표·9장 파견문·작업 장부 반영(2026-11-12)."""
import io


def rw(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


root = "임시/주차함수_증명"

# 1. 장부 2.8에 8장 새 기호 표 옮김 + 1.2 행 보강
lines = rw(root + "/대조/장8_집필대조.md").split("\n")
rows = []
started = False
for ln in lines[97:]:
    if ln.startswith("## ") and started:
        break
    if ln.startswith("## 장부에 없는 새 기호"):
        started = True
        continue
    if started and ln.startswith("| ") and not ln.startswith("| 기호/용어") and not ln.startswith("|---"):
        rows.append(ln)
p = root + "/장부_기호용어이름.md"
s = rw(p)
anchor = "### 2.9 9장 보증"
assert s.count(anchor) == 1
block = "\n".join([
    r"**8장 집필에서 추가된 기호(집필 대조 파일 「장부에 없는 새 기호·용어」 표를 옮김; 2026-11-12).** 열은 기호 / 뜻 / 정의 절 / 충돌 검사. 2.11이 세운 $P^y$, $p^y(a\to c)$, $\tau_\delta(c)$를 8.5·8.6이 그대로 쓴다.",
    "",
    "| 기호/용어 | 뜻 | 정의한 절 | 충돌 검사 |", "|---|---|---|---|"] + rows + ["", anchor])
s = s.replace(anchor, block, 1)
old = r"| 상수 $4/(3\sqrt{2\pi})=0.53192$ | — | $I_1$ ([re71a735]) | $\mathsf c_1$ | 4.3의 $I$·$\mathcal I_k$(Gauss형 계수)와 충돌 회피 |"
assert s.count(old) == 1, s.count(old)
new = old + "\n" + "\n".join([
    r"| 창 안 결손의 척도 좌표 $\delta/y^{2/3}$ | — | $x$ ([re71a735] §4) | $\chi$ | 3.4의 임계 창 $x$, 7.4의 $\xi$, 8.1의 $\zeta=\nu/k^{2/3}$와 구별(8장 집필 제안) |",
    r"| 기록의 $\theta$ 몫 | — | $\Theta(k,\nu)$ ([r3d0856b]) | $\mathsf T_\vartheta(k,\nu)$ | 문턱 손실 $\Theta_n$(6.8)과 글자 충돌 회피(8장 집필 제안) |",
    r"| 명제 T의 두 계수 | — | $\tau_h$, $\lambda$ ([r3d0856b] §3) | $\mathsf q_h$, $\mathsf p_{\mathrm{two}}$ | $\tau$(Borel 질량·2.11 기울임), $\lambda$(3.4)와 충돌 회피(8장 집필 제안) |",
])
s = s.replace(old, new)
old = r"| $u(j)=j\mathrm{Bor}(j)$ 갱신 다리 핵, $\mathcal I_1$, $\mathfrak Q(y,x)$, $\mathcal U(k;\bar\nu)$, $\Lambda_F(k)\to\mathcal L_F(k)$ | 8.6 |"
assert s.count(old) == 1, s.count(old)
s = s.replace(old, r"| $u(j)=j\mathrm{Bor}(j)$ 갱신 다리 핵, $\mathsf c_1$(기록 $I_1$), $\mathfrak Q(y,\chi)$, $\mathcal U(k;\bar\nu)$, $\Lambda_F(k)\to\mathcal L_F(k)$ | 8.6 |")
wr(p, s)
print("patched 장부 2.8 (+%d rows), 1.2 (+3), 8.6 행" % len(rows))

# 2. 9장 파견문 9.2 중복 집계 금지
p = root + "/파견/장9_부록_파견문.md"
s = rw(p)
old = "각 항목의 층은 의존지도 2·3절의 지위 열과 해당 장의 지위 표지에서 가져오고, 둘이 다르면 기록을 열어 확인한다."
assert s.count(old) == 1, s.count(old)
s = s.replace(old, old + " 8장이 정리 6.18의 증명 셋째 걸음(네 적분 위합 $50.62$, 배정밀도)을 되가리키는 자리는 정리 6.18의 행에 한 번만 집계한다(같은 계산을 두 행으로 세지 않는다). 7.5·8.7의 입력 표(각 장 끝)와 9.2의 표가 맞는지 대조한다.")
wr(p, s)
print("patched 9장 파견문 9.2")

# 3. 구조표 8.1의 「세 장부의 사전」이 있으면 생략 사유 부기
p = root + "/구조표.md"
s = rw(p)
if "세 장부의 사전" in s:
    s = s.replace("세 장부의 사전", "세 장부의 사전(기록 [r22df70]의 여섯 조각과의 대응은 파견 범위 밖이라 8.1은 세 단위의 뜻만 적음; 증명 사슬에 불필요하므로 생략)", 1)
    wr(p, s)
    print("patched 구조표 사전")
else:
    print("구조표에 「세 장부의 사전」 없음(8장 파견문 쪽 표현으로 보임; 생략 사유는 장부와 작업 장부에 적음)")

# 4. 작업 장부 사건 줄
p = root + "/작업_장부.md"
s = rw(p)
key = "- 2026-11-12 세션 판정 둘."
i = s.index(key)
j = s.index("\n", i)
add = "\n".join([
    r"- 2026-11-12 8장 집필 회수(완료; 38 진술; `장/장8.md` 165.0KB, `대조/장8_집필대조.md`). 중대 사항 없음(미지지·철회·지위 하향 없음). 8.7 셋째 고리에서 등록 함의의 전제 V* 대 이 글의 명제 6.19가 쓰는 (V)의 차이를 본문에 밝힘; 8.3·8.4·8.8 수치는 「배정밀도 관찰」로만. [re71a735]의 정리 A·B·C·S′·P, 명제 D·X, 보조정리 SS·F는 해설이 요지만 적어 같은 기록의 `evidence/producer/report.md` §3으로 완전 전개(2차 대조에 전수 확인 지시); 보조정리 1·3(iv)·명제 S의 일부 계산은 집필자 직접 전개(「작성자 판단」 표시 여부를 2차 대조가 판정). 새 라벨 다섯(Qstar2, cor-E, bulk-point-mass, sojourn-law, lemma-N); 따름정리 E·벌크 점질량 상계는 다른 장에 없음(grep). 새 기호 표를 장부 2.8로 옮기고 1.2에 세 행($\chi$, $\mathsf T_\vartheta$, $\mathsf q_h$·$\mathsf p_{\mathrm{two}}$) 추가. 「세 장부의 사전」([r22df70] 대응)은 범위 밖·증명 불필요로 생략. 9.2의 6.18 중복 집계 금지를 9장 파견문에 추가. 임시 조립: 1–8장 라벨 224개 전부 해소, 불변식은 부록 B 부재 한 건만 실패.",
    r"- 2026-11-12 8장 2차 대조 파견(`gp-fable-high`; 추가 확인 여덟: producer report 전개의 전수 대조와 assessment 지지 확인, 집필자 직접 전개의 옳음과 작성자 판단 표시, 8.7 고리(V*/(V))와 6.10 목록 일치, 배정밀도 관찰과 표지 문법·층, 새 라벨 중복, 타 장 라벨 실재, 금지어·검토·뿌리·걸음, 어긋남과 정정 넷). 산출 `대조/장8_2차대조.md`.",
])
s = s[:j + 1] + add + "\n" + s[j + 1:]
wr(p, s)
print("ledger appended")

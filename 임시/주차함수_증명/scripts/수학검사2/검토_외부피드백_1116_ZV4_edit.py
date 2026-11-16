# -*- coding: utf-8 -*-
"""ZV4 편집기. 외부 피드백 15.1(부록 D xcert-partAB 범위 3의 「단봉」→골짜기 모양)과
15.2(9장의 반올림 소수 등호 → 증명 방향의 부등식; 부록 D band-LP 「확인하는 진술」의 같은 꼴 셋)를 적용한다.
각 치환은 원문에 정확히 한 번 있어야 하며, 아니면 아무것도 쓰지 않고 멈춘다. python -I 로 실행."""
import io, os, sys
ROOT = r"C:\math\임시\주차함수_증명"
EDITS = {
    os.path.join(ROOT, "장v2", "부록D_장7A.md"): [
        # 15.1 — 범위 3 꼬리 수열의 모양
        (r"꼬리 수열의 단조성과 Abel 합: $n\le k-1$에서 $\mathrm{pr}^\circ_{n+1}/\mathrm{pr}^\circ_n=(1+1/(n-1))^{n-1}n/((n+1)e)$가 증가하므로 $n^j\varrho^{\mathrm{pr}}_n$은 $j\ge2$에서 $256<n\le k$에서 증가, $j\in\{0,1\}$에서 단봉이고, $|\sum_{n=257}^{k}n^j\varrho^{\mathrm{pr}}_ne^{\mathrm in\theta}|\le(\mathfrak y_{257}+2\mathfrak y_k)/\sin(\theta/2)$($j=0,1$), $\le2\mathfrak y_k/\sin(\theta/2)$($j\ge2$), $\mathfrak y_n:=n^j\varrho^{\mathrm{pr}}_n$, 원자 $n\le256$은",
         r"꼬리 수열의 모양과 Abel 합: $\mathfrak y_n:=n^j\varrho^{\mathrm{pr}}_n$의 이웃비는 $256<n\le k-1$에서 $\mathfrak y_{n+1}/\mathfrak y_n=(1+1/n)^{j-1}(1+1/(n-1))^{n-1}e^{\gamma_k-1}$이다. $j\ge2$에서는 $(1+1/n)(1+1/(n-1))^{n-1}>e$와 $\gamma_k>0$에서 이 비가 $1$보다 커 $\mathfrak y_n$이 $256<n\le k$에서 증가하고, $j\in\{0,1\}$에서는 이 비가 $n$에 증가하므로 $\mathfrak y_n$은 감소하다가 증가하는 골짜기 모양(한쪽 구간이 비는 단조도 포함)이라 전변동 $\sum_{n=257}^{k-1}|\mathfrak y_{n+1}-\mathfrak y_n|$이 $\mathfrak y_{257}+\mathfrak y_k$ 이하다. 따라서 Abel 합으로 $|\sum_{n=257}^{k}\mathfrak y_ne^{\mathrm in\theta}|\le(\mathfrak y_{257}+2\mathfrak y_k)/\sin(\theta/2)$($j=0,1$), $\le2\mathfrak y_k/\sin(\theta/2)$($j\ge2$)이고, 원자 $n\le256$은"),
    ],
    os.path.join(ROOT, "장v2", "장9.md"): [
        # 91행
        (r"대괄호가 $e^{-1/12}-e^{1/4}/4=0.5990$ 이상이고, $(2/\pi)^{1/2}\cdot0.5990=0.4779$이기 때문이다.",
         r"대괄호가 $e^{-1/12}-e^{1/4}/4$ 이상, 곧 $0.599$보다 크고, $(2/\pi)^{1/2}\cdot0.599>0.477$이기 때문이다."),
        # 193행
        (r"\Psi(d)\ge(2\pi)^{-1/2}\Bigl[2\sqrt{d+1}-2-\frac{\mathsf z_{3/2}}{12}\Bigr]=0.797885\sqrt{d+1}-0.884733\ge0.7978\sqrt d-0.8848",
         r"\Psi(d)\ge(2\pi)^{-1/2}\Bigl[2\sqrt{d+1}-2-\frac{\mathsf z_{3/2}}{12}\Bigr]\ge0.7978\sqrt{d+1}-0.8848\ge0.7978\sqrt d-0.8848"),
        # 201행
        (r"$\upsilon_1:=3132^{-1/3}=0.068348$로 둔다.",
         r"$\upsilon_1:=3132^{-1/3}$($<0.06835$)로 둔다."),
        # 237행
        (r"$0.8848\upsilon\le0.8848\sqrt{\xi/2}=0.6257\sqrt\xi$이고",
         r"$0.8848\upsilon\le0.8848\sqrt{\xi/2}<0.6257\sqrt\xi$이고"),
        # 241행(4단계) — 세 인자의 곱 1.0004·1.0035·1.0001은 1.0040을 넘는다
        (r"$\Phi\le1.0040\,\xi^{5/2}\bigl[",
         r"$\Phi\le1.0041\,\xi^{5/2}\bigl["),
        # 243행(5단계)
        (r"$0.7978\sqrt\xi\ge0.1381>0.0605=0.8848\upsilon_1$이므로",
         r"$0.7978\sqrt\xi\ge0.1381>0.0605>0.8848\upsilon_1$이므로"),
        # 245행(5단계) 문턱
        (r"\bigl((p-\frac12)\,0.7978\bigr)=p\cdot1.109\,\upsilon_1/(p-\frac12)$에서 증가한다. $\Phi$의 대괄호에서 나오는 $p=7/2,\,5/2,\,3$과 $\mathcal E$에서 나오는 $p=3/2,\,2,\,1$에서 문턱은 모두 $\xi\le0.0231$이다.",
         r"\bigl((p-\frac12)\,0.7978\bigr)$에서 증가한다. $0.8848/0.7978<1.11$이므로 $\sqrt\xi\ge1.11\,p\,\upsilon_1/(p-\frac12)$이면 충분하고, $\Phi$의 대괄호에서 나오는 $p=7/2,\,5/2,\,3$과 $\mathcal E$에서 나오는 $p=3/2,\,2,\,1$에서 이 문턱은 모두 $\xi\le0.0231$이다."),
        # 245행(5단계) 𝔠5
        (r"이것을 $[0.03,1]$에서의 최댓값, 곧 $\xi=0.03$의 값 $\mathfrak c_5:=5.68\times10^{-4}$로 바꾼",
         r"이것을 $[0.03,1]$에서의 최댓값인 $\xi=0.03$의 값보다 큰 상수 $\mathfrak c_5:=5.68\times10^{-4}$로 바꾼"),
        # 251행(6단계) 전체
        (r"**6단계(끝점).** $(\xi,\upsilon)=(1,\upsilon_1)$에서 $1+1/\ell_0=1.000319$, $q/\ell=0.068370$, $\mathfrak c_1=1.068370^{3/2}\cdot e^{1/(12\cdot3131)}=1.10432$, $\mathfrak u_q\le0.002360$, $e^{\mathfrak u_q}\le1.00237$이고 대괄호는 $0.11399+0.15958\upsilon_1^2+0.85108\upsilon_1=0.17291$이므로 $\Phi=0.19145$다. $\bar{\mathcal E}$의 분모는 $0.7978-0.060475=0.737325$, 분자의 대괄호는 $0.5320\upsilon_1+\mathfrak c_1(0.625+\upsilon_1^2)=0.036361+0.695358=0.731719$이므로 $\bar{\mathcal E}=1.104671\cdot(0.992397+0.000568)=1.09689$이고, $\bar{\mathcal L}=0.737325\cdot e^{-1.09689}/1.068689=0.23037$이다. 그러므로 $\bar R(1)=0.19145/0.23037=0.83106<1$이다.",
         r"**6단계(끝점).** $(\xi,\upsilon)=(1,\upsilon_1)$에서 $1+1/\ell_0<1.00032$, $\upsilon_1<0.06835$, $q/\ell=\upsilon_1(1+1/\ell_0)<0.06838$, $\mathfrak c_1\le1.06838^{3/2}\cdot e^{1/(12\cdot3131)}<1.10434$, $\mathfrak u_q\le1.00032^2(0.06835+0.06835^3)^2/2<0.00237$, $e^{\mathfrak u_q}<1.00238$이고 대괄호는 $0.11399+0.15958\upsilon_1^2+0.85108\upsilon_1<0.17292$이므로 $\Phi<1.00032\cdot1.10434\cdot1.00238\cdot0.17292<0.19148$이다. $\bar{\mathcal E}$의 분모는 $0.7978-0.8848\upsilon_1>0.7978-0.8848\cdot0.06835>0.73732$, 분자의 대괄호는 $0.5320\upsilon_1+\mathfrak c_1(0.625+\upsilon_1^2)<0.5320\cdot0.06835+1.10434\cdot(0.625+0.06835^2)<0.73174$이므로 $\bar{\mathcal E}<1.10434\cdot1.00032\cdot(0.73174/0.73732+0.000568)<1.0970$이고, $\bar{\mathcal L}$의 분모는 $1+(\upsilon_1+\upsilon_1^3)(1+1/\ell_0)<1.0687$이므로 $\bar{\mathcal L}>0.73732\cdot e^{-1.0970}/1.0687>0.2303$이다. 그러므로 $\bar R(1)<0.19148/0.2303<0.832<1$이다."),
        # 259행
        (r"$597^{3/2}+9\cdot597=19959.9\le20001<20005.5=598^{3/2}+9\cdot598$이므로",
         r"$597^{3/2}+9\cdot597<19960\le20001<20005<598^{3/2}+9\cdot598$이므로"),
        # 691행
        (r"$k\varrho^{\mathrm L}\le1.5\cdot0.112/1.112=0.152$,",
         r"$k\varrho^{\mathrm L}\le1.5\cdot0.112/1.112<0.152$,"),
        # 693행 — 부록 D.band-LP의 인증값 741.7817309, 2.0938508
        (r"$k=6668$에서 $k\mu/(1-\mu)=741.8\le0.1113k$이므로",
         r"$k=6668$에서 $k\mu/(1-\mu)<741.8\le0.1113k$이므로"),
        (r"$k=6668$에서 이 감소하는 양의 값이 $2.094$이므로",
         r"$k=6668$에서 이 감소하는 양의 값이 $2.094$ 이하이므로"),
        # 695행 — 인증값 0.0027348096
        (r"$\hat\Upsilon_k$가 감소) $k=6668$에서 $0.00273$이다.",
         r"$\hat\Upsilon_k$가 감소) $k=6668$에서 $0.00273$보다 크다."),
        # 834행
        (r"$e^{-1/(12\cdot366)}=0.999772\ge1-2.3\times10^{-4}$이며",
         r"$e^{-1/(12\cdot366)}\ge1-1/(12\cdot366)\ge1-2.3\times10^{-4}$이며"),
        # 857행
        (r"상수 $1.678$과의 차 $0.00006$은 $0.3989<(2\pi)^{-1/2}=0.398942$에서 생기는 여유 $0.000084\sqrt d-0.000095$로 $d\ge2$에서 메워지고, $d=1$은 $\Psi(1)=e^{-1}=0.3679>0.3989\cdot0.322$로 따로 성립한다.",
         r"상수 $1.678$과의 차 $0.00006$은 $0.3989<0.39894<(2\pi)^{-1/2}$에서 생기는 여유($0.000084\sqrt d-0.000095$ 이상)로 $d\ge2$에서 메워지고, $d=1$은 $\Psi(1)=e^{-1}>0.3989\cdot0.322$로 따로 성립한다."),
    ],
    os.path.join(ROOT, "장v2", "부록D_장9.md"): [
        # D.band-LP 「확인하는 진술」 (가) — 결과 줄의 인증값에 맞춘 부등식
        (r"$k=6668$에서 $k\mu(k)/(1-\mu(k))=741.8\le0.1113k$, $k^{1/3}\mu(k)/(1-\mu(k))=2.094$, $\mathcal Y_k(3k+1)=0.00273>0$.",
         r"$k=6668$에서 $k\mu(k)/(1-\mu(k))<741.8\le0.1113k$, $k^{1/3}\mu(k)/(1-\mu(k))\le2.094$, $\mathcal Y_k(3k+1)>0.00273>0$."),
    ],
}

def main():
    plan = []
    for path, pairs in EDITS.items():
        s = io.open(path, encoding="utf-8", newline="").read()
        for old, new in pairs:
            c = s.count(old)
            if c != 1:
                print(f"중단: {os.path.relpath(path, ROOT)} 에서 치환 원문이 {c}번 — {old[:60]}…")
                sys.exit(1)
        plan.append((path, s, pairs))
    for path, s, pairs in plan:
        for old, new in pairs:
            s = s.replace(old, new)
        io.open(path, "w", encoding="utf-8", newline="").write(s)
        print(f"고침: {os.path.relpath(path, ROOT)} — 치환 {len(pairs)}건")

if __name__ == "__main__":
    main()

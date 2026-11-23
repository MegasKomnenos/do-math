---
weight: unit
short: last-car recursion
---
## Description

The last-car recursion: the number $A(n+1,k)$ of parking functions of length $n+1$ with maximum displacement at most $k$ equals $\sum_{j=0}^{n}\min(j+1,k+1)\binom nj A(j,k)\,A(n-j,k)$.

## Statement

For all natural numbers $n$ and $k$,
$$A(n+1,k)\;=\;\sum_{j=0}^{n}\min(j+1,\,k+1)\,\binom{n}{j}\,A(j,k)\,A(n-j,k).$$
Here $A(m,k)$ (`Parking.A`) is the number of parking functions of length $m$ whose maximum displacement is at most $k$; in particular $A(0,k)=1$ (`Parking.A_zero`).

## Explanation

**What the terms count.** Just before the last of the $n+1$ cars arrives, the first $n$ cars occupy $n$ of the $n+1$ spots, so exactly one spot is free. Number the spots $0,\dots,n$ and let $j$ be the free spot: there are $j$ spots to its left and $n-j$ to its right. No car has driven past the spot $j$, because a car that reaches a free spot takes it. Hence each of the first $n$ cars parked on the side of $j$ on which its preference lies. The cars that parked on the left form, in their order of arrival, a parking function of length $j$ on the street $0,\dots,j-1$, and the cars that parked on the right form one of length $n-j$ on the street $j+1,\dots,n$; a translation of a street does not change displacements. The $j$ cars that go to the left may be any $j$ of the $n$ cars, which gives the factor $\binom nj$. The last car has to end in the spot $j$ with displacement at most $k$, so its preference is one of the spots $j-\min(j,k),\dots,j$, which gives the factor $\min(j+1,k+1)$. Conversely every choice of $j$, of the $j$ cars, of the two parking functions and of the last preference is a parking function of length $n+1$ with maximum displacement at most $k$. With the spots numbered $1,\dots,n+1$, as in the statement of the main theorem, the free spot is $i=j+1$ and the factor is $\min(i,k+1)$.

**Its place in the whole proof.** This is where the combinatorics of the problem enters. Every later argument uses the parking process only through this recursion, the initial value `Parking.A_zero`, and the relations between $b$ and $A$ that follow from the definitions (`Parking.A_mono`, `Parking.b_zero`, `Parking.b_succ_add_A`). Divided by $n!$ the recursion becomes the weighted recursion `Parking.IsWSol` with the weight $\min(t,y)$, $y=k+1$ (`Parking.zr_isWSol`). When $k\ge n$ the factor is $j+1$ for every $j$, and the recursion is the one that the numbers $(n+1)^{n-1}$ satisfy (`Parking.cc_rec` after division by $n!$); this is how the library obtains $A(n,k)=(n+1)^{n-1}$ for $n\le k+1$ (`Parking.A_eq_pow`). The table of the columns $2\le k\le81$ (`Parking.Tab.small_table`) and the table of the rows $n\le16$ (`Parking.Tab.small_rows`) compute the numbers $A(n,k)$ by this recursion; the table of two signs computes the complements $(n+1)^{n-1}-A(n,y-1)$ by the forward form of the single-chain formula (`Parking.IsWSol.fwd`).

**How the proof is organised, and why.** The proof does not construct the bijection described above. The difficulty of making that description exact is that the cars of the two sides arrive interleaved in one sequence, so that "the cars on the left form a parking function" speaks of a subsequence that has to be extracted and renumbered. The proof avoids this by counting a more general object: for an arbitrary finite set $O$ of spots, the preference sequences whose cars occupy exactly $O$. For this count, removing the last car gives a recursion (Step 1 of the proof), and the two facts that the description uses, namely that a block of spots behaves like a street of its own and that two blocks separated by a free spot do not interact, become two statements about the count that are proved by induction on the number of cars from that recursion (Steps 2 and 3). The factor $\binom nj$ then arises from Pascal's rule: the last car of an interleaved sequence belongs to the left block or to the right block.

**The Lean form.** The sum runs over `range (n + 1)`, the binomial coefficient is `n.choose j`, and `A (n - j) k` uses the subtraction of natural numbers, which is exact because $j\le n$. The Lean definitions number spots and preferences from $0$, as the proof below does.

## Proof

Throughout, $k$ is fixed. A street of length $N$ has the spots $0,1,\dots,N-1$, and a preference is a spot of the street. Cars arrive one after another; a car with preference $a$ takes the first free spot $s\ge a$ if there is one, and its displacement is then $s-a$ (`Parking.firstFree`, `Parking.parkFrom`, `Parking.dispList`). A sequence of preferences *parks* if every car finds a spot.

**The process.** Three elementary facts about the process are used.

- (P1) When exactly the spots of a set $U$ are occupied, a car with preference $a$ takes the spot $s$ if and only if $a\le s<N$, $s\notin U$, and every spot $i$ with $a\le i<s$ belongs to $U$.
- (P2) The spots taken by the cars of a sequence that parks are pairwise distinct spots of the street, and there are as many of them as there are cars.
- (P3) A sequence $(a_1,\dots,a_m,a)$ parks if and only if $(a_1,\dots,a_m)$ parks and a car with preference $a$ finds a spot when the spots taken by those $m$ cars are occupied. The first $m$ cars take the same spots in both sequences, so the displacements of $(a_1,\dots,a_m,a)$ are those of $(a_1,\dots,a_m)$ followed by the displacement of the last car.

(P1) is the definition of the first free spot. (P2) and (P3) are proved by induction on the length of the sequence. The definition of the process is a recursion on the first car, which parks and thereby changes the set of occupied spots for the cars after it; so the induction is carried out for a street on which an arbitrary set of spots is occupied at the start, where (P2) says in addition that the spots taken were free at the start, and the statements above are the case of an empty street. (P3) transfers the recursion from the first car to the last.

**The count by occupied spots.** For a finite set $O$ of natural numbers let $\mathcal G_N(O)$ be the set of preference sequences of length $|O|$ on the street of length $N$ that park, whose cars take exactly the spots of $O$, and all of whose displacements are at most $k$; let $g_N(O)=|\mathcal G_N(O)|$. For $s\in O$ let $L_N(O,s)$ be the set of preferences $a$ with which a car arriving when exactly the spots of $O\setminus\{s\}$ are occupied takes the spot $s$ with displacement at most $k$. By (P1),
$$a\in L_N(O,s)\iff s<N,\quad a\le s,\quad s-a\le k,\quad\text{and every spot } i \text{ with } a\le i<s \text{ belongs to } O. \tag{$*$}$$

**Step 1: removing the last car.** We have $g_N(\emptyset)=1$, since the empty sequence is the only sequence of length $0$. For nonempty $O$,
$$g_N(O)=\sum_{s\in O} g_N(O\setminus\{s\})\cdot|L_N(O,s)|. \tag{1}$$
Indeed, a sequence of length $|O|$ is uniquely of the form $(a_1,\dots,a_m,a)$ with $m=|O|-1$. By (P3) it belongs to $\mathcal G_N(O)$ if and only if $(a_1,\dots,a_m)$ parks with all displacements at most $k$, the last car takes some spot $s$ with displacement at most $k$, and the spots taken by the first $m$ cars together with $s$ are the set $O$. Since $s$ was free when the last car arrived, the last condition says that $s\in O$ and that the first $m$ cars take exactly the spots of $O\setminus\{s\}$. Hence $(a_1,\dots,a_m,a)\in\mathcal G_N(O)$ if and only if there is $s\in O$ with $(a_1,\dots,a_m)\in\mathcal G_N(O\setminus\{s\})$ and $a\in L_N(O,s)$. The spot $s$ is determined by $(a_1,\dots,a_m)$, being the one spot of $O$ that these cars do not take, so the sets of sequences belonging to different $s$ are disjoint; and for a fixed $s$ the sequence determines the pair $((a_1,\dots,a_m),a)$. Counting gives (1).

**Step 2: a block of spots is a street of its own.** Let $O$ be a finite set of spots of the street of length $N$, and let $c$ and $N'$ be such that $O+c=\{x+c: x\in O\}$ consists of spots of the street of length $N'$. Then
$$g_{N'}(O+c)=g_N(O). \tag{2}$$
The proof is by induction on $|O|$. For $O=\emptyset$ both sides are $1$. For the step, apply (1) to both sides; the sum on the left runs over the spots $s+c$, $s\in O$. Since $(O+c)\setminus\{s+c\}=(O\setminus\{s\})+c$, the induction hypothesis gives $g_{N'}((O+c)\setminus\{s+c\})=g_N(O\setminus\{s\})$, and it remains to see that $L_{N'}(O+c,s+c)=L_N(O,s)+c$. The conditions $s<N$ and $s+c<N'$ of $(*)$ hold by assumption. So by $(*)$, a preference $a'$ belongs to the left-hand side if and only if $a'\le s+c$, $s+c-a'\le k$, and every spot $i$ with $a'\le i<s+c$ belongs to $O+c$. Such an $a'$ satisfies $a'\ge c$: otherwise $a'<c\le s+c$, so the spot $i=a'$ would have to belong to $O+c$, all of whose elements are at least $c$. Writing $a'=a+c$, the conditions become the conditions $(*)$ for $a\in L_N(O,s)$. The two sets therefore have the same number of elements, and (2) follows.

**Step 3: two blocks separated by a free spot.** Let $O_1$ and $O_2$ be finite sets of spots and $h$ a spot such that every element of $O_1$ is smaller than $h$ and every element of $O_2$ is larger than $h$. Then
$$g_N(O_1\cup O_2)=\binom{|O_1|+|O_2|}{|O_1|}\,g_N(O_1)\,g_N(O_2). \tag{3}$$
The proof is by induction on $M=|O_1|+|O_2|$, and it rests on the following description of the last car. For $s\in O_1$ we have $L_N(O_1\cup O_2,s)=L_N(O_1,s)$, because the spots $i<s$ that $(*)$ speaks of are smaller than $h$, and such a spot belongs to $O_1\cup O_2$ exactly when it belongs to $O_1$. For $s\in O_2$ we have $L_N(O_1\cup O_2,s)=L_N(O_2,s)$: if $a\in L_N(O_1\cup O_2,s)$, then $a>h$, since otherwise $a\le h<s$ and by $(*)$ the spot $h$ would belong to $O_1\cup O_2$, which it does not; so all spots $i$ with $a\le i<s$ are larger than $h$, and they belong to $O_1\cup O_2$ exactly when they belong to $O_2$. In words, a last car that ends on the right of the free spot $h$ must have preferred a spot on the right of $h$, because it cannot drive past a free spot.

For $M=0$ both sides of (3) are $1$. Let $M\ge1$, and write $m_1=|O_1|$, $m_2=|O_2|$. If $O_1$ is empty, (3) reads $g_N(O_2)=g_N(O_2)$, because $\binom{M}{0}=1$ and $g_N(\emptyset)=1$; likewise if $O_2$ is empty. Suppose that both are nonempty. The sets $O_1$ and $O_2$ are disjoint, so (1), applied to $O_1\cup O_2$, splits into a sum over $s\in O_1$ and a sum over $s\in O_2$. For $s\in O_1$ the set $(O_1\cup O_2)\setminus\{s\}$ is $(O_1\setminus\{s\})\cup O_2$, the two parts are again separated by $h$, and the induction hypothesis gives $g_N((O_1\setminus\{s\})\cup O_2)=\binom{M-1}{m_1-1}g_N(O_1\setminus\{s\})\,g_N(O_2)$. Likewise for $s\in O_2$, with $\binom{M-1}{m_1}g_N(O_1)\,g_N(O_2\setminus\{s\})$. With the description of the last car,
$$g_N(O_1\cup O_2)=\binom{M-1}{m_1-1}g_N(O_2)\sum_{s\in O_1}g_N(O_1\setminus\{s\})\,|L_N(O_1,s)|+\binom{M-1}{m_1}g_N(O_1)\sum_{s\in O_2}g_N(O_2\setminus\{s\})\,|L_N(O_2,s)|.$$
By (1), applied to $O_1$ and to $O_2$, the two sums are $g_N(O_1)$ and $g_N(O_2)$, and Pascal's rule $\binom{M-1}{m_1-1}+\binom{M-1}{m_1}=\binom{M}{m_1}$ gives (3).

**Step 4: $A(n,k)$ as such a count.** We have
$$A(n,k)=g_n(\{0,\dots,n-1\}). \tag{4}$$
By definition $A(n,k)$ is the number of functions $\alpha$ from $\{1,\dots,n\}$ to the spots $0,\dots,n-1$ that park and whose maximum displacement is at most $k$. Such functions correspond bijectively to their sequences of values, which are the preference sequences of length $n$ on the street of length $n$. The maximum displacement is the largest entry of the list of displacements (and $0$ for the empty list), so it is at most $k$ exactly when every displacement is. Finally, by (P2), $n$ cars that park on $n$ spots take all the spots, so the condition that the cars take exactly the spots $0,\dots,n-1$ holds by itself.

**Step 5: the last car on a full street.** For $j\le n$, the condition $(*)$ for the street of length $n+1$ and $O=\{0,\dots,n\}$ reduces to $a\le j$ and $j-a\le k$, because every spot belongs to $O$. Hence $L_{n+1}(\{0,\dots,n\},j)$ consists of the $\min(j+1,k+1)$ preferences $a$ with $\max(j-k,0)\le a\le j$.

**Conclusion.** By (4) and (1),
$$A(n+1,k)=g_{n+1}(\{0,\dots,n\})=\sum_{j=0}^{n}g_{n+1}(\{0,\dots,n\}\setminus\{j\})\cdot\min(j+1,k+1).$$
The set $\{0,\dots,n\}\setminus\{j\}$ is the union of $O_1=\{0,\dots,j-1\}$ and $O_2=\{0,\dots,n-j-1\}+(j+1)$, which are separated by the spot $j$ and have $j$ and $n-j$ elements. By (3),
$$g_{n+1}(\{0,\dots,n\}\setminus\{j\})=\binom nj\,g_{n+1}(O_1)\,g_{n+1}(O_2).$$
By (2), with $c=0$ and with $c=j+1$, and by (4), $g_{n+1}(O_1)=g_j(\{0,\dots,j-1\})=A(j,k)$ and $g_{n+1}(O_2)=g_{n-j}(\{0,\dots,n-j-1\})=A(n-j,k)$. Substituting gives the recursion.

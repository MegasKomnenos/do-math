# The history forest of the parking process

**Why Cayley's counts, the Borel laws and their companions recur in the study of the maximum displacement of parking functions, and what the structure behind them gives for the unimodality conjecture**

## 1. Purpose and reading guide

### 1.1 The question this document answers

A parking function of length $n$ is a list of preferences on which $n$ cars, arriving one after another at $n$ spots in a row and each taking the first free spot at or after its preferred one, all succeed in parking. The displacement of a car is the distance between its preferred spot and the spot it takes, and Celano, Elder, Hadaway, Harris, Martin, Priestley and Udell conjectured that, for every $n$, the numbers of parking functions of length $n$ whose largest displacement is exactly $\ell$ form a unimodal sequence in $\ell$ [CEHHMPU, Conjecture 6.5]. Section 3 states the conjecture exactly.

A research effort of about two weeks attacked this conjecture from many sides: through the permutation that records which car ends where, through labeled forests, through generating functions and their differential equations, through chains of large subtrees, through limit theorems, and through comparison inequalities. Whatever the side, the same classical objects kept turning up, often several at once: Cayley's formula for labeled trees and forests, the Borel distribution and its convolutions (the Borel–Tanner laws), the tree function with Lagrange inversion, uniform random forests with the deletion of edges and the additive coalescent, the ancestral line of a marked vertex with a birthday-type law for its length, probabilities of order $m^{-3/2}$, and a window of width $n^{2/3}$. The same quantities appeared under different names in different places, and it was not said anywhere why.

This document answers one question: why do these tools recur and overlap? The answer is a structure, in the plain sense of a mathematical object with a few theorems about it. The parking process, watched in time, is a process in which blocks of occupied spots merge. Its history is a forest. The recurring tools fall into three groups. Some are the standard descriptions of that forest. Some are the results of one of two elementary mechanisms applied to it. The others, the order-theoretic inequalities and the analytic estimates, are general techniques that do not come from the forest. Where they use anything from it, they attach to it through a specific property of Cayley's coefficients or of their generating functions (Sections 7.3, 7.5 and 8); two of them, the inequalities of Harris and of Jensen, use nothing from it. One further tool, a decomposition along the street, belongs to none of the three groups and is tied to the forest in Section 7.5. Two entries of the list of recurring concepts are not covered by this account: one functional of the cutting process was not examined, and the comparison models of the earlier research are not the object (Section 7.2). The overlaps between the tools that this document examines are identities between the descriptions and between the results of the two mechanisms; Section 6.5 lists them, each with the statement that proves it. Section 2 gives the account in one page; Sections 4 to 7 develop it with proofs; Section 9 says which part of it is whose theorem.

### 1.2 The question it does not answer

A second question is easily confused with the first: why is the sequence unimodal? The structure does not answer it. It turns the question into a comparison of two exactly defined quantities, one coming from pairs of vertices whose subtrees are at least as large as a threshold and one from the vertices whose subtrees sit exactly at the threshold, and it supplies exact tools for this comparison. With these tools Section 11 proves three statements that hold for all sizes: far to the left the sequence increases, far to the right it decreases, and in a wide region on the right a decrease, once it has occurred, continues. Between these regions one precisely stated target remains unproved; Section 11.6 states it in indices, with the status of a conjecture. Unimodality is not a formal consequence of the forest structure alone. Two neighbouring models have rows that are not unimodal: parking with spare spots, which the structure covers, and a forest with another offspring law, which shares with it the representation by a conditioned Galton–Watson forest with independent uniform marks (Counterexamples 7.4 and 7.5). A proof must therefore use a property of the uniform forest with one empty spot that these models lack.

### 1.3 What a reader can rely on

Every claim carries one of six statuses, written in brackets at its head.

- **proved**: every step is in the text or in a cited source with its theorem number. Where a proof uses a finite exact computation, the bracket says so and names the script.
- **proof sketch**: the argument is given with the missing steps named. No claim of the present version carries this status.
- **computational evidence**: verified by exact computation in a stated finite range, with the script named. In the few places where the computation is in floating point, the bracket says so.
- **counterexample**: an exact instance; the text says what it refutes and what it does not.
- **conjecture**: believed, with the grounds stated.
- **open**: a question, or a statement for which no grounds for believing it are offered; where the text says why the question is asked, this is not a claim about its answer.

Citations are to the bibliography at the end, with theorem or equation numbers taken from the sources themselves; the table of attributions that accompanies this document records, for each citation of a source that was read, what the source states and whether the wording here differs from it. Five entries of the bibliography were not read; they are cited as attributions only, the text says so at each place, and no statement labeled proved depends on them. Where a result is known the text says whose it is. Where a result was not found in the literature, Section 9.4 says so and says exactly where it was looked for: in the sources read, or in addition by a database search whose queries are recorded; nothing is claimed to be new on the strength of such a search. Computations were done in exact integer or rational arithmetic unless a place says otherwise; Appendix C lists the scripts.

The document is self-contained with respect to the earlier research. That research produced, besides the notes from which the material here was drawn, a long computer-assisted argument claiming the conjecture for all $n$. It is not used here; it has not been refereed (an unrefereed archive of it has been deposited, see Section 9.4, item 6), and wherever this document says that something is open it means open on the basis of what is proved in these pages and in the public literature.

### 1.4 How the document is arranged

Sections 4 to 7 are the structure: the object (Section 4), the class of observables to which the maximum displacement belongs (Section 5), the two mechanisms with the dictionary to the classical names (Section 6), and the statements that account for the recurrence of the tools (Section 7), including the tools that are not instances of the structure and the precise place where they attach to it. Section 8 treats the two exponents. Section 9 compares the structure with the known theories. Section 10 shows that it covers other statistics and other families. Section 11 is the part specific to the unimodality problem. Section 12 lists questions the structure raises, Section 13 is the table of all claims with their statuses, and Appendix A goes through the recurring concepts one by one. A reader who wants only the explanation can read Sections 2, 3, 4, 5, 6, 7 and 8, Section 10.3, Lemma 11.8, Lemma B.2 and Appendix A; the references from these sections to Propositions 11.3 and 11.6 can be taken on trust. A reader who wants to work on the conjecture needs Section 3; Sections 4.1 and 4.2 with Theorem 4.9; Section 5; Section 6, as a toolbox; Theorem 7.1 and Sections 7.3 and 7.4, with Section 10.3; Section 8; Section 9.4, item 6, which says what the literature contains on the conjecture; Section 11 with Appendix B; and Section 12.

## 2. The account in brief

Put the $n$ spots on a circle together with one extra spot, so that there are $N=n+1$ spots, and let each car choose its preferred spot uniformly at random. Every car then parks, one spot stays empty, and after the rotation that moves the empty spot to the last place the preferences have the law of a uniform random parking function (Section 4.1). At any moment the circle is divided into blocks, a block being a run of occupied spots together with the empty spot that ends it. An arriving car lands in a block with probability proportional to the size of the block, fills the empty spot at its end, and thereby merges the block with the next one; its displacement is uniformly distributed over the block it landed in. This is all that happens.

**The object.** Record the history of the merging as a forest on the cars: the subtree of a car is the block it closed. The central theorem (Theorem 4.6) says what this forest is. If one forgets in which order the cars arrived, that is, if one keeps the shape of the forest and attaches labels to it afresh at random, it is the uniform random rooted labeled forest on $n$ vertices, and the largest displacement is distributed as $\max_v \lfloor U_v t_v\rfloor$, where $t_v$ is the size of the subtree of $v$ and the $U_v$ are independent uniform variables. The same object has two further standard descriptions. As a branching process, the uniform forest is a critical Poisson Galton–Watson tree conditioned on its size, with the root removed (Theorem 4.8). As a process in time, the blocks present at any intermediate moment have the sizes of independent Borel variables conditioned on their sum, and these sizes evolve as the additive coalescent (Theorems 4.9 and 4.10); the description as a process keeps the order in which the blocks merge, which the uniform forest has forgotten. So there is one random object with three descriptions, which keep different parts of the information: a merging process in time, which keeps the order of arrival; a uniform combinatorial structure, which forgets that order and keeps the sizes of the blocks with the displacements as a multiset; and a conditioned branching process, which describes the same uniform structure.

**The observables.** The probability that all displacements stay below a threshold $k$ is the expectation of $\prod_v \min(1,k/t_v)$ over the forest. This is a product over the vertices of a function of the subtree size, and it equals $1$ on every vertex whose subtree has size at most $k$. The statistics of Sections 10.1 to 10.3 are of the same kind, with an additional factor for each tree in Section 10.3. Section 10.4 treats the displacement of one particular car, which is read from the description in time.

**The two mechanisms.** First, normalisation by size. Counting forests of a given size gives Cayley's numbers; letting the size be random with the natural weights gives the Borel law; the tree function is the generating function that passes between the two, Lagrange inversion is the computation that does it for several trees at once and produces the Borel–Tanner laws, and in every formula for a fixed size the Borel masses are Cayley's counts in which the powers of $e$ cancel (Lemma 6.1). Second, decomposition at vertices. Choose a forest together with vertices of prescribed subtree sizes, uniformly among all such choices, and cut the forest at these vertices: the pieces are again uniform and, once their sets of labels are given, independent, and the number of ways to reassemble them is a product with one factor for each piece (Theorem 6.2). Every piece contributes a Borel mass, and this mass is multiplied by the size of the piece once for each further piece that may be attached to it at an arbitrary vertex; the product of the size and the Borel mass is the renewal sequence of the walk with Borel steps (Section 6.2); the number of pieces along the ancestral line of a uniform vertex has the birthday law. Under the uniform law, removing the last car, removing a root, marking a vertex, cutting an edge and merging two blocks are readings of this one decomposition. When the forests carry a weight, these operations differ in what they preserve (Section 6.4).

**Why the tools recur.** The observable equals $1$ at every vertex whose subtree has at most $k$ vertices. A subtree with at most $k$ vertices that hangs in the forest is therefore an arbitrary rooted tree and carries no factor: such subtrees are counted by Cayley's numbers and, after normalisation, by Borel masses, and only the vertices above the threshold carry a factor. Theorem 7.1 makes this exact: the number of parking functions with all displacements below $k$ is a sum over the configurations of the vertices above the threshold, with one threshold factor for each such vertex and with coefficients built from Cayley's coefficients of the sizes up to $k$. This much is proved. It accounts for the recurrence in the following sense, which can be checked statement by statement. Each route by which the maximum displacement was computed, through outcome permutations, by removing the last car, along chains of large subtrees, through generating functions, is one of the statements of Sections 4, 6 and 11, and in each of these statements the numbers of the dictionary enter where trees without a factor are counted (Section 7.1 names the statement and the place for each route). One route, the decomposition of the street at its breakpoints, is of a different kind; Section 7.5 relates it to the forest. The order $m^{-3/2}$ of the Borel masses is Stirling's formula for Cayley's coefficients. The scale $n^{2/3}$ is connected with it as follows: blocks that lack at most $q$ of the $N$ spots occur about $\sqrt q$ times in the history, and a car closing such a block reaches the threshold $n-q$ with probability of order $q/n$, so the expected number of such cars is of order $q^{3/2}/n$. This computation proves one side of the scale, namely that the maximum rarely comes closer to $n$ than a small multiple of $n^{2/3}$ (Proposition 8.2); that $n^{2/3}$ is the exact scale, with a limit law, is a theorem of Petersson (Theorem 8.3).

**What lies outside.** The order-theoretic tools (the FKG inequality, total positivity, likelihood-ratio orders) are not instances of the structure. In this document they attach to it through two properties of Cayley's coefficients (the earlier research used a third as well, the total positivity of the array of the numbers of forests, which is a known theorem and is not used here; Section 7.3): the log-convexity of $j\mapsto j^{j-1}/j!$, on which the correlation inequalities rest (Section 7.3) and which is also what makes the most direct positivity arguments fail, and a convolution identity, on which a monotone coupling in the number of pieces rests (Lemma 11.8). The analytic tools attach through the singularities of the generating functions: the square-root singularity of the tree function, which gives the exponents, and, for a fixed threshold, the simple pole of the generating function that counts the parking functions below the threshold (Section 7.5).

## 3. The problem and the notation

### 3.1 The conjecture

Let $n\ge 1$. There are $n$ parking spots in a row, numbered $1,\dots,n$, and $n$ cars, numbered $1,\dots,n$, which arrive in the order of their numbers. A preference list is a sequence $\alpha=(\alpha_1,\dots,\alpha_n)$ of integers between $1$ and $n$. Car $i$ drives to spot $\alpha_i$; it parks there if the spot is free, and otherwise it parks in the first free spot to the right of $\alpha_i$; if there is none, it fails. A preference list on which every car parks is a *parking function* of length $n$, and $\mathrm{PF}_n$ denotes the set of parking functions of length $n$. If car $i$ parks in spot $s_i$, its *displacement* is $d_i=s_i-\alpha_i\ge 0$, and the *maximum displacement* of $\alpha$ is $M(\alpha)=\max_i d_i$. The displacements depend on the order of arrival: the lists $(1,1,2)$ and $(1,2,1)$ have the same entries and maximum displacements $1$ and $2$.

For integers $n\ge1$ and $\ell\ge0$ put
$$
A_{n,\ell}=\#\{\alpha\in\mathrm{PF}_n: M(\alpha)\le \ell\},\qquad b_{n,\ell}=\#\{\alpha\in\mathrm{PF}_n: M(\alpha)=\ell\},
$$
with the conventions $A_{n,-1}=0$ and $A_{0,\ell}=1$, so that $b_{n,\ell}=A_{n,\ell}-A_{n,\ell-1}$. The maximum displacement is at most $n-1$; hence $A_{n,\ell}=|\mathrm{PF}_n|$ for $\ell\ge n-1$ and $b_{n,\ell}=0$ for $\ell\ge n$. The sequence $b_{n,0},b_{n,1},\dots,b_{n,n-1}$ is called the *row* of $n$.

> **Conjecture P** [CEHHMPU, Conjecture 6.5]. For every integer $n\ge1$ there is an integer $c\in\{0,\dots,n-1\}$ such that $b_{n,k}\le b_{n,k+1}$ for $0\le k<c$ and $b_{n,k}\ge b_{n,k+1}$ for $c\le k<n-1$.

The peak need not be a single term, and $c$ may depend on $n$. The statement is about all $n$; a result for particular $n$ or for particular kinds of lists does not settle it. The rows for $n\le 6$ are

| $n$ | $b_{n,0},\dots,b_{n,n-1}$ | sum |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 2, 1 | 3 |
| 3 | 6, 7, 3 | 16 |
| 4 | 24, 51, 34, 16 | 125 |
| 5 | 120, 421, 377, 253, 125 | 1296 |
| 6 | 720, 3963, 4594, 3688, 2546, 1296 | 16807 |

(computed by running the parking process on all $n^n$ lists; Appendix C, item C1). The two ends of every row are $b_{n,0}=n!$, since $M=0$ exactly when the list is a permutation, and $b_{n,n-1}=n^{n-2}$ (Corollary 4.7), and the sum of the row is $|\mathrm{PF}_n|=(n+1)^{n-1}$ (Theorem 4.1).

### 3.2 Notation used throughout

| symbol | meaning |
|---|---|
| $n$, $N=n+1$ | the number of cars; the number of spots on the circle of Section 4.1 |
| $p_n=(n+1)^{n-1}$ | the number of parking functions of length $n$; $p_0=1$ |
| $k=\ell+1$ | the *threshold*: "all displacements are smaller than $k$" means $M\le k-1$ |
| $Z_n(k)=A_{n,k-1}$ | the number of parking functions of length $n$ with $M<k$, for integers $k\ge1$; Section 5.2 extends $Z_n(y)$ to real $y>0$; $Z_0=1$, and $Z_n(0)=0$ for $n\ge1$ |
| $d_{n,k}=b_{n,k}-b_{n,k-1}$ | the *step* at position $(n,k)$, $1\le k\le n-1$; $d_{n,k}=Z_n(k+1)-2Z_n(k)+Z_n(k-1)$ |
| $r=n-k$ | the distance of position $(n,k)$ from the right end of the row |
| $a_j=j^{j-1}/j!$ | Cayley's coefficient: the number of rooted labeled trees on $j$ vertices divided by $j!$ |
| $\mathrm{Bor}(j)=e^{-j}a_j$ | the mass of the Borel distribution with parameter $1$ at $j\ge1$ |
| $\mathrm{Ren}(j)=j\,\mathrm{Bor}(j)$ | $j^je^{-j}/j!$ for $j\ge 1$; $\mathrm{Ren}(0)=1$ |
| $T(z)=\sum_{j\ge1}a_jz^j$ | the tree function; $T=ze^{T}$ |
| $t_v$ | the size of the subtree of a vertex $v$ of a rooted forest: the number of vertices in $\{v\}$ together with all descendants of $v$ |
| $[x^m]f$ | the coefficient of $x^m$ in a power series $f$ |
| $(x)_j$ | the falling factorial $x(x-1)\cdots(x-j+1)$; $(x)_0=1$ |

Letters that are introduced inside a proof, a subsection or an appendix (for instance $C$, $P$ and $U$ in Appendix B.1) are local to it. Some letters are reused with a local meaning, which is defined at each place; the following list names the reuses a reader is most likely to stumble over and is not complete. The letter $r$ is also the number of sets in the corollary of Section 6.1, the ratio $r(t)$ of two weights in the paragraph after Theorem 6.7, and the number of empty spots in Counterexample 7.4 and in Sections 9.1 and 10.3, where the circle has $N=m+r$ spots. The letter $q$ has no fixed meaning: according to the place it is a number of trees, blocks, pieces or parts, a bound on the deficit $n-M$ (Sections 2 and 8), the variable of a $q$-analogue (Sections 6.3 and 10.1), or an index. The letter $k$ is a number of trees in the formulas quoted from the literature in Section 9.2. In Proposition 7.3 and in the sentence on kernels that follows it, $(a_j)$ is an arbitrary positive sequence. The letter $X$ is the limit variable of Theorem 8.3, and $X_q$ in Lemma 11.8 is a random composition. The word *layer* denotes a piece of an occurrence of a pattern in Section 6.2 and, in the expression *first layer*, a set of positions (Section 11.4).

A *rooted labeled forest on $[n]$* is a graph on the vertex set $[n]=\{1,\dots,n\}$ each of whose components is a tree with a distinguished root; the children of a vertex are not ordered. There are $(n+1)^{n-1}$ of them, and $j^{j-1}$ rooted labeled trees on $j$ vertices (Cayley's formula; [FS, Section II.5.1, (46)–(47)]). It is often convenient to join all roots of a forest on $[n]$ to an additional vertex $0$, the *virtual root*; this turns the forest into a rooted tree on $\{0,1,\dots,n\}$ with root $0$, and every such tree arises once.

In terms of the steps, a row is unimodal exactly when it contains no decrease followed later by an increase:

$$
\text{row } n \text{ is unimodal}\iff \text{there are no } 1\le i<j\le n-1 \text{ with } d_{n,i}<0<d_{n,j}. \tag{3.1}
$$

## 4. The object: one random forest with three descriptions

This section constructs the object on which everything else rests. It starts from the parking process itself and reads it in time (4.1), records the history of the process as a forest and identifies the law of that forest (4.2), and then gives the two further descriptions of the same law, as a conditioned branching process (4.3) and as the state of a coalescent at intermediate times (4.4). The statements are classical or elementary; what matters here is that they are statements about one object. Section 9 says which statement is whose.

### 4.1 The parking process on a circle

Place $N=n+1$ spots on a circle, numbered $1,\dots,N$ clockwise, with spot $1$ following spot $N$. A preference list is now an element $\alpha$ of $\{1,\dots,N\}^n$; car $i$ parks in the first free spot met when going clockwise from $\alpha_i$, starting with $\alpha_i$ itself. No car can fail, and exactly one spot stays empty. The displacement of a car on the circle is the number of clockwise steps from its preferred spot to the spot it takes.

**Theorem 4.1** (Konheim and Weiss; the argument is Pollak's) [proved; the argument is given in [FR, Section 2, p. 13]; the count is usually attributed to [KW], which was not read for this document]. For every $\alpha\in\{1,\dots,N\}^n$, exactly one of the $N$ lists obtained from $\alpha$ by adding a constant to all entries modulo $N$ leaves spot $N$ empty. A list leaves spot $N$ empty if and only if it is a parking function of length $n$, and then every car takes the same spot, with the same displacement, as on the row. Hence $|\mathrm{PF}_n|=(n+1)^{n-1}$, and if the preferences of the $n$ cars are independent and uniform on the circle, then, after the rotation that moves the empty spot to $N$, the list is uniformly distributed on $\mathrm{PF}_n$.

*Proof.* Adding $1$ to every preference rotates the whole process by one spot, so the empty spot runs through all $N$ spots as the constant varies; this gives the first assertion. If spot $N$ stays empty, no car preferred it (the car would have taken it) and no car passed it (a car passes only occupied spots), so all preferences lie in $[n]$ and the process never leaves the row $1,\dots,n$: the list is a parking function and the two processes coincide. Conversely a parking function fills $1,\dots,n$ on the row and therefore leaves $N$ empty on the circle. The $N^n$ lists fall into classes of $N$ rotations, each containing one parking function, which gives the count and the statement about the uniform law. $\square$

The rotation changes neither the displacements nor anything else that is defined by the relative positions of cars and empty spots. Statements about such quantities can therefore be made and proved on the circle with independent uniform preferences, and they hold for uniform parking functions.

At a moment when some cars have parked, call a *block* a maximal run of consecutive occupied spots together with the empty spot that follows it clockwise; a single empty spot preceded by an empty spot is a block of size $1$. The blocks partition the circle, their sizes add up to $N$, and their number is the number of empty spots.

**Lemma 4.2** (one step) [proved; known: both assertions are in [Pet, Section 2, pp. 457–458], in the running text]. Suppose the blocks are $B_1,\dots,B_q$ with $q\ge2$, and a car arrives whose preference is uniform on the $N$ spots. Then its preferred spot lies in $B_i$ with probability $|B_i|/N$; in that case the car parks in the empty spot at the end of $B_i$, its displacement is uniformly distributed on $\{0,1,\dots,|B_i|-1\}$, and after it has parked $B_i$ and the block that follows $B_i$ clockwise form one block.

*Proof.* A car whose preference is a spot of $B_i$ moves clockwise through occupied spots until it reaches the empty spot of $B_i$; the $|B_i|$ spots of the block correspond to the displacements $|B_i|-1,\dots,1,0$. Once that spot is filled, the run of $B_i$ continues into the run of the next block. $\square$

We say that this car *closes* the block $B_i$: it fills the empty spot that ends it. So the parking process is a process of merging blocks: it starts from $N$ blocks of size $1$ and ends, after $n$ cars, with one block of size $N$. The law of a car's displacement is decided at the moment of its arrival by the block it lands in, and by nothing else: given that block, the displacement is uniform on it.

### 4.2 The history of the process as a forest

We now record which blocks were merged by which cars. Let $\alpha\in\mathrm{PF}_n$. The *outcome* of $\alpha$ is the permutation $\sigma=(\sigma_1,\dots,\sigma_n)$ in which $\sigma_i$ is the number of the car parked in spot $i$. For a permutation $\sigma$ and a spot $i$ define the *capacity*
$$
h_i=h_i(\sigma)=i-\max\bigl(\{j<i:\ \sigma_j>\sigma_i\}\cup\{0\}\bigr).
$$

**Theorem 4.3** (the parking functions with a given outcome) [proved; known: with the threshold, [CEHHMPU, Section 4.1, (6)–(8)]; the description of the lists with a given outcome and the product without threshold, [GL, Lemma 2.5]; the case without threshold is attributed in [CEHHMPU] to [KW] (not read)]. Let $\sigma$ be a permutation of $[n]$. In every parking function with outcome $\sigma$, when the car $\sigma_i$ arrives, the spots $i-h_i+1,\dots,i-1$ are occupied and the spot $i-h_i$ (if $i-h_i\ge1$) is empty; thus $h_i$ is the size of the block which that car closes. The parking functions with outcome $\sigma$ are exactly the lists in which, for every $i$, the car $\sigma_i$ prefers one of the spots $i-h_i+1,\dots,i$. Consequently they correspond bijectively to the vectors of displacements $(\delta_1,\dots,\delta_n)$ with $0\le\delta_i\le h_i-1$, where $\delta_i$ is the displacement of the car parked in spot $i$, and for every $k\ge1$
$$
Z_n(k)=\sum_{\sigma\in S_n}\ \prod_{i=1}^n\min(h_i(\sigma),k). \tag{4.1}
$$

*Proof.* Fix $\sigma$ and a spot $i$, and put $z=i-h_i$. The cars that have arrived before $\sigma_i$ are those with smaller numbers, so at the arrival of $\sigma_i$ the occupied spots are $\{j:\sigma_j<\sigma_i\}$. By the definition of $h_i$ the spots $z+1,\dots,i-1$ hold cars with smaller numbers and are occupied, while $z$, if it is a spot, holds a car with a larger number and is empty; spot $i$ is empty. If $\alpha$ has outcome $\sigma$, the car $\sigma_i$ cannot have preferred a spot $\le z$, since it would have stopped at $z$ or earlier, nor a spot $>i$; so its preference is in $\{z+1,\dots,i\}$. Conversely, choose for each $i$ a preference in that range and let the cars arrive; by induction on the number of the car, when $\sigma_i$ arrives the cars with smaller numbers stand where $\sigma$ puts them, so the spots from its preference up to $i-1$ are occupied, spot $i$ is empty, and the car parks in $i$. The choices for different spots do not constrain each other. Finally $M<k$ means $\delta_i\le k-1$ for all $i$, which leaves $\min(h_i,k)$ choices at spot $i$. $\square$

The capacities of a permutation are the sizes of the blocks closed during the process, and these blocks are nested or disjoint. The forest that records the nesting is the history of the process.

**Definition** (history forest). For a permutation $\sigma$ of $[n]$, the *history forest* $\Psi(\sigma)$ is the rooted forest on the set of spots $[n]$ in which the parent of spot $i$ is the smallest $j>i$ with $\sigma_j>\sigma_i$, and $i$ is a root if there is no such $j$. Each spot $i$ is labeled by its car $\sigma_i$.

The parent of $i$, when $i$ has one, is the first spot to the right of $i$ that is empty when the car $\sigma_i$ arrives, that is, the empty spot at the end of the block which this car has just enlarged; the car that later fills this spot closes a block containing $i$. A spot $i$ is a root when every spot to its right is already occupied at that moment; on the circle the empty spot at the end of its block is then the spot $N$, which corresponds to the virtual root.

**Proposition 4.4** (the history forest) [proved; parts (a) to (c) are known: [GL, Lemma 3.2, and Lemma 3.3 with its proof]; part (d) was not found in the sources read, see Section 9.4, item 1]. Let $\sigma$ be a permutation of $[n]$.

(a) The subtree of spot $i$ in $\Psi(\sigma)$ consists of the spots $i-h_i+1,\dots,i$. In particular $t_i=h_i$: the size of the subtree of a car is the size of the block the car closed.

(b) Every spot carries a larger label than each of its children: a car arrives after all the other cars in its subtree. Call a forest on the label set $[n]$ with this property *decreasing*.

(c) The map $\sigma\mapsto\Psi(\sigma)$, with the spots replaced by their labels, is a bijection from the permutations of $[n]$ onto the decreasing forests on $[n]$.

(d) Join the roots of $\Psi(\sigma)$ to a virtual root placed at the spot $N=n+1$ of the circle. For $0\le t\le n$, delete the edges that join the spots of the cars $t+1,\dots,n$ to their parents. The trees of the resulting forest are the blocks of the parking process after $t$ cars: each tree consists of an empty spot, which is its root, and of the run of occupied spots that precedes it.

*Proof.* (a) Write $W_i=\{i-h_i+1,\dots,i\}$. If $j\in W_i$ and $j\ne i$, then $\sigma_j<\sigma_i$, and the first spot to the right of $j$ with a larger label is at most $i$; so the parent of $j$ lies in $W_i$, and following parents from $j$ one stays in $W_i$ and moves to the right until one reaches $i$. Hence $W_i$ is contained in the subtree of $i$. Conversely, if $i$ is the parent of $j$, then all spots strictly between $j$ and $i$ carry labels smaller than $\sigma_j<\sigma_i$, so $j\in W_i$ and moreover $W_j\subseteq W_i$, because a spot to the left of $j$ that lies in $W_j$ carries a label smaller than $\sigma_j$. By induction along the path, every descendant of $i$ lies in $W_i$.

(b) holds by the definition of the parent.

(c) Let $i_1<\dots<i_m$ be the children of a spot $j$, or the roots. Then $\sigma_{i_1}>\dots>\sigma_{i_m}$, since if $\sigma_{i_a}<\sigma_{i_b}$ for some $a<b$, the parent of $i_a$ would be a spot at most $i_b$, and $i_a$ would be neither a child of $j$ nor a root. By (a) the subtrees occupy consecutive intervals, each ending at its root. Thus $\sigma$ is recovered from the labeled forest: order the roots, and the children of every vertex, by decreasing label from left to right, and place the vertices on the spots $1,\dots,n$ in postorder (every subtree before its root). Conversely, starting from any decreasing forest, this procedure produces a permutation $\sigma$, and $\Psi(\sigma)$ is the given forest: in postorder, the vertices that come after a vertex $v$ and before its parent belong to the subtrees of later siblings of $v$, whose labels are smaller than the label of $v$, so the first larger label to the right of $v$ is that of its parent, and a root has no larger label to its right.

(d) After $t$ cars the occupied spots are those with $\sigma_i\le t$. Let $e$ be an empty spot (a spot with $\sigma_e>t$, or the spot $N$) and let $i$ be a spot of the run of occupied spots that precedes it. The parent of $i$ is the first spot to the right of $i$ whose car is later than $\sigma_i$; it lies in the run or is $e$, because $e$ carries a later car than every spot of the run (or is the virtual root). Following parents from $i$ one therefore reaches $e$ without leaving the run. Since the edges above the empty spots are deleted and no others, the tree of $e$ in the resulting forest is $e$ together with its run. $\square$

Part (d) is the link between the forest and the process in time: removing the cars in the reverse order of their arrival takes the history forest apart into the blocks of the earlier moments. The edges are removed here in an order determined by the arrivals, from the top of the forest downwards, and not in uniform random order.

The decreasing forests are a small part of all labeled forests, and a uniform parking function does not choose its outcome uniformly: by Theorem 4.3 the outcome $\sigma$ has probability $\prod_i h_i(\sigma)/p_n$. The next lemma is the classical count of decreasing labelings, and the theorem after it shows that the two effects cancel exactly.

**Lemma 4.5** (hook length formula for forests) [proved; the last assertion is classical: [GS, Lemma 2.1], where it is credited to [Kn3, Exercise 20, p. 70] (not read); the same lemma gives the mutual independence of the events $\iota_v=0$; the full joint law was not found in the sources read, see Section 9.1]. Fix a rooted forest with $n$ vertices and label its vertices by a uniformly random bijection onto $[n]$. For a vertex $v$ let $\iota_v$ be the number of vertices in the subtree of $v$, other than $v$, whose label is larger than the label of $v$. Then the variables $\iota_v$ are independent, and $\iota_v$ is uniformly distributed on $\{0,\dots,t_v-1\}$. In particular the probability that the labeling is decreasing, that is, that $\iota_v=0$ for every $v$, is $\prod_v 1/t_v$.

*Proof.* Consider first a tree with $t$ vertices and root $x$. The label of the root is uniformly distributed among the $t$ labels, so $\iota_x$ is uniform on $\{0,\dots,t-1\}$. Given the label of the root and the sets of labels that fall into the subtrees of the children of the root, the labelings of these subtrees are independent and uniform, and for a vertex $v$ of one of these subtrees $\iota_v$ depends only on the relative order of the labels inside that subtree. By induction on the number of vertices, the variables $\iota_v$ of each of these subtrees are independent and uniform on their ranges, and their joint law does not depend on the conditioning; hence all the variables $\iota_v$ of the tree are independent. For a forest, the labelings of the components are independent and uniform given their label sets, and the same argument applies. $\square$

**Theorem 4.6** (the law of the history forest) [proved; the consequence (4.3) is in the literature in bijective form: [GL, Theorem 3.4 and Remark 3.5], [Sh, Lemma 2]; see Section 9]. Let $f$ be a function on the positive integers with values in a commutative ring containing the rational numbers. Then
$$
\sum_{\sigma\in S_n}\ \prod_{i=1}^n f(h_i(\sigma))\;=\;\sum_{F}\ \prod_{v\in F}\frac{f(t_v)}{t_v}, \tag{4.2}
$$
where $F$ runs through the rooted labeled forests on $[n]$. Consequently:

(a) For every function $w$ on the non-negative integers with values in such a ring,
$$
\sum_{\alpha\in\mathrm{PF}_n}\ \prod_{i=1}^n w(d_i)\;=\;\sum_{F}\ \prod_{v\in F}\ \frac1{t_v}\sum_{d=0}^{t_v-1}w(d). \tag{4.3}
$$

(b) Let $\alpha$ be a uniform random parking function of length $n$. Let $F$ be a uniform random rooted labeled forest on $[n]$ and, given $F$, let $(D_v)_{v\in F}$ be independent with $D_v$ uniform on $\{0,\dots,t_v-1\}$. Then the multiset of pairs (size of the block closed by a car, displacement of that car) of $\alpha$ has the same law as the multiset $\{(t_v,D_v):v\in F\}$.

(c) For every $k\ge1$ and every shape $S$ of a rooted forest with $n$ vertices, the number of parking functions with $M<k$ whose history forest has the shape $S$ is $\frac{n!}{|\mathrm{Aut}(S)|}\prod_{v\in S}\min(1,k/t_v)$, that is, the number of labeled forests of shape $S$ times $\Phi_{g_k}$ in the notation of Section 5. In particular the shape of the history forest of a uniform parking function has the law of the shape of a uniform random rooted labeled forest.

*Proof.* By Proposition 4.4 the left side of (4.2) equals $\sum_\Delta\prod_{v}f(t_v)$ over the decreasing forests $\Delta$ on $[n]$. Group the labeled forests by their shape, that is, by the isomorphism class of the underlying unlabeled rooted forest. The product $\prod_v f(t_v)$ depends only on the shape. A shape $S$ with automorphism group of order $|\mathrm{Aut}(S)|$ carries $n!/|\mathrm{Aut}(S)|$ labeled forests, and by Lemma 4.5 the fraction $\prod_v 1/t_v$ of them is decreasing, because the property of being decreasing is invariant under automorphisms. Hence both sides of (4.2) equal $\sum_S \frac{n!}{|\mathrm{Aut}(S)|}\prod_{v\in S}\frac{f(t_v)}{t_v}$.

(a) By Theorem 4.3, the sum over the parking functions with outcome $\sigma$ of $\prod_i w(d_i)$ is $\prod_i\sum_{d<h_i}w(d)$. Summing over $\sigma$ and applying (4.2) with $f(t)=\sum_{d<t}w(d)$ gives (4.3).

(b) Apply the same argument with $f(t)=\sum_{d<t}x_{t,d}$, where the $x_{t,d}$ are independent indeterminates. The left side becomes the generating polynomial of the multiset of pairs over all parking functions, and the right side is $p_n$ times the expectation of $\prod_v x_{t_v,D_v}$. A random finite multiset is determined in law by this expectation.

(c) This is what the proof of (4.2) gives shape by shape, with $f(t)=\min(t,k)$: the parking functions with outcome $\sigma$ and $M<k$ number $\prod_i\min(h_i,k)$ by Theorem 4.3, and the decreasing forests of shape $S$ number $\frac{n!}{|\mathrm{Aut}(S)|}\prod_v1/t_v$. $\square$

Thus the uniform random rooted labeled forest is the history of the parking process with the order of arrival forgotten, and, together with independent uniform marks on its subtree sizes, it gives the law of the displacements as a multiset. Two cautions belong here. The labels of the uniform forest are not the numbers of the cars; the history forest itself is decreasing and is far from uniform among labeled forests. And the statement concerns the multiset of displacements: which car has which displacement is not recorded by the uniform forest.

**Corollary 4.7** (the maximum displacement) [proved]. With $F$ and $(D_v)$ as in Theorem 4.6(b), $M(\alpha)$ has the law of $\max_v D_v$, and for every integer $k\ge1$
$$
\frac{Z_n(k)}{p_n}=\Pr(M<k)=\mathbb E\prod_{v\in F}\min\Bigl(1,\frac{k}{t_v}\Bigr). \tag{4.4}
$$
Equivalently $D_v=\lfloor U_vt_v\rfloor$ with independent uniform variables $U_v$ on $[0,1)$. In particular $b_{n,n-1}=n^{n-2}$: the maximum equals $n-1$ exactly when the forest is a single tree, which happens for $n^{n-1}$ of the $p_n$ forests, and the mark of its root equals $n-1$, which has probability $1/n$.

In the language of the process, (4.4) says that the probability of the event $M<k$ is the expectation of the product, over the cars, of the probability $\min(1,k/h)$ that a car landing in a block of size $h$ has displacement smaller than $k$ (Lemma 4.2). The threshold $k$ acts on each car separately, and only through the size of the block the car closes.

### 4.3 The same forest as a conditioned branching process

**Theorem 4.8** (Poisson Galton–Watson trees) [proved; cited: [J12, Example 10.2]]. Let $0<\lambda\le1$ and let $\mathcal T$ be the family tree of a Galton–Watson process started from one individual in which every individual has a Poisson($\lambda$) number of children; for these $\lambda$ the tree is finite with probability $1$, as the proof shows. Forget the order of the children and label the vertices by a uniformly random bijection onto $\{1,\dots,|\mathcal T|\}$. Then every rooted labeled tree $\tau$ with $m$ vertices has probability
$$
\Pr(\mathcal T=\tau)=\frac{e^{-\lambda m}\lambda^{m-1}}{m!}. \tag{4.5}
$$
Consequently the size of $\mathcal T$ has the Borel distribution, $\Pr(|\mathcal T|=m)=e^{-\lambda m}(\lambda m)^{m-1}/m!$, and conditionally on $|\mathcal T|=m$ the tree is uniform on the $m^{m-1}$ rooted labeled trees with $m$ vertices, for every such $\lambda$. For $\lambda=1$ the size has the law $\mathrm{Bor}$ of Section 3.2.

*Proof.* An ordered rooted tree in which the vertex $v$ has $c_v$ children has probability $\prod_v e^{-\lambda}\lambda^{c_v}/c_v!=e^{-\lambda m}\lambda^{m-1}\prod_v 1/c_v!$, since $\sum_vc_v=m-1$. A rooted labeled tree $\tau$ without order arises from $\prod_vc_v!$ ordered labeled trees, each of which is obtained from one ordered tree and one of the $m!$ labelings. This gives (4.5); the right side depends on $\tau$ only through $m$, and there are $m^{m-1}$ trees of size $m$. Summing (4.5) over all trees gives the probability that the tree is finite, $\sum_{m\ge1}m^{m-1}e^{-\lambda m}\lambda^{m-1}/m!=T(\lambda e^{-\lambda})/\lambda$, and this equals $1$ for $0<\lambda\le1$, because by the proof of Lemma 6.1(c) the function $T$ is on $[0,1/e]$ the inverse of $u\mapsto ue^{-u}$ on $[0,1]$. $\square$

Formula (4.5) shows why the mean disappears: the law of $\mathcal T$ is an exponential family in which the size is the sufficient statistic, so conditioning on the size removes the parameter. The value $\lambda=1$ is distinguished only as the critical one: for $\lambda<1$ the size has the masses $\lambda^{-1}(\lambda e^{1-\lambda})^m\,e^{-m}a_m$, which carry the exponentially decaying factor $(\lambda e^{1-\lambda})^m$ in addition to $e^{-m}a_m$; at $\lambda=1$ this factor is absent, the masses are $e^{-m}a_m$, and their sum is $T(1/e)=1$. The restriction to $\lambda\le1$ serves only to make the tree finite with probability $1$: the proof of (4.5) uses no bound on $\lambda$, so for $\lambda>1$ the finite trees have the same probabilities and, given its size, the tree is again uniform.

Combining Theorem 4.8 with the remark on the virtual root in Section 3.2: take a Poisson($\lambda$) Galton–Watson tree conditioned to have $n+1$ vertices, label it uniformly by $\{0,\dots,n\}$, condition on the root having label $0$ (an event independent of the shape) and remove the root. The result is the uniform random rooted labeled forest on $[n]$, the object of Theorem 4.6. The number of its components is the number of children of the root and is not fixed.

### 4.4 Intermediate times: forests with a fixed number of trees, and the additive coalescent

The history can be stopped after $t$ cars. On the circle there are then $q=N-t$ blocks.

**Theorem 4.9** (the blocks at an intermediate time) [proved; known: [KY, Proposition 2.5] for the count, [CL, Section 5.1] and [P99, Proposition 7 and Section 4.1] for the law; the law of the block sizes at every time is stated in [J05, p. 183, with Lemma 3.1] and, without proof, in [Pet, Section 2, remark on p. 459]]. Let $n$ cars with independent uniform preferences park on the circle of $N=n+1$ spots, and consider the moment after the first $t$ cars, $0\le t\le n$; put $q=N-t$. Choose one of the $q$ empty spots uniformly at random and read the sizes of the blocks clockwise, starting after the chosen spot. The resulting composition $(s_1,\dots,s_q)$ of $N$ has probability proportional to $\prod_{i}a_{s_i}$. Equivalently, it has the law of $q$ independent Borel variables conditioned on their sum being $N$, and the law of the sizes of the trees, in uniform random order, of a uniform random rooted labeled forest with $q$ trees on $N$ vertices. Moreover, a given set $O$ of $t$ spots is the set of occupied spots with probability $t!\,N^{-t}\prod_ia_{s_i}$, where the $s_i$ are the sizes of its blocks; in particular all configurations with the same multiset of block sizes are equally likely.

*Proof.* Let $O$ be a set of $t$ spots whose complement consists of $q$ empty spots, and let the block ending at the $i$-th empty spot contain $c_i=s_i-1$ occupied spots. A list of $t$ preferences leaves exactly $O$ occupied if and only if, for each $i$, exactly $c_i$ cars prefer the occupied spots of the $i$-th block and these cars, in their order of arrival, form a parking function on those $c_i$ consecutive spots: cars cannot pass an empty spot, and a car preferring an empty spot of the final configuration would have taken it. The number of such lists is $\frac{t!}{c_1!\cdots c_q!}\prod_i(c_i+1)^{c_i-1}$, and $(c+1)^{c-1}/c!=s^{s-2}/(s-1)!=a_s$ for $s=c+1$. So the probability of $O$ is $t!\,N^{-t}\prod_ia_{s_i}$, which depends on $O$ only through the block sizes; the first assertion follows because a pair (configuration, chosen empty spot) is the same as a pair (position of the chosen spot, composition). Since $\mathrm{Bor}(s)=e^{-s}a_s$ and the sizes add up to $N$, the weight $\prod_ia_{s_i}$ is proportional to $\prod_i\mathrm{Bor}(s_i)$. Finally the number of pairs consisting of a rooted labeled forest with $q$ trees on $N$ vertices and an ordering of its trees in which the sizes are $s_1,\dots,s_q$ is $N!\prod_ia_{s_i}$, and every forest has $q!$ orderings; so the sizes of the trees of a uniform forest, taken in uniform random order, have the same law. $\square$

The representation of the tree sizes of a uniform forest by conditioned independent variables is due to Pavlov; see [P99, Proposition 7 and Section 4.1]. Theorem 4.9 shows that it holds for the blocks of the parking process at every time, by a direct count.

The evolution in time is also classical. By Lemma 4.2 the block in which a car lands is chosen with probability proportional to its size, and it merges with its clockwise neighbour. By Theorem 4.9 all configurations with the same multiset of block sizes are equally likely, so at a single time the neighbour is a uniformly chosen other block; Theorem 4.10 below says, and its proof shows, that this remains true when the earlier sizes are known as well. Chassaing and Louchard observed this merging rule and its coincidence with the coalescent of Aldous and Pitman [CL, Sections 1.4 and 8].

**Theorem 4.10** (additive coalescent) [proved; the statement is in [CL, Section 1.4, formula (1.5), and Section 8], derived there in the running text; the identification in the last sentence is cited]. The multiset of block sizes of the parking process on the circle, as a function of the number of cars, is a Markov chain. When there are $q\ge2$ blocks, with $m_x$ blocks of size $x$, the next car merges a block of size $x$ with a block of size $y\ne x$ with probability $(x+y)\,m_xm_y/(N(q-1))$, and two blocks of size $x$ with probability $x\,m_x(m_x-1)/(N(q-1))$. Equivalently, if the blocks are numbered in uniformly random order and have sizes $s_1,\dots,s_q$, the blocks $i$ and $j$ are merged with probability $(s_i+s_j)/(N(q-1))$. This is the discrete-time additive coalescent: the same chain describes the sizes of the trees when the edges of a uniform random labeled tree on $N$ vertices are deleted in uniform random order and time is reversed [AP, Lemma 1].

*Proof.* Let $\mathfrak M_t$ be the multiset of block sizes after $t$ cars and $O_t$ the set of occupied spots. We show by induction on $t$ that, conditionally on $\mathfrak M_0,\dots,\mathfrak M_t$, the set $O_t$ is uniformly distributed over the sets of $t$ spots whose block sizes form the multiset $\mathfrak M_t$. This holds for $t=0$. Suppose it holds for $t$, and let $O'$ be a set of $t+1$ spots with multiset $\mathfrak M'$, obtained from $\mathfrak M_t$ by replacing two sizes $x,y$ by $x+y$. If emptying a spot $z$ of $O'$ divides a block of size $b$ into blocks of sizes $a$ and $b-a$ and leaves a set with multiset $\mathfrak M_t$, then the multisets $\{x+y,a,b-a\}$ and $\{b,x,y\}$ coincide, and comparing their largest elements gives $b=x+y$ and $\{a,b-a\}=\{x,y\}$. So the sets $O$ with multiset $\mathfrak M_t$ from which one car can produce $O'$ are obtained by emptying a spot $z$ of $O'$ that divides a block of size $x+y$ of $O'$ into a block of size $x$ ending at $z$ followed by a block of size $y$, or the same with $x$ and $y$ exchanged; by Lemma 4.2 the car fills $z$ with probability $x/N$, respectively $y/N$. Hence the probability of the event $\{O_{t+1}=O'\}$ together with the given history is the constant probability of each $O$ times $\frac{x+y}N$ times the number of blocks of size $x+y$ of $O'$ (times $\frac12$ if $x=y$), which depends on $O'$ only through $\mathfrak M'$. This proves the claim for $t+1$. Given the history, $O_t$ is thus uniform over the configurations with multiset $\mathfrak M_t$. By the correspondence between configurations with a marked empty spot and pairs (position, composition) used in the proof of Theorem 4.9, the sequence of block sizes read from a uniformly chosen empty spot is then uniform over the arrangements of $\mathfrak M_t$; so, for blocks numbered in uniformly random order, the block that follows block $i$ clockwise is each of the other $q-1$ blocks with probability $1/(q-1)$. By Lemma 4.2 the next car lands in block $i$ with probability $s_i/N$ and merges it with the block that follows it, which gives the probability $(s_i+s_j)/(N(q-1))$ for the pair $\{i,j\}$; summing over the pairs of blocks with given sizes gives the first form. These probabilities depend on the history only through $\mathfrak M_t$. $\square$

For $N=7$ the transition probabilities and the Markov property were also checked by enumerating all histories (Appendix C, item C3).

### 4.5 Summary: one object

The uniform random parking function comes with a history, and the following are descriptions of it.

1. *As a process.* Blocks on a circle of $N=n+1$ spots merge; each car lands in a block chosen with probability proportional to its size, closes it, and has a displacement uniform on it (Lemma 4.2). The block sizes form the additive coalescent (Theorem 4.10), and at each time they are conditioned Borel variables (Theorem 4.9).
2. *As a combinatorial structure.* The history is a decreasing forest whose subtrees are the closed blocks (Proposition 4.4); with the order of arrival forgotten it is the uniform random rooted labeled forest on $[n]$, and the displacements are independent uniform marks on its subtree sizes (Theorem 4.6).
3. *As a branching process.* The uniform forest is a Poisson Galton–Watson tree conditioned on having $n+1$ vertices, with its root removed; the mean of the Poisson law is irrelevant, and the critical mean $1$ is the normalisation in which the unconditioned size law is the Borel law without an exponential factor (Theorem 4.8).

We refer to this object, in any of its descriptions, as the history of the parking process. The name *history forest* stays with the forest $\Psi(\sigma)$ of Section 4.2, of which there is one for each outcome; when the order of arrival is forgotten we speak of its shape or of the uniform forest. It is not a new random structure, and each of its descriptions is in the literature: the merging of parking blocks as an additive coalescent is due to Chassaing and Louchard; the uniformity of a displacement on the block in which the car lands is in Petersson's paper; the decreasing tree whose subtrees give the ranges of the displacements is in the paper of Guedes de Oliveira and Las Vergnas and, with a rank rule for the displacements, in that of Kenyon and Yin, who refer it to a construction of Knuth; the forest whose inversion counts are the displacements is Shin's; and the conditioned Galton–Watson description is classical. Section 9.1 gives the places. What Section 4 does is to put them together. The decreasing tree is the merge history of the block process, so the subtree of a car is the block it closes; and the displacements are governed by this one object: the history forest with its arrival labels gives, car by car, the range of the displacement and its conditional law, and the uniform forest gives the law of the multiset of displacements.

## 5. The observables, and the four laws that occur

Section 4 identified the object. This section fixes the class of quantities that are computed on it and the probability laws under which they are computed. Both are short to state, and both need to be kept in view later: most of the confusions that arise when the tools of Section 6 are combined come from applying a statement valid under one law to another law.

### 5.1 Functionals of the subtree sizes

For a function $g$ on the positive integers, with values in a commutative ring containing the rational numbers, and a rooted forest $F$ put
$$
\Phi_g(F)=\prod_{v\in F}g(t_v),\qquad Z_n[g]=\sum_{F}\Phi_g(F),
$$
the sum being over the rooted labeled forests on $[n]$, with $Z_0[g]=1$. Thus $Z_n[g]/p_n$ is the expectation of $\Phi_g$ over the uniform forest, and by (4.2) with $f(t)=t\,g(t)$
$$
Z_n[g]=\sum_{\sigma\in S_n}\prod_{i=1}^n h_i(\sigma)\,g(h_i(\sigma)). \tag{5.1}
$$
We call $\Phi_g$ a *subtree-size functional*. In the literature on trees the number $t_v$ is called the hook length of $v$, and sums of such products over families of trees are the subject of hook length formulas (Section 9).

By Theorem 4.6(a), every sum over parking functions of a product $\prod_iw(d_i)$ of a function of the displacements is of this form, with $g(t)=\frac1t\sum_{d<t}w(d)$. This is the reason why the class matters: the sum over the parking functions of any product over the cars of one function of the displacement is the total $Z_n[g]$ of a subtree-size functional over the forests, and the law of every statistic of the multiset of displacements is obtained from such sums (as a coefficient of a generating function, or directly, as for the maximum). The maximum displacement is the case $w=\mathbf 1_{\{d<k\}}$; Section 10 gives others.

### 5.2 The threshold functional

For real $y>0$ let $g_y(t)=\min(1,y/t)$ and write
$$
Z_n(y)=Z_n[g_y]=\sum_F\prod_{v\in F}\min\Bigl(1,\frac{y}{t_v}\Bigr).
$$
For an integer $y=k\ge1$ this is the number of parking functions of length $n$ with $M<k$, by (4.4), so the notation agrees with Section 3.2. The function $y\mapsto Z_n(y)$ is continuous, non-decreasing and piecewise polynomial, with $Z_n(y)=p_n$ for $y\ge n$.

Relative to a threshold $y$, a vertex $v$ is *heavy* if $t_v>y$ and *light* if $t_v\le y$; for an integer threshold $k$, a vertex with $t_v=k$ is a *threshold vertex*. The functional $\Phi_{g_y}$ equals $\prod_{v\text{ heavy}}y/t_v$: light vertices contribute the factor $1$. Two consequences will be used constantly. For $y$ in an interval $[j,j+1)$ between two consecutive integers the set of heavy vertices of a given forest is the same, namely the vertices with $t_v\ge j+1$, so that on the closed interval $[j,j+1]$ the functional $\Phi_{g_y}(F)$ is a constant times $y$ raised to the number of these vertices. And the subtrees of heavy vertices are large: two heavy vertices are either nested or have disjoint subtrees of size greater than $y$ each, so a forest on $[n]$ contains at most $n/y$ heavy vertices no one of which is an ancestor of another, and if $n<2y$ the heavy vertices lie on one path descending from a root.

### 5.3 Four laws

The formulas of the following sections live under four different laws on forests. We name them once.

- **(U)** The uniform law on the rooted labeled forests on $[n]$, equivalently on the rooted trees on $\{0,\dots,n\}$ with root $0$. This is the history of the full parking process (Theorem 4.6). The number of trees is free.
- **(Q)** The uniform law on the rooted labeled forests with exactly $q$ trees on $N$ vertices. The sizes of its trees have the law of the block sizes of the process at an intermediate time (Theorems 4.9 and 4.10), and of the blocks of a parking process with spare spots (Section 10.3).
- **(B)** The unconditioned law of Theorem 4.8 with $\lambda=1$, under which a rooted labeled tree with $m$ vertices has probability $e^{-m}/m!$ and the size has the Borel law. Removing the root gives a forest whose trees, as shapes, are independent copies of the tree itself (the labels of the trees are a uniform relabeling and are of course not independent); the number of trees is Poisson with mean $1$. In the language of analytic combinatorics this is the Boltzmann model of the class of rooted labeled trees at its critical parameter. It mixes all sizes $n$, and a statement proved under (B) is a statement about a mixture of rows, not about one row.
- **(W)** The law on the forests on $[n]$ with probability $\Phi_{g_y}(F)/Z_n(y)$. For an integer $y=k$ this is the law of the history forest (as an unlabeled shape, or with uniform labels) of a parking function conditioned on $M<k$. It is not uniform, and it changes with $y$.

The first mechanism of Section 6 passes between (U), (Q) and (B). No mechanism turns (W) into one of the others: the decomposition of Section 6.2 can be applied under (W), but the pieces above the threshold then carry their weights with them (Section 6.4).

In the language of the process, (W) is the law of the shape of the history forest when the parking process is conditioned to survive, where each arriving car survives with probability $\min(1,y/h)$ if it lands in a block of size $h$, independently of the other cars once the blocks are given; for an integer $y=k$ the survival of a car is the event that its displacement is smaller than $k$. Under this conditioning the block in which a car lands is no longer chosen with probability proportional to its size.

## 6. Two mechanisms and the dictionary

Computations on the history forest use two mechanisms. The first changes the normalisation: it passes between counting structures of a fixed size and assigning probabilities to structures of all sizes. The second cuts the forest at chosen vertices into pieces that are again uniform. This section states each as a lemma or theorem, derives the classical formulas from them, and ends with the dictionary that lists, for each classical name, the place it occupies.

### 6.1 Normalisation by size: Cayley's counts and the Borel masses are the same numbers

**Lemma 6.1** (normalisation) [proved; the generating-function facts are standard: [FS, Section II.5.1, (44)–(47), Note II.18, and Theorem A.2]]. For all integers $m\ge1$ and $q\ge1$:

(a) The number of rooted labeled trees on $m$ vertices is $m^{m-1}=m!\,e^{m}\,\mathrm{Bor}(m)$; the number of such trees with one marked vertex is $m^{m}=m!\,e^{m}\,\mathrm{Ren}(m)$; the number of unrooted labeled trees is $m^{m-2}=m!\,e^{m}\,\mathrm{Bor}(m)/m$; the number of rooted labeled forests on $m$ vertices is $p_m=(m+1)^{m-1}=m!\,e^{m+1}\,\mathrm{Bor}(m+1)$.

(b) $[z^m]\,T(z)^q=\dfrac qm\,\dfrac{m^{m-q}}{(m-q)!}$ for $q\le m$ (Lagrange inversion applied to $T=ze^T$). Equivalently, the number of rooted labeled forests with exactly $q$ trees on $m$ vertices is $\binom{m-1}{q-1}m^{m-q}$, and the sum of $q$ independent variables with law $\mathrm{Bor}$ has the Borel–Tanner law
$$
\mathrm{Bor}^{*q}(m)=e^{-m}[z^m]T(z)^q=\frac qm\,\frac{e^{-m}m^{m-q}}{(m-q)!}.
$$

(c) $\sum_{m\ge1}\mathrm{Bor}(m)=T(1/e)=1$.

(d) $\sum_{m\ge1}\dfrac{a_m}{m}z^m=T(z)-\dfrac{T(z)^2}{2}$; the coefficient $a_m/m=m^{m-2}/m!$ is the number of unrooted labeled trees on $m$ vertices divided by $m!$.

*Proof.* (a) is Cayley's formula together with the definitions of $\mathrm{Bor}$ and $\mathrm{Ren}$; a rooted forest on $[m]$ is a tree on $\{0,\dots,m\}$ rooted at $0$, and there are $(m+1)^{m}/(m+1)$ of those. (b) An ordered $q$-tuple of rooted trees on disjoint label sets with union $[m]$ is counted by $m!\,[z^m]T^q$, and the coefficient is given by the Lagrange inversion formula $[z^m]H(T)=\frac1m[u^{m-1}]H'(u)e^{mu}$ with $H(u)=u^q$; dividing by $q!$ gives the forests, and multiplying by $e^{-m}$ gives the convolution, since $\mathrm{Bor}(j)=e^{-j}[z^j]T$. (c) The series $T$ has non-negative coefficients and converges for $0\le x<1/e$, since $a_{m+1}/a_m=(1+1/m)^{m-1}\to e$; there $T$ is continuous and increasing, $T(0)=0$, and $T(x)e^{-T(x)}=x$. The function $u\mapsto ue^{-u}$ is an increasing bijection from $[0,1]$ onto $[0,1/e]$ and takes the value $1/e$ only at $u=1$; so $T(x)$ cannot reach $1$ for $x<1/e$, $T$ is the inverse of this bijection on $[0,1/e)$, $T(x)\to1$ as $x\to1/e$, and $T(1/e)=1$ by monotone convergence. In the language of Theorem 4.8 this says that the critical Galton–Watson tree is finite with probability $1$. (d) Differentiating $T=ze^T$ gives $T'=T/z+TT'$, that is, $T'(1-T)=T/z$; so the derivative of $T-T^2/2$ is $T/z=\sum a_mz^{m-1}$, and both sides vanish at $0$. $\square$

Part (a) contains the answer to the question why Cayley's formula and the Borel distribution overlap. They are one sequence in two normalisations: $a_m=m^{m-1}/m!$ counts rooted trees per labeling, and $\mathrm{Bor}(m)=e^{-m}a_m$ is the probability of size $m$ under the law (B). The following consequence is what one sees in every formula for a fixed size $n$.

**Corollary** (cancellation of the exponentials) [proved]. Suppose that a family of structures on the label set $\{0,\dots,n\}$ is in bijection with the choices of: an ordered partition of the labels into sets of sizes $\gamma_1,\dots,\gamma_r$ with $0$ in the first set, and on the $i$-th set a structure from a class having $c_i(\gamma_i)$ members. Then the number of structures divided by $p_n$ is
$$
\frac{\gamma_1}{\mathrm{Bor}(N)}\ \prod_{i=1}^r\frac{c_i(\gamma_i)\,e^{-\gamma_i}}{\gamma_i!},\qquad N=n+1=\gamma_1+\dots+\gamma_r .
$$
Each factor is the normalised count of one class, a Borel-type mass, and no power of $e$ is left because the sizes add up to $N$.

*Proof.* The number of ordered partitions is $\frac{N!}{\gamma_1!\cdots\gamma_r!}\cdot\frac{\gamma_1}{N}$, and $p_n=n!\,e^{N}\mathrm{Bor}(N)=N!\,e^N\mathrm{Bor}(N)/N$. $\square$

### 6.2 Decomposition at vertices: the pattern formula

Let $\tau$ be a rooted tree on $\{0,\dots,n\}$ with root $0$, that is, a forest on $[n]$ with its virtual root; put $N=n+1$.

**Definition** (pattern, occurrence, layer). A *pattern* is a finite rooted tree $\mathfrak p$ with root $\varrho$ in which every node $u\ne\varrho$ carries a positive integer $t_u$ and a type, *child* or *descendant*. Put $t_\varrho=N$ and, for every node $u$,
$$
\gamma_u=t_u-\sum_{u'\ \text{child of}\ u\ \text{in}\ \mathfrak p}t_{u'};
$$
we require $\gamma_u\ge1$ for all $u$. An *occurrence* of $\mathfrak p$ in $\tau$ is a map $u\mapsto v_u$ from the nodes of $\mathfrak p$ to the vertices of $\tau$ with $v_\varrho=0$ such that, for every node $u\ne\varrho$ with parent $u^-$ in $\mathfrak p$: the subtree of $v_u$ has $t_u$ vertices; $v_u$ is a proper descendant of $v_{u^-}$, and a child of $v_{u^-}$ if $u$ has type child; and the subtrees of $v_u$ and $v_{u'}$ are disjoint whenever $u\ne u'$ have the same parent in $\mathfrak p$. The *layer* of a node $u$ is the set of vertices of the subtree of $v_u$ that lie in none of the subtrees of the $v_{u'}$, $u'$ a child of $u$; it has $\gamma_u$ vertices, contains $v_u$, and is connected.

A pattern with a single non-root node asks for a vertex whose subtree has a given size. A path asks for a chain of nested subtrees of given sizes. A node with two children asks for two disjoint subtrees inside a third.

**Theorem 6.2** (pattern formula) [proved]. Let $\tau$ be uniformly distributed on the rooted labeled trees on $\{0,\dots,n\}$ with root $0$, and let $\mathfrak p$ be a pattern. For a node $u$ let $c_u$ be the number of its children in $\mathfrak p$ of type descendant.

(a) The expected number of occurrences of $\mathfrak p$ in $\tau$ is
$$
\frac{1}{\mathrm{Bor}(N)}\ \prod_{u\in\mathfrak p}\mathrm{Bor}(\gamma_u)\,\gamma_u^{\,c_u}. \tag{6.1}
$$

(b) Choose a pair consisting of a tree and an occurrence of $\mathfrak p$ in it uniformly among all such pairs. Conditionally on the sets of labels of the layers, the layers are independent; the layer of $u\ne\varrho$, rooted at $v_u$, is a uniform rooted labeled tree on its label set, the layer of $\varrho$ is a uniform tree on its label set rooted at $0$, and for each node $u'$ of type descendant the vertex of the layer of its parent $u$ to which $v_{u'}$ is attached is uniform on that layer, independently of everything else.

*Proof.* Given $\tau$ and an occurrence, cut the edges between each $v_{u'}$, $u'\ne\varrho$, and its parent in $\tau$. The components are the layers. The layer of $u\ne\varrho$ is a tree with root $v_u$; the layer of $\varrho$ is a tree with root $0$. The parent of $v_{u'}$ lies in the layer of the pattern-parent $u$ of $u'$: it is a descendant of $v_u$ or $v_u$ itself, and it cannot lie in the subtree of another $v_{u''}$ with the same pattern-parent, because that subtree is disjoint from the subtree of $v_{u'}$. Conversely, choose an ordered partition of the labels into sets of sizes $\gamma_u$ with $0$ in the set of $\varrho$, a rooted tree on each set (with root $0$ on the set of $\varrho$), and for each $u'\ne\varrho$ a vertex of the layer of its pattern-parent, which must be the root of that layer if $u'$ has type child; attaching the root of the layer of $u'$ to the chosen vertex, for all $u'$, gives a tree $\tau$ with an occurrence, and the subtree of $v_u$ has $\gamma_u$ plus the sizes of the subtrees below it, that is $t_u$, vertices. The two constructions are inverse to each other. The number of rooted trees on a set of size $\gamma$ is $\gamma^{\gamma-1}$, of those with a prescribed root $\gamma^{\gamma-2}$, and the number of admissible attachment vertices is $\gamma_u^{c_u}$ in total for the children of $u$. By the corollary of Lemma 6.1, with the classes "rooted tree together with a choice of the attachment vertices" for $u\ne\varrho$ and "tree rooted at $0$ together with a choice of the attachment vertices" for $\varrho$ (where the factor $\gamma_\varrho$ of the corollary turns $\gamma_\varrho^{\gamma_\varrho-2}$ into $\gamma_\varrho^{\gamma_\varrho-1}$), the number of pairs (tree, occurrence) divided by $p_n$ is (6.1). Part (b) is the statement that the bijection is with a product set. $\square$

The formula has one factor for each piece. A piece contributes its Borel mass, multiplied by its size once for each further piece that may be attached to it at an arbitrary vertex. All the counting formulas for uniform forests used in the study of the conjecture are instances; we list the ones that carry classical names.

**Corollary 6.3** [proved; known: the count of (a), and the counts for two vertices, for conditioned Galton–Watson trees in general [J16, Lemma 5.1 and Lemma 6.1]; the first formula of (c) [MM78, (5.2)] and the law of the depth [AP2, (107)]; the decomposition behind (d) [P01, Section 4.1]; no source was found for (b) with more than two vertices]. Let $F$ be a uniform random rooted labeled forest on $[n]$, $N=n+1$.

(a) *Subtrees of a given size.* For $1\le s\le n$ the expected number of vertices $v$ with $t_v=s$ is $\mathrm{Ren}(N-s)\,\mathrm{Bor}(s)/\mathrm{Bor}(N)$, and the expected number of trees of $F$ with $s$ vertices is $\mathrm{Bor}(N-s)\,\mathrm{Bor}(s)/\mathrm{Bor}(N)$. For $s>n/2$ there is at most one vertex with $t_v=s$; the first number is then the probability that such a vertex exists, and the second the probability that $F$ has a tree with $s$ vertices.

(b) *Chains.* For $n\ge t_1>\dots>t_j\ge1$, the expected number of chains $v_1,\dots,v_j$ in which $v_{i+1}$ is a proper descendant of $v_i$ and $t_{v_i}=t_i$ is
$$
\frac{\mathrm{Bor}(t_j)}{\mathrm{Bor}(N)}\prod_{i=1}^{j}\mathrm{Ren}(\gamma_i),\qquad \gamma_1=N-t_1,\quad \gamma_i=t_{i-1}-t_i\ (i\ge2),
$$
and a factor $\mathrm{Ren}(\gamma_i)$ is replaced by $\mathrm{Bor}(\gamma_i)$ if $v_i$ is required to be a child of $v_{i-1}$ (a root of $F$, for $i=1$).

(c) *The ancestral line of a vertex and the birthday law.* The expected number of vertices at distance $d$ from the virtual root is $\mathrm{Bor}^{*(d+1)}(N)/\mathrm{Bor}(N)=(d+1)(N-1)_d/N^{d}$. Hence, if $V$ is a uniform random vertex of a uniform random rooted labeled tree on $N$ vertices and $D$ is its distance from the root,
$$
\Pr(D\ge d)=\frac{(N-1)(N-2)\cdots(N-d)}{N^{d}},
$$
which is the probability that $d+1$ independent uniform draws from $N$ values are distinct.

(d) *The renewal identity.* $\mathrm{Ren}(j)=\sum_{i\ge1}\mathrm{Bor}^{*i}(j)$ for $j\ge1$; in generating functions $zT'(z)=T(z)/(1-T(z))$.

*Proof.* (a) and (b) are (6.1) for a pattern that is a path, with all types descendant, or with the indicated types child; the last assertion of (a) holds because two subtrees with more than $n/2$ vertices each cannot be disjoint, and nested subtrees have different sizes. (c) A vertex at distance $d$ from $0$ is the end of a path of $d$ nodes of type child with arbitrary sizes; summing (6.1) over the sizes gives the sum of $\prod_{i=0}^d\mathrm{Bor}(\gamma_i)$ over the compositions $(\gamma_0,\dots,\gamma_d)$ of $N$, divided by $\mathrm{Bor}(N)$, and Lemma 6.1(b) evaluates it. Dividing by $N$ gives $\Pr(D=d)=(d+1)(N-1)_d/N^{d+1}=\frac{(N-1)_d}{N^d}-\frac{(N-1)_{d+1}}{N^{d+1}}$; the law of the shape of a uniform rooted tree does not depend on which label the root carries. (d) Cut a rooted tree with a marked vertex along the path from the root to the marked vertex: it becomes a sequence of $i\ge1$ rooted trees, the roots of which are the vertices of the path. Counting both sides with Lemma 6.1(a) and (b) gives the identity. $\square$

Part (d) is the reason for the name of $\mathrm{Ren}$: if $X_1,X_2,\dots$ are independent with law $\mathrm{Bor}$, then $\mathrm{Ren}(j)$ is the probability that some partial sum $X_1+\dots+X_i$ equals $j$; the sequence of these partial sums is what is called the *Borel walk*, and $\mathrm{Ren}$ is its renewal sequence. For forests with $q$ trees the analogue of part (c) is the following [proved; not found in the sources read for this document, see Section 9.4, item 7]: if $V$ is a uniform vertex of a uniform random rooted labeled forest with $q$ trees on $N$ vertices and $D$ is its distance from the root of its tree, then $\Pr(D\ge d)=(N-q)_d/N^d$. The proof is the same count: the pairs (forest, vertex at depth $d$) correspond to sequences of $d+1$ trees along the path together with $q-1$ further trees, and Lemma 6.1(b) evaluates their number.

### 6.3 The same decomposition at the top: the last car

The decomposition can also be made at the top of the forest, and then it is a recursion in $n$. In the process this is the removal of the last car.

**Proposition 6.4** (last-car recursion and exponential formula) [proved; known: the recursion (6.2) for the threshold weight [AF, Theorem 3.7] and for the weight $[t]_q/t$ of the total displacement [Kn98, (2.1)]; the equation (6.3) for an arbitrary weight [CGG, Theorems 4.1 and 4.4]]. For every weight $g$ and every $n\ge1$,
$$
Z_n[g]=\sum_{j=0}^{n-1}\binom{n-1}{j}\,(j+1)\,g(j+1)\,Z_j[g]\,Z_{n-1-j}[g]. \tag{6.2}
$$
Equivalently the exponential generating function $F_g(x)=\sum_{n\ge0}Z_n[g]x^n/n!$ satisfies
$$
F_g'(x)=F_g(x)\sum_{t\ge1}t\,g(t)\,Z_{t-1}[g]\frac{x^{t-1}}{(t-1)!},\qquad\text{that is,}\qquad F_g=\exp\Bigl(\sum_{t\ge1}t\,g(t)\,Z_{t-1}[g]\frac{x^{t}}{t!}\Bigr). \tag{6.3}
$$

*Proof.* Use (5.1). In a permutation $\sigma$ of $[n]$ let $j+1$ be the spot of the last car $n$. Its capacity is $j+1$: the last car closes the block formed by the $j$ cars to its left. The capacities of the spots to the left depend only on the relative order of the cars there, and so do those to the right, because the last car separates the two sides. Choosing which $j$ cars stand on the left, and the two smaller permutations, gives (6.2). Multiplying by $x^{n-1}/(n-1)!$ and summing gives the first form of (6.3). The series in the exponent is the generating function of the trees weighted by $\Phi_g$: a tree with $t$ vertices is a root, with $t$ possible labels and weight $g(t)$, and a forest on the other $t-1$ labels. $\square$

In the forest, the last car is a root, its subtree is the block on its left, and (6.2) is the statement that a forest is a set of trees and a tree is a root with a forest below it. In the process it says that just before the last car arrives, once the position of the one empty spot and the set of cars parked on its left are given, the street consists of two independent parking processes on the two sides of that spot.

**Proposition 6.5** (the threshold weight: Riccati equation and integrating factor) [proved]. For an integer $k\ge1$ let $F_k(x)=\sum_{n\ge0}Z_n(k)x^n/n!$ and $\Omega_k(x)=\sum_{t=1}^{k-1}(k-t)\,p_{t-1}\frac{x^{t-1}}{(t-1)!}$. Then, as formal power series,
$$
F_k'=kF_k^2-\Omega_kF_k,\qquad F_k(x)=\frac{\eta_k(x)}{1-k\int_0^x\eta_k(u)\,du},\qquad \eta_k(x)=\exp\Bigl(-\sum_{t=1}^{k-1}(k-t)\,\frac{a_t}{t}\,x^t\Bigr),
$$
and for $k\ge2$
$$
\log\eta_{k+1}-2\log\eta_k+\log\eta_{k-1}=-\frac{a_k}{k}\,x^k=-\frac{k^{k-2}}{k!}x^k. \tag{6.4}
$$

*Proof.* For $g=g_k$ one has $t\,g(t)=\min(t,k)$ and $Z_{t-1}(k)=p_{t-1}$ for $t\le k$, so the series in (6.3) is $kF_k-\Omega_k$. The function $1/F_k$ then satisfies a linear equation, which the integrating factor $\eta_k=\exp(-\int \Omega_k)$ solves; $\int_0^x\Omega_k=\sum_{t<k}(k-t)p_{t-1}x^t/t!$ and $p_{t-1}/t!=t^{t-2}/t!=a_t/t$. The second difference in $k$ of the coefficient $(k-t)_+$ is $1$ for $t=k$ and $0$ otherwise. $\square$

The coefficient $a_k/k$ in (6.4) is the normalised number of unrooted labeled trees on $k$ vertices. Identity (6.4) is a property of the truncated linear weights $(k-t)_+$ and holds for any coefficients in place of $a_t/t$; what is specific to the forest is which coefficient appears. The identity does not transfer to $F_k$ itself, because of the denominator in the closed formula.

### 6.4 What happens to a weight when the forest is cut

Under the uniform law the pieces of a decomposition are uniform. Under a weight $\Phi_g$ they are not, for a simple reason: removing the subtree of a vertex $v$ lowers the subtree sizes of all ancestors of $v$ by $t_v$. Reading this backwards gives the rule by which weights pass through the decomposition.

**Proposition 6.6** (attaching a subtree) [proved]. Let $g$ be a weight with values in a field and without zeros (for instance a positive real weight), let $E$ be a rooted forest, $u$ one of its vertices or the virtual root, and $S$ a rooted tree with $s$ vertices on a disjoint label set. Let $F$ be the forest obtained by making the root of $S$ a child of $u$. Then
$$
\Phi_g(F)=\Phi_g(S)\,\Phi_g(E)\prod_{x}\frac{g(t_x+s)}{g(t_x)},
$$
the product being over $u$ and its ancestors in $E$ (excluding the virtual root), the product being indexed by these vertices $x$, with $t_x$ the subtree size in $E$. For the threshold weight $g_k$ the factor of a vertex $x$ is $\max(t_x,k)/\max(t_x+s,k)$; if $s\ge k$ this is $\max(t_x,k)/(t_x+s)$.

*Proof.* Attaching $S$ changes the subtree size of a vertex of $E$ if and only if the vertex is $u$ or an ancestor of $u$, and then by $s$. $\square$

For the uniform law the product is empty of content, the number of ways to attach $S$ to a forest $E$ on $m$ vertices is $m+1$ whatever $E$ is, and this is why, when an edge of a uniform tree is deleted, the two pieces are independent uniform trees once their sets of labels are given (the case of a constant weight in the theorem below). For which weights does this persist?

**Theorem 6.7** (cutting is compatible with exactly two weights) [proved; the analogous characterisation for weights on the degrees is [Pa, Lemma 1]]. Let $w=(w_s)_{s\ge1}$ be a sequence of positive numbers. For a finite label set $A$ let $P^w_A$ be the law on the rooted labeled trees on $A$ with probability proportional to $\prod_vw_{t_v}$. Consider the following property: for every $m\ge2$ and every partition of $[m]$ into non-empty sets $A$ and $B$, if a tree is drawn from $P^w_{[m]}$ and one of its edges, chosen uniformly, is deleted, then conditionally on the two components having vertex sets $A$ and $B$ they are independent with laws $P^w_A$ and $P^w_B$ (the component not containing the old root being rooted at the lower end of the deleted edge). This property holds if and only if either $w_s=c$ for all $s$, or $w_s=c/s$ for all $s$, with a constant $c>0$.

*Proof.* For a rooted tree $\tau$ with $a$ vertices and an integer $b\ge1$ put
$$
G_b(\tau)=\sum_{u\in\tau}\ \prod_{v\ \text{on the path from the root to}\ u}\frac{w_{t_v+b}}{w_{t_v}} .
$$
By Proposition 6.6, if $\tau$ and $\tau'$ are trees on $A$ and $B$ with $a$ and $b$ vertices, the total weight of the trees on $[m]$ from which the deletion of one edge produces the pair $(\tau,\tau')$ is $\prod_vw_{t_v(\tau)}\prod_vw_{t_v(\tau')}\,\bigl(G_b(\tau)+G_a(\tau')\bigr)$: the first term for $\tau'$ attached below a vertex of $\tau$, the second for $\tau$ attached below a vertex of $\tau'$. Every tree on $[m]$ has $m-1$ edges. Hence the property holds if and only if, for every $b$, $G_b(\tau)$ depends on $\tau$ only through its number of vertices $a$; write $\pi_b(a)$ for the common value.

Splitting according to whether $u$ is the root or lies in the subtree $\tau_i$ of a child of the root gives
$$
G_b(\tau)=\frac{w_{a+b}}{w_a}\Bigl(1+\sum_iG_b(\tau_i)\Bigr). \tag{6.5}
$$
Assume the property. Comparing, among the trees with $a+1$ vertices, the one whose root has a single child with a subtree of $a$ vertices and the one whose root has $a$ leaves as children, (6.5) gives $\pi_b(a)=a\,\pi_b(1)$, by induction on $a$. Inserting this into (6.5) for an arbitrary tree with $a$ vertices gives $a\pi_b(1)=\frac{w_{a+b}}{w_a}\bigl(1+(a-1)\pi_b(1)\bigr)$, that is,
$$
\frac{w_{a+b}}{w_a}=\frac{a}{a+\delta_b},\qquad \delta_b=\frac1{\pi_b(1)}-1 .
$$
Write $\delta=\delta_1$. Going from $a$ to $a+2$ in two steps or in one gives $(a+1)(a+\delta_2)=(a+\delta)(a+1+\delta)$ for all $a\ge1$; comparing coefficients, $\delta_2=2\delta$ and $\delta_2=\delta(\delta+1)$, so $\delta\in\{0,1\}$. If $\delta=0$ then $w$ is constant; if $\delta=1$ then $w_{a+1}/w_a=a/(a+1)$ and $w_s=w_1/s$.

Conversely, for constant $w$ one has $G_b(\tau)=a$. For $w_s=c/s$ the claim $G_b(\tau)=a/(b+1)$ follows from (6.5) by induction: $\frac{a}{a+b}\bigl(1+\frac{a-1}{b+1}\bigr)=\frac a{b+1}$. $\square$

The constant weight is the uniform law on rooted labeled trees. For it the property is part of a theorem of Pitman [P99, Theorem 4], which says more: the forest that results from the cut is uniform among the forests with two trees, the sizes of the two pieces included. The weight $c/s$ is, by Lemma 4.5, the law of the shape of a uniform decreasing tree (a random recursive tree), for which the splitting property is well known (it is commonly attributed to Meir and Moon [MM]; that paper was not read and the attribution is not verified here; the property is in any case the case $w_s=c/s$ of the theorem above). For this weight only the conditional statement holds. For example, if a rooted tree on $\{1,2,3,4\}$ is drawn with probability proportional to $\prod_v1/t_v$ and a uniform edge is deleted, the result is the forest in which the vertices $1$ and $2$ are roots and $3,4$ are children of $1$ with probability $7/216$, whereas under the law proportional to $\prod_v1/t_v$ on the forests with two trees this forest has probability $1/33$: the sizes of the pieces are distributed differently (Appendix C, item C4). The threshold weight $g_k(s)=\min(1,k/s)$ is the first of the two weights on subtrees of size at most $k$ and $k$ times the second on larger ones. It interpolates between the two cases in which cutting is harmless, and for $k\ge2$ it is neither: the property holds for trees with at most $k+1$ vertices and fails for trees with $m\ge k+2$ vertices. Indeed, with $b=1$ and $a=m-1\ge k+1$, put $r(t)=w_{t+1}/w_t$, so that $r(t)=1$ for $t<k$ and $r(t)=t/(t+1)$ for $t\ge k$; by (6.5) the tree in which the root has $a-1$ leaves as children has $G_1=a\,r(a)$, the tree in which the root has one child carrying $a-2$ leaves has $G_1=r(a)\bigl(1+(a-1)r(a-1)\bigr)$, and these differ because $r(a-1)<1$. For $m\le k+1$ the only factor different from $1$ is that of the root, which depends only on the sizes. (For $k=2,3,4,5$ the smallest sizes at which the property fails are $4,5,6,7$, also by direct computation; Appendix C, item C4.) So under the capacity-weighted law (W) the pieces of a cut at a uniform edge are not independent members of the same family, and the weights have to be carried through the decomposition by Proposition 6.6; this is what Section 11 does. The cut at the top is different: for every weight $g$, removing the root of a tree drawn with probability proportional to $\Phi_g$ leaves a forest drawn with probability proportional to $\Phi_g$, because the factor of the root depends only on the size, and the trees of such a forest are independent given their vertex sets. This is the content of Proposition 6.4. The decomposition in the order of arrival is thus compatible with every subtree-size weight, and the decomposition at a uniform edge with only two.

### 6.5 The dictionary

The following table places the classical names. The first column is what is done to the object, in its uniform description or, where a row speaks of cars, in its description as a process; the second is the identity that results, the third the name under which the identity is known. Each line is a statement proved or cited in Section 4, in this section, or, for the last line, in Section 8.

| operation | identity | classical name |
|---|---|---|
| count the rooted labeled forests on $n$ vertices | $p_n=(n+1)^{n-1}$, $m^{m-1}$ rooted trees | Cayley's formula; number of parking functions (Theorem 4.1) |
| let the size be random with weight $e^{-m}/m!$ per tree | size law $\mathrm{Bor}(m)=e^{-m}m^{m-1}/m!$ | Borel distribution; critical Poisson Galton–Watson tree (Theorem 4.8) |
| condition on the size | uniform tree, for every mean $0<\lambda\le1$ | conditioned Galton–Watson tree; the size is a sufficient statistic |
| generating function of rooted trees | $T=ze^T$, $T(1/e)=1$ | tree function |
| extract the coefficient for $q$ trees | $[z^m]T^q=\frac qm\frac{m^{m-q}}{(m-q)!}$ | Lagrange inversion; Borel–Tanner law; forests with $q$ trees (Lemma 6.1) |
| stop the process after $t$ cars | block sizes $\propto\prod a_{s_i}$ | Pavlov's representation (Theorem 4.9) |
| let one more car arrive | merge with probability $\propto s_i+s_j$ | additive coalescent (Theorem 4.10) |
| remove the cars in reverse order | block sizes distributed as the tree sizes of uniform forests with $q=1,2,\dots$ trees | the same process of sizes as when the edges of a uniform tree are deleted in uniform random order (Theorem 4.10); the cars themselves are removed in the reverse order of their arrival, not in uniform order (Proposition 4.4(d)) |
| cut out a subtree that hangs at a prescribed vertex | factor $\mathrm{Bor}(\gamma)$ | (Theorem 6.2) |
| cut out a subtree that may hang at any vertex of the piece that remains, a piece of size $\gamma$ | factor $\gamma\,\mathrm{Bor}(\gamma)=\mathrm{Ren}(\gamma)$ for the remaining piece | size-biasing; renewal sequence of the Borel walk; $zT'=T/(1-T)$ |
| follow the ancestors of a uniform vertex | $\Pr(D\ge d)=(N-1)_d/N^d$ | spine decomposition; birthday problem (Corollary 6.3) |
| remove the last car | $Z_n=\sum\binom{n-1}{j}(j+1)g(j+1)Z_jZ_{n-1-j}$ | last-car recursion; exponential formula; Riccati equation (Propositions 6.4, 6.5) |
| forget the roots, or count vertices minus edges | $a_m/m$, $T-T^2/2$ | unrooted trees (Lemma 6.1(d)) |
| let $m\to\infty$ in $\mathrm{Bor}(m)$ | $\mathrm{Bor}(m)\sim(2\pi)^{-1/2}m^{-3/2}$ | Stirling's formula; square-root singularity of $T$ at $1/e$ (Section 8) |

Read by rows, the table lists descriptions of the object (rows 1 and 6 to 8), the normalisation by size (rows 2 to 5, of which rows 2 and 3 are at the same time the third description of the object), and uses of the decomposition at vertices (rows 9 to 12); row 13 belongs to both mechanisms, and row 14 is the asymptotic form of row 2. An overlap between two tools is a place where two rows give the same number. The overlaps met in this document are the following; each is an identity, proved or, for the last member of item 5, cited in the statement named.

1. *Cayley's counts and the Borel masses*: $m^{m-1}=m!\,e^m\,\mathrm{Bor}(m)$, and the powers of $e$ cancel in every formula for a fixed total size (Lemma 6.1(a) and its corollary).
2. *Forests with $q$ trees, the Borel–Tanner law and the block sizes at an intermediate time*: the count $\binom{m-1}{q-1}m^{m-q}$ of forests is $\frac{m!}{q!}[z^m]T^q$, the mass $\mathrm{Bor}^{*q}(m)$ is $e^{-m}[z^m]T^q$, and the blocks of the parking process after $t$ cars have the sizes of the trees of a uniform forest with $q$ trees, that is, of $q$ Borel variables conditioned on their sum (Lemma 6.1(b), Theorem 4.9).
3. *Trees with a marked vertex, the renewal sequence and sequences of trees*: $m^m=m!\,e^m\,\mathrm{Ren}(m)$ and $\mathrm{Ren}(j)=\sum_{i\ge1}\mathrm{Bor}^{*i}(j)$ (Lemma 6.1(a), Corollary 6.3(d)).
4. *The depth of a uniform vertex, the birthday problem and the number of parts of a composition with Cayley weights*: $\Pr(D\ge d)=(N-1)_d/N^d$ and $\Pr(Q\ge j)=(m)_j/m^j$ (Corollary 6.3(c), Lemma B.2).
5. *The merging of parking blocks, the additive coalescent and the deletion of the edges of a uniform tree*: one Markov chain on the multisets of sizes (Theorem 4.10, whose last link, with the deletion of edges, is cited from [AP, Lemma 1]).
6. *A ratio of Cayley counts and a product of Borel and renewal masses*: the expected number of vertices whose subtree has $s$ vertices is at once $\binom ns s^{s-1}(n-s+1)^{n-s}/(n+1)^{n-1}$ (choose the labels of the subtree, a rooted tree on them, a forest on the rest and one of its $n-s+1$ attachment places) and $\mathrm{Ren}(N-s)\,\mathrm{Bor}(s)/\mathrm{Bor}(N)$ (Corollary 6.3(a)).
7. *Unrooted trees*: the number $k^{k-2}=k!\,a_k/k$ of unrooted labeled trees on $k$ vertices appears as the coefficient $a_k/k$ in the identity (6.4) and in the series $T-T^2/2$, and as $k^{k-2}$ in the loss formula (11.2) (Lemma 6.1(d), Proposition 11.3).

The list is of the overlaps that occur in the statements of this document. Whether the earlier research met others was not examined.

## 7. Why the tools recur

Sections 4 to 6 contain the structure. This section draws the conclusion for which it was built. It first states, as a theorem, the expansion of the threshold functional over the vertices above the threshold, which is built from the objects of the dictionary (7.1), then reports the result of testing the account against the list of recurring concepts (7.2), then treats the order-theoretic tools, which are not instances of the structure, and says exactly where they attach to it (7.3), then marks what the structure does not imply (7.4), and finally treats the one exact decomposition that is not obtained from the two mechanisms (7.5).

### 7.1 The skeleton expansion

Let $k\ge1$ and let $g$ be a weight with $g(t)=1$ for $t\le k$; the threshold weight $g_y$ with $k\le y<k+1$ is of this kind. Let $F$ be a forest on $[n]$ with its virtual root $0$. In this section a vertex is called heavy if $t_v>k$ and light otherwise (this is the notion of Section 5.2 for any threshold $y$ with $k\le y<k+1$). Every ancestor of a heavy vertex is heavy, so the heavy vertices together with $0$ form a tree, the *skeleton* of $F$. Each skeleton vertex $u$ carries, besides its heavy children, light children whose subtrees have at most $k$ vertices; $u$ together with these light subtrees is the *bush* of $u$. Put
$$
S_k(z)=\sum_{t=1}^{k}a_tz^t,\qquad \kappa_k(j)=[z^j]\;z\,e^{S_k(z)} .
$$
Then $j!\,\kappa_k(j)$ is the number of rooted labeled trees on $j$ vertices in which the subtree of every child of the root has at most $k$ vertices, and $\kappa_k(j)=a_j$ for $j\le k+1$, because the restriction is then empty.

**Theorem 7.1** (skeleton expansion) [proved]. Let $g(t)=1$ for $t\le k$. Then
$$
\frac{Z_n[g]}{n!}=\sum_{\mathfrak p}\ \frac{1}{|\mathrm{Aut}(\mathfrak p)|}\ \prod_{u\in\mathfrak p}\kappa_k(\gamma_u)\ \prod_{u\ne\varrho}g(t_u), \tag{7.1}
$$
where the sum is over the isomorphism classes of patterns $\mathfrak p$ (Section 6.2) all of whose nodes $u\ne\varrho$ have type child and size $t_u>k$, and $\mathrm{Aut}(\mathfrak p)$ is the group of automorphisms of $\mathfrak p$ preserving the sizes. If $n\le 2k+1$, the patterns that contribute are paths, they have no automorphisms, and every factor $\kappa_k(\gamma_u)$ except that of the last node equals $a_{\gamma_u}$.

*Proof.* Each forest has exactly one skeleton, and the skeleton with its subtree sizes is an occurrence of a unique pattern class of the kind described; it is counted $|\mathrm{Aut}(\mathfrak p)|$ times as an occurrence. In the bijection of the proof of Theorem 6.2, an occurrence is the skeleton of the tree if and only if in every layer all vertices other than the root of the layer are light, that is, if and only if every layer is a tree in which the subtrees of the children of the root have at most $k$ vertices; a vertex of a layer other than its root has its whole subtree inside the layer, because the pattern-children are attached to the root of the layer. The number of such trees on $\gamma$ labels is $\gamma!\,\kappa_k(\gamma)$, and, with the root prescribed to be $0$, it is $(\gamma-1)!\,\kappa_k(\gamma)$. Counting as in Theorem 6.2 gives $n!\prod_u\kappa_k(\gamma_u)$ pairs (forest, occurrence that is its skeleton) for each pattern, and the weight of the forest is $\prod_{u\ne\varrho}g(t_u)$. If $n\le2k+1$, two heavy vertices cannot have disjoint subtrees, so the skeleton is a path; the layers other than the last have at most $N-(k+1)\le k+1$ vertices in total. $\square$

The theorem is the precise form of the explanation. A threshold functional sees a forest only through its skeleton, the vertices whose subtrees are larger than the threshold. Everything outside the skeleton consists of subtrees with at most $k$ vertices, which are arbitrary rooted trees and carry no factor. They enter through the coefficients $\kappa_k$, which are built from Cayley's coefficients $a_t$ with $t\le k$ and equal $a_j$ as long as a bush has at most $k+1$ vertices. The number $Z_n(k')$ is therefore given by the sum (7.1) for every threshold $k'\ge k$, since $g_{k'}(t)=1$ for $t\le k$: the light parts of the forest enter only through the coefficients $\kappa_k$, which are polynomials in $a_1,\dots,a_k$, and the heavy vertices only through their threshold factors. A step $d_{n,k}$ with $k\ge2$ involves the thresholds $k-1$, $k$ and $k+1$, and is obtained in the same way from (7.1) with $k-1$ in place of $k$.

This is what the theorem proves. It does not prove that a computation of the maximum displacement has to pass through this expansion. What can be checked is which statement of this document each route of the earlier research is, and where the numbers of the dictionary enter it; in each case they enter where trees without a factor are counted. The route through outcome permutations is (4.1) with (4.2), which turns the sum over permutations into the sum over forests; in (4.2) with $f(t)=\min(t,k)$ the factor $f(t_v)/t_v$ equals $1$ at every vertex with $t_v\le k$, so the subtrees with at most $k$ vertices are counted as rooted trees without a factor, that is, by Cayley's numbers. The last-car recursion is Proposition 6.4; it removes the root of the last tree, whether or not that root lies above the threshold, and the Cayley numbers are the values $Z_j(k)=p_j$ for $j\le k$, from which the recursion starts. The chains of large subtrees are Corollary 6.3(b), where the law is uniform and every piece is a tree without a factor, and, with the weights, Proposition 11.6, where the parts of the compositions are the bushes above the lowest vertex of the chain; such a bush is a root with a set of subtrees of at most $k$ vertices each, and since it has at most $k+1$ vertices in all, its coefficient $\kappa_k(\gamma)$ is Cayley's $a_\gamma$. The generating functions are Proposition 6.5, where the coefficients $a_t/t$ of $\eta_k$ are Cayley's. A formula such as (4.1) or (6.2) does not display Cayley's coefficients; (7.1) is a closed evaluation of the same number in which they are displayed. Divided by $p_n$ it becomes an expression in Borel masses, by the cancellation of Section 6.1 (each skeleton vertex contributes the factor $\mathrm{Bor}(1)=e^{-1}$ for itself). Where the pieces of a run carry Cayley's coefficients and the factors attached to them do not depend on their individual sizes, summing over the sizes of $q$ pieces with $q$ fixed gives a Borel–Tanner mass (Lemma 6.1(b)), and summing over $q$ as well gives the renewal sequence $\mathrm{Ren}$ (Corollary 6.3(d)). The one derivation of the earlier research that proceeds otherwise, the decomposition along the street, organises the same total differently and is treated in Section 7.5.

The same counting shows why the tools appear several at once. Already the expected number of vertices with a prescribed subtree size $s$, which is $\mathrm{Ren}(N-s)\,\mathrm{Bor}(s)/\mathrm{Bor}(N)$ by Corollary 6.3(a), involves all of them. The subtree is counted by a Cayley number, whose normalised form is the Borel mass $\mathrm{Bor}(s)$. The rest of the tree, to any vertex of which the subtree may be attached, contributes its size times its Borel mass, a term of the renewal sequence. The normalisation by the number of all trees contributes $\mathrm{Bor}(N)$, so that for $s$ close to $n$ the formula contains a ratio of two Borel masses of sizes near $n$, and this is where the asymptotics $m^{-3/2}$ enter.

### 7.2 The test against the recurring concepts

The account was tested concept by concept. This subsection reports the test; the mathematical statements it relies on are those cited in it and in Appendix A, and the report itself is the author's. The list of concepts was drawn from the vocabulary of the earlier research (its glossary and index), from the notes under examination and from the long manuscript; for each concept the forms in which it was used were collected from the sources, and a derivation from Sections 4 to 6 was written or the concept was recorded as not derivable. Appendix A gives the table. The result is as follows.

*Descriptions of the object.* Cayley's counts, the Borel distribution, the critical Boltzmann law, Poisson Galton–Watson trees and their conditioning, the uniform random forest with free or fixed number of trees, Pavlov's representation and the additive coalescent are the three descriptions of Section 4 and the normalisation of Section 6.1. The tree function and Lagrange inversion are the generating-function form of the same normalisation.

*Uses of the decomposition.* The renewal sequence and the Borel walk, the formulas for chains of nested subtrees, the chain that follows the largest subtree downwards, with its transition probabilities, in the range $n\le2k+1$ where the heavy vertices lie on one path, the spine of a marked vertex with the birthday law, the last-car recursion with the exponential formula and the Riccati equation, the identities for the boundary and curvature terms of that range (Proposition 11.6; the recursions by which the earlier notes computed these terms are not used in this document), the transplanting and leaf-attachment identities, and the expressions called Palm expressions in the notes are instances of Theorem 6.2, Proposition 6.4 or Proposition 6.6. In the earlier research two kinds of chain were kept apart, and the test confirms that they must be: a chain of vertices with prescribed subtree sizes is counted by Theorem 6.2 for every $n$, but the count is guaranteed to be a probability only in the range where the sizes exceed $n/2$, in which a vertex with a given subtree size is unique (Corollary 6.3(a)); in that range "the chain of the largest subtrees" is a well-defined random path whose law the counts give, and outside it a count may exceed $1$.

*A third decomposition.* One recurring tool is an exact decomposition of the parking process that is not obtained from the two mechanisms on the history forest: the decomposition of a parking function along the street at its breakpoints (the positions $j$ such that exactly $j$ cars prefer a spot at most $j$) into prime parking functions. It was used in the earlier research for a fixed threshold $k$ and $n$ large. Section 7.5 states what it is and how it is tied to the forest.

*Tools that are not instances.* The order-theoretic tools and the analytic tools are generic techniques. Section 7.3 identifies the two properties of the structure on which the order-theoretic tools depend in this document, and names a third, the total positivity of the array of the numbers of forests [So, Theorem 1.1(a)], which only the earlier research used. The analytic tools use the singularities of the generating functions: the square-root singularity of the tree function (Section 8.1) and, for a fixed threshold, the simple pole of $F_k$ (Section 7.5).

*Models.* Several comparison models of the earlier research (forests grown by uniform attachment, clocks with independent drops, a model with independent Poisson numbers of subtrees of each size) are not the object. The first of them is placed in Appendix A (it is the random recursive forest, the weight $1/s$ of Theorem 6.7); the other two are not defined or examined in this document. The evidence about what the structure does not imply consists of Counterexamples 7.4 and 7.5 (Section 7.4). One further entry of the list, the number of uniformly deleted edges after which all components of a tree are small, is by Theorem 4.10 a functional of the block process read backwards, and was not examined further (Appendix A).

In terms of the working hypothesis from which this document started, namely that one object (the critical Poisson Galton–Watson forest seen through its subtree sizes) and three operations (conditioning on size, marking a vertex, cutting an edge) account for every recurrence: the hypothesis holds in substance and is revised in three points. The object is better described as the history of the parking process, of which the conditioned Galton–Watson forest is one description; this supplies the reason, absent from the hypothesis, why the displacement statistic is a functional of subtree sizes. Marking a vertex and cutting an edge are one decomposition, so there are two mechanisms and not three operations. And the street decomposition is an additional exact decomposition which the hypothesis did not contain.

### 7.3 The order-theoretic tools and the two properties they use in this document

The comparison arguments of the earlier research and of the notes (positive association of cut-point sets, monotone couplings in a parameter, total positivity of certain coefficient arrays, likelihood-ratio orders for the number of pieces) are applications of general theorems to laws on compositions or on sets of cut points. The laws come from the structure: by Theorem 7.1, for $n\le2k+1$ the skeleton is a path (this is the range used in Section 11.4), and the positions at which it is cut into bushes form a subset $S$ of $\{1,\dots,m-1\}$ with weight
$$
\mathcal W(S)=\prod_{\text{gaps}}a_{\text{gap}}\ \prod_{s\in S}\lambda_s, \tag{7.2}
$$
where the gaps are the differences of consecutive elements of $\{0\}\cup S\cup\{m\}$ and the $\lambda_s>0$ are factors attached to the positions. In terms of Theorem 7.1: the lowest skeleton vertex $u_0$, with its subtree, is held fixed, and $m=N-t_{u_0}$ is its deficit, the number of vertices outside its subtree; the elements of $S$ are the deficits $N-t_u$ of the skeleton vertices $u$ strictly between the virtual root and $u_0$; the gaps are the sizes of the layers above the lowest vertex, whose coefficients are Cayley's by the last sentence of the theorem; and $\lambda_s=g(N-s)$. What the general theorems need from this law are two properties of Cayley's coefficients. The correlation inequalities and the comparison of laws with different factors need the log-convexity treated in this subsection. The comparisons of the number of pieces in the likelihood-ratio order (a law $\mu'$ on the integers is larger than $\mu$ in this order if $\mu'(j)/\mu(j)$ is non-decreasing in $j$) need a coupling that adds one cut at a time (Lemma 11.8), which rests on the identity $\sum_{\alpha+\beta=t}\alpha\,a_\alpha a_\beta=(t-1)a_t$, a form of Lemma 6.1(b) for two trees.

**Lemma 7.2** [proved]. The ratio $a_{j+1}/a_j=(1+1/j)^{j-1}$ is strictly increasing in $j\ge1$. Thus $(a_j)$ is log-convex: $a_ja_{j+2}>a_{j+1}^2$.

*Proof.* The derivative of $x\mapsto(x-1)\log(1+1/x)$ is $\log(1+1/x)-\frac{x-1}{x(x+1)}$, and $\log(1+1/x)>\frac1{x+1}>\frac{x-1}{x(x+1)}$ for $x>0$. $\square$

**Proposition 7.3** (lattice condition) [proved]. Let $(a_j)_{j\ge1}$ be any positive sequence. The weight (7.2) satisfies $\mathcal W(S\cup S')\,\mathcal W(S\cap S')\ge\mathcal W(S)\,\mathcal W(S')$ for all $m\ge1$, all positive $\lambda$ and all $S,S'\subseteq\{1,\dots,m-1\}$ if and only if $(a_j)$ is log-convex in the weak sense, $a_ja_{j+2}\ge a_{j+1}^2$ for all $j\ge1$.

*Proof.* On the Boolean lattice it suffices to verify the inequality for $S\cup\{i\}$ and $S\cup\{j\}$ with $i<j$ not in $S$. If an element of $S$ lies between $i$ and $j$, the two insertions concern different gaps and equality holds. Otherwise let the gap containing $i$ and $j$ be divided by them into lengths $u,v,w$; the factors $\lambda$ cancel and the inequality reads $a_v\,a_{u+v+w}\ge a_{u+v}\,a_{v+w}$, which holds for all $u,v,w\ge1$ if and only if $a_{j+1}/a_j$ is non-decreasing. $\square$

By the FKG inequality [FKG, Proposition 1], a strictly positive law with the property of Proposition 7.3 makes increasing functions of $S$ positively correlated. Raising the factors makes $S$ stochastically larger: if $\lambda'_s\ge\lambda_s$ for all $s$, then the law with the factors $\lambda'$ has, with respect to the law with the factors $\lambda$, a density proportional to $\varpi(S)=\prod_{s\in S}\lambda'_s/\lambda_s$, which is non-decreasing in $S$; so for every non-decreasing function $\phi$ of $S$, $\mathbb E_{\lambda'}\phi=\mathbb E_\lambda[\phi\varpi]/\mathbb E_\lambda[\varpi]\ge\mathbb E_\lambda\phi$ by the positive correlation of $\phi$ and $\varpi$ under the law with the factors $\lambda$. So for the history forest, where the gap weights are Cayley's, cutting more makes further cuts more likely, uniformly in the position-dependent factors. This is the common source of the positive-association statements of the notes.

The same property works against the most direct positivity arguments. A kernel of the form $(n,t)\mapsto a_{n-t}$ (with $a_j=0$ for $j\le0$) is totally positive of order $2$ if and only if $(a_j)$ is log-concave [proved]: for rows $n<n'$ and columns $t<t'$ the minor of order $2$ is $a_xa_y-a_pa_q$ with $x=n-t$, $y=n'-t'$, $p=n-t'$, $q=n'-t$, so that $p<x,y<q$ and $x+y=p+q$, and it is non-negative for all such indices exactly when the positive sequence $(a_j)$ is log-concave. So kernels built in this way from Borel masses are not totally positive of order $2$; the earlier research recorded several failures of total positivity of exactly this origin. (The rows themselves are not log-concave either; Section 11.8 records this as a fact, without deriving it from the present one.) The Harris inequality for product measures and Jensen's inequality, which were also used, need nothing from the structure. A third property of the forest numbers, the total positivity of the array of the numbers of forests by their number of trees [So, Theorem 1.1(a)], was used in the earlier notes for a comparison with equal factors at all cut points; it is not used in this document.

### 7.4 What the structure does not imply

The account explains why the tools occur. It does not make the rows unimodal. The first of the two exact computations below shows that no argument using only the structure can, since the structure covers spare spots (Section 10.3); the second shows the same for arguments that use only the representation by a conditioned Galton–Watson forest with independent uniform marks.

**Counterexample 7.4** (spare spots) [counterexample; Appendix C, item C9]. In this counterexample, as in Section 10.3, the letter $r$ denotes the number of empty spots of the circle on which the process runs, not the deficit $n-k$ of Section 3.2. Let $m$ cars park on $m+r-1$ spots in a row, by the same rule, and count the lists on which all cars park by their maximum displacement. For $r=1$ this is the row of $m$. By Section 10.3 the displacements are again independent uniform marks on the subtree sizes of a random forest on the cars, in which every tree carries the weight $r$: the trees are distributed among $r$ virtual roots, one for each empty spot (the $r-1$ spare ones and the spot $m+r$ of the circle), and the trees attached to one virtual root form, together with it, one block of the circle process stopped when $r$ blocks remain; the sizes of these blocks follow the law (Q). For $m=121$ and $r=5$ the resulting sequence is not unimodal: it increases up to $\ell=56$, decreases to $\ell=60$, increases to $\ell=65$ and decreases afterwards. For $r\le5$ and $m\le121$ this is the only pair $(r,m)$ at which the sequence is not unimodal. It refutes the analogue of Conjecture P for four spare spots at $m=121$; it does not bear on Conjecture P itself.

**Counterexample 7.5** (another offspring law) [counterexample; Appendix C, item C9]. Replace the uniform random forest by the forest formed by the two subtrees of the root of a uniformly random full binary plane tree with $n+1$ vertices ($n$ even), and let the maximum be that of $\lfloor U_vt_v\rfloor$ over its vertices, as in Corollary 4.7. For $n=8$ the probabilities of the values $0,\dots,6$ are $\frac{31}{2205},\frac{31}{315},\frac{589}{2205},\frac{47}{245},\frac{11}{49},\frac{5}{49},\frac5{49}$, which decrease from the third to the fourth and increase from the fourth to the fifth; the sequence is not unimodal for any even $n$ from $8$ to $20$. Here the object is a conditioned Galton–Watson forest with a different offspring law, and the statistic is the same functional of the subtree sizes (Section 10.5 says which parts of Sections 5 and 6 carry over).

The earlier research examined further comparison models and reported unimodality in some and failures in others; those models and results are not reproduced or used in this document. What distinguishes the laws with unimodal rows from the others is not known. For the present purpose the conclusion is the following. If the rows of Conjecture P are unimodal, as the conjecture asserts and as the computed rows with $n\le300$ are, this is a property of the particular law (U) with one empty spot, not of the class of objects to which it belongs. The two questions separated in Section 1 are indeed different questions.

### 7.5 The decomposition along the street

A *breakpoint* of a parking function $\alpha$ of length $n$ is an integer $j\in\{0,\dots,n\}$ such that exactly $j$ cars prefer a spot in $\{1,\dots,j\}$; the cars preferring the spots between two consecutive breakpoints park exactly on those spots. A parking function of length $n\ge1$ with no breakpoint other than $0$ and $n$ is *prime*.

**Proposition 7.6** (street decomposition) [proved; classical: [GS, Section 10] for the decomposition; the count is the case $u=1$ of [GS, Corollary 10.3]]. Cutting a parking function at its breakpoints represents it uniquely as a sequence of prime parking functions on consecutive intervals of spots, with the cars distributed among the intervals, and every car keeps its displacement. Hence, for every $k\ge1$, with $C_k(x)$ the exponential generating function of the prime parking functions with $M<k$,
$$
F_k(x)=\sum_{n\ge0}Z_n(k)\frac{x^n}{n!}=\frac{1}{1-C_k(x)},
$$
and without restriction $e^{T(x)}=1/(1-C_\infty(x))$, that is, $C_\infty=1-e^{-T}$; the number of prime parking functions of length $m\ge1$ is $(m-1)^{m-1}$ (equal to $1$ for $m=1$).

*Proof.* Let $j$ be a breakpoint. A spot in $\{1,\dots,j\}$ can only be taken by a car that prefers a spot at most $j$, there are exactly $j$ such cars, and all $n$ spots are taken in the end; so these $j$ cars take exactly the spots $1,\dots,j$, and the other $n-j$ cars take the spots $j+1,\dots,n$. The first group parks as it would on a street of length $j$, and the second as it would on a street of length $n-j$, since a car of one group never meets a car of the other on its way. Iterating gives the decomposition, and the converse construction is clear. The maximum displacement of $\alpha$ is the maximum over its prime pieces, which gives the first identity; the second is the case without threshold, by (6.3) with $g=1$, and $[x^m](1-e^{-T})=(m-1)^{m-1}/m!$ by Lagrange inversion. $\square$

So the generating function of the rows has two exact factorisations: as a set of trees (Proposition 6.4), which comes from the history in time, and as a sequence of prime pieces, which comes from the street. The places at which the second cuts the street do not depend on the order of arrival, and it cuts the street into smaller intervals than the first, in the following sense.

**Proposition 7.7** [proved]. Every tree of the history forest occupies an interval of spots that is a union of consecutive prime pieces.

*Proof.* The trees of $\Psi(\sigma)$ are the intervals that end at the spots $i$ with $\sigma_i>\sigma_j$ for all $j>i$. Let $i$ be such a spot. Every car parked to the right of $i$ arrived before the car $\sigma_i$, at a time when spot $i$ was empty; it cannot have passed an empty spot, so it preferred a spot to the right of $i$. Hence exactly $i$ cars prefer spots at most $i$, and $i$ is a breakpoint. $\square$

The street decomposition is the tool for the regime of a fixed threshold $k$ and large $n$. There $F_k$ has a simple pole at a positive number $\rho_k$ with $C_k(\rho_k)=1$, and $C_k(\rho_kx)$ is the generating function of a probability law on the positive integers [proved]. Indeed, by Proposition 6.5, $F_k=\eta_k/(1-k\int_0^x\eta_k)$ with $\eta_k$ entire and without zeros, so $F_k$ is meromorphic; its coefficients $Z_n(k)/n!$ are at least $1$, so its radius of convergence is at most $1$, and since the coefficients are non-negative the singularity of smallest modulus is a positive zero $\rho_k$ of $1-k\int_0^x\eta_k$ (Pringsheim's theorem [FS, Theorem IV.6]); the zero is simple because the derivative there is $-k\eta_k(\rho_k)\ne0$. Finally $C_k=1-1/F_k=1-(1-k\int_0^x\eta_k)/\eta_k$ is entire with non-negative coefficients and $C_k(\rho_k)=1$. Under the change of normalisation $x\mapsto\rho_kx$ the prime pieces form a renewal process: pieces with independent lengths of this law are laid one after another, and $\rho_k^{\,n}Z_n(k)/n!$, the coefficient of $x^n$ in $F_k(\rho_kx)=\sum_{i\ge0}C_k(\rho_kx)^i$, is the probability that some partial sum of the lengths equals $n$. This is the first mechanism (a change of normalisation by size) applied to the sequence decomposition, and it is the one place where the earlier research used a normalisation other than the critical one. This document does not develop that regime further.

## 8. The exponents $3/2$ and $2/3$

Two exponents accompanied the tools everywhere: Borel masses decay like $m^{-3/2}$, and the maximum displacement falls short of $n$ by an amount of order $n^{2/3}$. The first is Stirling's formula applied to Cayley's coefficients. The second is connected with the first through the structure: one side of it is proved here, and the exact scale with its limit law is a theorem of Petersson, whose proof follows the largest block of the process (Remark 8.4).

### 8.1 The exponent $3/2$

**Lemma 8.1** (Stirling's formula with a remainder) [proved, from Stirling's formula $m!\sim\sqrt{2\pi m}\,(m/e)^m$, for which see [FS, (32), p. 37, with a proof in Appendix B.6]]. For every integer $m\ge1$ write $m!=\sqrt{2\pi m}\,(m/e)^me^{\varepsilon_m}$. Then $0<\varepsilon_m<\frac1{12m}$ and $\varepsilon_m$ is decreasing in $m$. Consequently
$$
\mathrm{Bor}(m)=\frac{e^{-\varepsilon_m}}{\sqrt{2\pi}\,m^{3/2}},\qquad \mathrm{Ren}(m)=\frac{e^{-\varepsilon_m}}{\sqrt{2\pi m}},\qquad e^{-1/12}<e^{-\varepsilon_m}<1,
$$
the sequence $\mathrm{Bor}$ is strictly decreasing, and $1<\mathrm{Bor}(m)/\mathrm{Bor}(m')\le(m'/m)^{3/2}$ for $m<m'$.

*Proof.* From the definition, $\varepsilon_m-\varepsilon_{m+1}=(m+\frac12)\log(1+\frac1m)-1$. With $u=1/(2m+1)$ one has $\log(1+\frac1m)=\log\frac{1+u}{1-u}=2\bigl(u+\frac{u^3}3+\frac{u^5}5+\dots\bigr)$ and $m+\frac12=\frac1{2u}$, so
$$
0<\varepsilon_m-\varepsilon_{m+1}=\frac{u^2}3+\frac{u^4}5+\dots<\frac{u^2}{3(1-u^2)}=\frac1{12m(m+1)}=\frac1{12m}-\frac1{12(m+1)} .
$$
Thus $\varepsilon_m$ is decreasing and $\varepsilon_m-\frac1{12m}$ is increasing. By Stirling's formula $\varepsilon_m\to0$; hence $\varepsilon_m>0$ and $\varepsilon_m-\frac1{12m}<0$ for every $m$. The formulas for $\mathrm{Bor}$ and $\mathrm{Ren}$ are the definitions with $m!$ written in this form, and $e^{-1/12}<e^{-\varepsilon_m}<1$. Finally $\mathrm{Bor}(m+1)/\mathrm{Bor}(m)=e^{-1}(1+1/m)^{m-1}<1$, and for $m<m'$ the ratio $\mathrm{Bor}(m)/\mathrm{Bor}(m')=(m'/m)^{3/2}e^{\varepsilon_{m'}-\varepsilon_m}$ is at most $(m'/m)^{3/2}$ because $\varepsilon$ is decreasing. $\square$

The bounds $\frac1{12m+1}<\varepsilon_m<\frac1{12m}$ are commonly attributed to Robbins [Rob]; that note was not read for this document, and the attribution is not verified here. Only the upper bound and the monotonicity, proved above, are used.

In the language of generating functions the same fact is the square-root singularity of the tree function, $T(z)=1-\sqrt{2(1-ez)}+O(1-ez)$ as $z\to1/e$ [FS, Section II.5 and Chapter VI]. The analytic tools of the earlier research (contour integrals around this singularity, the Airy-type functions that arise when a saddle point approaches it) are ways of extracting asymptotics from it, and they use the structure through this expansion. (For a fixed threshold $k$ and large $n$ the relevant singularity is a different one, the simple pole of $F_k$ of Section 7.5.) The exponent $3/2$ is thus the exponent of the size of a critical tree, and $1/2$ is the exponent of the renewal sequence: $\sum_{j\le q}\mathrm{Ren}(j)$ is of order $\sqrt q$.

### 8.2 The scale $n^{2/3}$: what is proved here

For $1\le q\le n$ let $\mathsf H_q$ be the number of cars with displacement at least $n-q$ in a uniform random parking function of length $n$; the event $M\ge n-q$ is the event $\mathsf H_q\ge1$.

**Proposition 8.2** (the number of cars near the top) [proved]. For $1\le q\le n/2$,
$$
\mathbb E \mathsf H_q=\sum_{j=1}^{q}\frac{\mathrm{Ren}(j)\,\mathrm{Bor}(N-j)}{\mathrm{Bor}(N)}\cdot\frac{q+1-j}{N-j},\qquad \frac{q^{3/2}}{6N}\ \le\ \mathbb E \mathsf H_q\ \le\ \frac{8\,q^{3/2}}{N},
$$
and as $q\to\infty$ with $q/n\to0$, $\mathbb E\mathsf H_q\sim\frac23\sqrt{\frac2\pi}\,\frac{q^{3/2}}{n}$. Consequently $\Pr(M\ge n-q)\le 8q^{3/2}/N$: the deficit $n-M$ exceeds $\epsilon n^{2/3}$ with probability at least $1-8\epsilon^{3/2}$.

*Proof.* By Theorem 4.6(b), $\mathbb E\mathsf H_q$ is the expectation over the uniform forest of $\sum_v\Pr(D_v\ge n-q\mid F)=\sum_v (t_v-n+q)_+/t_v$. Grouping the vertices by $t_v=N-j$ and using Corollary 6.3(a) gives the formula. By Lemma 8.1, $1\le\mathrm{Bor}(N-j)/\mathrm{Bor}(N)\le(N/(N-j))^{3/2}$ and $\frac1N\le\frac1{N-j}\le\frac1N\cdot\frac N{N-q}$, so $\mathbb E\mathsf H_q$ lies between $\Sigma/N$ and $(N/(N-q))^{5/2}\Sigma/N$ with $\Sigma=\sum_{j=1}^q\mathrm{Ren}(j)(q+1-j)$. Since $x\mapsto(q+1-x)x^{-1/2}$ is decreasing, $\Sigma\le(2\pi)^{-1/2}\int_0^q(q+1-x)x^{-1/2}dx=(2\pi)^{-1/2}\bigl(\frac43q^{3/2}+2q^{1/2}\bigr)\le\frac{10}{3\sqrt{2\pi}}q^{3/2}$, and $\Sigma\ge\frac{e^{-1/12}}{\sqrt{2\pi}}\,q^{-1/2}\sum_{j=1}^q(q+1-j)\ge\frac{e^{-1/12}}{2\sqrt{2\pi}}q^{3/2}$. With $(N/(N-q))^{5/2}\le2^{5/2}$ this gives the two bounds; the asymptotic statement follows from $\mathrm{Ren}(j)\sim(2\pi j)^{-1/2}$ and $\int_0^q(q-x)x^{-1/2}dx=\frac43q^{3/2}$. The last assertion is the bound of a probability by an expectation. $\square$

The proof shows the mechanism. A car can have displacement at least $n-q$ only if the block it closes has at least $n-q+1$ spots, that is, lacks at most $j\le q$ of the $N$ spots. Blocks this large are nested: they are the states of the one giant block at those moments, near the end of the process, at which a car lands in it and closes it. (A car that lands in a small block next to the giant block also enlarges the giant block, but the block it closes is the small one.) The expected number of them with deficit exactly $j$ is $\mathrm{Ren}(j)\,\mathrm{Bor}(N-j)/\mathrm{Bor}(N)$ by Corollary 6.3(a); for $j$ small compared with $n$ this is close to $\mathrm{Ren}(j)$, of order $j^{-1/2}$, so about $\sqrt q$ of them have deficit at most $q$. The renewal sequence of the Borel walk appears here for the following reason. The vertices of the chain are each the child of the preceding one, and by Corollary 6.3(b), with the type child, the probability that the chain has prescribed deficits $j_1<\dots<j_i$, with $j_i<N/2$, and no further vertex of deficit at most $j_i$ is $\mathrm{Bor}(j_1)\,\mathrm{Bor}(j_2-j_1)\cdots\mathrm{Bor}(j_i-j_{i-1})$ times the ratio $\mathrm{Bor}(N-j_i)/\mathrm{Bor}(N)$ [proved: vertices with deficits below $N/2$ are nested and have distinct sizes, so the pattern of Corollary 6.3(b) occurs at most once and its expected number is a probability; the vertices lying between two vertices of the chain belong to the chain]. So, read from the end of the process backwards, the deficits of the giant block at its successive closings are the partial sums of independent Borel steps, up to that ratio; and the probability that such a walk visits $j$ is $\mathrm{Ren}(j)$ (Corollary 6.3(d)). The steps are the numbers of spots that the giant block gains between two of its closings. They are not the sizes of the small blocks present at one moment, which for finite $N$ have a different joint law (Theorem 4.9), although their total is the same deficit. A car closing a block of deficit $j$ has a displacement of at least $n-q$ with probability $(q+1-j)/(N-j)$, which is about $(q-j)/n$ when $q-j$ is large. The product of the number of chances, $\sqrt q$, and the size of each chance, $q/n$, is $q^{3/2}/n$, which is of order $1$ when $q$ is of order $n^{2/3}$. The same mechanism, the largest block and the items removed from it, carries Petersson's proof of the limit law (Remark 8.4).

### 8.3 The limit law

**Theorem 8.3** (Petersson) [proved; cited: [Pet, Theorem 5.1], with the limit variable described by [Pet, Theorem 4.7], which is [JP, Corollary 2.4]; transferred to parking functions by Theorem 4.1]. Let $M_n$ be the maximum displacement of a uniform random parking function of length $n$. Then $(n+1-M_n)/(n+1)^{2/3}$ converges in distribution to a random variable $X>0$ with
$$
\Pr(X>x)=\mathbb E\exp\bigl(-x^{3/2}\mathcal B\bigr),\qquad \mathcal B=\int_0^1\sup_{0\le s\le t}B(s)\,dt,
$$
where $B$ is a standard Brownian motion.

Petersson's theorem is stated for linear probing hashing on a circle of $m$ cells with $m-1$ items, conditioned on the last cell remaining empty (the displacements have the same law without this conditioning); by Theorem 4.1 this is the uniform parking function of length $n=m-1$. In the source the limit law reads $\Pr(Y\le z)=1-\psi(z^{3/2})$ with $\psi(s)=\mathbb E\,e^{-s\mathcal B}$ the Laplace transform of $\mathcal B$ (there denoted $A$), which is the formula above. Explicitly [JP, Corollary 2.4],
$$
\psi(s)=\frac1{\Gamma(2/3)}\sum_{j\ge0}\frac{\Gamma(j+\frac23)}{\Gamma(\frac{3j}2+1)}\Bigl(-\frac{3\sqrt2}{4}\,s\Bigr)^{j},
$$
a series that converges for every complex $s$. In the summary of Petersson's thesis the same statements are numbered Theorem 2.1 and Corollary 2.11.

**Remark 8.4** (how the limit law is proved, and what the structure adds to it) [the statements attributed to [Pet] are proved there and are cited; the displayed identity is (4.4), proved; the sentences that relate the two are explanation and carry no status]. Petersson's proof of Theorem 8.3 follows the giant block. The items are removed in the reverse order of their arrival, and an item is called *marked* if it belongs to the largest block at the moment of its removal. The proof has three steps.

First, the deficit of the largest block, as a process in the number of items removed, converges after rescaling to the stable subordinator of index $\frac12$ [Pet, Theorem 3.2, proved with Lemmas 3.3 to 3.5; the distributional input is a theorem of Pavlov on the largest tree of a random forest, quoted there as Theorem 3.1]. The inverse of this subordinator has the law of the running maximum of a Brownian motion [Pet, pp. 471–472, where a textbook is cited for it].

Second, given the path of the sizes of the largest block, the events that the successive marked items have a displacement of at least $m-zm^{2/3}$, in a table of $m$ cells, are independent, each with probability $(\eta'-m+zm^{2/3})_+/\eta$, where $\eta$ and $\eta'$ are the sizes of the largest block before and after the removal (the independence is asserted there in one sentence); the number of these events that occur is then approximated by a Poisson variable through Le Cam's inequality [Pet, Lemma 4.2 and its proof, pp. 468–470].

Third, the number of items with such a displacement converges in distribution to a variable that, given the limit process $(\mathsf S_t)$, is Poisson with the random parameter $\int_0^\infty(z-\mathsf S_t)_+\,dt$, and this parameter has the law of $z^{3/2}\mathcal B$ [Pet, Theorems 4.1 and 4.5 and pp. 471–472]; and the maximum displacement is at least $m-zm^{2/3}$ exactly when this number is positive [Pet, proof of Theorem 5.1].

Let $q<n/2$. In the terms of this document, the marked items that can have a displacement of at least $n-q$ are then the vertices $v$ with $t_v>n-q$, that is, the chain of the giant block. Given the forest, the marks of the vertices are independent, so by (4.4)
$$
\Pr(M<n-q)=\mathbb E\prod_{v:\ t_v>n-q}\Bigl(1-\frac{t_v-n+q}{t_v}\Bigr)
$$
for every $n$ and every integer $q$ with $0\le q\le n-1$ (this needs no restriction on $q$; for $q=n$ both sides vanish), and for $q<n/2$ the product is over that chain. The second step of the proof is the form which this identity takes for $q$ of order $n^{2/3}$, with the conditioning on the sizes of the largest block in place of the conditioning on the forest. For $q<n/2$ the two conditional probabilities are consistent: the one of the proof is the one of the identity averaged over the information that the sizes of the largest block do not contain, namely which of the two parts the removed item closed. Only the case $\eta'>n-q$ matters, and then $\eta'>N/2$, so the larger of the two parts into which the removal divides the block is the largest block after the removal. Given the sizes $\eta$ and $\eta'$, the removed item closed that part with probability $\eta'/\eta$, because a car lands in a block with probability proportional to its size and the two orders of the parts are equally likely beforehand (Lemma 4.2 and the last assertion of Theorem 4.9); in that case $t_v=\eta'$ and its displacement reaches the threshold $n-q$, which stands for $m-zm^{2/3}$, with probability $(\eta'-n+q)/\eta'$, the factor of the identity. If it closed the smaller part, which has at most $n/2<n-q$ spots, its displacement cannot reach the threshold. The product $(\eta'-n+q)_+/\eta$ is the probability used in the second step. The first step has its discrete counterpart in Corollary 6.3(b): the deficits $N-t_v$ along the chain form a renewal sequence with Borel steps, up to the factors $\mathrm{Bor}(N-j)/\mathrm{Bor}(N)$, and the tail of the Borel law, $\sum_{m>j}\mathrm{Bor}(m)\sim\sqrt{2/\pi}\,j^{-1/2}$ by Lemma 8.1, has the exponent $\frac12$ of that subordinator. Proposition 8.2 is the statement at the level of first moments: the limit variable of the third step has expectation $\frac{4}{3\sqrt{2\pi}}z^{3/2}$ [Pet, Corollary 4.10], and $\frac{4}{3\sqrt{2\pi}}=\frac23\sqrt{2/\pi}=\mathbb E\mathcal B$ is the constant of Proposition 8.2.

So the limit law, with a proof along the giant block, is Petersson's. What this document adds are statements for finite $n$ that were not found in that paper, which was read in full (rows L12-6 and L12-7 of the table): the identity (4.4) written as an expectation over the uniform forest, for all $n$ and $k$; the paper describes, in the running text of its Section 2, the backward fragmentation in which the displacement of each removed item is uniform on its left block, from which a product formula over the fragmentation follows at once, but it writes no such formula, builds no forest, and uses the conditional probabilities only for marked items in the window (p. 469); the renewal description of the chain; and the exact formula and the two-sided bounds of Proposition 8.2, where the paper has the expectation of the limit variable. The paper contains no statement on the individual probabilities $\Pr(M=k)$ or on their differences (row L12-8).

The limit law gives the scale and the limiting distribution function of the row, not the comparison of two neighbouring terms: a sequence of distributions can converge to a unimodal limit without being unimodal.

## 9. What is whose: the structure and the known theories

Almost every statement of Sections 4 to 8 is classical or a short step from a classical result, and this section says which is which. It goes through the object (9.1), the two mechanisms (9.2) and the tools attached from outside (9.3), names for each statement the place in the literature where it or its nearest relative is found, and then lists what this document adds, together with the literature searches on which the word "adds" rests (9.4). The statements about the sources are taken from the table of attributions that accompanies the document; where a source was read in a preprint or report version, the table says so, and where a source could not be read the citation is marked here.

### 9.1 The object

*Counting and the circle.* The number $(n+1)^{n-1}$ of parking functions is usually attributed to Konheim and Weiss [KW] (not read for this document). The circular argument of Theorem 4.1 is Pollak's; it is given, with this attribution, in [FR, Section 2, p. 13]. The same argument with $r$ empty spots gives the count $r(m+r)^{m-1}$ of Proposition 10.3, which is in [KY, Theorem 2.2] (there credited to Pitman and Stanley).

*The parking functions with a given outcome.* The product formula of Theorem 4.3 without threshold is attributed to Konheim and Weiss by Celano et al., who prove the form with threshold: [CEHHMPU, Section 4.1, (6)–(8)], with the refinement by total displacement in [CEHHMPU, Theorem 4.3], which is the first equality of Proposition 10.1(a). The description of the lists with a given outcome, and the product formula without threshold, are also [GL, Lemma 2.5]. 

*The history forest.* Parts (a) to (c) of Proposition 4.4 are in the paper of Guedes de Oliveira and Las Vergnas; part (d), which ties the forest to the blocks at earlier times, was not found there. Their map $\varphi$ sends the outcome permutation to the decreasing tree obtained when one does "just connect each vertex to the next greater vertex" on its right [GL, Lemma 3.2], which is the forest $\Psi(\sigma)$ of Section 4.2 with its virtual root, and from their Lemma 2.5, formula (2.1), together with their Lemma 3.3 it follows that the number of displacements available to a car is the number of its descendants in that tree plus one [GL, Lemma 2.5 and Lemma 3.3]; in their words this idea "is the crux of our construction. It is implicit in [Shin's paper], but we believe it was unobserved before" [GL, p. 5]. The two lemmas give the count; the paper does not state it in one sentence and does not use the words subtree size. The same tree occurs in the paper of Kenyon and Yin, as an auxiliary tree in which the parent of a car is the first later car to its right in the outcome, with the rule that the displacement of a car plus one is the rank of a label within the subtree of its vertex [KY, Section 2.4]; they present it as an extension of a construction in Knuth's book ([Kn3], Section 6.4 of the 1998 edition, not read for this document). The tree may therefore be older than the sources read here. The hook length formula of Lemma 4.5 is classical: it is the case of all vertices of [GS, Lemma 2.1], where it is credited to Knuth [Kn3, Exercise 20, p. 70] (the book was not read for this document).

*The displacements as marks on the forest.* Theorem 4.6 is known in bijective form. Shin constructs a bijection between rooted labeled forests and parking functions under which the number of inversions at a vertex (the number of its descendants with smaller label) is the displacement of the corresponding car, and the number of trees is the number of cars that leave no empty spot to their right [Sh, Lemma 2 and Theorem 3]; Guedes de Oliveira and Las Vergnas give another such bijection [GL, Theorem 3.4 and Remark 3.5]. For a uniform labeling of a fixed forest the numbers of inversions at the vertices are independent and uniform on $\{0,\dots,t_v-1\}$; this is the joint law of Lemma 4.5, read with the order of the labels reversed, and it is proved there. No source was found for it in this form among those read (row L4-16 of the table; Section 9.4, item 1). Part of it is known: [GS, Lemma 2.1] gives, for every set $S$ of vertices, the probability $\prod_{v\in S}1/t_v$ that no vertex of $S$ has an inversion, that is, the mutual independence of the events "no inversion at $v$"; its case of all vertices is the hook length formula, and its proof by a cyclic relabeling contains the mechanism for the general case. The full joint law, independent and uniform on $\{0,\dots,t_v-1\}$, was not found. The generating function of the total number of inversions that follows from the joint law is known: it is quoted in [CGG2, Theorem 1.1, p. 3] as Theorem 1.3 of [BW], a paper that could not be read and that may contain more (Section 10.1). Combined with either bijection, the joint law gives the law of the multiset of displacements stated in Theorem 4.6(b); that route is not carried out here, and the proof of Section 4.2 does not use the bijections. Neither paper states the result in probabilistic form or treats the maximum. An older relative is Kreweras's theorem [Kr, Théorèmes I and II], which in the later formulation says that the total displacement of parking functions is equidistributed with the number of inversions of labeled trees (Section 10.1); the correspondence of Chassaing and Marckert [CM, Proposition 4.1] between parking functions and trees through breadth-first search carries the total displacement to the area under the search walk, and Kenyon and Yin extend it to $m$ cars on $n$ spots [KY, Theorems 2.3 and 2.4]. The proof of Theorem 4.6 given in Section 4.2, by the hook length formula and without a bijection on parking functions, was not found in these sources.

*The conditioned Galton–Watson tree.* Theorem 4.8 is [J12, Example 10.2]: the conditioned Galton–Watson tree with offspring law $\mathrm{Po}(1)$ is, after forgetting the order of the children and labeling at random, the uniform rooted labeled tree, and "any other Poisson distribution yields an equivalent weight sequence, and thus the same conditioned Galton–Watson tree"; the size law is the Borel distribution [J12, (10.10) and (12.29)]. The statement is older than the survey: for the Poisson law of mean $1$ it is a remark of Aldous [Ald, remark after Lemma 9, p. 242], and Pitman states it for every mean $0<\lambda\le1$ and attributes it to Aldous, with references to further authors [P99, Section 4.2]. The invariance under the change $w_k\mapsto ab^kw_k$ of the weights is [J12, Section 4, (4.1)–(4.3)]; the reading of it as a statement about a sufficient statistic, in Section 4.3, is a gloss of this document. The forest obtained by removing the root, and forests with a given number of trees, are treated in [J12, Examples 12.6 and 12.8].

*The displacement of a car.* That a car's displacement is uniform on the block in which it lands (Lemma 4.2) is in Petersson's paper: removing the last item from an almost full table splits it into a left and a right block, the removed item "must have targeted one of the cells in the left block", uniformly, and the procedure is repeated inside the blocks [Pet, Section 2, pp. 457–458, in the running text]. The same section states that a new item targets a block with probability proportional to its size [Pet, p. 457]. This backward fragmentation is the description of the object as a process, together with its marks. In Sections 3 to 5 of the paper the event that the maximum displacement is at least $m-zm^{2/3}$ is analysed through conditionally independent events along the largest block [Pet, Lemma 4.2]; Remark 8.4 describes that proof. The forest with marks on its subtree sizes, and an exact identity for $\Pr(M<k)$ valid for all $n$ and $k$ such as (4.4), were not found in the paper, which was read in full (rows L9-11 and L12-6). The paper asserts a correspondence between confined tables and rooted forests and says that its construction is not needed [Pet, pp. 458–459]. For the displacement of a single car the same facts are in an earlier paper of Janson, for a table with any number of keys: the insertion of a key is an unsuccessful search in the table built so far [J05, (34), p. 195]; given the table, the number of starting cells from which such a search has displacement $k$ is the number of blocks longer than $k$ [J05, (4), p. 181]; and the block lengths are Borel variables conditioned on their sum [J05, p. 183, with Lemma 3.1, quoted there from an earlier paper of the same author]. Proposition 10.4 follows from these three statements by one summation and one expectation. That paper prints the limit law and two exact moments of the displacement of an unsuccessful search [J05, Theorem 4.5 and Section 6], and the exact law of the displacement of a key chosen at random from the finished table [J05, Theorem 7.2], which is also [Vi, Theorem 5.1, (33)]; it does not print the formula of Proposition 10.4, and it has no statement on the maximum displacement or on the joint law of all displacements (rows L13-2, L13-4 and L13-5; both papers were read in full).

*The blocks at an intermediate time.* For the parking blocks themselves, the law of the block sizes at every time, as Borel variables conditioned on their sum, is stated in [J05, p. 183, with Lemma 3.1], where it is quoted from an earlier paper of the same author, and, without proof, in [Pet, Section 2, remark on p. 459], after a construction that the paper refers to Pavlov's book. The count in the proof of Theorem 4.9 is [KY, Proposition 2.5] and, in the form of the law of the block of a given car, [CL, (2.6)]. Chassaing and Louchard identify the blocks with the trees of a forest of Pavlov's type, tree sizes corresponding to block sizes [CL, Section 5.1]. The representation of the tree sizes of a uniform forest with a given number of trees by independent Borel variables conditioned on their sum is Pavlov's; it is stated in [P99, Proposition 7 and Section 4.1] and [J12, Example 12.6].

*The additive coalescent.* The merging rule of Theorem 4.10 is in Chassaing and Louchard: two blocks with $x$ and $y$ cars merge at the next arrival with probability $(x+y+2)/((l-1)m)$ when there are $m$ places and $l$ empty ones [CL, Section 1.4, (1.5)], and, with the empty place counted in the block, "the process of sizes of blocks has the same distribution as the discrete Markovian coalescent" obtained by Aldous and Pitman from a uniform random tree whose edges are deleted in random order [CL, Section 8]; the transition probabilities of that coalescent are [AP, Lemma 1] and [P99, Theorem 5, (10)]. Pitman's construction adds an edge from a uniformly chosen vertex to the root of a uniformly chosen other tree and keeps the forest uniform at every stage [P99, Theorem 4]; the parking process realises the same choice of trees, by the spot at which the car lands. Chassaing and Louchard also describe a tree, built from a breadth-first correspondence [CL, Section 5.1], from which forests with the tree sizes of the blocks at all earlier times are obtained by erasing the edges above the cars in the reverse order of their arrival [CL, Section 8]. That tree is not the history forest. For the parking function $(1,1)$ the breadth-first correspondence gives the tree in which both cars are children of the root (the cars preferring the first place are the children of the root), whereas in the history forest the first car is a child of the second, whose subtree is the block of size $2$ that it closed; so in their tree the subtree of a car is not the block it closed. What the two trees have in common is the property of Proposition 4.4(d) at the level of sizes. Their statements are made in the text, without numbered theorems; Theorem 4.10 is proved in Section 4.4 for this reason.

So each of the three descriptions of Section 4 is in the literature, and so are two links between them: between the decreasing tree and the ranges of the displacements [GL], and between the merging of blocks and a tree with its edges erased in time [CL]. What Section 4 adds is the observation that the tree of the first link is the merge history of the process of the second, so that one object carries both, and the probabilistic form of the statement about displacements.

### 9.2 The mechanisms

*Normalisation by size.* The tree function, Cayley's formula $n^{n-1}$ for rooted labeled trees and the count $\binom{n-1}{k-1}n^{n-k}$ of forests with $k$ trees are in [FS, Section II.5.1, (44)–(47), and Note II.18]; the forest count is also [P99, (5)], where it is credited to Riordan. Lagrange inversion in the form used in Lemma 6.1 is [FS, Theorem A.2]. The law of the sum of several Borel variables is stated in [Tan, (6)] and is named the Borel–Tanner distribution in the title of [HB]. The formula for the size of a Galton–Watson tree through a random walk, of which the Borel law is the Poisson case, is attributed in [J12, Theorem 15.5] to Otter and Dwass. The law (B) is the exponential Boltzmann model of the class of rooted labeled trees at its singularity, in the sense of [DFLS, Section 2]; that paper does not name the Borel law, and the identification is immediate from its formula (2.3).

*Decomposition at vertices.* Two functional equations lie behind the second mechanism. The first, "a tree is a root with a set of trees", is the standard specification of the symbolic method [FS, Section II.5.1, (44)] and the equation of rooted trees in the language of species [BLL, Introduction, (1)]. The second, "a tree with a marked vertex is a sequence of trees", is the description of doubly pointed trees (vertebrates) as non-empty sequences of rooted trees [BLL, Example 2.34]. The counting step in the proof of Theorem 6.2 is of the same kind as Pitman's lemma that a rooted forest with $k$ trees on $n$ vertices is contained in exactly $n^{k-1}$ rooted trees [P99, Lemma 1], and as the containment formula for random forests defined by a general distribution on the vertices [P01, Lemma 23]. The expected number of vertices at a given distance from the root of a uniform rooted labeled tree, the first formula of Corollary 6.3(c), is [MM78, (5.2)], and the law of the depth of a uniform vertex is [AP2, (107)]; in the setting of trees built from the birthday problem it is [P01, Corollary 8(ii)] with [CP]. The decomposition of a tree with a marked vertex along its ancestral line into a forest, used in Corollary 6.3(d), is the bijection of Joyal as presented in [P01, Section 4.1]. For conditioned Galton–Watson trees in general, the limit in distribution of the subtree at a random vertex is [J12, Theorem 7.12], after Aldous, and the expected number of vertices whose subtree has a given size, and the corresponding count for pairs of vertices, nested or disjoint, are [J16, Lemma 5.1 and Lemma 6.1 with (6.8)]; for Poisson offspring these are the patterns with one and with two nodes. Theorem 6.2 itself, as one formula for an arbitrary pattern of nested and disjoint subtrees, was not found (see 9.4).

*Weights that are products over vertices of a function of the subtree size.* Such weights are the subject of the literature on hook length formulas for trees. The equation satisfied by the generating function is (6.3): for rooted labeled trees and forests it is [CGG, Theorems 4.1 and 4.4], where the case of the weight $1/s$ is Theorem 4.3, and in the setting of degree-weighted ordered trees it is [KP, Theorem 1 and Example 3] and [JY, Theorem 3.1]; sums over forests of such products occur in [GS, Lemma 2.4]. The last-car recursion for the threshold weight is the recursion of Aguilar-Fraga et al. for $\ell$-interval parking functions, the parking functions in which every car parks at most $\ell$ spots after its preferred one, that is, those with $M\le\ell$ [AF, Theorem 3.7]; for the total displacement it is [Kn98, (2.1)], and for the statistic of lucky cars the identity of Proposition 10.1(b) is proved in [GS, Section 10] by showing that both sides satisfy the same differential equation.

*Cutting.* For the uniform law, the fact that deleting a uniform edge leaves uniform pieces is part of [P99, Theorem 4]. Among the families of trees defined by weights on the degrees of the vertices, Panholzer characterised those that are preserved by the removal of a random edge [Pa, Lemma 1]: three families, one of which is the family of labeled unordered trees. Theorem 6.7 is the analogous characterisation for weights on the subtree sizes. The splitting property of random recursive trees, which is the case $w_s=c/s$, is commonly attributed to Meir and Moon [MM]; that paper was not read, the abstract that was seen does not state the property, and the attribution is not verified here.

*The street.* The decomposition of a parking function into prime parking functions and their count are classical; see [GS, Section 10], where the count $(n-1)^{n-1}$ is the case $u=1$ of Corollary 10.3, and [DG, (4) and Theorem 1], where the count is attributed to Gessel.

### 9.3 The tools attached from outside

The correlation inequality used in Section 7.3 and in Appendix B.3 is [FKG, Proposition 1]; the comparison of two laws that differ by increasing factors is derived from it in the text. For product measures the positive correlation of increasing events is Harris's lemma, which is the special case (3.22) of [FKG, Proposition 1']. The total positivity of the triangular array of the numbers of forests of rooted trees by number of components, which the earlier notes used for the homogeneous comparison, is [So, Theorem 1.1(a)]. The remainder in Stirling's formula used in Lemma 8.1 is proved in the text; the two-sided bounds are commonly attributed to Robbins [Rob]; that note was not read, and the attribution is not verified here. The square-root expansion of the tree function and the resulting exponent $3/2$ are [FS, Theorem VI.6 and Example VI.8]. The limit law of the maximum displacement is Petersson's [Pet, Theorem 5.1], with the Laplace transform of the limit variable from [JP, Corollary 2.4]. For the total displacement, the exact moments and the limit law are in [FPV, Theorems 3 and 4], and the coefficients of its generating polynomial are log-concave [Pap, Theorem 3.1], in contrast with the rows of the maximum displacement (Section 11.8); the correspondence of [CM, Proposition 4.1] relates the total displacement to the walk that explores a tree in breadth-first order.

### 9.4 What this document adds, and on what searches this rests

The following statements were not found in the sources read for this document, which are the entries of the bibliography that are not marked "not read"; the table of attributions records for each source the passages read. For some of the statements a search of databases was made in addition, and the table records its queries and hits; where no such search was made, this is said. A search of this kind does not show that a statement is new; it shows where it was looked for.

1. *The assembly of Section 4*: that the decreasing tree of [GL] is the merge history of the block process of [CL] (Proposition 4.4(d)), with the displacement of each car uniform on the block it lands in, as in [Pet, Section 2], and hence Theorem 4.6(b) and Corollary 4.7 as statements about one random object. The ingredients are known, as described in 9.1; the nearest statements found are in Petersson's paper: the backward fragmentation of its Section 2, in which the displacement of each removed item is uniform on its left block, for a table of any size [Pet, p. 458], and the conditional independence along the largest block which [Pet, Lemma 4.2] uses in the window of the limit law. With the fragmentation, the finite mark structure of the displacements is in that paper, in the language of the process; what was not found there is its identification with the subtree sizes of the uniform forest and the identity (4.4). The joint law of Lemma 4.5 belongs to this item as well: the independence of the events $\iota_v=0$ is [GS, Lemma 2.1], and the full law was not found (rows L4-extra-7 and L4-16). A bounded database search for the forest sum of $\prod_v\min(t_v,k)/t_v$ and for the statement on independent uniform marks found neither (row L4-16: two queries in zbMATH and one in OpenAlex; arXiv could not be searched at that time).
2. *The pattern formula* (Theorem 6.2) as a single statement. Its instances for one vertex and for two vertices [J16], for the depth [AP2], and the containment count behind it [P99, Lemma 1] are known. A limited search (row L10-12: two queries on arXiv abstracts) found no general statement; two papers that it returned, on fringe trees and on subtree patterns in conditioned trees (arXiv:2312.04243 and arXiv:2607.22291), were seen by title only and should be consulted before any claim of novelty.
3. *The characterisation of the weights compatible with cutting* (Theorem 6.7). The nearest result found is [Pa, Lemma 1], for weights on degrees. A search (row L9-10: three queries in zbMATH and arXiv) found no characterisation for weights on subtree sizes.
4. *The skeleton expansion* (Theorem 7.1), which is a direct consequence of the pattern formula. No database search was made for it.
5. *The coupling of Lemma 11.8*, with the remark that the rule determines the Cayley coefficients. For partitions of a set, Berestycki and Pitman characterised the weights for which a fragmentation process of one particular kind, defined by a recursive Gibbs splitting rule together with a linear selection rule, has Gibbs laws at all its stages, and the partition generated by a uniform forest, with block weights $j^{j-1}$, is one of their examples [BP, Theorem 2 and Example 4]; the general question which fragmentation processes have Gibbs laws is left open there. A rule that adds cuts at fixed positions of a segment and passes exactly through the conditioned Borel compositions was not found in the sources read, nor by a search (row L9-9: queries in zbMATH and arXiv on the additive coalescent with ordered structures). That search returned a paper on an ordered additive coalescent (G. Miermont, Electronic Journal of Probability 6 (2001), paper 14), which was not read and should be consulted before any claim of novelty; the backward fragmentation of a parking table into ordered blocks is described in [Pet, Section 2].
6. *The three theorems of Section 11* (Theorems 11.4, 11.5 and 11.7) and the reduction of Corollary 11.9. Apart from the paper of Celano et al. itself, no refereed article and no preprint with a proof of its conjecture, or with a partial result on it, was found by the searches of rows L5-12, L11-1 and L4-16 (queries on arXiv, zbMATH and a citation index for works citing the source; about ninety hits, judged by their titles). In particular none of the three statements of Theorems 11.4, 11.5 and 11.7 was found. The one item found that addresses the conjecture is an unrefereed deposit of the earlier research mentioned in Section 1.3 (Zenodo, doi:10.5281/zenodo.24110810), which by its own description is neither refereed nor machine-checked; it is not used here. The partial results found are those stated in the source itself: the two ends of each row, and the inequalities for the first two steps and the last step, which are discussed, with the small values of $n$ at which they fail, in the remark of Section 11.3.
7. *The depth of a vertex in a forest with several trees* (the paragraph after Corollary 6.3): $\Pr(D\ge d)=(N-q)_d/N^d$ for a uniform vertex of a uniform forest with $q$ trees on $N$ vertices. The case $q=1$ is known (Section 9.2). For general $q$ no statement was found in the sources read (rows L2-6, L3-11 and L3-12); no database search was made.

The other statements that are proved in the text and for which this section names no source are the corollary of Lemma 6.1, Corollary 6.3(b) for chains of more than two vertices, Propositions 6.5 and 6.6, Lemma 7.2, Propositions 7.3 and 7.7, the statement on the pole of $F_k$ in Section 7.5, Propositions 11.1, 11.3, 11.6 and 11.12, Corollary 11.11 and Lemmas B.1 and B.2, together with the route by which Proposition 10.2 obtains its values, which are themselves known [FPV, Theorem 4]. Proposition 8.2 has a known counterpart in the limit: its asymptotic formula agrees, for $q=zn^{2/3}$, with the expectation $\frac4{3\sqrt{2\pi}}z^{3/2}$ of the limit variable in [Pet, Corollary 4.10]. The paper does not state the convergence of the expectations, and the exact formula and the two-sided bounds for finite $n$ were not found there (row L12-7). These are direct computations with the statements of Sections 4 to 6. No source for them was found among those read, no database search was made for them, and they are not claimed as new.

## 10. Generality: other statistics and other families

The structure was built to explain the tools met in the study of one statistic. This section shows that it is not tied to that statistic: it treats in the same way every statistic that is a symmetric function of the displacements taken car by car (10.1), it gives the first two moments of the total displacement by the pattern formula (10.2), it covers parking with spare spots (10.3), and it reads statistics of a particular car from the description in time (10.4). The last subsection says what it does not cover.

### 10.1 Statistics of the displacements

By Theorem 4.6(a), for every function $w$ on the non-negative integers,
$$
\sum_{\alpha\in\mathrm{PF}_n}\prod_{i=1}^nw(d_i)=\sum_{\sigma\in S_n}\prod_{i=1}^n\ \sum_{d<h_i(\sigma)}w(d)=\sum_F\prod_{v\in F}\frac1{t_v}\sum_{d<t_v}w(d).
$$
The maximum displacement is the case $w=\mathbf 1_{\{d<k\}}$. Two other cases are classical.

**Proposition 10.1** [proved; the closed formulas quoted in (b) and in the remark after the proof are cited]. Let $[t]_q=1+q+\dots+q^{t-1}$.

(a) *Total displacement.* $\displaystyle\sum_{\alpha\in\mathrm{PF}_n}q^{d_1+\dots+d_n}=\sum_{\sigma\in S_n}\prod_i[h_i(\sigma)]_q=\sum_F\prod_{v\in F}\frac{[t_v]_q}{t_v}$.

(b) *Lucky cars.* Call a car lucky if its displacement is $0$. Then $\displaystyle\sum_{\alpha\in\mathrm{PF}_n}x^{\#\text{lucky cars}}=\sum_{\sigma\in S_n}\prod_i\bigl(h_i(\sigma)-1+x\bigr)=\sum_F\prod_{v\in F}\frac{t_v-1+x}{t_v}$, and this polynomial equals $x\prod_{i=1}^{n-1}\bigl(i+(n-i+1)x\bigr)$ [GS, Theorem 10.1]; the equality with the product was checked for $n\le7$ by enumeration (Appendix C, item C10).

*Proof.* Take $w(d)=q^d$ and $w(d)=x^{\mathbf 1\{d=0\}}$ in the identity above. $\square$

In (a), the right-hand side is a sum over forests of a product over vertices of a function of the subtree size. By a theorem of Kreweras the same polynomial enumerates the labeled trees on $\{0,\dots,n\}$ by a statistic that later authors call the number of inversions [Kr, Théorèmes I and II]; Kreweras states it for sequences that he calls suites majeures, and the translation to parking functions and their total displacement is made in [Kn98], where the recursion (6.2) for the weight $[t]_q/t$ appears as formula (2.1), with the remark that its factor "corresponds to the displacement of the $n$th car". In the present terms Kreweras's theorem is (a) together with the following consequence of Lemma 4.5 [proved]. Fix a rooted forest with $n$ vertices. Its $n!$ labelings by bijections onto $[n]$, counted by $q$ to the number of pairs (ancestor, descendant) in which the descendant has the larger label, give $n!\prod_v[t_v]_q/t_v$, because that number of pairs is $\sum_v\iota_v$ and the $\iota_v$ are independent and uniform; reversing the order of the labels gives the same for the pairs in which the descendant has the smaller label, which are the inversions. The $n!$ labelings yield each labeled forest of the shape $S$ of the given forest exactly $|\mathrm{Aut}(S)|$ times, and the number of inversions does not change under an automorphism. Hence the labeled forests $F$ of shape $S$, counted by $q$ to their number of inversions $\operatorname{inv}(F)$, give $\frac{n!}{|\mathrm{Aut}(S)|}\prod_v[t_v]_q/t_v$, which is the sum of $\prod_{v\in F}[t_v]_q/t_v$ over these forests; summing over the shapes, $\sum_Fq^{\operatorname{inv}(F)}=\sum_F\prod_{v\in F}[t_v]_q/t_v$, the right-hand side of (a). Finally, a forest on $[n]$ is a tree on $\{0,\dots,n\}$ rooted at $0$, and the vertex $0$, which carries the smallest label, takes part in no inversion, so the inversions of the forest are those of the tree. This formula for all labelings of a fixed forest is quoted in [CGG2, Theorem 1.1, p. 3] as Theorem 1.3 of Björner and Wachs [BW], together with the same formula for a second statistic, the major index. The paper [BW] itself could not be read, so the attribution rests on that quotation; whether [BW] also contains the joint law of Lemma 4.5 is not known, and the pages read of [CGG2] attribute no such statement to it (rows L13-6, L13-7 and L13-extra-1).

### 10.2 A consequence: the mean and the variance of the total displacement

The earlier research did not treat the total displacement. Its first two moments are a direct application of the structure, and they show the second mechanism at work on a quantity that is not a threshold functional.

For a forest $F$ put $\mathrm{pl}(F)=\sum_{v\in F}(t_v-1)$. This is the number of pairs (ancestor, descendant) of $F$, that is, the sum over the vertices of their distances from the root of their tree (the path length of $F$).

**Proposition 10.2** [proved; the exact values for $n\le7$ were also checked by enumeration, Appendix C, item C10]. Let $\mathsf T$ be the total displacement of a uniform random parking function of length $n$, and let $F$ be the uniform random rooted labeled forest on $[n]$. Then
$$
\mathbb E\,\mathsf T=\tfrac12\,\mathbb E\,\mathrm{pl}(F)=\frac n2\sum_{j\ge1}\frac{(n-1)_j}{(n+1)^j},\qquad
\operatorname{Var}\mathsf T=\frac1{12}\,\mathbb E\sum_{v\in F}(t_v^2-1)+\frac14\operatorname{Var}\mathrm{pl}(F).
$$
Both terms of the variance are given by the pattern formula. With $N=n+1$ and
$$
\theta(s)=\frac{\mathrm{Ren}(N-s)\mathrm{Bor}(s)}{\mathrm{Bor}(N)},\quad
\theta_2(s,s')=\frac{\mathrm{Ren}(N-s)\mathrm{Ren}(s-s')\mathrm{Bor}(s')}{\mathrm{Bor}(N)},\quad
\theta_\perp(s,s')=\frac{\gamma^2\,\mathrm{Bor}(\gamma)\mathrm{Bor}(s)\mathrm{Bor}(s')}{\mathrm{Bor}(N)}\ \ (\gamma=N-s-s'\ge1),
$$
one has $\mathbb E\sum_vf(t_v)=\sum_{s=1}^nf(s)\theta(s)$ for every $f$, and
$$
\mathbb E\,\mathrm{pl}(F)^2=\sum_{s}(s-1)^2\theta(s)+2\sum_{s>s'}(s-1)(s'-1)\,\theta_2(s,s')+\sum_{s,s'}(s-1)(s'-1)\,\theta_\perp(s,s').
$$
Here the first sum is over $1\le s\le n$, the second over $1\le s'<s\le n$, and the third over all $s,s'\ge1$ with $s+s'\le n$. For example $\mathbb E\mathsf T=\frac13,\frac{15}{16},\frac{222}{125}$ and $\operatorname{Var}\mathsf T=\frac29,\frac{207}{256},\frac{29716}{15625}$ for $n=2,3,4$.

*Proof.* By Theorem 4.6(b), $\mathsf T$ has the law of $\sum_vD_v$, where, given $F$, the $D_v$ are independent and uniform on $\{0,\dots,t_v-1\}$, with mean $(t_v-1)/2$ and variance $(t_v^2-1)/12$. Hence $\mathbb E[\mathsf T\mid F]=\mathrm{pl}(F)/2$ and $\operatorname{Var}[\mathsf T\mid F]=\sum_v(t_v^2-1)/12$, and the formula for the variance is the decomposition of a variance into the mean of the conditional variance and the variance of the conditional mean. For the mean, join the roots of $F$ to the virtual root $0$; then $\mathrm{pl}(F)=\sum_{v\ne0}(\operatorname{dist}(v,0)-1)$. By Corollary 6.3(c) the distance $D$ of a uniform vertex of the tree on $N$ vertices from its root has $\mathbb E D=\sum_{d\ge1}(N-1)_d/N^d$, so $\mathbb E\,\mathrm{pl}(F)=N\,\mathbb ED-n=N\sum_{d\ge2}(N-1)_d/N^d=n\sum_{j\ge1}(n-1)_j/(n+1)^j$. The expression for $\mathbb E\sum_vf(t_v)$ is Corollary 6.3(a). For $\mathbb E\,\mathrm{pl}(F)^2$, expand the square of $\sum_v(t_v-1)$ into the sum over ordered pairs of vertices: a pair consists of one vertex twice, of two nested vertices (in two orders), or of two vertices with disjoint subtrees. The expected numbers of such pairs with prescribed subtree sizes are given by Theorem 6.2 for the patterns consisting of one node, of a path of two nodes, and of two nodes attached to the root, all of type descendant; these are $\theta$, $\theta_2$ and $\theta_\perp$. $\square$

The first term of the variance is at most of order $n^{5/2}$ [proved]: by Lemma 8.1, $\theta(s)\le e^{1/12}(2\pi)^{-1/2}N^{3/2}s^{-3/2}(N-s)^{-1/2}$, so that $\sum_{s=1}^ns^2\theta(s)\le e^{1/12}(2\pi)^{-1/2}N^{2}\sum_{s=1}^n(N-s)^{-1/2}\le2e^{1/12}(2\pi)^{-1/2}N^{5/2}$. The variance itself is of order $n^3$ by the classical analysis of linear probing hashing: the limit law of the total displacement of a table with one empty cell, divided by $(n/2)^{3/2}$, is the Airy distribution, whose variance is $\frac{10}3-\pi$ [FPV, Theorem 3], and with the convergence of moments of that analysis this gives $\operatorname{Var}\mathsf T\sim\frac{10-3\pi}{24}n^3$ [proved; cited: [FPV, Theorem 3, with the moment asymptotics (24), p. 501, of that paper]; the source prints the expansion for the completely full table in its Theorem 2 and does not print the constant for the present case as a separate formula]. Granting this asymptotic formula, $\operatorname{Var}\mathsf T\sim\frac14\operatorname{Var}\mathrm{pl}(F)$: the randomness that remains once the forest is known contributes a lower order. The formulas agree with that analysis: the exact mean and second moment of the total displacement for $n$ keys in a table of $n+1$ cells are the case $m=n+1$ of [FPV, Theorem 4], whose mean is the closed form above and whose values for $n=2,3,4$ coincide with those given here; numerically the exact variance divided by $n^3$ is $0.02467$, $0.02432$, $0.02414$ for $n=50,100,200$, against $\frac{10-3\pi}{24}=0.02397\ldots$ [computational evidence: the exact variance, with the final division in floating point; Appendix C, item C10].

### 10.3 Parking with spare spots

In this subsection $r$ denotes the number of empty spots of the circle on which the process runs, not the deficit $n-k$ of Section 3.2. Let $m$ cars park by the same rule on a row of $m+r-1$ spots, $r\ge1$; $r-1$ spots stay empty. The case $r=1$ is that of the conjecture.

**Proposition 10.3** (spare spots) [proved; known: the count [KY, Theorem 2.2]; the product formula for the weight $w(d)=x^d$ [Kn98, (1.3)]]. The number of preference lists in $\{1,\dots,m+r-1\}^m$ on which all $m$ cars park is $r(m+r)^{m-1}$. For every function $w$ of the displacements, with $g(t)=\frac1t\sum_{d<t}w(d)$ and $F_g$ as in Proposition 6.4, the sum on the left being over the lists $\alpha$ on which all cars park and the sum on the right over the rooted labeled forests $E$ on $[m]$,
$$
\sum_{\alpha}\prod_{i=1}^mw(d_i)=m!\,[x^m]\,F_g(x)^r=\sum_{E\ \text{on}\ [m]}r^{\,\#\text{trees of }E}\,\Phi_g(E).
$$
The history of this process is the history of the parking process on the circle of $N=m+r$ spots, stopped after $m$ cars, when $r$ blocks remain; the sizes of the blocks follow the law (Q) of Section 5.3 with $q=r$.

*Proof.* On the circle of $N=m+r$ spots every list parks and $r$ spots stay empty. As in Theorem 4.1, a list leaves spot $N$ empty if and only if it is a list on which all cars park on the row $1,\dots,N-1$, and exactly $r$ of the $N$ rotations of a list leave spot $N$ empty; this gives $rN^m/N$ lists. On the row, the $r-1$ empty spots divide the occupied spots into $r$ intervals, some of which may be empty, and, as in the proof of Theorem 4.9, the cars that park in an interval of $c$ spots form a parking function of length $c$ on that interval. Summing $\prod w(d_i)$ over the lists with given intervals and given sets of cars gives the product of the numbers $Z_c[g]$ of the intervals, by Theorem 4.6(a), and the sum over the ways to distribute the cars is $m!\,[x^m]F_g^r$. Finally $F_g$ is the exponential of the generating function of the weighted trees by (6.3), so $F_g^r$ is the generating function of the forests in which every tree carries the additional weight $r$. For the last assertion: by the rotation argument a uniform list on which all cars park is obtained from a uniform list on the circle by choosing one of its $r$ empty spots uniformly and rotating it to position $N$; reading the blocks from spot $N$ is then reading them from a uniformly chosen empty spot, and Theorem 4.9 with $t=m$ and $q=r$ gives their law. $\square$

So the spare spots change the law of the forest by a factor $r$ per tree and change nothing else: the observables, the two mechanisms and the skeleton expansion apply as before. The same family arises inside the original problem, as the state of the process before the last $r-1$ cars arrive. Counterexample 7.4 concerns this family: for $r=5$ the analogue of Conjecture P fails at $m=121$.

### 10.4 Statistics of a particular car

The uniform forest forgets the order of arrival, so it does not contain the displacement of, say, the last car. The description in time does.

**Proposition 10.4** [proved; known in substance: an immediate consequence of three statements of [J05], namely (34), p. 195, (4), p. 181, and the law of the block lengths on p. 183; that paper does not print the assembled finite formula]. In a uniform random parking function of length $n$, for $0\le t\le n-1$ and $j\ge0$, the displacement of car $t+1$ satisfies
$$
\Pr(d_{t+1}\ge j)=\frac{q}{N}\sum_{s>j}(s-j)\,\frac{\mathrm{Bor}(s)\,\mathrm{Bor}^{*(q-1)}(N-s)}{\mathrm{Bor}^{*q}(N)},\qquad q=N-t,
$$
(here $q\ge2$).

*Proof.* On the circle the preference of car $t+1$ is uniform and independent of the first $t$ cars. By Lemma 4.2 its displacement is at least $j$ with probability $\sum_i(s_i-j)_+/N$, where the $s_i$ are the sizes of the $q$ blocks present. By Theorem 4.9 each block size has the law of the first of $q$ independent Borel variables conditioned on their sum being $N$. $\square$

For the last car ($t=n-1$, $q=2$) this gives $\Pr(d_n\ge j)=\frac2N\sum_{s>j}(s-j)\,\mathrm{Bor}(s)\mathrm{Bor}(N-s)/\mathrm{Bor}^{*2}(N)$; for $n=2$ and $j=1$ the value is $\frac13$, in agreement with the three parking functions $11,12,21$.

### 10.5 What is not covered

The structure covers the parking rule of Section 3.1 under the uniform law on the lists on which all cars park (on the circle: independent uniform preferences), with any number of spare spots, and statistics that are functions of the displacements. For another offspring law in place of the Poisson law (as in Counterexample 7.5) the conditioned forest is not uniform, the factor of a freely attached piece in Theorem 6.2 is no longer the size of the layer, and no merging process in time behind the forest is constructed here; the normalisation by size and the factor of a piece attached at a prescribed vertex persist. Parking rules in which a car that finds its spot taken does something other than move to the next free spot, and statistics that depend on the preferred spots beyond the displacements, were not examined.

## 11. The unimodality problem inside the structure

This section is specific to Conjecture P. It first writes the step $d_{n,k}=b_{n,k}-b_{n,k-1}$ as a difference of two counts on the history forest (11.1, 11.2). It then states what is proved for all sizes: the rows increase far on the left and decrease far on the right (11.3), and on the right a decrease, once it occurs, continues (11.4, 11.5). From these it derives an exact reduction of the conjecture to one target (11.6) and a second, conditional route (11.7). It ends with the exact facts that constrain strategies (11.8) and with the open targets written in indices (11.9). The three theorems are proved in full in Appendix B; each is preceded here by an overview of its proof.

By (3.1), Conjecture P for a given $n$ says that the sequence of steps $d_{n,1},\dots,d_{n,n-1}$ has no negative term followed later by a positive one.

### 11.1 The step is a count of pairs minus a count of single vertices

For a forest $F$ and a real $y>0$ write $\chi_y(F)=\#\{v:t_v>y\}$ for the number of heavy vertices, and for an integer $k\ge1$ write $\nu_k(F)=\#\{v:t_v=k\}$ for the number of threshold vertices.

**Proposition 11.1** (curvature and loss) [proved]. Let $1\le k\le n-1$.

(a) $\displaystyle d_{n,k}=\sum_F\Phi_{g_k}(F)\Bigl[\bigl(1+\tfrac1k\bigr)^{\chi_k(F)}+\bigl(1-\tfrac1k\bigr)^{\chi_k(F)+\nu_k(F)}-2\Bigr]$, the sum being over the rooted labeled forests on $[n]$.

(b) The function $y\mapsto Z_n(y)$ is a polynomial on each interval $[j,j+1]$, $j\ge0$ an integer, with $Z_n''(y)=\sum_F\Phi_{g_y}(F)\,\chi_y(F)(\chi_y(F)-1)/y^2$ in the interior, and
$$
d_{n,k}=V_{n,k}-L_{n,k},\qquad V_{n,k}=\int_{k-1}^{k+1}\bigl(1-|y-k|\bigr)Z_n''(y)\,dy,\qquad L_{n,k}=\frac1k\sum_F\Phi_{g_k}(F)\,\nu_k(F). \tag{11.1}
$$

*Proof.* For $k=1$ the threshold $k-1$ is $0$; then $Z_n(0)=0$ by the convention of Section 3.2, in agreement with the formulas below, since every vertex has $t_v\ge1$ and $Z_n(y)$ is a constant times $y^n$ on $(0,1]$. (a) For a fixed forest, passing from the threshold $k$ to $k+1$ multiplies the factor $k/t_v$ of every vertex with $t_v>k$ by $1+\frac1k$ and changes nothing else; passing from $k$ to $k-1$ multiplies the factors of the vertices with $t_v\ge k$ by $1-\frac1k$. Sum $\Phi_{g_{k+1}}-2\Phi_{g_k}+\Phi_{g_{k-1}}$ over the forests. (b) On $(j,j+1)$ the set of heavy vertices of each forest is constant and $\Phi_{g_y}(F)$ is a constant times $y^{\chi_y(F)}$; this gives the first assertion. By Taylor's formula on $[k,k+1]$ and on $[k-1,k]$,
$Z_n(k\pm1)-Z_n(k)=\pm Z_n'(k\pm)+\int(1-|y-k|)Z_n''(y)\,dy$, the integrals being over the two intervals, and adding the two gives $d_{n,k}=V_{n,k}-\bigl(Z_n'(k-)-Z_n'(k+)\bigr)$. The left derivative at $k$ of $\Phi_{g_y}(F)$ is $\Phi_{g_k}(F)$ times $\#\{v:t_v\ge k\}/k$ and the right derivative is $\Phi_{g_k}(F)\,\chi_k(F)/k$. $\square$

So the sign of a step is decided by a competition. The *curvature* $V_{n,k}$ is positive and counts, with weights, ordered pairs of distinct vertices that are heavy for the running threshold $y$ of the integral: pairs of cars each of which closed a block with more than $k$ spots when $y$ lies in $(k,k+1)$, and with at least $k$ spots when $y$ lies in $(k-1,k)$. Vertices with $t_v=k$ thus enter the curvature as well as the loss. The *loss* $L_{n,k}$ counts single vertices at the threshold: cars that closed a block of size exactly $k$. In the language of Section 5, $L_{n,k}=Z_n(k)\,\mathbb E_k[\nu_k]/k$ and, for $k<y<k+1$, $Z_n''(y)=Z_n(y)\,\mathbb E_y[\chi_y(\chi_y-1)]/y^2$, with expectations under the law (W).

A pair of heavy vertices is either nested or has disjoint subtrees. Disjoint pairs can occur only if $n\ge2k$; on the far left their contribution alone exceeds the loss (Theorem 11.4). For $n\le2k-1$ every pair is nested, and the comparison is between the chain of large nested blocks and the one block at the threshold; this is the regime of Sections 11.4 and 11.5.

Formula (a) shows the competition forest by forest: a forest with a threshold vertex and no heavy vertex contributes negatively, one with many heavy vertices positively. For a single forest the resulting sequence need not be unimodal.

**Counterexample 11.2** (a fixed outcome) [counterexample; Appendix C, item C9]. For the outcome $\sigma=(1,2,3,5,4,6,7)$, with capacities $(1,2,3,4,1,6,7)$, the numbers of parking functions with outcome $\sigma$ and maximum displacement $0,1,\dots,6$ are $1,31,130,222,216,264,144$. This sequence is not unimodal. Seven is the smallest length at which an outcome with this property exists. The same numbers divided by $1008$ are the distribution of $\max_vD_v$ for any forest with subtree sizes $1,1,2,3,4,6,7$. Hence unimodality cannot be proved outcome by outcome or forest by forest: it is a property of the sum.

### 11.2 The loss

The loss is a count of occurrences of a one-node pattern under the weighted law, and Proposition 6.6 evaluates it.

**Proposition 11.3** (loss formula) [proved]. For $1\le k\le n$, with $L_{n,k}=\frac1k\sum_F\Phi_{g_k}(F)\,\nu_k(F)$ as in (11.1) (the formula defines $L_{n,n}$ as well),
$$
L_{n,k}=\binom nk\,k^{k-2}\sum_{E}\Phi_{g_k}(E)\sum_{u}\ \prod_{x\in P(u)}\frac{\max(t_x,k)}{t_x+k}, \tag{11.2}
$$
where $E$ runs through the rooted labeled forests on $n-k$ vertices, $u$ through the vertices of $E$ and the virtual root, and $P(u)$ is the set consisting of $u$ and its ancestors in $E$ (empty if $u$ is the virtual root). Consequently
$$
\frac{n+1}{k+1}\ \le\ \frac{L_{n,k}}{\binom nk k^{k-2}\,Z_{n-k}(k)}\ \le\ n-k+1. \tag{11.3}
$$

*Proof.* A pair (forest $F$, vertex $v$ with $t_v=k$) is obtained exactly once by choosing the $k$ labels of the subtree of $v$, a rooted tree $S$ on them, a forest $E$ on the other labels and the vertex $u$ of $E$, or the virtual root, below which $S$ is attached. All vertices of $S$ have subtree size at most $k$, so $\Phi_{g_k}(S)=1$ and there are $k^{k-1}$ choices of $S$; by Proposition 6.6 the weight of $F$ is $\Phi_{g_k}(E)$ times the product in (11.2), since $g_k(t+k)/g_k(t)=\max(t,k)/(t+k)$. Dividing by $k$ gives (11.2). Each factor of the product lies between $t_x/(t_x+k)$ and $1$. With all factors equal to $1$ the inner sum is $n-k+1$. With the factors $t_x/(t_x+k)$ the sum over the vertices $u$ of a tree of $E$ with $a$ vertices is $a/(k+1)$, by the last step of the proof of Theorem 6.7 (the case $w_s=c/s$, $b=k$), so the inner sum is at least $1+(n-k)/(k+1)$. $\square$

The factor $k^{k-2}$ is the number of unrooted labeled trees on $k$ vertices: the choice of the root among the $k$ labels cancels the factor $1/k$ of the slope. The two bounds in (11.3) correspond to the two weights of Theorem 6.7: the upper bound is what the formula gives when attaching costs nothing, as under the uniform law, and the lower bound what it gives when every ancestor is charged the factor $t/(t+k)$, as in a recursive tree. For $1<k<n$ both inequalities are strict.

### 11.3 Two regions in which the sign is known

**Theorem 11.4** (increase far on the left) [proved; Appendix B.1]. If $k\ge1$ and $n\ge21k^2$, then $d_{n,k}>0$, that is, $b_{n,k}>b_{n,k-1}$.

*Overview of the proof.* Only pairs of heavy vertices lying in different trees of the forest are used. Under the law (W) the trees are independent given their vertex sets, and a tree with $a>k$ vertices contains on average at least $a/(2k)$ heavy vertices; this follows from the last-car recursion by induction. The expected sum of $|A|\,|B|$ over the ordered pairs of distinct trees with more than $k$ vertices is computed from the generating function $F_k$ of Proposition 6.5 through one algebraic identity, and is at least $(n-1)(n-4k^2)/2$. Hence the curvature is at least $Z_n(k)(n-1)(n-4k^2)/(16k^4)$, while the loss is at most $Z_n(k)\,n/k^2$ because subtrees of size exactly $k$ are disjoint.

**Theorem 11.5** (decrease far on the right) [proved; Appendix B.2]. If $1\le k<n$ and $k\ge4(n-k+1)^{3/2}$, then $d_{n,k}<0$, that is, $b_{n,k}<b_{n,k-1}$.

*Overview of the proof.* Here $n<2k$, so two heavy vertices are nested, and the expected number of nested pairs is given by Corollary 6.3(b): it is a sum of products $\mathrm{Bor}\cdot\mathrm{Ren}\cdot\mathrm{Ren}$, which Lemma 8.1 bounds. The loss is evaluated by (11.2): the forest $E$ has fewer than $k$ vertices and is unweighted, and the cost of the attachment is controlled by the expected sum of the subtree sizes along the path to the attachment vertex, again a pattern count. With $R=n-k+1$, the ratio of the curvature to the loss is at most a constant times $R^{3/2}/k$.

The theorem bounds from one side the position of the first decrease of a row: the loss dominates as soon as $n-k$ is below a constant times $k^{2/3}$, which is the scale $n^{2/3}$ of Section 8. That the first decrease does not occur much earlier is not proved; it is the content of Target T below.

**Remark** (the first two steps and the last step) [proved, using the exact computation of the rows with $n\le300$, script `c13_rows.py`]. For all $n\ge3$, $d_{n,1}>0$; for all $n\ge6$, $d_{n,2}>0$; for all $n\ge2$, $d_{n,n-1}<0$. Indeed Theorem 11.4 gives the first for $n\ge21$ and the second for $n\ge84$, Theorem 11.5 with $k=n-1$ gives the third for $n\ge13$, and the remaining cases are in the computed rows. The exceptions are real: $d_{2,1}<0$ and $d_{n,2}<0$ for $n=3,4,5$ (Section 3.1). These are the inequalities $b_{n,0}\le b_{n,1}\le b_{n,2}$ and $b_{n,n-2}\ge b_{n,n-1}$ which the paper that states the conjecture gives as consequences of its enumerative results "for all $n\ge1$" [CEHHMPU, Section 6, before Conjecture 6.5]; as the rows of Section 3.1 show, they hold from $n=3$, $n=6$ and $n=2$ on, respectively. That paper also identifies $Z_n(2)$, the number of parking functions with all displacements at most $1$, with the Fubini numbers [CEHHMPU, Example 2.8]. In the notation of the limit law, Theorem 11.4 concerns thresholds of order $\sqrt n$ and Theorem 11.5 deficits $n-k$ below about $(k/4)^{2/3}$, asymptotically $4^{-2/3}n^{2/3}\approx0.40\,n^{2/3}$; in the computed rows the first decrease lies in between: for $n=300$ it is at $n-k=35\approx0.85\,k^{2/3}$ (Section 11.6).

### 11.4 The first layer

A position $(n,k)$ with $k+2\le n\le2k-1$ is said to lie in the *first layer*; equivalently $r=n-k$ satisfies $2\le r\le k-1$. In the first layer two vertices with subtrees of size at least $k$ are nested, a forest has at most one vertex with $t_v=k$ and at most one with $t_v=k+1$, and the positions $(n,k)$ and $(n,k+1)$ can be compared through one polynomial. Throughout this subsection and the next, $N=n+1$.

For a first-layer position $(n,k)$ put
$$
K(y)=K_{n,k}(y)=\sum_F\ \prod_{v:\ t_v>k}\frac{y}{t_v},
$$
the *frozen polynomial*: the set of heavy vertices is frozen at the threshold $k$, and $y$ is a free variable. It is a polynomial in $y$ with non-negative coefficients, $K(k)=Z_n(k)$ and $K(k+1)=Z_n(k+1)$. Define
$$
\begin{aligned}
C_-&=K(k+1)-2K(k)+K(k-1), &\qquad B_-&=K(k-1)-Z_n(k-1),\\
C_+&=K(k+2)-2K(k+1)+K(k), &\qquad B_+&=K(k+2)-Z_n(k+2).
\end{aligned}
$$
For a composition $(\gamma_0,\dots,\gamma_{j})$ of an integer $m$, its *cut points* are the partial sums $\gamma_0,\ \gamma_0+\gamma_1,\ \dots$ strictly between $0$ and $m$. Put
$$
\Lambda_m(y)=\Lambda_m(y;N)=\sum_{(\gamma_0,\dots,\gamma_j)}\ \prod_{i=0}^{j}a_{\gamma_i}\ \prod_{s\ \text{cut point}}\frac{y}{N-s},
$$
the sum being over all compositions of $m$ (with any number of parts).

**Proposition 11.6** (the first layer) [proved]. Let $(n,k)$ be in the first layer, $r=n-k$. Then
$$
d_{n,k}=C_--B_-,\qquad d_{n,k+1}=C_+-B_+, \tag{11.4}
$$
$$
\frac{K(y)}{n!}=\kappa_k(N)+\sum_{m=1}^{r}\frac{\kappa_k(N-m)}{N-m}\;y\,\Lambda_m(y), \tag{11.5}
$$
$$
\frac{B_-}{n!}=\frac{a_k}{k}\,\Lambda_{r+1}(k-1),\qquad \frac{B_+}{n!}=\frac{a_{k+1}}{k+1}\,\Lambda_r(k+2), \tag{11.6}
$$
with $\kappa_k$ as in Section 7.1. All four quantities $B_\pm$, $C_\pm$ are positive, and
$$
d_{n,k+1}=\frac{B_+}{B_-}\,d_{n,k}-\frac{\mathcal S_{n,k}}{B_-},\qquad \mathcal S_{n,k}=B_+C_--B_-C_+ . \tag{11.7}
$$

*Proof.* The factor of a vertex in $\Phi_{g_{k-1}}$ differs from its factor in the product defining $K(k-1)$ only if $t_v=k$, where it is $\frac{k-1}k$ instead of $1$; there is at most one such vertex. Hence $B_-=\frac1k\sum_F\mathbf 1\{\nu_k(F)=1\}\prod_{t_v>k}\frac{k-1}{t_v}$. In the same way, a vertex with $t_v=k+1$ has the factor $\frac{k+2}{k+1}$ in $K(k+2)$ and $1$ in $\Phi_{g_{k+2}}$, so $B_+=\frac1{k+1}\sum_F\mathbf 1\{\nu_{k+1}(F)=1\}\prod_{t_v>k+1}\frac{k+2}{t_v}$. With $K(k)=Z_n(k)$ and $K(k+1)=Z_n(k+1)$ this gives (11.4), and (11.7) follows from (11.4) by elimination.

Formula (11.5) is Theorem 7.1 for the weight equal to $y/t$ for $t>k$ and to $1$ otherwise. The skeleton is a path with sizes $t_1>\dots>t_j>k$. If $j\ge1$, put $m=N-t_j$, so that $1\le m\le r$; the layers above the last node form a composition $(\gamma_0,\dots,\gamma_{j-1})$ of $m$, each with $\gamma_i\le r\le k+1$ and therefore with $\kappa_k(\gamma_i)=a_{\gamma_i}$; the node $i<j$ has size $N-s$ with $s$ the $i$-th cut point, and the last node has size $N-m$ and layer coefficient $\kappa_k(N-m)$. The skeleton without heavy vertices gives $\kappa_k(N)$.

For (11.6), let $v$ be the vertex with $t_v=k$. A vertex $w$ with $t_w>k$ is not a descendant of $v$, and if it were not an ancestor of $v$ its subtree would be disjoint from that of $v$ and have at most $n-k<k$ vertices; so the heavy vertices are exactly the ancestors of $v$. The forests with such a vertex therefore correspond to the occurrences of the patterns that are paths of nodes of type child ending in a node of size $k$, with no condition on the layers: the layers above $v$ form a composition of $N-k=r+1$, the layer of $v$ is an arbitrary rooted tree on $k$ vertices, and the ancestors of $v$ have the sizes $N-s$, $s$ a cut point. By the count in the proof of Theorem 6.2 the number of forests for a given composition is $n!\,a_k\prod a_{\gamma_i}$. The case of $B_+$ is the same with $k+1$ in place of $k$: the vertices with $t_w>k+1$ are the ancestors of the vertex of size $k+1$. Positivity of $B_\pm$ is clear from (11.6), and that of $C_\pm$ follows from (11.5): for $r\ge2$ the polynomial $K$ has a term of degree $2$ with positive coefficient, so $K''>0$ on $y>0$, and $C_\pm$ are integrals of $K''$ against a positive weight. $\square$

In (11.4) the quantity $C_-$ is the curvature of the frozen polynomial: by (11.5) it counts pairs of marks among the parts of a composition, that is, pairs of heavy vertices on the chain. The quantity $B_-$ is the boundary term: the one vertex at the threshold. They play for the frozen polynomial the roles that the curvature and the loss play in (11.1). The two decompositions of $d_{n,k}$ are not the same term by term: $L_{n,k}$ is a jump of the slope at $k$, while $B_-$ is a difference of two values at $k-1$ and contains the factors $\frac{k-1}{t}$ of the ancestors. The sums in (11.5) and (11.6) run over compositions with the same weights $a_\gamma$ of the parts and with cut factors of the same form $y/(N-s)$. They differ in the value of $y$ and in the length of the composed segment, which takes the values $m=1,\dots,r$ in (11.5) and is $r+1$ or $r$ in (11.6). This common form is what makes a comparison possible; the proof of Theorem 11.7 passes between the lengths $r+1$ and $r$ by removing the first unit of a composition (Appendix B.3, Step 2).

*Example.* For $(n,k)=(5,3)$: $K(2),K(3),K(4),K(5)=697,918,1171,1456$ and $Z_5(1),\dots,Z_5(5)=120,541,918,1171,1296$. Hence $C_-=C_+=32$, $B_-=697-541=156$, $B_+=1456-1296=160$, $d_{5,3}=32-156=-124=b_{5,3}-b_{5,2}$, $d_{5,4}=32-160=-128=b_{5,4}-b_{5,3}$, and $\mathcal S_{5,3}=160\cdot32-156\cdot32=128>0$ (Appendix C, item C6).

### 11.5 A decrease continues: the propagation theorem

By (11.7), if $\mathcal S_{n,k}>0$ and $d_{n,k}\le0$ then $d_{n,k+1}<0$. The cross product $\mathcal S_{n,k}$ is positive when the boundary term grows faster than the curvature, $B_+/B_->C_+/C_-$.

**Theorem 11.7** (propagation of a decrease) [proved; the proof uses two finite exact computations, script `c08_propagation.py`: the rational numbers $\mathcal M(r,k)$ of Appendix B.3 for $2\le r\le255$, from $k=\lceil r^{3/2}\rceil$ up to the first positive value for each $r$, and the cross product at the $122$ positions with $\mathcal M(r,k)\le0$, all of which have $n\le102$; Appendix B.3]. Let $r=n-k\ge2$ and $k\ge r^{3/2}$. Then $(n,k)$ lies in the first layer and
$$
\frac{B_+}{B_-}>\frac{C_+}{C_-}\ge1 ,
$$
so that $\mathcal S_{n,k}>0$. Consequently, if $d_{n,k}\le0$ at such a position, then $d_{n,k'}<0$ for every $k<k'\le n-1$, and moreover $d_{n,k+1}<d_{n,k}$.

The proof rests on a coupling of the laws on compositions that occur in (11.5) and (11.6), which is a statement about the structure and is stated here.

**Lemma 11.8** (coupling of Borel compositions) [proved; Appendix B.3]. Let $m\ge1$. For $1\le q\le m$ let $\pi_q$ be the law on the compositions of $m$ with $q$ parts in which a composition has probability proportional to the product of $a_{\gamma}$ over its parts $\gamma$ (the law of $q$ independent Borel variables conditioned on their sum being $m$). There are random compositions $X_1,\dots,X_m$ on one probability space such that $X_q$ has the law $\pi_q$ and the set of cut points of $X_q$ is contained in that of $X_{q+1}$, for every $q<m$. One step of the coupling, from $q+1$ parts to $q$, is the following: choose one of the $m$ unit cells and one of the $q$ cut points, independently and uniformly, and delete the first cut point met when moving from the cell towards the chosen cut point.

The lemma says that the conditioned Borel compositions can be refined one cut at a time without moving the cuts already made. It is a statement about the chain of nested blocks at fixed positions, and differs from the additive coalescent of Theorem 4.10, in which the blocks are exchangeable; conversely, a sequence of weights for which this deletion rule works must be Cayley's, up to the changes that do not affect the laws (Appendix B.3, remark after the proof). Its use is the following comparison. If each cut point $s$ carries an additional factor $\lambda_s\le1$, the number of parts becomes smaller in the likelihood-ratio order, because under the coupling the product of the factors decreases when a cut is added; if $\lambda_s\ge\rho$ for all $s$, the number of parts is larger than under the homogeneous factor $\rho$. When the number of parts is left free and a composition of $m$ has probability proportional to the product of $a_\gamma$ over its parts, the number of parts $Q$ has the birthday law $\Pr(Q\ge j)=(m)_j/m^j$: by the proof of Corollary 6.3(d), $Q-1$ is the depth of a uniform vertex of a uniform rooted tree on $m$ vertices, and Corollary 6.3(c) gives its law. Its moments are explicit.

*Overview of the proof of Theorem 11.7.* The exponent of $y$ in a term of $y\Lambda_m(y)$ is the number of parts. Hence $yK'''/K''$ is the mean of $Q-2$, where $Q$ is the number of parts, under the law that gives a composition its weight in $K$ multiplied by $Q(Q-1)$, the number of ordered pairs of its parts; and since all cut factors $y/(N-s)$ are at most $1$ for $y\le k+2$, the comparison bounds it, for the compositions of each length $m\le r$, by its value $D_m$ under the birthday law, and $D_m\le D_r<1.9\sqrt r$. Integrating, $1\le C_+/C_-\le\exp(D_r/(k-1))$. For the boundary terms, (11.6) gives $B_+/B_-=(1+\frac1k)^{k-2}\Lambda_r(k+2)/\Lambda_{r+1}(k-1)$. Removing the first cell of a composition and the monotonicity in the cut factors that follows from Proposition 7.3 and the FKG inequality give $\Lambda_{r+1}(k-1)\le(1+\frac1r)^r\Lambda_r(k)$, and the comparison with the homogeneous factor $\rho=k/(k+r)$ together with Jensen's inequality gives $\Lambda_r(k+2)/\Lambda_r(k)\ge(1+\frac2k)^{\mu}$, where $\mu$ is the mean number of cuts under the homogeneous law; a moment identity shows $\mu>\frac67\sqrt r-1$ when $k\ge r^{3/2}$. The two bounds combine to $k\log\frac{B_+C_-}{B_-C_+}>\mathcal M(r,k)$ for an explicit rational function $\mathcal M$, which is positive for $r\ge256$ by these estimates and, for $2\le r\le255$, for all $k\ge r^{3/2}$ except $122$ pairs $(r,k)$; at those pairs, all with $n\le102$, the cross product is computed exactly and is positive.

The hypothesis $k\ge r^{3/2}$ enters only at the end: the gain of the boundary ratio over $1$ is about $\frac{12}{7}\sqrt r/k$ from the cuts and $\frac1{2r}$ from the Cayley coefficients, and the excess of the curvature ratio is at most $1.9\sqrt r/k$; the balance is positive when $k/r$ is at least of the order of $\sqrt r$.

### 11.6 The reduction of the conjecture

**Corollary 11.9** (reduction) [proved; it uses Theorem 11.7, whose proof uses the finite computations of the script `c08_propagation.py`]. Let $n\ge2$ and suppose that $d_{n,k}\ge0$ for every $k$ with $1\le k\le n-1$ and $k<(n-k)^{3/2}$. Then the row of $n$ is unimodal.

*Proof.* If no step is negative, the row is non-decreasing. Otherwise let $k_1$ be the smallest index with $d_{n,k_1}<0$; by hypothesis $k_1\ge(n-k_1)^{3/2}$. If $n-k_1\ge2$, Theorem 11.7 at $(n,k_1)$ shows that all later steps are negative; if $n-k_1=1$ there is no later step. By (3.1) the row is unimodal. $\square$

The rows of all $n\le300$ have been computed in exact integer arithmetic and are unimodal [computational evidence; Appendix C, item C5]. Therefore:

> **Target T.** For every $n\ge301$ and every $k$ with $1\le k\le n-1$ and $k^2<(n-k)^3$: $d_{n,k}\ge0$.
>
> Target T implies Conjecture P [proved, by Corollary 11.9, using the exact computation of the rows with $n\le300$, script `c13_rows.py`, and, through Theorem 11.7, the computations of the script `c08_propagation.py`]. Target T itself is a **conjecture**; it is not proved here, and the grounds for it are stated next.

What is known about Target T is the following. It holds for $n\ge21k^2$ (Theorem 11.4) [proved]. The same inequality, asked for smaller $n$ and all $k$ with $k^2<(n-k)^3$, holds for all $95\le n\le300$, and fails for exactly $81$ values of $n\le94$, the smallest being $4$ and the largest $94$; those rows are unimodal all the same [computational evidence; item C5]. In the computed range the first negative step sits just behind the curve $k=(n-k)^{3/2}$ and moves away from it slowly:

| $n$ | first $k$ with $d_{n,k}<0$ | $r=n-k$ | $k/r^{3/2}$ |
|---|---|---|---|
| 94 | 76 | 18 | 0.995 |
| 95 | 77 | 18 | 1.008 |
| 100 | 82 | 18 | 1.074 |
| 150 | 127 | 23 | 1.151 |
| 200 | 173 | 27 | 1.233 |
| 300 | 265 | 35 | 1.280 |

No step $d_{n,k}$ with $n\le300$ is zero. The curve $k=(n-k)^{3/2}$ is the scale of the limit law: on it $n-k=k^{2/3}$, so that $(n+1-k)/(n+1)^{2/3}$, the normalisation of Theorem 8.3 applied to the position $k$ in place of the maximum, tends to $1$ as $n\to\infty$; and Target T says that the row has no decrease at the positions where the deficit is larger than on the curve. For large $n$ this is what one expects if the mode of the limit law lies below $1$ and the convergence is regular enough to be read off neighbouring terms; neither is proved here.

### 11.7 A second route

The propagation theorem covers the part of the first layer behind the curve. The exact computations suggest that the cross product is positive on the whole first layer.

> **Conjecture 11.10.** $\mathcal S_{n,k}>0$ for every position of the first layer, that is, for all $k\ge3$ and $k+2\le n\le2k-1$.

Grounds: the cross product is positive at all $15{,}252$ first-layer positions with $n\le250$ [computational evidence; item C5]; it is proved for $k\ge(n-k)^{3/2}$ (Theorem 11.7), which contains the two infinite families at the end of the layer, $n=k+2$ for all $k\ge3$ and $n=k+3$ for all $k\ge6$. This is the sharpest proved form; the conjecture is the open form. The estimates of Appendix B.3 do not extend to the whole layer, because for $r$ of the order of $k$ the excess of $C_+/C_-$ over $1$ and the gain of $B_+/B_-$ are both of order $\sqrt r/k$ with constants that the present bounds do not separate.

**Corollary 11.11** [proved]. Let $n\ge4$. Suppose that $d_{n,k}\ge0$ for $1\le k\le\lfloor n/2\rfloor$ and that $\mathcal S_{n,k}>0$ for all first-layer positions $(n,k)$. Then the row of $n$ is unimodal.

*Proof.* The first-layer positions of the row are those with $\lfloor n/2\rfloor+1\le k\le n-2$. If $k_1$ is the first index with $d_{n,k_1}<0$, then $k_1\ge\lfloor n/2\rfloor+1$, and (11.7) applied at $k_1,k_1+1,\dots,n-2$ shows that all later steps are negative. $\square$

Thus Conjecture P follows from Conjecture 11.10 together with the non-decrease of the rows $n\ge15$ on their left halves, $d_{n,k}\ge0$ for $k\le\lfloor n/2\rfloor$, the rows with $n\le14$ being known [proved, by Corollary 11.11, using the exact computation of the rows with $n\le14$, script `c13_rows.py`]. The non-decrease on the left half holds for $n=1,3,13$ and for all $15\le n\le300$, and fails for $n\in\{2,4,5,6,7,8,9,10,11,12,14\}$ [computational evidence; item C5]. Compared with Target T, this route replaces the sign of the step in the part of the first layer before the curve by the sign of the cross product there.

### 11.8 Exact facts that constrain strategies

The following facts are exact computations. Each rules out a natural strengthening.

1. *The rows are not log-concave* [counterexample; item C5]. The first failure is at $n=80$: $b_{80,40}^2<b_{80,39}\,b_{80,41}$, and every row with $80\le n\le300$ fails to be log-concave. So unimodality cannot be obtained from log-concavity of the rows. Section 7.3 records a related fact, that kernels built from Cayley's coefficients are not totally positive of order $2$ because these coefficients are log-convex; a derivation of the failure at $n=80$ from that fact is not given here.
2. *The ratio of curvature to boundary is not log-concave in $k$* [counterexample; item C9]. For all $1\le k\le n-1$ define $C_{n,k}$ and $E_{n,k}$ by the formulas for $C_-$ and $B_-$ of Section 11.4 with the frozen polynomial $K_{n,k}$ of the same $k$; then $d_{n,k}=C_{n,k}-E_{n,k}$ for every position, and $d_{n,k}>0$ exactly when $R_n(k)=C_{n,k}/E_{n,k}>1$. For $n=172$: $R_{172}(87)^2<R_{172}(86)\,R_{172}(88)$. So the passage of the ratio through $1$ cannot be controlled by log-concavity in $k$.
3. *No argument outcome by outcome* (Counterexample 11.2).
4. *No argument from the class of models* (Counterexamples 7.4 and 7.5): the analogous sequences for four spare spots and for binary offspring are not unimodal.
5. *The proved regions contain no violation in the computed range, and they are far from sharp* [computational evidence; item C5]. For $n\le300$ there is no position with $n\ge21k^2$ and $d_{n,k}\le0$ among the $609$ such positions, and none with $k\ge4(n-k+1)^{3/2}$ and $d_{n,k}\ge0$ among the $2629$ such positions. For $n=300$ the two regions are $k\le3$ and $k\ge284$, while the row increases up to $k=264$ and decreases from $k=265$ on. The region of Theorem 11.5 has the scale of the first decrease, a deficit of order $n^{2/3}$; the region of Theorem 11.4 reaches only thresholds of order $\sqrt n$.

One more exact tool belongs here, because it is the natural expansion for the left half, where disjoint heavy subtrees matter. Call a vertex $v$ of the marked forest of Theorem 4.6(b) a *minimal violator* (for the threshold $k$) if $D_v\ge k$ and $D_w<k$ for all proper descendants $w$ of $v$. The event $M<k$ is the event that there is no minimal violator.

**Proposition 11.12** (expansion over minimal violators) [proved; checked against the recursion for $n\le14$, Appendix C, item C7]. For $n\ge0$ and $k\ge1$,
$$
Z_n(k)=\sum_{j\ge0}(-1)^j\beta_j(n,k),\qquad
\beta_j(n,k)=\frac{n!}{j!}\sum_{s_1,\dots,s_j}\ a_{\gamma}\,\gamma^{\,j}\ \prod_{i=1}^{j}\frac{(s_i-k)\,Z_{s_i-1}(k)}{s_i!},
$$
where the sum is over the $j$-tuples of integers $s_i\ge k+1$ with $\gamma=n+1-s_1-\dots-s_j\ge1$; $\beta_0(n,k)=p_n$, and $\beta_j(n,k)=0$ when $j(k+1)>n$. In particular $Z_n(k)=p_n-\sum_{s=k+1}^{n}\binom ns(s-k)\,Z_{s-1}(k)\,(n-s+1)^{n-s}$ for $n\le2k+1$.

*Proof.* Minimal violators have pairwise disjoint subtrees, each with at least $k+1$ vertices. By inclusion and exclusion, the indicator of the event that there is none is $\sum_j(-1)^j$ times the number of $j$-element sets of minimal violators. The expected number of ordered $j$-tuples of vertices with disjoint subtrees of sizes $s_1,\dots,s_j$ is given by Theorem 6.2 for the pattern with $j$ nodes of type descendant attached to the root: multiplied by $p_n$ it is $n!\,a_\gamma\gamma^j\prod_ia_{s_i}$. By Theorem 6.2(b) the subtrees are independent uniform rooted trees, and the probability that the root of a uniform rooted tree with $s$ vertices is a minimal violator is $\frac{s-k}{s}\cdot Z_{s-1}(k)/p_{s-1}$, because the forest below the root is uniform on $s-1$ vertices. Finally $a_s\cdot\frac{s-k}s\cdot\frac1{p_{s-1}}=\frac{s-k}{s!}$. $\square$

### 11.9 The open targets, in indices

The following statements are not proved in this document. Items 1 to 5 are conjectures in the sense of Section 1.3, the grounds being the computations and partial results quoted with each; item 6 is an open question. Each is stated so that it can be taken up separately; $d_{n,k}=b_{n,k}-b_{n,k-1}$, and $b_{n,\ell}$ is as in Section 3.1.

1. **Target T** (Section 11.6): for all $n\ge301$ and $1\le k\le n-1$ with $k^2<(n-k)^3$, $d_{n,k}\ge0$. It implies Conjecture P. By Theorem 11.4 only the positions with $n<21k^2$ remain. They are the positions of items 2 and 4 together with the central positions $k=\lceil n/2\rceil$: given Theorem 11.4, Target T is equivalent to the conjunction of item 2, item 4 and the inequality $d_{n,\lceil n/2\rceil}\ge0$ for $n\ge301$ of item 3 [proved: for $n\ge301$ the positions with $k<\lceil n/2\rceil$ satisfy $k^2<(n-k)^3$, and those with $k>\lceil n/2\rceil$ and $k^2<(n-k)^3$ have $n-k\ge2$ and lie in the first layer].
2. **The left region** $n\ge2k+1$ (equivalently $k<\lceil n/2\rceil$): for all $n\ge301$ and all $k$ with $2k+1\le n<21k^2$: $d_{n,k}\ge0$. In the computed rows the inequality holds at all positions with $2k+1\le n$ for $15\le n\le300$ [computational evidence; item C5]. Here pairs of heavy vertices in disjoint subtrees contribute, and the tools are Proposition 11.1, the bound of Theorem 11.4 with its proof, and Proposition 11.12.
3. **The centre**: the step at the middle index $m=\lceil n/2\rceil$ of every row. For even $n$ this is the position $n=2k$, which lies between the left region and the first layer; for odd $n\ge5$ it is the first position of the first layer, $n=2k-1$. The target is: *for every $n\ge301$, $d_{n,m}\ge0$, that is, $b_{n,m}\ge b_{n,m-1}$.* It is the instance $k=m$ of Target T, since $m^2<(n-m)^3$ for these $n$. The earlier research stated the centre in a weaker form, which is recorded here in its own indices: *for every integer $n\ge1$, with $m=\lceil n/2\rceil$, there is no integer $j$ with $m\le j\le n-2$ such that $b_{n,m-1}>b_{n,m}$ and $b_{n,j}<b_{n,j+1}$*; it only forbids an increase after a decrease at the centre, and it follows from $d_{n,m}\ge0$. Tools: for $n\le2k+1$ the skeleton is a path, so the expansion (11.5) of the frozen polynomial holds at $n=2k$ as well (with $r=k$), and so does the closed formula of Proposition 11.12; the formula (11.6) for $B_-$ does not hold at $n=2k$, because a forest can then contain two vertices with $t_v=k$, in disjoint subtrees, and the corresponding term has to be added. For $n\le300$ the weaker statement holds, because the rows are unimodal. The inequality $d_{n,m}\ge0$ itself holds for $16\le n\le300$, where $d_{n,m}>0$, and fails for $2\le n\le15$, where $d_{n,m}<0$ [computational evidence; item C5]. At the position $n=2m$ two disjoint subtrees of size $m$ are possible for the first time.
4. **The first layer before the curve**, apart from the central position: for all $n\ge301$ and all $k$ with $\lceil n/2\rceil<k$ and $k^2<(n-k)^3$: $d_{n,k}\ge0$, that is, $C_-\ge B_-$ in the notation of Proposition 11.6. These positions lie in the first layer. In the computed rows the inequality holds at all such positions for $95\le n\le300$ [computational evidence; item C5]. The tools are (11.5), (11.6) and Lemma 11.8.
5. **Conjecture 11.10** (cross product on the whole first layer), which with the left half ($d_{n,k}\ge0$ for $k\le\lfloor n/2\rfloor$, all $n\ge15$) and the computed rows $n\le14$ also implies Conjecture P (Corollary 11.11).
6. **The regularity behind the curve.** Section 11.6 describes informally that for large $n$ the first negative step lies behind the curve $k=(n-k)^{3/2}$. For all sufficiently large $n$, the part of Target T in which $n-k$ is at most a fixed multiple of $n^{2/3}$ would follow from two statements, neither of which is proved here. Let $G(x)=\Pr(X\le x)=1-\psi(x^{3/2})$ be the distribution function of the limit variable of Theorem 8.3, with $\psi$ the series given after that theorem. (i) *The shape of the limit law*: there is a number $x_0<1$ such that $G''>0$ on $(0,x_0)$ and $G''<0$ on $(x_0,\infty)$. Numerically this is what the series shows: on the grid $x=0.01,0.02,\dots,6$ one finds $G''>0$ for $x\le0.59$ and $G''<0$ for $x\ge0.60$, with a zero at $x_0=0.59962\ldots$ [computational evidence: floating-point evaluation of the series; Appendix C, item C12]. (ii) *A local limit theorem for the step*: with $x=(n+1-k)/(n+1)^{2/3}$,
$$
(n+1)^{4/3}\,\frac{d_{n,k}}{p_n}=-G''(x)+o(1)\qquad(n\to\infty),
$$
uniformly for $x$ in every compact subset of $(0,\infty)$. The form of (ii) is what the convergence in distribution suggests: $b_{n,k}/p_n=\Pr(M=k)$ should be close to $(n+1)^{-2/3}G'(x)$, and a step of $k$ by one is a step of $x$ by $-(n+1)^{-2/3}$. From (i) and (ii) it follows that for every compact interval $I\subset(x_0,\infty)$ there is $n_0$ with $d_{n,k}>0$ for all $n\ge n_0$ and all $k$ with $x\in I$ [proved: $-G''$ is continuous and positive on $I$, hence bounded below there by a positive number]; since the curve corresponds to $x$ near $1$, this settles, for all sufficiently large $n$, the part of Target T in which $n-k$ is at most a fixed multiple of $n^{2/3}$. The positions between the left region and that window would still have to be treated. The known proof of the limit law rests on the convergence of the process of the largest block [Pet, Theorem 3.2] and on a Poisson approximation for conditionally independent events along it [Pet, Lemma 4.2]; a proof of (ii) would have to sharpen both to statements about single values of $k$, and the paper contains no local statement (Remark 8.4). In the computed rows the peak is at the values $0.92$, $0.85$, $0.82$ of $(n+1-\ell)/(n+1)^{2/3}$ for $n=100,200,300$ [computational evidence; item C5]; these are still far from the numerical value of $x_0$, so the convergence in (ii), if it holds, is slow.

The earlier research divided Conjecture P into four statements. Each of them is made for every $n\ge1$, with $m=\lceil n/2\rceil$, and forbids a pair of indices $i<j\le n-2$ with $b_{n,i}>b_{n,i+1}$ and $b_{n,j}<b_{n,j+1}$, that is, a decrease followed later by an increase, for one range of the pair: both on the left, $0\le i<j<m$; across the centre, $0\le i<m-1$ and $m\le j$; at the centre, $i=m-1$ and $m\le j$, which is the weaker form quoted in item 3; and both on the right, $m\le i<j$. The four ranges exhaust the pairs $i<j\le n-2$, so by (3.1) the four statements together are Conjecture P. The derivations that follow are proved by the statements they name. In the present terms, for $n\ge301$, the first two follow from $d_{n,k}\ge0$ for $k<m$, which is item 2 together with Theorem 11.4; the third follows from item 3; and the fourth follows from Theorem 11.7 together with item 4, or from Conjecture 11.10. For $n\le300$ all four hold, because the rows are unimodal [computational evidence; item C5].

## 12. Questions the structure raises

The questions below are raised by the structure and are not answered in this document. Each is followed by the grounds for asking it; these are not claims about the answer, and all the questions carry the status open. The targets specific to Conjecture P are listed in Section 11.9 and are not repeated.

1. **Which laws give unimodal rows?** The sequence of the maximum displacement is unimodal in every computed row of the original problem, and is not unimodal for four spare spots at $m=121$ or for binary offspring at $n=8$ (Counterexamples 7.4 and 7.5). All three are conditioned Galton–Watson forests with a threshold functional. What property of the law (U) with one empty spot is responsible is not known. Grounds: the two counterexamples show that the answer is not "the forest structure"; a property that separates the cases would be a candidate for the missing ingredient of a proof. An answer would be a property of a law on forests that holds for the law (U) with one empty spot, fails for the laws of the two counterexamples, and implies a comparison of neighbouring terms of the row. [open]

2. **A coupling for the cross product.** Lemma 11.8 refines the conditioned Borel compositions one cut at a time, and it was used to compare the number of parts under different cut factors. The cross product compares two different functionals of the same compositions: two marked parts in (11.5), one distinguished last part in (11.6). Is there a coupling, or a monotone rearrangement, that compares these two directly on the whole first layer? Grounds: Conjecture 11.10 holds at all $15{,}252$ positions computed; the present proof loses a constant because it bounds the two sides separately. An answer would be a proof, by a coupling or otherwise, of the inequality $B_+C_->B_-C_+$ on the whole first layer, or on a part of it that Theorem 11.7 does not cover. [open]

3. **A local form of the limit law.** Theorem 8.3 gives the limit of $(n+1-M_n)/(n+1)^{2/3}$ in distribution. A comparison of neighbouring terms $b_{n,k}$ and $b_{n,k-1}$ in the window where $n-k$ is of the order of $n^{2/3}$ needs more: the two statements (i) and (ii) of Section 11.9, item 6, on the shape of the limit law and on a local limit theorem for the step. Can (ii) be proved from the structure? In the first layer the structure provides exact finite formulas for all the quantities involved, (11.5) and (11.6): sums over compositions whose parts carry Cayley's coefficients, that is, Borel masses up to a power of $e$ that depends only on the total, and whose cut points $s$ carry the factors $y/(N-s)$. Grounds: the table of Section 11.6; the two statements together would settle Target T for large $n$ inside the window, and Theorem 11.5 suggests that to the right of the window cruder bounds suffice. An answer would be a proof of (ii), or of a weaker local statement that still determines the sign of the step in the window. [open]

4. **The process conditioned to stay below the threshold.** The law (W) is the law of the shape of the history forest of a parking process conditioned on $M<k$. Equivalently, let each car that lands in a block of size $h$ survive with probability $\min(1,k/h)$, independently, and condition on the survival of all $n$ cars. The conditioned process is again a Markov chain on the configurations of blocks, but its transition probabilities involve the future through the conditioning. Theorem 6.7 shows that for $k\ge2$ its history does not split under uniform cutting into independent pieces of the same family, once the trees have at least $k+2$ vertices. Is there a description of this conditioned merging process, for instance of the law of the block sizes at intermediate times, that is as explicit as Theorem 4.9? Grounds: the first-layer identities (11.5) and (11.6) are statements about the last stage of this process; an explicit description at all stages would extend them beyond the first layer. An answer would be a formula for the law of the block sizes after $t$ cars under this conditioning, or a proof that this law is not of the product form of Theorem 4.9. [open]

5. **Is the coupling of Lemma 11.8 known, and does it have a continuum limit?** The deletion rule preserves the positions of the cuts already present, which distinguishes it from the fragmentations of exchangeable partitions. It was not found in the sources read for this document (Section 9.4, item 5). Under the law $\mathbb P_1$ of Appendix B.3 (all compositions of $m$, weighted by the product of the Cayley coefficients of their parts) the cut points are those of a renewal sequence with Borel steps conditioned to hit $m$. Since the Borel law has a tail of index $\frac12$, one expects the set of cut points, divided by $m$, to converge as $m\to\infty$ to the zero set of a Brownian bridge, and the coupling, which removes the cut points one at a time, to converge to a process that thins this set. Neither convergence is proved here. Grounds: the remark after the proof in Appendix B.3 shows that the rule characterises the Cayley coefficients, which suggests that it is canonical. An answer to the first part would be a source for the rule; an answer to the second would be a process on the zero set of a Brownian bridge, defined without reference to the discrete rule, to which the rescaled coupling converges. [open]

6. **Other threshold statistics.** For $j\ge1$ let $X^{(j)}(\alpha)$ be the number of cars of $\alpha$ with displacement at least $j$, and for $n\ge2$ let $M_2(\alpha)$ be the second largest displacement, that is, the second term when the displacements are arranged in non-increasing order. Two questions: for $n\ge3$ and $2\le j\le n-1$, is the sequence $\ell\mapsto\#\{\alpha\in\mathrm{PF}_n:X^{(j)}(\alpha)=\ell\}$ unimodal? And is the sequence $\ell\mapsto\#\{\alpha\in\mathrm{PF}_n:M_2(\alpha)=\ell\}$ unimodal for every $n\ge2$? Both statistics are functionals of the same forest (Section 10.1): the generating polynomial of $X^{(j)}$ is given by Theorem 4.6(a) with $w(d)=x^{\mathbf 1\{d\ge j\}}$ and can be computed by the recursion (6.2), and $M_2<j$ exactly when $X^{(j)}\le1$. Proposition 8.2 computes the mean of $X^{(j)}$ for $j=n-q$ with $q\le n/2$. The case $j=1$ is settled [proved]: $X^{(1)}$ is $n$ minus the number of lucky cars, so its generating polynomial is obtained from the product of Proposition 10.1(b) by reversing the order of the coefficients, and is $\prod_{i=1}^{n-1}\bigl((n-i+1)+ix\bigr)$. The coefficients of a product of factors $a+bx$ with $a,b>0$ form a log-concave sequence of positive numbers, because multiplication by such a factor preserves this property: if $c_0,\dots,c_L$ are positive and log-concave, $c_i=0$ for the other $i$, and $e_i=ac_i+bc_{i-1}$, then $e_0,\dots,e_{L+1}$ are positive and $e_i^2-e_{i-1}e_{i+1}=a^2(c_i^2-c_{i-1}c_{i+1})+b^2(c_{i-1}^2-c_{i-2}c_i)+ab(c_ic_{i-1}-c_{i+1}c_{i-2})\ge0$, the last bracket being non-negative because the ratios $c_{i+1}/c_i$ do not increase. A log-concave sequence of positive numbers is unimodal. For $j\ge n$ the sequence has one term. Grounds: these laws were not studied in the earlier research; the weight belonging to $w$ equals $1$ on subtrees with at most $j$ vertices, so the skeleton expansion (Theorem 7.1) applies; both sequences are unimodal in the range computed, the first for all $1\le j\le n-1$ with $n\le40$ and the second for $2\le n\le120$ [computational evidence; Appendix C, item C13]; and the answers can be compared with Conjecture P and with Counterexamples 7.4 and 7.5. An answer would be a proof, or a counterexample with its $n$ and $j$. [open]

## 13. Status of every claim

The table lists every numbered claim of the document, and every claim of the running text that carries a status bracket, with its status and with the support on which the status rests: the place of the proof, the independent checks (Appendix C items for computations; the cited source for results taken from the literature). "Checked" in the last column means that the statement was also tested by exact computation in the range given in Appendix C; it is additional to the proof and is not what the status rests on, except where the status is computational evidence or counterexample.

| claim | content in one line | status | support |
|---|---|---|---|
| Conjecture P (3.1) | every row $b_{n,0},\dots,b_{n,n-1}$ is unimodal | conjecture, due to [CEHHMPU] | rows $n\le300$ unimodal (C5); the reductions of Section 11 |
| Section 3.1, table | the rows for $n\le6$ | computational evidence | C1 |
| Theorem 4.1 | circle argument; $|\mathrm{PF}_n|=(n+1)^{n-1}$; uniform law | proved; classical | proof in 4.1; [FR]; [KW] (not read); checked (C3) |
| Lemma 4.2 | a car lands in a block with probability proportional to its size; displacement uniform on the block | proved; known | proof in 4.1; [Pet, Section 2]; checked (C3) |
| Theorem 4.3 | the parking functions with a given outcome; $Z_n(k)=\sum_\sigma\prod\min(h_i,k)$ | proved; known | proof in 4.2; [CEHHMPU, (6)–(8)], [GL, Lemma 2.5]; checked (C1, C2) |
| Proposition 4.4 | history forest: subtree equals closed block; bijection with decreasing forests; (d) the blocks at earlier times | proved; (a) to (c) known; (d) not found in the sources read | proof in 4.2; [GL, Lemmas 3.2, 3.3] for (a) to (c); Section 9.4, item 1; checked (C2) |
| Lemma 4.5 | under a uniform labeling the counts $\iota_v$ are independent and uniform; hook length formula for forests | proved; the hook length formula and the independence of the events $\iota_v=0$ are known; the full joint law not found in the sources read | proof in 4.2; [GS, Lemma 2.1]; hook length formula checked (C2) |
| Theorem 4.6, Corollary 4.7 | the history forest with the order forgotten is the uniform forest; displacements are uniform marks on subtree sizes; formula (4.4) | proved; known in bijective form | proof in 4.2; [Sh], [GL]; checked (C2) |
| Theorem 4.8 | Poisson Galton–Watson tree conditioned on its size is uniform, for every mean | proved; classical | proof in 4.3; [J12, Example 10.2] |
| Theorem 4.9 | block sizes after $t$ cars are conditioned Borel variables | proved; known | proof in 4.4; [KY], [CL], [P99], [J05], [Pet]; checked (C3) |
| Theorem 4.10 | block sizes form a Markov chain with the additive kernel; same chain as for forests | proved; known, with the identification with the chain of [AP] cited | proof in 4.4; [CL, (1.5) and Section 8], [AP, Lemma 1]; checked (C3) |
| Lemma 6.1 and Corollary | Cayley counts are Borel masses; Lagrange inversion; cancellation of exponentials | proved; classical | proof in 6.1; [FS]; part (b) checked (C3) |
| Theorem 6.2 | pattern formula (6.1) | proved | proof in 6.2; checked (C4) |
| Corollary 6.3 | subtree counts; chains; birthday law of the depth; renewal identity | proved; (a), (c) and (d) known | proof in 6.2; [J16], [MM78, (5.2)], [AP2, (107)], [P01, Section 4.1]; checked (C4) |
| paragraph after Corollary 6.3 | depth of a uniform vertex in a uniform forest with $q$ trees: $\Pr(D\ge d)=(N-q)_d/N^d$ | proved; for $q\ge2$ not found in the sources read | proof in 6.2; Section 9.4, item 7 |
| Proposition 6.4 | last-car recursion; exponential formula | proved; known | proof in 6.3; (6.2): [AF], [Kn98]; (6.3): [CGG], [KP]; checked (C1, C4) |
| Proposition 6.5 | Riccati equation; integrating factor; identity (6.4) | proved | proof in 6.3; checked (C4) |
| Proposition 6.6 | effect of attaching a subtree on a weight | proved | proof in 6.4; checked (C4) |
| Theorem 6.7 | cutting compatible exactly with the weights $c$ and $c/s$; failure for threshold weights from $k+2$ vertices on | proved | proof in 6.4; nearest known result [Pa, Lemma 1]; checked (C4) |
| Theorem 7.1 | skeleton expansion | proved | proof in 7.1; checked (C4) |
| Lemma 7.2, Proposition 7.3 | log-convexity of $a_j$; lattice condition if and only if log-convex | proved | proof in 7.3; checked (C4) |
| Section 7.3 | a kernel $(n,t)\mapsto a_{n-t}$ is totally positive of order $2$ if and only if $(a_j)$ is log-concave | proved | argument at the place |
| Counterexample 7.4 | spare spots, $(m,r)=(121,5)$: not unimodal | counterexample | C9 |
| Counterexample 7.5 | binary offspring, even $n=8,\dots,20$: not unimodal | counterexample | C9 |
| Propositions 7.6, 7.7 | street decomposition; trees are unions of prime pieces | proved; 7.6 classical | proof in 7.5; [GS, Section 10]; checked (C4) |
| Section 7.5, last paragraph | $F_k$ has a simple pole at a positive $\rho_k$ with $C_k(\rho_k)=1$; $C_k(\rho_kx)$ generates a probability law | proved | proof in 7.5, using Proposition 6.5 and Pringsheim's theorem |
| Lemma 8.1 | Stirling's formula with a remainder, and consequences for Bor and Ren | proved, from Stirling's formula | proof in 8.1; checked (C11) |
| Proposition 8.2 | $q^{3/2}/(6N)\le\mathbb E\mathsf H_q\le8q^{3/2}/N$ | proved | proof in 8.2; checked (C11) |
| Section 8.2, after Proposition 8.2 | the vertices with deficit at most $j_i<N/2$ have exactly the deficits $j_1<\dots<j_i$ with probability $\mathrm{Bor}(j_1)\cdots\mathrm{Bor}(j_i-j_{i-1})\,\mathrm{Bor}(N-j_i)/\mathrm{Bor}(N)$ | proved | Corollary 6.3(b); argument at the place |
| Theorem 8.3 | limit law of $(n+1-M_n)/(n+1)^{2/3}$ | proved; cited | [Pet, Theorem 5.1], [JP, Corollary 2.4] |
| Remark 8.4 | the steps of the proof of the limit law in [Pet] along the largest block; what (4.4), Corollary 6.3(b) and Proposition 8.2 add for finite $n$ | the steps of [Pet]: proved; cited. The identity: proved, (4.4). The correspondence between them: explanation, no status | [Pet, Theorems 3.2, 4.1, 4.5, Lemma 4.2, Corollary 4.10, proof of Theorem 5.1] |
| Propositions 10.1–10.4 | total displacement, lucky cars; mean and variance; spare spots; a particular car | proved (closed forms in 10.1(b) and after 10.1, 10.2 cited); 10.4 known in substance | proofs in Section 10; [GS], [FPV], [KY], [Kn98]; for 10.4 [J05, (4), (34), p. 183]; checked (C10) |
| Section 10.1, after Proposition 10.1 | the labelings of a fixed forest, counted by $q$ to the number of inversions, give $n!\prod_v[t_v]_q/t_v$; equidistribution of the total displacement with the inversions of labeled trees | proved | Lemma 4.5; Proposition 10.1(a) |
| Section 10.2, after Proposition 10.2 | the first term of the variance is at most of order $n^{5/2}$ | proved | Lemma 8.1 |
| Section 10.2, after Proposition 10.2 | $\operatorname{Var}\mathsf T\sim\frac{10-3\pi}{24}n^3$, hence $\operatorname{Var}\mathsf T\sim\frac14\operatorname{Var}\mathrm{pl}(F)$ | proved; cited | [FPV, Theorem 3, with (24), p. 501]; the numerical values of the exact variance: C10 |
| Proposition 11.1 | $d_{n,k}=V_{n,k}-L_{n,k}$ | proved | proof in 11.1; checked (C6) |
| Counterexample 11.2 | a fixed outcome with a non-unimodal sequence | counterexample | C9 |
| Proposition 11.3 | loss formula and two-sided bound | proved | proof in 11.2; checked (C6) |
| Theorem 11.4 | $n\ge21k^2\Rightarrow d_{n,k}>0$ | proved | Appendix B.1; checked (C5, C7) |
| Theorem 11.5 | $k\ge4(n-k+1)^{3/2}\Rightarrow d_{n,k}<0$ | proved | Appendix B.2; checked (C5, C7) |
| Proposition 11.6 | first-layer identities (11.4)–(11.7) | proved | proof in 11.4; checked (C5, C6) |
| Lemma 11.8 | coupling of Borel compositions | proved | Appendix B.3; checked (C6) |
| Theorem 11.7 | $r\ge2$, $k\ge r^{3/2}\Rightarrow\mathcal S_{n,k}>0$; a decrease continues | proved, using two finite exact computations ($\mathcal M(r,k)$ for $2\le r\le255$; the cross product at $122$ positions, $n\le102$) | Appendix B.3; C8; checked directly for $n\le250$ (C8) |
| Corollary 11.9 | no negative step before the curve implies unimodality of the row | proved, using Theorem 11.7 and thereby its finite computations | proof in 11.6; C8 |
| Section 11.6 | Target T implies Conjecture P | proved, using the exact rows $n\le300$ and, through Theorem 11.7, its finite computations | Corollary 11.9; C5, C8 |
| Section 11.7 | Conjecture 11.10 together with non-decrease on the left halves for $n\ge15$ implies Conjecture P | proved, using the exact rows $n\le14$ | Corollary 11.11; C5 |
| rows $n\le300$ | unimodal; no zero step; table of Section 11.6 | computational evidence | C5 |
| Target T, and its three parts (Section 11.9, items 1 to 4) | $n\ge301$, $k^2<(n-k)^3\Rightarrow d_{n,k}\ge0$ | conjecture | grounds: the statement holds for $95\le n\le300$ (C5); proved part: Theorem 11.4 |
| Remark in Section 11.3 | $d_{n,1}>0$ ($n\ge3$), $d_{n,2}>0$ ($n\ge6$), $d_{n,n-1}<0$ ($n\ge2$) | proved, using the exact rows $n\le300$ | Theorems 11.4, 11.5; C5 |
| Conjecture 11.10 | $\mathcal S_{n,k}>0$ on the whole first layer | conjecture | grounds in 11.7; C5 |
| Section 11.7 | the cross product is positive at all $15{,}252$ first-layer positions with $n\le250$ | computational evidence | C5 |
| Corollary 11.11 | left half and cross product imply unimodality | proved | proof in 11.7 |
| Section 11.8, facts 1, 2 | rows not log-concave ($80\le n\le300$); ratio not log-concave ($n=172$) | counterexample | C5, C9 |
| Section 11.8, fact 5 | no violation in the two proved regions for $n\le300$ | computational evidence | C5 |
| Sections 11.6, 11.7, 11.9 | the inequality of Target T, asked for smaller $n$, fails for exactly $81$ values $n\le94$ and holds for $95\le n\le300$; left halves non-decreasing for $n=1,3,13$ and $15\le n\le300$; central step positive for $16\le n\le300$ and negative for $2\le n\le15$; items 2 and 4 of Section 11.9 hold for $15\le n\le300$ and $95\le n\le300$; peak positions $0.92$, $0.85$, $0.82$ for $n=100,200,300$ | computational evidence | C5 |
| Section 11.9, item 1 and last paragraph | Target T is equivalent, given Theorem 11.4, to items 2 and 4 with the central inequality; the four statements on pairs of indices are together Conjecture P and follow from the items named | proved | arguments at the places; Theorem 11.7, Corollary 11.9 |
| Proposition 11.12 | expansion over minimal violators | proved | proof in 11.8; checked (C7) |
| Lemmas B.1, B.2; remark after Lemma 11.8 | comparison through the coupling; the number of parts; the rule determines the weights | proved | Appendix B.3; checked (C6) |
| Section 11.9, item 6 | statements (i) and (ii) imply $d_{n,k}>0$ for $x$ in a compact subset of $(x_0,\infty)$ and large $n$ | proved | argument at the place |
| Section 11.9, item 6, statement (i), on a grid | $G''$ has one sign change for $0.01\le x\le6$, at $x_0\approx0.5996$ | computational evidence (floating point) | C12 |
| Appendix A, row "stopping the cutting" | the number of deleted edges after which all components have at most $k$ vertices has the law of $n-\tau$ | proved, with the cited identification of Theorem 4.10 | argument in the row |
| Section 12, question 6 | the case $j=1$ of the first question | proved | Proposition 10.1(b) |
| Section 12, question 6 | both sequences unimodal for $n\le40$ (all $j$) and for $2\le n\le120$ | computational evidence | C13 |
| Section 11.9, item 6; Section 12 | questions | open | — |

## Appendix A. The recurring concepts, one by one

This appendix records the test of Section 7.2. The list of concepts was fixed before the account was written, from the vocabulary of the earlier research; one entry stands for a concept, not for each formula in which it occurred. For every concept, except the two that are marked as not examined, the table gives its place in the structure and the statement from which it is derived. The last column classifies it: **D**, a description of the object (Section 4); **N**, the normalisation by size (Section 6.1); **V**, a use of the decomposition at vertices (Sections 6.2 to 6.4); **O**, the observable (Section 5); **P**, part of the problem layer built on these (Section 11); **S**, the street decomposition (Section 7.5); **X**, not an instance, with the place where it attaches; an entry marked "not examined" was not tested.

The earlier notes referred to the dictionary of Section 6.5 by a name of their own, "Cayley–Borel coherence". The name is not used in this document: the content of the dictionary is the standard theory listed in Section 9.

| concept, as it occurred | place in the structure | derived from | class |
|---|---|---|---|
| Cayley's counts of rooted trees and forests: $t^{t-1}$, $(n+1)^{n-1}$, $\binom{N-1}{q-1}N^{N-q}$, unrooted $k^{k-2}$ | the number of rooted labeled forests (the uniform description) and of parking functions | Theorem 4.1, Lemma 6.1; $k^{k-2}$ in (6.4) and (11.2) | D, N |
| the Borel distribution; the critical Boltzmann law | the size of an unconditioned tree; the normalised form of Cayley's coefficient | Theorem 4.8, Lemma 6.1(a) | D, N |
| Borel–Tanner laws and convolutions of Borel masses | the total size of $q$ trees; the block sizes at an intermediate time | Lemma 6.1(b), Theorem 4.9 | N, D |
| the tree function, Lagrange inversion, the square-root singularity | the generating function that passes between fixed size and random size; its singular expansion | Lemma 6.1, Section 8.1 | N; analytic use X (attached through the singularity) |
| Poisson Galton–Watson trees and their conditioning; independence of the mean | the third description of the object | Theorem 4.8 | D |
| the forest representation of the displacements; independent uniform marks on subtree sizes | the second description, with the reason for it: the subtree of a car is the block it closes | Proposition 4.4, Theorem 4.6, Corollary 4.7 | D, O |
| outcome permutations and capacities; the product structure of the parking functions with a given outcome | the history before the order of arrival is forgotten | Theorem 4.3 | D |
| last-car recursion, exponential formula, Riccati equation, integrating factor, the second-difference identity (6.4) | the decomposition at the top of the forest | Propositions 6.4, 6.5 | V |
| marked vertex, ancestral line (spine), depth and the birthday law | the pattern formula for a path of child nodes, summed over sizes | Corollary 6.3(c) | V |
| the renewal sequence $j\,\mathrm{Bor}(j)$; the Borel walk | the factor of a freely attached piece; the sum over the number of pieces on a path | Theorem 6.2, Corollary 6.3(d) | V |
| chains of vertices with prescribed subtree sizes; expected numbers of subtrees of a given size | the pattern formula for a path | Corollary 6.3(a),(b) | V |
| the chain of the largest tree and its transition probabilities; renewal bridges | the skeleton for $n\le2k+1$, where it is a single path and counts are probabilities | Theorem 7.1, Corollary 6.3(a), Proposition 11.6 | V, P |
| edge cutting, fragmentation, additive coalescence | the first description, read forwards and backwards; its failure under the weighted law | Theorems 4.9, 4.10, 6.7 | D, V |
| stopping the cutting when all components are small | a functional of the first description: by Theorem 4.10 the number of uniformly deleted edges of a uniform tree on $N=n+1$ vertices after which every component has at most $k$ vertices has the law of $n-\tau$, where $\tau$ is the largest number of cars after which all blocks of the parking process still have at most $k$ spots [proved, with the identification of the two chains that Theorem 4.10 cites: after $e$ deletions there are $e+1$ components and after $t$ cars $N-t$ blocks, and the property is monotone in time]; the law of $\tau$ is not derived in this document | Theorem 4.10 for the placement only | D (not examined further) |
| growth in $n$: attaching a leaf or a subtree, transplanting identities | the rule by which weights pass through the decomposition | Proposition 6.6 | V |
| curvature decomposition: pairs of heavy vertices against the vertex at the threshold; frozen polynomial | the second difference of the threshold functional | Proposition 11.1, Section 11.4 | O, P |
| first-layer identities: boundary and curvature terms as sums over compositions with Cayley weights | skeleton expansion in the first layer | Proposition 11.6 | V, P |
| order tools: FKG, total positivity of order 2, likelihood-ratio orders, monotone couplings; Harris, Jensen | general theorems applied to laws on compositions; they use the log-convexity of $a_j$ (the FKG inequality and the comparison of laws derived from it), the convolution identity $\sum_{\alpha+\beta=t}\alpha\,a_\alpha a_\beta=(t-1)a_t$ of Cayley's coefficients (the coupling of Lemma 11.8), or nothing from the structure (Harris, Jensen) | Lemma 7.2, Proposition 7.3; Lemma 11.8 for the coupling | X (attached, in this document, through two properties of the Cayley coefficients: their log-convexity, and the convolution identity of Lemma 6.1(b) for two trees; the earlier notes also used the total positivity of the array of forest numbers, a known theorem, see the comment below the table) |
| the exponents $3/2$ and $2/3$; Brownian limit objects | Stirling's formula for $a_j$; first-moment computation on the chain of the giant block; the limit law by citation | Lemma 8.1, Proposition 8.2, Theorem 8.3, Remark 8.4 | N, V; limit theory X |
| breakpoints, prime parking functions, the pole of $F_k$ | a third exact decomposition, along the street | Propositions 7.6, 7.7 | S |
| other statistics and families: total displacement, lucky cars, spare spots | other weights on the same forest; the law (Q) | Section 10 | O, D |
| unrooted trees; vertices minus edges; centroid arguments | $a_k/k$ as the coefficient of the identity (6.4) and of the loss; $T-T^2/2$ | (6.4), Proposition 11.3; Section 6.5 | N, V |
| subtree-size (hook length) weights as a class; recursive trees as the weight $1/s$ | the class of observables; the two weights compatible with cutting | Section 5.1, Theorem 6.7 | O |
| comparison models of the earlier research (forests grown by uniform attachment, and two further models) | replacements of one description by a simpler one; not the object; not examined here | see the note below | X (models) |

Three entries deserve a comment. The chains of the earlier research were used in two ways: as counts of chains of vertices with prescribed subtree sizes, and as the law of the chain that follows the largest subtree downwards. Both are given by Theorem 6.2, but the counts are the probabilities of a well-defined random path only for sizes above $n/2$, where a vertex with a given subtree size is unique (Corollary 6.3(a)). The ancestral line of a marked vertex is a third use, Corollary 6.3(c). The expressions called Palm expressions in the notes are expectations under the law of Theorem 6.2(b), in which a tree is chosen together with a vertex of prescribed subtree size. And the total positivity of the array of forest numbers, which the notes used in the homogeneous case, is a known theorem (Section 9); the inhomogeneous comparison that the problem needs is the cross product of Section 11 and is not a consequence of it.

Some names in the first column come from the earlier research and are used nowhere else in this document; they are defined here in its terms. A *renewal bridge* is the law (7.2) on the cut points of a segment: a sequence of pieces with Cayley weights, conditioned on its total length, with a factor attached to each cut point. The *transplanting* and *leaf-attachment identities* are Proposition 6.6 with $S$ an arbitrary subtree and with $S$ a single vertex. *Palm expressions* are expectations under the law of Theorem 6.2(b), in which a pair consisting of a tree and a vertex with a prescribed subtree size is chosen uniformly. If several such vertices can occur in one tree, the tree is thereby weighted by their number, which is not the same as conditioning on the existence of one; the two coincide when at most one such vertex is possible, as for sizes above $n/2$. *Centroid arguments* use the fact that a tree has one vertex more than it has edges to pass from rooted to unrooted trees; in generating functions this is Lemma 6.1(d). *Stopping the cutting when all components are small* refers to the number of uniformly deleted edges of a uniform tree after which every component has at most $k$ vertices; it is placed by Theorem 4.10 (see the table) and is not treated further in this document; Theorem 6.7 shows why uniform cutting does not preserve the weighted law. Among the *comparison models*, the forest grown by attaching each new vertex to a uniformly chosen earlier vertex, or leaving it as a root, is the random recursive forest, whose shape has the weight $1/s$ of Theorem 6.7; the two further models of the earlier research are not defined or examined here, and nothing in this document depends on them.

## Appendix B. Proofs of the three theorems of Section 11

Notation is that of Sections 3, 5 and 11. In particular $a_j=j^{j-1}/j!$, $\mathrm{Bor}(j)=e^{-j}a_j$, $\mathrm{Ren}(j)=j\,\mathrm{Bor}(j)$, $N=n+1$, and in B.1 the symbol $\mathbb E_k$ denotes expectation under the law (W) of Section 5.3, in which a forest $F$ on $[m]$ has probability $\Phi_{g_k}(F)/Z_m(k)$. In B.3 the letters $\mathbb P$ and $\mathbb E$ with a subscript refer to laws on compositions, which are defined there.

### B.1 Proof of Theorem 11.4 (increase far on the left)

Fix $k\ge1$. Put $c_i=\min(i+1,k)$ and $f_m=Z_m(k)/m!$, so that $F_k(z)=\sum_{m\ge0}f_mz^m$; we write $F$ for $F_k$, and in this subsection forests are denoted by $\mathcal F$. For a forest let $\chi=\chi_k$ be the number of its vertices with $t_v>k$, and let $\mu_m=\mathbb E_k\chi$ for the forests on $m$ vertices ($\mu_0=0$).

*Step 1: $\mu_m\ge\frac{m+1}{2k}-1$ for all $m\ge0$.* For real $y$ with $k\le y<k+1$ the recursion (6.2) with $g=g_y$ reads
$$
Z_m(y)=\sum_{i+j=m-1}\binom{m-1}{i}\min(i+1,y)\,Z_i(y)\,Z_j(y),
$$
and on this interval $Z_m(y)=\sum_{\mathcal F}\Phi_{g_k}(\mathcal F)(y/k)^{\chi(\mathcal F)}$. Applying $y\frac{d}{dy}$ at $y=k$ from the right gives
$$
Z_m(k)\,\mu_m=\sum_{i+j=m-1}\binom{m-1}{i}c_i\,Z_i(k)Z_j(k)\,\bigl(\mu_i+\mu_j+\mathbf 1\{i\ge k\}\bigr),
$$
because at $y=k$, from the right, $y\frac d{dy}\min(i+1,y)$ equals $k=c_i$ if $i\ge k$ and $0$ otherwise. Since $Z_m(k)=\sum\binom{m-1}ic_iZ_iZ_j$, the number $\mu_m$ is a weighted average of the brackets. Group the terms $(i,j)$ and $(j,i)$: they have the same binomial coefficient and the same product $Z_iZ_j$, and weights $c_i$ and $c_j$. We prove the claim by induction on $m$; it holds for $m=0$. If $i,j\ge k$, the bracket is at least $\frac{i+1}{2k}-1+\frac{j+1}{2k}-1+1=\frac{m+1}{2k}-1$. If $i\ge k>j$, the average of the indicator over the two orders is $c_i/(c_i+c_j)=k/(k+j+1)\ge\frac12\ge\frac{j+1}{2k}$, and $\mu_i\ge\frac{i+1}{2k}-1$, $\mu_j\ge0$, so the average of the two brackets is at least $\frac{m+1}{2k}-1$. If $i,j<k$, then $m+1\le2k$, so the bracket, which is non-negative, is at least $\frac{m+1}{2k}-1\le0$.

Consequently, a tree with $a>k$ vertices drawn with probability proportional to $\Phi_{g_k}$ has on average at least $a/(2k)$ vertices with $t_v>k$: its root is one, the factor $k/a$ of the root does not depend on the tree, and the forest below the root follows the law (W) on $a-1$ vertices, so the mean is $1+\mu_{a-1}\ge\frac a{2k}$.

*Step 2: pairs of large trees.* By (6.3), $F'=F\,\Theta$ with $\Theta=\sum_{i\ge0}c_if_iz^i$; $\Theta$ is the generating function of the weighted trees with a marked vertex, in the sense that $z\Theta(z)=\sum_{a\ge1}a\,\omega_az^a/a!$ with $\omega_a$ the total weight of the rooted trees on $a$ labels. Put
$$
P=\sum_{i=0}^{k-1}(i+1)f_iz^i,\qquad C=\sum_{i=0}^{k-1}(k-i-1)f_iz^i,\qquad U=\Theta-P=\sum_{i\ge k}k\,f_iz^i .
$$
Then $\Theta=kF-C$, and $zU$ marks a vertex in a tree with more than $k$ vertices. Since a forest is a set of trees, the sum over the forests $\mathcal F$ on $[n]$ of $\Phi_{g_k}(\mathcal F)\sum|A|\,|B|$, the inner sum over the ordered pairs of distinct trees $A\ne B$ of $\mathcal F$ with more than $k$ vertices each, is $n!\,[z^n]\,(zU)^2F$. We claim
$$
2FU^2=F''-(C+4P)F'+(C'+2P^2)F. \tag{B.1}
$$
Indeed $F'=F\Theta=F(U+P)$, so $FU=F'-PF$ and $UF'=FU^2+P\cdot FU=FU^2+PF'-P^2F$. Differentiating $F'=F\Theta$ and using $\Theta'=kF'-C'$ and $kF=U+P+C$,
$$
F''=F\Theta^2+F(kF'-C')=\bigl(FU^2+2P(F'-PF)+P^2F\bigr)+\bigl(UF'+(P+C)F'\bigr)-C'F=2FU^2+(4P+C)F'-(2P^2+C')F .
$$

Next, $f_if_j\le f_{i+j}$ for all $i,j\ge0$. The recursion (6.2) divided by $(m-1)!$ is $mf_m=\sum_{s=0}^{m-1}c_sf_sf_{m-1-s}$. By induction on $i+j$ (the cases $i=0$ or $j=0$ being trivial),
$$
(i+j)f_if_j=\sum_{s=0}^{i-1}c_sf_s\,f_{i-1-s}f_j+\sum_{s=0}^{j-1}c_s\,f_if_s\,f_{j-1-s}\le\sum_{s=0}^{i-1}c_sf_sf_{i+j-1-s}+\sum_{s=0}^{j-1}c_{i+s}f_{i+s}f_{j-1-s}=(i+j)f_{i+j},
$$
using $f_{i-1-s}f_j\le f_{i+j-1-s}$, $f_if_s\le f_{i+s}$ and $c_s\le c_{i+s}$. In particular $f_{m-1}\le f_m$, since $f_1=1$.

Now take the coefficient of $z^{n-2}$ in (B.1), for $n>k$. The coefficients of $(C'+2P^2)F$ are non-negative. $[z^{n-2}]F''=n(n-1)f_n$. Since $C+4P=\sum_{i<k}(k+3i+3)f_iz^i$,
$$
[z^{n-2}](C+4P)F'=\sum_{i=0}^{k-1}(k+3i+3)\,f_i\,(n-1-i)f_{n-1-i}\le(n-1)f_n\sum_{i=0}^{k-1}(k+3i+3)=(n-1)f_n\,\frac{5k^2+3k}{2}\le4k^2(n-1)f_n .
$$
Hence $[z^{n-2}]FU^2\ge\frac12(n-1)(n-4k^2)f_n$, that is,
$$
\mathbb E_k\sum_{A\ne B,\ |A|,|B|>k}|A|\,|B|\ \ge\ \frac{(n-1)(n-4k^2)}2 . \tag{B.2}
$$

*Step 3: comparison.* Let $n\ge21k^2$. For $k<y<k+1$ and a forest $\mathcal F$ containing two vertices with $t_v>k$, $\Phi_{g_y}(\mathcal F)/y^2=\Phi_{g_k}(\mathcal F)\,y^{\chi(\mathcal F)-2}/k^{\chi(\mathcal F)}\ge\Phi_{g_k}(\mathcal F)/k^2$. Keeping in $Z_n''(y)$ only the ordered pairs of such vertices that lie in different trees, and in $V_{n,k}$ only the interval $(k,k+1)$, on which the weight $1-|y-k|$ has integral $\frac12$,
$$
V_{n,k}\ \ge\ \frac{Z_n(k)}{2k^2}\ \mathbb E_k\sum_{A\ne B}\chi(A)\chi(B),
$$
where $\chi(A)$ is the number of vertices of the tree $A$ with $t_v>k$. Under the law (W) the trees of the forest are independent given their vertex sets, each with probability proportional to $\Phi_{g_k}$; by Step 1 the conditional mean of $\chi(A)$ is at least $|A|/(2k)$ if $|A|>k$. By the independence, the conditional mean of $\chi(A)\chi(B)$ for $A\ne B$ is the product of the two conditional means, and the pairs in which one of the trees has at most $k$ vertices contribute nothing negative. With (B.2), $V_{n,k}\ge Z_n(k)\,(n-1)(n-4k^2)/(16k^4)$. On the other hand the subtrees of the vertices with $t_v=k$ are pairwise disjoint, so $\nu_k\le n/k$ and $L_{n,k}\le Z_n(k)\,n/k^2$. Therefore
$$
\frac{V_{n,k}}{L_{n,k}}\ \ge\ \frac{n-1}{n}\cdot\frac{n-4k^2}{16k^2}\ \ge\ \frac{20}{21}\cdot\frac{17}{16}=\frac{85}{84}>1,
$$
and $d_{n,k}=V_{n,k}-L_{n,k}>0$ by (11.1). $\square$

### B.2 Proof of Theorem 11.5 (decrease far on the right)

Let $1\le k<n$ and $k\ge4R^{3/2}$ with $R=n-k+1\ge2$; then $N=k+R$, $k\ge12$ and $n-k<k$. Put $w_d=\sum_{h=1}^{d-1}\mathrm{Ren}(h)\mathrm{Ren}(d-h)$. We use four facts, all consequences of Lemma 8.1: $\mathrm{Bor}$ is decreasing; $\mathrm{Ren}(j)<(2\pi j)^{-1/2}$; $R^{3/2}\mathrm{Bor}(R)>e^{-1/24}/\sqrt{2\pi}>\frac38$ for $R\ge2$; and $w_d<\frac12$ for all $d\ge2$. For the last one, the function $x\mapsto(x(d-x))^{-1/2}$ is convex on $(0,d)$ (its logarithm is convex), so its value at an integer $h$ with $1\le h\le d-1$ is at most its integral over $[h-\frac12,h+\frac12]$, and $\sum_{h=1}^{d-1}(h(d-h))^{-1/2}\le\int_0^d(x(d-x))^{-1/2}dx=\pi$.

*The curvature.* For non-integer $y\in(k-1,k+1)$, a vertex with $t_v>y$ has $t_v\ge k$, and $\Phi_{g_y}\le1$; so by Proposition 11.1(b), $Z_n''(y)\le(k-1)^{-2}$ times the number of triples (forest, ordered pair of distinct vertices with subtree sizes at least $k$); and the weight $1-|y-k|$ has integral $1$ over $(k-1,k+1)$, so $V_{n,k}$ satisfies the same bound. Since $n<2k$ the two vertices are nested. By Corollary 6.3(b), the number of pairs (forest, chain $v_1,v_2$ with $v_2$ a proper descendant of $v_1$, $t_{v_2}=i$ and $t_{v_1}=i+h$) is $p_n\,\mathrm{Bor}(i)\mathrm{Ren}(h)\mathrm{Ren}(N-i-h)/\mathrm{Bor}(N)$, and $p_n/\mathrm{Bor}(N)=n!\,e^N$. Summing over $h\ge1$ with $N-i-h\ge1$ and over $k\le i\le n-1$, and counting both orders,
$$
\frac{V_{n,k}}{n!\,e^N}\ \le\ \frac{2}{(k-1)^2}\sum_{i=k}^{n-1}\mathrm{Bor}(i)\,w_{N-i}\ <\ \frac{2}{(k-1)^2}\cdot(R-1)\cdot\mathrm{Bor}(k)\cdot\frac12\ <\ \frac{R\,\mathrm{Bor}(k)}{(k-1)^2}.
$$

*The loss.* In (11.2) the forest $E$ has $R-1<k$ vertices, so $\Phi_{g_k}(E)=1$ and every factor is $k/(t_x+k)$. There are $R^{R-2}$ forests $E$ and $R$ attachment places for each. Hence, with $(E,u)$ uniformly distributed,
$$
L_{n,k}=\binom nk k^{k-2}R^{R-1}\ \mathbb E\prod_{x\in P(u)}\Bigl(1+\frac{t_x}{k}\Bigr)^{-1},\qquad \binom nkk^{k-2}R^{R-1}=n!\,e^N\,\frac{\mathrm{Bor}(k)}{k}\,R\,\mathrm{Bor}(R).
$$
Given $E$, a vertex $x$ belongs to $P(u)$ with probability $t_x/R$. By Corollary 6.3(a) for the uniform forest on $R-1$ vertices,
$$
\mathbb E\sum_{x\in P(u)}t_x=\frac1R\sum_{s=1}^{R-1}s^2\,\frac{\mathrm{Ren}(R-s)\mathrm{Bor}(s)}{\mathrm{Bor}(R)}=\frac{\sum_{s}s\,\mathrm{Ren}(s)\mathrm{Ren}(R-s)}{R\,\mathrm{Bor}(R)}=\frac{w_R}{2\,\mathrm{Bor}(R)},
$$
the last step by the symmetry $s\leftrightarrow R-s$. Since $\prod_i(1+x_i)^{-1}\ge1-\sum_ix_i$ for non-negative $x_i$,
$$
\frac{L_{n,k}}{n!\,e^N}\ \ge\ \frac{\mathrm{Bor}(k)}{k}\,R\,\mathrm{Bor}(R)\Bigl(1-\frac{w_R}{2k\,\mathrm{Bor}(R)}\Bigr)=\frac{R\,\mathrm{Bor}(k)}{k^2}\Bigl(k\,\mathrm{Bor}(R)-\frac{w_R}2\Bigr).
$$

*Conclusion.* By the hypothesis, $k\,\mathrm{Bor}(R)\ge4R^{3/2}\mathrm{Bor}(R)>\frac32$; also $w_R/2<\frac14$ and $k^2/(k-1)^2\le\frac{144}{121}<\frac54$. Hence
$$
\frac{L_{n,k}-V_{n,k}}{n!\,e^N}>\frac{R\,\mathrm{Bor}(k)}{k^2}\Bigl(k\,\mathrm{Bor}(R)-\frac{w_R}2-\frac{k^2}{(k-1)^2}\Bigr)>0,
$$
and $d_{n,k}=V_{n,k}-L_{n,k}<0$. $\square$

The same sum $w_d$ counts the ways to nest two marked subtrees and gives the mean cost of re-attaching one; the ratio of the two effects is of order $1/(k\,\mathrm{Bor}(R))$, that is, $R^{3/2}/k$.

### B.3 Proof of Lemma 11.8 and of Theorem 11.7

Throughout, a composition of $m$ is identified with its set $S\subseteq\{1,\dots,m-1\}$ of cut points; its parts are the gaps between consecutive elements of $\{0\}\cup S\cup\{m\}$, and $Q=|S|+1$ is the number of parts. For positive factors $\lambda=(\lambda_s)_{1\le s\le m-1}$ put $\mathcal W_\lambda(S)=\prod_{\text{parts}}a_{\text{part}}\prod_{s\in S}\lambda_s$, as in (7.2), and let $\mathbb P_\lambda$ be the probability law on the subsets of $\{1,\dots,m-1\}$ proportional to $\mathcal W_\lambda$; $\mathbb P_1$ is the law with all factors equal to $1$, and $\mathbb P_\rho$ the law with all factors equal to a constant $\rho$. Thus $\Lambda_m(y;N)$ is the total mass of $\mathcal W_\lambda$ for $\lambda_s=y/(N-s)$. The total mass of the compositions of $m$ with $q$ parts under $\mathcal W_1$ is, by Lemma 6.1(b),
$$
T_{m,q}=[z^m]T^q=\frac qm\,\frac{m^{m-q}}{(m-q)!},\qquad \sum_{q=1}^mT_{m,q}=[z^m]\frac{T}{1-T}=m\,a_m .
$$

**Proof of Lemma 11.8.** Let $X$ have the law $\pi_{q+1}$, $1\le q<m$, and apply the deletion rule. Number the cut points of $X$ from left to right. If the $i$-th cut point has the parts $\alpha$ and $\beta$ on its left and right, it is the first one met exactly when the chosen cell lies in the left part and the chosen cut point is the $i$-th or a later one, or the cell lies in the right part and the chosen cut point is the $i$-th or an earlier one; so it is deleted with probability $\bigl((q+1-i)\alpha+i\beta\bigr)/(qm)$. Let $\mathbf j=(j_1,\dots,j_q)$ be a composition of $m$ with $q$ parts. The compositions from which $\mathbf j$ arises are obtained by dividing one part $j_i=t$ into $\alpha+\beta=t$. By Lemma 6.1(b), $[z^t]T^2=2(t-1)a_t/t$, so by symmetry $\sum_{\alpha+\beta=t}\alpha\,a_\alpha a_\beta=\sum_{\alpha+\beta=t}\beta\,a_\alpha a_\beta=(t-1)a_t$. Hence the total $\mathcal W_1$-mass that the rule sends to $\mathbf j$, divided by $\mathcal W_1(\mathbf j)$, is
$$
\sum_{i=1}^q\frac{(q+1-i)(j_i-1)+i(j_i-1)}{qm}=\frac{(q+1)(m-q)}{qm},
$$
which does not depend on $\mathbf j$. So the result has the law $\pi_q$. Starting from the composition of $m$ into $m$ parts and applying the rule $m-1$ times gives $X_m,X_{m-1},\dots,X_1$ with decreasing sets of cut points. $\square$

*Remark* [proved]. The rule determines the weights. If $(w_t)_{t\ge1}$ is a positive sequence such that, for all $m$ and $q$, the deletion rule maps the law proportional to $\prod w_{\text{part}}$ on compositions with $q+1$ parts to the corresponding law with $q$ parts, then $w_t=c\,\vartheta^ta_t$ for constants $c,\vartheta>0$, and these weights define the same laws as $(a_t)$. Indeed, with $\Xi(t)=\sum_{\alpha+\beta=t}\alpha\,w_\alpha w_\beta/w_t$ the computation above shows that the mass sent to a composition $\mathbf j$ divided by the mass of $\mathbf j$ is $\frac{q+1}{qm}\sum_i\Xi(j_i)$, which must be the same for the compositions $(1,t+1)$ and $(2,t)$; as $\Xi(1)=0$ this gives $\Xi(t)=(t-1)\Xi(2)$. In terms of $G(z)=\sum w_tz^t$ and $c=\Xi(2)$ this reads $c\,(zG'-G)=zGG'$, whose solutions with $G(0)=0$ are $G(z)=c\,T(\vartheta z)$, because $zT'-T=zTT'$.

**Lemma B.1** (comparison) [proved]. Let $\lambda$ be positive factors on $\{1,\dots,m-1\}$. (a) If $\lambda_s\le1$ for all $s$, then $\mathbb P_\lambda(Q=q)/\mathbb P_1(Q=q)$ is non-increasing in $q$. (b) If $\lambda_s\ge\rho>0$ for all $s$, then $\mathbb P_\lambda(Q=q)/\mathbb P_\rho(Q=q)$ is non-decreasing in $q$. In case (a), $\mathbb E_\lambda\phi(Q)\le\mathbb E_1\phi(Q)$ for every non-decreasing $\phi$, and, for $m\ge2$, the same holds for the laws obtained from $\mathbb P_\lambda$ and $\mathbb P_1$ by reweighting with $Q(Q-1)$; in case (b), $\mathbb E_\lambda\phi(Q)\ge\mathbb E_\rho\phi(Q)$.

*Proof.* $\mathbb P_\lambda(Q=q)$ is proportional to $T_{m,q}\,\mathbb E\prod_{s\in S(X_q)}\lambda_s$, with $X_q$ as in Lemma 11.8 and $S(X_q)$ its set of cut points. Since $S(X_q)\subseteq S(X_{q+1})$, the product does not increase with $q$ if all factors are at most $1$; this is (a). For (b) apply the same argument to the factors $\lambda_s/\rho\ge1$, noting that $\mathcal W_\lambda(S)=\mathcal W_\rho(S)\prod_{s\in S}(\lambda_s/\rho)$. If two laws on a finite set of integers have a non-decreasing ratio $\ell$, then $\mathbb E'\phi=\mathbb E[\phi\ell]/\mathbb E[\ell]\ge\mathbb E\phi$ for non-decreasing $\phi$, because two non-decreasing functions of one random variable are non-negatively correlated; reweighting both laws by the same function does not change their ratio. $\square$

**Lemma B.2** (the number of parts under $\mathbb P_1$) [proved]. Under $\mathbb P_1$ on the compositions of $m$: $\Pr(Q\ge j)=P_j:=(m)_j/m^j$ for $1\le j\le m$. With $s_m=\mathbb EQ=\sum_{j=1}^mP_j$,
$$
\mathbb E\,Q(Q-1)=2(m-s_m),\qquad\mathbb E\,Q(Q-1)(Q-2)=3\bigl((m+2)s_m-3m\bigr),
$$
and for $m\ge2$ the number $D_m=\mathbb E\,Q(Q-1)(Q-2)/\mathbb E\,Q(Q-1)$ satisfies $D_m\le\frac32(s_m-1)\le\frac32\sqrt{\pi m/2}<\frac{19}{10}\sqrt m$ and $D_m\le D_{m+1}$.

*Proof.* $\Pr(Q=q)=T_{m,q}/(ma_m)=\frac qmP_q=P_q-P_{q+1}$, which gives the tail. Hence $\sum_jjP_j=m\sum_j\Pr(Q=j)=m$ and $\sum_jj^2P_j=m\,\mathbb EQ=ms_m$, and summation by parts gives $\mathbb EQ(Q-1)=\sum_j2(j-1)P_j$ and $\mathbb EQ(Q-1)(Q-2)=\sum_j3(j-1)(j-2)P_j$, which are the two formulas. From $\mathbb EQ^2=2m-s_m\ge s_m^2$ one gets $(m+2)s_m-3m\le(s_m-1)(m-s_m)$, that is, $D_m\le\frac32(s_m-1)$. Further $s_m-1=\sum_{j\ge1}P_{j+1}$ and $P_{j+1}=\prod_{i=1}^j(1-\frac im)\le e^{-j^2/(2m)}$, so $s_m-1\le\int_0^\infty e^{-x^2/(2m)}dx=\sqrt{\pi m/2}$, and $\frac32\sqrt{\pi/2}<\frac{19}{10}$. Finally $T_{m+1,q}/T_{m,q}=m(1+\frac1m)^{m-q}/(m+1-q)$ is increasing in $q\le m$, so the law of $Q$ for $m+1$ has a non-decreasing ratio to the law for $m$; more precisely, the law for $m+1$ conditioned on $Q\le m$ has a non-decreasing ratio to the law for $m$, and its remaining mass sits at the largest value $m+1$. This persists after reweighting by $Q(Q-1)$, and $D_m$ is the mean of $Q-2$ under the reweighted law; so $D_m\le D_{m+1}$. $\square$

**Proof of Theorem 11.7.** Let $r=n-k\ge2$ and $k\ge r^{3/2}$; then $k\ge r+1$, $k\ge3$, and $(n,k)$ is in the first layer. We use Proposition 11.6.

*Step 1: the curvature ratio.* In $y\Lambda_m(y)$ the composition $S$ contributes a constant times $y^{Q}$. Hence $\frac{d^2}{dy^2}(y\Lambda_m)$ and $\frac{d^3}{dy^3}(y\Lambda_m)$ have non-negative coefficients, and for $y>0$ and $m\ge2$
$$
\frac{y\,(y\Lambda_m)'''}{(y\Lambda_m)''}=\frac{\mathbb E_\lambda\,Q(Q-1)(Q-2)}{\mathbb E_\lambda\,Q(Q-1)},\qquad\lambda_s=\frac{y}{N-s}\quad(1\le s\le m-1).
$$
For $m\le r$ the cut points satisfy $N-s\ge N-r+1=k+2$, so $\lambda_s\le1$ whenever $y\le k+2$, and by Lemmas B.1(a) and B.2 the quotient is at most $D_m\le D_r$. The term $m=1$ of (11.5) is linear in $y$. Since the coefficients in (11.5) are positive, $K'''\ge0$ and $yK'''(y)\le D_rK''(y)$ for $0<y\le k+2$, and $K''>0$. As $K$ is a polynomial, $C_-=\int_{k-1}^{k+1}(1-|y-k|)K''(y)\,dy$ and $C_+=\int_{k-1}^{k+1}(1-|y-k|)K''(y+1)\,dy$. From $K'''\ge0$ and $(\log K'')'\le D_r/y\le D_r/(k-1)$ on $[k-1,k+2]$,
$$
1\ \le\ \frac{C_+}{C_-}\ \le\ \exp\Bigl(\frac{D_r}{k-1}\Bigr). \tag{B.3}
$$

*Step 2: the boundary ratio.* By (11.6) and $a_{k+1}/a_k=(1+\frac1k)^{k-1}$,
$$
\frac{B_+}{B_-}=\Bigl(1+\frac1k\Bigr)^{k-2}\,\frac{\Lambda_r(k+2)}{\Lambda_{r+1}(k-1)} .
$$
We first show $\Lambda_{r+1}(k-1)\le(1+\frac1r)^r\Lambda_r(k)$. Remove the first unit cell from a composition of $r+1$. If its first part is $1$, the part and the cut point $1$ disappear; otherwise the first part $j+1$ becomes $j$. What remains is a composition of $r$ whose cut points carry the inherited factors $\lambda'_i=(k-1)/(N-i-1)$, $1\le i\le r-1$. Reading this backwards, with $h=(k-1)/(N-1)$ the factor of the cut point $1$ and $\gamma_0$ the first part of the composition of $r$,
$$
\Lambda_{r+1}(k-1)=\Lambda'\cdot\Bigl(h+\mathbb E_{\lambda'}\frac{a_{\gamma_0+1}}{a_{\gamma_0}}\Bigr),\qquad\Lambda'=\sum_S\mathcal W_{\lambda'}(S).
$$
(i) $\lambda'_i\le k/(N-i)$, because $N-i\ge k$; hence $\Lambda'\le\Lambda_r(k)$. (ii) $\lambda'_i\ge h$ for all $i$. By Proposition 7.3 and Lemma 7.2, $\mathcal W_h$ satisfies the lattice condition, so by the FKG inequality [FKG, Proposition 1] two non-decreasing functions of $S$ are non-negatively correlated under $\mathbb P_h$. The law $\mathbb P_{\lambda'}$ has with respect to $\mathbb P_h$ a density proportional to $\varpi(S)=\prod_{s\in S}\lambda'_s/h$, which is non-decreasing in $S$. Hence $\mathbb E_{\lambda'}\phi=\mathbb E_h[\phi\varpi]/\mathbb E_h[\varpi]\ge\mathbb E_h\phi$ for every function $\phi$ that is non-decreasing in $S$ (this is the argument of Section 7.3). The first part $\gamma_0=\min(S\cup\{r\})$ is non-increasing in $S$ and $a_{\gamma_0+1}/a_{\gamma_0}$ is increasing in $\gamma_0$ (Lemma 7.2), so $\mathbb E_{\lambda'}[a_{\gamma_0+1}/a_{\gamma_0}]\le\mathbb E_h[a_{\gamma_0+1}/a_{\gamma_0}]$. (iii) For the homogeneous factor $h$ on both lengths the same removal of the first cell gives $h+\mathbb E_h[a_{\gamma_0+1}/a_{\gamma_0}]=\Upsilon(h)$ with
$$
\Upsilon(h)=\frac{\sum_{q=1}^{r+1}T_{r+1,q}h^{q-1}}{\sum_{q=1}^{r}T_{r,q}h^{q-1}}=\mathbb E_h\Bigl[\frac{T_{r+1,Q}}{T_{r,Q}}\Bigr]+\frac{T_{r+1,r+1}}{\sum_{q=1}^rT_{r,q}h^{q-1-r}} .
$$
Both terms are non-decreasing in $h$: the first because $T_{r+1,q}/T_{r,q}$ increases with $q$ (proof of Lemma B.2) and the law of $Q$ under $\mathbb P_h$ increases with $h$ in the likelihood-ratio order, the second because the exponents $q-1-r$ are negative. Since $h<1$, $\Upsilon(h)\le \Upsilon(1)=(r+1)a_{r+1}/(ra_r)=(1+\frac1r)^r$. Together, $\Lambda_{r+1}(k-1)\le\Lambda_r(k)\,\Upsilon(h)\le(1+\frac1r)^r\Lambda_r(k)$.

Next, $\Lambda_r(k+2)/\Lambda_r(k)=\mathbb E_\lambda(1+\frac2k)^{Q-1}$ with $\lambda_s=k/(N-s)$, and $\lambda_s\ge k/(N-1)=\rho$ with $\rho=k/(k+r)$. By Lemma B.1(b) and Jensen's inequality, $\Lambda_r(k+2)/\Lambda_r(k)\ge\mathbb E_\rho(1+\frac2k)^{Q-1}\ge(1+\frac2k)^{\mu}$, where $\mu=\mathbb E_\rho(Q-1)$ on the compositions of $r$. Altogether
$$
\log\frac{B_+}{B_-}\ \ge\ (k-2)\log\Bigl(1+\frac1k\Bigr)-r\log\Bigl(1+\frac1r\Bigr)+\mu\log\Bigl(1+\frac2k\Bigr). \tag{B.4}
$$

*Step 3: a lower bound for $\mu$.* Under $\mathbb P_\rho$ on the compositions of $r$, the variable $J=Q-1$ has $\Pr(J=j)$ proportional to $T_{r,j+1}\rho^j$, that is, to $(j+1)v_j$ with $v_j=\rho^j(r-1)_j/r^j$, $0\le j\le r-1$. From $r\,(j+1)\Pr(J=j+1)=\rho\,(j+2)(r-1-j)\Pr(J=j)$, summed over $j$, $r\mu=\rho\,\mathbb E[(J+2)(r-1-J)]$, and since $1/\rho=1+r/k$,
$$
\mathbb EJ^2+\Bigl(3+\frac{r^2}{k}\Bigr)\mu=2(r-1).
$$
Moreover $\mathbb E\,J(J-1)\le\frac32\mu^2$. To see this, give the pair $(I,H)$ of non-negative integers with $I+H\le r-1$ a probability proportional to $v_{I+H}$. Then $I+H$ has the law of $J$, and given $I+H=j$ the variable $I$ is uniform on $\{0,\dots,j\}$, so $\mathbb E[IH\mid I+H=j]=j(j-1)/6$ and $\mathbb EI=\mathbb EH=\mu/2$. Because $v_{j+1}/v_j$ is decreasing in $j$, the conditional law of $H$ given $I=i$ decreases in the likelihood-ratio order as $i$ grows, so $I$ and $H$ are non-positively correlated: $\frac16\mathbb EJ(J-1)=\mathbb E\,IH\le\mu^2/4$.

Therefore $2(r-1)\le\frac32\mu^2+\bigl(4+\frac{r^2}k\bigr)\mu\le\frac32\mu^2+(4+x)\mu$ with $x=\sqrt r$, since $k\ge r^{3/2}$. If $\mu\le\frac67x-1$, the right side would be at most $\frac{96}{49}x^2-\frac x7-\frac52<2(x^2-1)$. Hence
$$
\mu>\tfrac67\sqrt r-1. \tag{B.5}
$$

*Step 4: the criterion.* For $t>0$, $t-\frac{t^2}2\le\log(1+t)\le t-\frac{t^2}2+\frac{t^3}3$. Inserting these into (B.3) and (B.4),
$$
k\log\frac{B_+C_-}{B_-C_+}\ \ge\ \mathcal M(r,k)+\frac1k,\qquad \mathcal M(r,k)=k\Bigl(\frac1{2r}-\frac1{3r^2}\Bigr)-\frac52+2\Bigl(1-\frac1k\Bigr)\mu-\frac{k}{k-1}D_r,
$$
where $\mu=\mu(r,k)$ is the mean of Step 3 and $D_r$ is as in Lemma B.2. Hence $\mathcal S_{n,k}>0$ whenever $\mathcal M(r,k)\ge0$. Steps 5 and 6 show that $\mathcal M(r,k)>0$ except at finitely many pairs $(r,k)$, and at those pairs the cross product is computed directly.

*Step 5: $r\ge256$.* Here $x=\sqrt r\ge16$ and $k\ge x^3$. By (B.5) and Lemma B.2: $k(\frac1{2r}-\frac1{3r^2})\ge\frac x2-\frac1{3x}$; $2(1-\frac1k)\mu\ge2(1-x^{-3})(\frac67x-1)\ge\frac{12}7x-2-\frac{12}{7x^2}$; and $\frac k{k-1}D_r\le\frac{19}{10}x+\frac{19}{10}\cdot\frac{x}{x^3-1}\le\frac{19}{10}x+\frac2{x^2}$. Hence
$$
\mathcal M(r,k)\ \ge\ \frac{11}{35}x-\frac92-\frac1{3x}-\frac4{x^2}\ >0\qquad(x\ge16),
$$
since the right side is increasing and exceeds $0.49$ at $x=16$.

*Step 6: $2\le r\le255$.* For fixed $r$, $\mathcal M(r,k)$ is strictly increasing in $k$: the first term increases; $\mu(r,k)\ge0$ increases with $\rho=k/(k+r)$, because the law of $J$ increases with $\rho$ in the likelihood-ratio order; and $k/(k-1)$ decreases while $D_r\ge0$. So for each $r$ it suffices to find the smallest integer $k_0(r)\ge r^{3/2}$ with $\mathcal M(r,k_0(r))>0$ and to treat the integers $k$ with $r^{3/2}\le k<k_0(r)$ directly. The numbers $\mathcal M(r,k)$ are rational and were computed exactly: there are $122$ pairs $(r,k)$ with $2\le r\le255$, $k\ge r^{3/2}$ and $\mathcal M(r,k)\le0$; the largest value of $n=k+r$ among them is $102$; and at each of them the integer $\mathcal S_{n,k}=B_+C_--B_-C_+$, computed from the definitions of Section 11.4, is positive (Appendix C, item C8).

*Conclusion.* In all cases $B_+/B_->C_+/C_-\ge1$, so $\mathcal S_{n,k}>0$. If $d_{n,k}\le0$, then by (11.7) $d_{n,k+1}=\frac{B_+}{B_-}d_{n,k}-\mathcal S_{n,k}/B_-<d_{n,k}\le0$. The position $(n,k+1)$ has $r-1$ in place of $r$ and again satisfies $k+1\ge(r-1)^{3/2}$; if $r-1\ge2$ the argument applies again, and after $r-1$ applications all steps $d_{n,k+1},\dots,d_{n,n-1}$ are seen to be negative. $\square$

## Appendix C. Index of computations

All computations cited in this document were carried out by scripts written for this purpose from the definitions in the text, in Python with exact integer and rational arithmetic (the places where decimal arithmetic with 60 significant digits or floating-point arithmetic was used are marked). Parking functions were generated by running the parking process on all lists; forests by enumerating all trees on $\{0,\dots,n\}$ through their Prüfer sequences. The scripts and their recorded outputs accompany the document (folder `computation`, with a `README.md`); the table gives, for each item cited in the text, the scripts, what was checked, the range, and the result.

| item | scripts | what is checked | range | result |
|---|---|---|---|---|
| C1 | `c01_counts.py` | the rows $b_{n,\ell}$ by running the parking process on all $n^n$ lists; formula (4.1) over all permutations; the recursion (6.2); the ends and sums of the rows; agreement with the table of [CEHHMPU] | lists $n\le8$; permutations $n\le9$; recursion $n\le30$; the published table $n\le9$ ($45$ values) | all agree |
| C2 | `c02_forest.py` | Theorem 4.3, Proposition 4.4, Lemma 4.5, identity (4.2), Theorem 4.6(b), formula (4.4) | permutations and forests $n\le7$ (of Lemma 4.5 only the probability of a decreasing labeling, for $n\le6$; the multiset law for $n\le6$); (4.4) over all forests for $n\le8$ ($4\,782\,969$ forests) | all hold |
| C3 | `c03_blocks.py` | Theorem 4.1, Lemma 4.2, Theorem 4.9 (count of lists leaving a given set occupied), Theorem 4.10 (Markov property and additive transition probabilities of the block sizes), Lemma 6.1(b) | circle with $N\le8$ spots, all lists; Theorem 4.10 for $N=7$, all $7^6$ lists and all histories; Lemma 6.1(b) for $q\le m\le14$ | all hold |
| C4 | `c04_pattern.py`, `c05_recursions.py`, `c06_skeleton.py` | Theorem 6.2 for eleven typed patterns and all sizes; Corollary 6.3; Propositions 6.4, 6.5 (including (6.4)), 6.6; Theorem 6.7 for the two weights, its failure for threshold weights, the example $7/216$ and $1/33$; Theorem 7.1 (paths, and all pattern classes with automorphisms); Lemma 7.2; Proposition 7.3; Propositions 7.6, 7.7 | all trees $n\le7$; series to $x^{40}$, $k\le12$; cutting on trees with at most $6$ vertices (threshold weights up to $7$); skeletons for all $k\le n\le7$ and paths for $n\le\min(2k+1,12)$; parking functions $n\le7$ | all hold; for the threshold weight with $k=2,3,4,5$ the cutting property first fails on trees with $4,5,6,7$ vertices. The recorded output contains one line marked FAIL: it tests a sentence of an earlier draft of Section 6.4, according to which the property fails for every $1<k<m$, which is false at $k=m-1$ and was corrected |
| C5 | `c13_rows.py` | all rows; unimodality; zero steps; log-concavity; the data of Sections 11.6 to 11.9; the regions of Theorems 11.4 and 11.5; the cross product on the first layer | $n\le300$ ($44\,850$ steps); cross product at the $15\,252$ first-layer positions with $n\le250$ | every row unimodal; no zero step; rows not log-concave exactly for $80\le n\le300$; all other data as stated in the text |
| C6 | `c11_step.py`, `c12_first_layer.py` | Propositions 11.1 and 11.3; Proposition 11.6 including (11.5), (11.6) from the definitions; the example $(5,3)$; Lemma 11.8; Lemmas B.1 and B.2; the intermediate inequalities (B.3), (B.4), (B.5) of the proof of Theorem 11.7 | forests $n\le7$; the $342$ first-layer positions with $n\le40$ ((11.5), (11.6) from sums over compositions for $n\le26$); Lemma 11.8 for $m\le10$; Lemma B.1 for $m\le9$; Lemma B.2 for $m\le300$; the proof steps at the $633$ positions with $k\ge r^{3/2}$, $n\le80$ (logarithms with 60-digit decimals) | all hold |
| C7 | `c14_two_theorems.py` | the steps of Appendix B.1 (the bound for $\mu_m$, identity (B.1), $f_if_j\le f_{i+j}$, inequality (B.2)) and of Appendix B.2 ($w_d<\frac12$, $R^{3/2}\mathrm{Bor}(R)>\frac38$, the two bounds, the path identity); Proposition 11.12 | $k\le6$, $m\le60$; series to $z^{40}$; (B.2) for $k\le4$, $n\le80$; $d,R\le2000$ (60-digit decimals); the $124$ positions of Theorem 11.5 with $n\le60$; Proposition 11.12 for $n\le14$ | all hold |
| C8 | `c08_propagation.py` | Step 6 of the proof of Theorem 11.7: the rational numbers $\mathcal M(r,k)$ for $2\le r\le255$ and $k\ge r^{3/2}$ up to the first positive value; the cross product at the pairs with $\mathcal M(r,k)\le0$; also $\mathcal S_{n,k}>0$ at all positions with $k\ge r^{3/2}$, $n\le250$ | all $2\le r\le255$ | $122$ pairs with $\mathcal M\le0$, largest $n=102$, cross product positive at each; $\mathcal S_{n,k}>0$ at all $4885$ positions with $k\ge r^{3/2}$, $n\le250$ |
| C9 | `c09_other_families.py`, `c15_ratio.py`, `c11_step.py` | Counterexample 7.4 (spare spots), Counterexample 7.5 (binary offspring), Counterexample 11.2 (a fixed outcome), fact 2 of Section 11.8 (ratio at $n=172$) | spare spots: all $r\le5$, $m\le121$, with brute-force validation of the formula in $19$ small cases; binary: even $n\le20$, with enumeration for $n\le10$; outcomes: all permutations $n\le7$; ratio: exact rationals | as stated in the text |
| C10 | `c10_statistics.py` | Propositions 10.1 to 10.4 | parking functions $n\le7$; spare spots $m\le5$, $r\le3$; the variance formula evaluated at $n=50,100,200$ (floating point for the final division) | all hold |
| C11 | `c07_exponents.py` | the consequences of Lemma 8.1; Proposition 8.2 (formula against enumeration; both bounds) | $m\le3000$; enumeration $n\le7$; bounds for all $n\le300$, $q\le n/2$ (exact) | all hold; in this range $(N\,\mathbb E\mathsf H_q)^2/q^3$ lies between $0.129$ and $1$ |
| C12 | `c17_limit_density.py` | the sign of $G''$ for the distribution function $G(x)=1-\psi(x^{3/2})$ of the limit variable of Theorem 8.3, from the series for $\psi$ differentiated term by term (floating point with `mpmath`: 120 digits and 700 terms, repeated with 200 digits and 1100 terms) | the grid $x=0.01,0.02,\dots,6$; the sign alone for $6\le x\le9$ in steps of $0.1$ | exactly one sign change, from positive to negative, between $0.59$ and $0.60$; zero of $G''$ at $x_0=0.5996252\ldots$; the two runs agree; the checks $-\psi'(0)=\frac23\sqrt{2/\pi}$ and $\psi''(0)=\frac5{12}$ hold to 25 digits. Numerical evidence, not a proof; nothing is claimed for $x>9$ |
| C13 | `c18_threshold_statistics.py` | the generating polynomial of the number of cars with displacement at least $j$, by the recursion (6.2) with the weight of Section 12, question 6, and the counts of the second largest displacement; unimodality of both sequences | validation against all parking functions for $n\le6$; the first sequence for all $1\le j\le n-1$, $n\le40$ ($780$ pairs); the second for $2\le n\le120$ | both sequences unimodal in the whole range |

Two computations are recorded in the `README.md` although the document does not cite them: a check of explicit formulas of the earlier notes for the boundary and curvature terms at $n=k+2$ and $n=k+3$ (`c16_boundary_formulas.py`, $k\le100$; they hold), which Theorem 11.7 supersedes, and the exploration scripts from which the expected values of the items above were first obtained (folder `computation/owner`).

## Bibliography

Theorem, equation and page numbers in the citations are those of the version named in each entry. The table of attributions that accompanies this document (`literature/attributions.md`) records for every citation the passage on which it rests and the way the source was obtained; for an entry marked "not read", the entry says on what the citation rests.

[AF] T. Aguilar-Fraga, J. Elder, R. E. Garcia, K. P. Hadaway, P. E. Harris, K. J. Harry, I. B. Hogan, J. Johnson, J. Kretschmann, K. Lawson-Chavanu, J. C. Martínez Mori, C. D. Monroe, D. Quiñonez, D. Tolson III and D. A. Williams II, Interval and $\ell$-interval rational parking functions, arXiv:2311.14055, version 5; Discrete Mathematics and Theoretical Computer Science 26:1 (2024). Numbering of that version.

[Ald] D. Aldous, Asymptotic fringe distributions for general families of random trees, Annals of Applied Probability 1 (1991), 228–266. Read from a scan; pages 229, 230, 238, 239 and 241 to 243.

[AP] D. J. Aldous and J. Pitman, The standard additive coalescent, Annals of Probability 26 (1998), 1703–1726.

[AP2] D. Aldous and J. Pitman, Tree-valued Markov chains derived from Galton–Watson processes, Annales de l'Institut Henri Poincaré, Probabilités et Statistiques 34 (1998), 637–686.

[BLL] F. Bergeron, G. Labelle and P. Leroux, Introduction to the Theory of Species of Structures, Université du Québec à Montréal, 2013 (the authors' public text; the corresponding book is Combinatorial Species and Tree-like Structures, Cambridge University Press, 1998). Numbering of the 2013 text.

[BP] N. Berestycki and J. Pitman, Gibbs distributions for random partitions generated by a fragmentation process, Journal of Statistical Physics 127 (2007), 381–418. Read as arXiv:math/0512378, version 2.

[BW] A. Björner and M. L. Wachs, $q$-hook length formulas for forests, Journal of Combinatorial Theory, Series A 52 (1989), 165–187. Not read (the file could not be obtained); its Theorem 1.3 is cited as quoted in [CGG2].

[CEHHMPU] K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell, $\ell$-Interval parking functions: Foata invariance, statistic generating functions, and ciphers, arXiv:2507.07243, version 2 (2026); version 1 (2025) is titled "Statistics on $\ell$-interval parking functions". Numbering of version 2.

[CGG] W. Y. C. Chen, O. X. Q. Gao and P. L. Guo, Hook length formulas for trees by Han's expansion, Electronic Journal of Combinatorics 16 (2009), #R62. Read as arXiv:0903.3342, version 1; numbering of that version.

[CGG2] W. Y. C. Chen, O. X. Q. Gao and P. L. Guo, $q$-Hook length formulas for signed labeled forests, arXiv:1004.1811, version 2. Pages 1 to 9 read.

[CL] P. Chassaing and G. Louchard, Phase transition for parking blocks, Brownian excursion and coalescence, Random Structures and Algorithms 21 (2002), 76–119. Read in the authors' posting arXiv:math/0501060; section and equation numbers of that posting.

[CM] P. Chassaing and J.-F. Marckert, Parking functions, empirical processes, and the width of rooted labeled trees, Electronic Journal of Combinatorics 8 (2001), #R14.

[CP] M. Camarri and J. Pitman, Limit distributions and random trees derived from the birthday problem with unequal probabilities, Electronic Journal of Probability 5 (2000), paper 2.

[DFLS] P. Duchon, P. Flajolet, G. Louchard and G. Schaeffer, Boltzmann samplers for the random generation of combinatorial structures, Combinatorics, Probability and Computing 13 (2004), 577–625.

[DG] R. Duarte and A. Guedes de Oliveira, The number of prime parking functions, arXiv:2302.04210, version 1.

[FKG] C. M. Fortuin, P. W. Kasteleyn and J. Ginibre, Correlation inequalities on some partially ordered sets, Communications in Mathematical Physics 22 (1971), 89–103.

[FPV] P. Flajolet, P. Poblete and A. Viola, On the analysis of linear probing hashing, Algorithmica 22 (1998), 490–515.

[FR] D. Foata and J. Riordan, Mappings of acyclic and parking functions, Aequationes Mathematicae 10 (1974), 10–22.

[FS] P. Flajolet and R. Sedgewick, Analytic Combinatorics, Cambridge University Press, 2009. Read in the authors' web edition; numbering of that edition.

[GL] A. Guedes de Oliveira and M. Las Vergnas, Parking functions and labeled trees, Séminaire Lotharingien de Combinatoire 65 (2011), Article B65e.

[GS] I. M. Gessel and S. Seo, A refinement of Cayley's formula for trees, Electronic Journal of Combinatorics 11(2) (2006), #R27.

[J16] S. Janson, Asymptotic normality of fringe subtrees and additive functionals in conditioned Galton–Watson trees, Random Structures and Algorithms 48 (2016), 57–101. Read as arXiv:1312.1211, version 1; numbering of that version.

[HB] F. A. Haight and M. A. Breuer, The Borel–Tanner distribution, Biometrika 47 (1960), 143–150.

[J05] S. Janson, Individual displacements for linear probing hashing with different insertion policies, ACM Transactions on Algorithms 1 (2005), 177–213.

[J12] S. Janson, Simply generated trees, conditioned Galton–Watson trees, random allocations and condensation, Probability Surveys 9 (2012), 103–252. Numbering of the published version (the arXiv version 1 numbers Sections 9 onward one lower).

[JP] S. Janson and N. Petersson, The integral of the supremum process of Brownian motion, Journal of Applied Probability 46 (2009), 593–600. Read as arXiv:0707.0989, version 1; numbering of that version.

[JY] B. R. Jones and K. Yeats, Tree hook length formulae, Feynman rules and B-series, Annales de l'Institut Henri Poincaré D 2 (2015), 413–430; arXiv:1412.6053.

[Kn3] D. E. Knuth, The Art of Computer Programming, Volume 3: Sorting and Searching, Addison-Wesley. Not read. It is cited from [GS], which refers to Exercise 20, p. 70, of the edition of 1973, and from [KY], which refers to Section 6.4 of the edition of 1998.

[Kn98] D. E. Knuth, Linear probing and graphs, Algorithmica 22 (1998), 561–568. Read as arXiv:cs/9801103, pages 1 to 5; numbering of the preprint.

[KP] M. Kuba and A. Panholzer, A unifying approach for proving hook-length formulas for weighted tree families, Graphs and Combinatorics 29 (2013), 1839–1865. Read in the authors' preprint; numbering of the preprint.

[Kr] G. Kreweras, Une famille de polynômes ayant plusieurs propriétés énumératives, Periodica Mathematica Hungarica 11 (1980), 309–320. Pages 309 to 316 read.

[KW] A. G. Konheim and B. Weiss, An occupancy discipline and applications, SIAM Journal on Applied Mathematics 14 (1966), 1266–1274. Not read; the attribution of the product formula without threshold to this paper is taken from [CEHHMPU], and the attribution of the count $(n+1)^{n-1}$ from secondary sources recorded in the table of attributions (row L4-6).

[KY] R. Kenyon and M. Yin, Parking functions: from combinatorics to probability, Methodology and Computing in Applied Probability 25 (2023), Article 32. Read as arXiv:2103.17180, version 1; numbering of that version.

[MM] A. Meir and J. W. Moon, Cutting down recursive trees, Mathematical Biosciences 21 (1974), 173–181. Not read; the attribution of the splitting property to this paper is the common one and is not verified here (the abstract seen does not state the property).

[MM78] A. Meir and J. W. Moon, On the altitude of nodes in random trees, Canadian Journal of Mathematics 30 (1978), 997–1015. Pages 997 to 1008 read.

[P99] J. Pitman, Coalescent random forests, Journal of Combinatorial Theory, Series A 85 (1999), 165–193. Read in the accepted version, Technical Report 457, Department of Statistics, University of California, Berkeley; numbering of that version.

[P01] J. Pitman, Random mappings, forests, and subsets associated with Abel–Cayley–Hurwitz multinomial expansions, Séminaire Lotharingien de Combinatoire 46 (2001), Article B46h.

[Pa] A. Panholzer, Cutting down very simple trees, Quaestiones Mathematicae 29 (2006), 211–227.

[Pap] J. Pappe, A note on the log-concavity of parking functions, arXiv:2412.19783, version 1.

[Pet] N. Petersson, The maximum displacement for linear probing hashing, Combinatorics, Probability and Computing 22 (2013), 455–476. Numbering of the journal article; the summary of the author's thesis (Uppsala Dissertations in Mathematics 63, 2009) numbers the same statements Theorem 2.1 and Corollary 2.11.

[Rob] H. Robbins, A remark on Stirling's formula, American Mathematical Monthly 62 (1955), 26–29. Not read; the attribution of the two-sided bounds to this note is the common one and is not verified here. The citation is not used: the upper bound that Lemma 8.1 needs is proved there.

[Sh] H. Shin, A new bijection between forests and parking functions, arXiv:0810.0427, version 2.

[So] A. D. Sokal, Total positivity of some polynomial matrices that enumerate labeled trees and forests, I: Forests of rooted labeled trees, Monatshefte für Mathematik 200 (2023), 389–452; arXiv:2105.05583. Numbering of the arXiv version 2.

[Tan] J. C. Tanner, A problem of interference between two queues, Biometrika 40 (1953), 58–69.

[Vi] A. Viola, Exact distribution of individual displacements in linear probing hashing, ACM Transactions on Algorithms 1 (2005), 214–242.

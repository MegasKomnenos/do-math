# The staircase of parking functions counted by maximum displacement

This repository is a Lean 4 proof, with Mathlib, of two theorems about the numbers of parking functions of a given length counted by their maximum displacement. The first, the *staircase*, says that each of these sequences rises strictly to a peak and falls strictly after it, with at most one pair of equal neighbours, and that the peak stays where it is or moves one position to the right when the length grows by one. The second is the corollary that each of these sequences is unimodal, which is Conjecture 6.5 of Celano, Elder, Hadaway, Harris, Martin, Priestley and Udell ([arXiv:2507.07243](https://arxiv.org/abs/2507.07243)).

The unimodality was proved in Lean before, by another route, in the repository [`MegasKomnenos/parking-unimodality`](https://github.com/MegasKomnenos/parking-unimodality), which is registered in the [Palomar registry](https://palomar-registry.org/) as PALOMAR-2026-11-25-000002. The proof here is built on the library of that repository. What this repository adds is the staircase, and with it a second proof of the conjecture. As far as the literature search described below found, the staircase was not stated or proved anywhere before this repository and the package from which it was made; that it is new is not established. The repository is laid out for submission to the registry, whose submission form is at <https://submit.palomar-registry.org/>.

## The two theorems

Suppose that $n$ cars arrive one after another at a one-way street with $n$ spots. Each car has a preferred spot, drives to it, and parks in the first empty spot at or after it. The sequence of the $n$ preferences, in the order in which the cars arrive, is a *parking function* of length $n$ if every car parks. The *displacement* of a car is the distance between the spot it takes and its preferred spot, and the *maximum displacement* of a parking function is the largest displacement among its cars. Let $b_{n,\ell}$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$. *Row* $n$ is the sequence $b_{n,0}, b_{n,1}, \dots, b_{n,n-1}$.

Row $n$ has its *peak at* $p$, where $0 \le p \le n-1$, if

$$b_{n,0} < b_{n,1} < \dots < b_{n,p} \;\ge\; b_{n,p+1} > b_{n,p+2} > \dots > b_{n,n-1},$$

and a *strict peak at* $p$ if in addition $b_{n,p} > b_{n,p+1}$. For $p = n-1$ the part of the chain after $b_{n,p}$ is absent.

**Theorem (staircase).** For every $n \ge 2$ there is a position $p$ such that row $n$ has its peak at $p$, and row $n+1$ has its peak at the same $p$ or a strict peak at $p+1$.

**Corollary (unimodality).** For every $n \ge 1$ the sequence $b_{n,0}, b_{n,1}, \dots, b_{n,n-1}$ is unimodal: there is an index $p \le n-1$ such that $b_{n,\ell-1} \le b_{n,\ell}$ for $1 \le \ell \le p$ and $b_{n,\ell+1} \le b_{n,\ell}$ for $p \le \ell \le n-2$.

In Lean the two statements are `Parking.staircase` and `Parking.unimodal_via_staircase`:

```lean
theorem staircase (n : ℕ) (hn : 2 ≤ n) :
    ∃ p, IsPeak b n p ∧ (IsPeak b (n + 1) p ∨ IsStrictPeak b (n + 1) (p + 1))

theorem unimodal_via_staircase (n : ℕ) (hn : 1 ≤ n) :
    ∃ p, p ≤ n - 1 ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ)
```

The first rows show what the staircase describes. Rows 2 to 7, counted for this README by going through all preference sequences, are

$$(2,1),\quad (6,7,3),\quad (24,51,34,16),\quad (120,421,377,253,125),\quad (720,3963,4594,3688,2546,1296),$$

$$(5040,\,42253,\,62145,\,57398,\,46142,\,32359,\,16807),$$

with their peaks at the positions $0, 1, 1, 1, 2, 2$. From row 2 to row 3 and from row 5 to row 6 the peak moves one position to the right, and between the other rows it stays, so both alternatives of the theorem occur. (The conjecture's source tabulates the rows up to $n = 9$.)

Unimodality alone allows equal neighbours anywhere in a row, and it says nothing about how the largest entry of one row stands to that of the next. The staircase says three things more. Every row rises strictly and falls strictly. Two neighbouring entries of a row can be equal in one place only, directly after the peak, and not at all in a row whose peak has just moved. And the position of the peak never decreases when the length grows, and grows by at most one at each step. Two questions stay open. The staircase does not give the position of the peak as a function of $n$, and it does not decide whether the one equality that it allows ever occurs. The package's record of the staircase reports a computation with exact integers that found no two equal neighbours in the rows up to $n = 319$, in the columns up to 279; that computation is not part of the proof and was not repeated for this repository.

### How the Lean statements match the statements in words

The numbers `b n ℓ` are defined in [`Parking/Defs.lean`](Parking/Defs.lean) directly from the parking process. A preference sequence is a function `α : Fin n → Fin n`. `Parking.firstFree` gives the spot that a car takes, `Parking.parkFrom` runs the cars in order of arrival and returns `none` if some car cannot park, `Parking.maxDisp α` is the maximum displacement, or `none` when `α` is not a parking function, and `b n ℓ` counts the `α` with `maxDisp α = some ℓ`.

The peak is defined in [`Staircase/Peak.lean`](Staircase/Peak.lean) for an arbitrary array `f : ℕ → ℕ → ℕ`, and the theorems apply it to the array `b`:

```lean
def IsPeak (f : ℕ → ℕ → ℕ) (n p : ℕ) : Prop :=
  p ≤ n - 1 ∧
    (∀ k, 1 ≤ k → k ≤ p → f n (k - 1) < f n k) ∧
    (p + 1 ≤ n - 1 → f n (p + 1) ≤ f n p) ∧
    (∀ k, p + 2 ≤ k → k ≤ n - 1 → f n k < f n (k - 1))

def IsStrictPeak (f : ℕ → ℕ → ℕ) (n p : ℕ) : Prop :=
  p ≤ n - 1 ∧
    (∀ k, 1 ≤ k → k ≤ p → f n (k - 1) < f n k) ∧
    (∀ k, p + 1 ≤ k → k ≤ n - 1 → f n k < f n (k - 1))
```

The four parts of `IsPeak` are the four parts of the chain above: the position lies in the row; the row rises strictly up to it; the next entry, if the row has one, is not larger; and from the entry after that the row falls strictly. `IsStrictPeak` joins the last two parts into one strict fall.

The Lean statements differ from the statements in words in the following conventions, and none of them changes what is stated.

- Spots and preferences are numbered $0, \dots, n-1$ instead of $1, \dots, n$. A displacement is the difference of a spot and a preference, both shifted by one, so every displacement and every $b_{n,\ell}$ is the same.
- `b n ℓ` is defined for every natural number `ℓ`. The theorems use it only for `ℓ ≤ n - 1` in row `n` and for `ℓ ≤ n` in row `n + 1`.
- All subtractions are subtractions of natural numbers, which stop at zero. In the two theorems each of them is the ordinary difference: `n - 1` occurs only for rows $n \ge 1$, and `k - 1` and `ℓ - 1` occur under `1 ≤ k` and `1 ≤ ℓ`. The displacement of a car is computed as such a difference of its spot and its preference, which is exact because a car parks at or after its preference.
- In the corollary the second range, $p \le \ell \le n-2$ in the conjecture, is written `ℓ + 1 ≤ n - 1`. Natural-number subtraction would make `n - 2` equal to `0` for `n = 1` and admit `ℓ = 0`. Written as `ℓ + 1 ≤ n - 1`, the range is empty for `n = 1`, as it is in the conjecture.
- The hypothesis `1 ≤ n` of the corollary is part of the conjecture. The Lean proof does not use it.
- The staircase is stated from $n = 2$ on, the rows for which the two sign rules behind it are stated and proved. Its instance for $n = 1$ is not part of the theorem. It would say that rows 1 and 2 both have their peak at 0, which is true: row 1 has a single entry, and row 2 is $(2,1)$. The corollary covers row 1.

The conjecture is displayed in its source as a chain $n! = b_{n,0} \le \dots \le b_{n,c} \ge \dots \ge b_{n,n-1} = n^{n-2}$. Its two end values are given in the source (Example 2.8 and Section 6). The corollary formalizes the unimodality and does not restate these end values, and neither theorem asserts the count $(n+1)^{n-1}$ of the parking functions of length $n$.

Jaehyoung Kim, the maintainer of this repository, read the two Lean statements in `Challenge.lean`, with the definitions they use, against the statements in words.

### What is new here, and what was known

*The conjecture.* The unimodality is Conjecture 6.5 of K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell, *ℓ-Interval parking functions: Foata invariance, statistic generating functions, and ciphers*, [arXiv:2507.07243](https://arxiv.org/abs/2507.07243), version 2. Version 1, of 9 July 2025, is titled *Statistics on ℓ-interval parking functions* and numbers the conjecture the same way; arXiv's listing still shows that title. In that paper's terms, a parking function whose maximum displacement is at most $\ell$ is an $\ell$-interval parking function. The paper tabulates $b_{n,\ell}$ for $n \le 9$ and gives the two end values of each row. Just before the conjecture it derives from its enumerative results the inequalities $b_{n,0} \le b_{n,1} \le b_{n,2}$ and $b_{n,n-2} \ge b_{n,n-1}$, and says that experimentally the pattern seems to continue. (Two of these inequalities fail for small $n$, as the rows above show: $b_{2,0} > b_{2,1}$, and $b_{n,1} > b_{n,2}$ for $n = 3, 4, 5$.) The paper gives no proof of the conjecture, and it does not state the staircase.

*The earlier formal proof of the conjecture.* The repository [`MegasKomnenos/parking-unimodality`](https://github.com/MegasKomnenos/parking-unimodality), registered at commit `61ecdf2eb6b2e81ae61fae5df07cae879f3bd157`, proves the unimodality as `Parking.root_unimodal`. Its Lean statement is the statement of `Parking.unimodal_via_staircase` here, over the same definitions. Its proof excludes, in each row, a descent that is followed by an ascent, and it does not determine how the peak of a row stands to the peak of the next row. That proof is written out in words in an unrefereed paper of 143 pages, *Unimodality of the number of parking functions with a given maximum displacement*, in the folder [`solved/parking-unimodality`](https://github.com/MegasKomnenos/do-math/tree/f70448b977718d449348874d98098e6e803d1299/solved/parking-unimodality) of the do-math repository; the paper does not speak of the staircase. So the corollary of this repository is a second proof of a theorem that was already proved formally. It is among the compared theorems because it is the conjecture from which the staircase arose and which the staircase implies.

*The staircase.* As far as the search described below found, it is first presented publicly, as a proved theorem, by the package from which this repository was made, the folder [`solved/parking-staircase`](https://github.com/MegasKomnenos/do-math/tree/f70448b977718d449348874d98098e6e803d1299/solved/parking-staircase) of the do-math repository, and by this repository. Two earlier works of the same project come near it, and neither proves it.

The first is a statement of the library of the repository named above. In a module that is not part of this repository, and outside its compared declaration, that library has `Parking.row_peak`: for $n \ge 335$, row $n$ does not decrease up to a position $p$, rises strictly from $b_{n,81}$ to $b_{n,p}$, satisfies $b_{n,p+1} \le b_{n,p}$ and falls strictly from $b_{n,p+1}$ on, and $p$ lies within a stated distance of order $n^{2/3}$ of the right end of the row. The staircase says more in three respects: it holds for every $n \ge 2$, it is strict from the first entry on, and it relates the peaks of consecutive rows. It says less in one: it gives no bound for the position of the peak.

The second is the earlier of the two research runs on the conjecture, which the section "How the proof was produced" describes. According to the history of the research in the package (`history/timeline.md`, section 4.8), that run recorded two things on 10 November 2026. One is the observation that in exactly computed rows up to $n = 170$ the peak moves by zero or one position from each row to the next; the run did not prove this. The other is a reduction, proved in words and accepted by the run's reviews: if the step of every column, once it is not negative, stays so in all later rows, and the first such row does not decrease from one column to the next, then every row is unimodal; and for rows without equal neighbours a converse holds, under which the peak moves by at most one position exactly when a negative step stays negative one row down and one column to the right. A reduction of this kind was found again in the later run, and the induction on the row by which the staircase follows here from the two sign rules is of the same kind. The reduction is not the staircase, which needs the two rules themselves. The knowledge base of the earlier run as it stood on 12 November 2026 is archived on Zenodo ([doi:10.5281/zenodo.24110810](https://doi.org/10.5281/zenodo.24110810)). By its description the archive holds 340 records, and the description says that the run reached an informal proof of the conjecture, some of whose steps rest on finite checks and on floating-point computations under a stated error model, and that the conjecture remains open. The archive was not opened for this repository, so it was not checked that it contains the two records of 10 November.

*Other sources.* The proof starts from a recursion, on the spot of the car that arrives last, for the number of parking functions whose maximum displacement is at most a given bound. It is Theorem 3.7 of T. Aguilar-Fraga et al. (fifteen authors), *Interval and ℓ-interval rational parking functions*, Discrete Math. Theor. Comput. Sci. 26(1) (2024), Paper 10 ([arXiv:2311.14055](https://arxiv.org/abs/2311.14055)); the library proves it for itself, from the definition of the parking process (`Parking.A_succ`). A limit theorem for the maximum displacement is due to N. Petersson (*The maximum displacement for linear probing hashing*, doctoral thesis, Uppsala University, 2009, Theorem 2.1 of the summary). Read for a parking function of length $n$ chosen uniformly at random, it places all but an arbitrarily small fraction of the sum of row $n$ at a distance of order $n^{2/3}$ from the right end of the row. It is a statement of convergence in distribution and compares no two neighbouring entries of a row, so it decides neither theorem, and the proof does not use it.

*Literature search.* The history of the research in the package records a search made on 19 November 2026 for a proof of the conjecture and for results on the monotonicity of the rows, on the position of their largest entry, or on a local form of the limit law: six queries on arXiv, the lists of the works that cite the conjecture's source, Aguilar-Fraga et al. and Petersson, and keyword queries in zbMATH, OpenAlex and Crossref. About 210 records were examined, by their titles and, for the newest, by their abstracts, and none has such a result. Two keyword queries could not be run, and MathSciNet, Web of Science, Scopus and Google Scholar were not searched. On 25 November 2026, for this repository, the arXiv listing of the papers whose abstract contains "interval parking functions" was read again: twelve records, all by title and the two of 2026 by abstract, and none concerns the shape of these rows. Two further keyword queries on arXiv that day returned no record at all and therefore show nothing. These searches show where a statement like the staircase was looked for and not found. They do not establish that it is new, and whether it is new is not known.

*Previous formalizations.* The repository `MegasKomnenos/parking-unimodality` described above. No other formalization of either theorem is known.

### Why the result is of interest

Unimodality and log-concavity of combinatorial sequences are a classical theme of enumerative combinatorics; Stanley's survey *Log-concave and unimodal sequences in algebra, combinatorics, and geometry* (Ann. New York Acad. Sci. 576, 1989) collects the methods and many examples. Parking functions are standard objects of the same field: they are equinumerous with labelled trees and occur in the study of noncrossing partitions, hyperplane arrangements and diagonal harmonics (see C. H. Yan's survey *Parking functions* in the *Handbook of Enumerative Combinatorics*, 2015).

Parking functions go back to Konheim and Weiss, who studied in 1966 an occupancy discipline in which each ball is placed into the first free cell at or after a cell assigned to it, and applied it to cars that park along a street (*An occupancy discipline and applications*, SIAM J. Appl. Math. 14). Hashing with linear probing places the items of a table by the same discipline. The displacement of a car or of an item has been studied in both settings. For the total displacement of a parking function, the sum of the displacements of its cars, a result on the shape of a sequence of counts is known: the total displacement is essentially equivalent to the sum of the preferences, and the generating polynomial of that sum over the parking functions of length $n$ has log-concave coefficients (J. Pappe, *A note on the log-concavity of parking functions*, [arXiv:2412.19783](https://arxiv.org/abs/2412.19783), Theorem 3.1). For the maximum displacement, the limit theorem of Petersson describes the distribution on the scale $n^{2/3}$, and the shape of the rows is the subject of the conjecture that the seven authors named above posed in 2025. Other conjectures of their paper are being worked on as well: a preprint of November 2026 announces a proof of its Conjecture 6.3, which is on another subject (E. Sombhatta, *Foata and spot commutation for parking functions*, [arXiv:2611.28049](https://arxiv.org/abs/2611.28049)).

Divided by $(n+1)^{n-1}$, row $n$ is the distribution of the maximum displacement of a parking function of length $n$ chosen uniformly at random. In these terms the staircase says that this distribution increases strictly up to its mode and decreases strictly after it, that it has one mode or two neighbouring ones, and that the position of its first mode never decreases and grows by at most one when the length grows by one. The intended readers are enumerative and algebraic combinatorialists who work on parking functions and on unimodality, and analysts of algorithms who study linear probing.

Of the works named in this section, the survey of Stanley was not opened for this repository or for the package; it is cited as the standard reference for its theme. The others were opened, the preprint of Sombhatta for this repository and the rest for the paper of the package. The sentence on what the survey of Yan covers is taken from the README of the repository `MegasKomnenos/parking-unimodality` and was not compared with the survey again.

## What is in this repository

- [`Challenge.lean`](Challenge.lean) states the two theorems with their proofs left as `sorry`, together with the definitions that the statements use. It imports only Mathlib. Its definitions are copied character for character from [`Parking/Defs.lean`](Parking/Defs.lean) and [`Staircase/Peak.lean`](Staircase/Peak.lean), except that `Parking.IsParkingFunction` and `Parking.A` of `Parking/Defs.lean`, which the statements do not use, are left out.
- [`Solution.lean`](Solution.lean) imports the proof in [`Staircase/Main.lean`](Staircase/Main.lean).
- [`comparator.json`](comparator.json) tells Comparator to check `Parking.staircase` and `Parking.unimodal_via_staircase` in the Solution against the Challenge, with the three axioms `propext`, `Quot.sound` and `Classical.choice`.
- [`Staircase/`](Staircase/) is the proof of the staircase: 28 modules, about 7,600 lines.
- [`Parking/`](Parking/) is the library that the proof is built on: 52 modules, about 20,200 lines, with the definitions, the counting and series identities, tables of signs and analytic arguments.
- [`Check.lean`](Check.lean) prints the two statements and the axioms of the two proved theorems.
- [`formalization.yaml`](formalization.yaml) holds the structured metadata: provenance, sources, classification, automation and review.
- [`.github/workflows/palomar-preflight.yml`](.github/workflows/palomar-preflight.yml) runs Palomar's own mechanical verifier on this repository, on demand from the Actions tab.

## Building and checking

The project pins Lean `v4.36.0-rc2` and Mathlib `v4.36.0-rc2`, at commit `9d581dfff2e41de989072ea63abf3daf69311520`. The package from which this repository was made uses the stable `v4.36.0`. This repository uses the release candidate because Palomar's renderer cannot yet display a Challenge built with `v4.36.0`: for that version the renderer's Verso writes KaTeX `.ttf` fonts, which its output sanitizer rejects ([PalomarSubmission issue #203](https://github.com/PalomarRegistry/PalomarSubmission/issues/203), open on 25 November 2026).

```sh
lake exe cache get              # Mathlib's compiled files
lake build                      # the two libraries, Challenge and Solution
lake env lean Check.lean        # the two statements and their axioms
lake comparator --config comparator.json
```

`lake build` prints two expected warnings, one for each `sorry` in `Challenge.lean`. `lake env lean Check.lean` prints the two statements and their axioms:

```
Parking.staircase : ∀ (n : ℕ),
  2 ≤ n →
    ∃ p,
      Parking.IsPeak Parking.b n p ∧
        (Parking.IsPeak Parking.b (n + 1) p ∨ Parking.IsStrictPeak Parking.b (n + 1) (p + 1))
Parking.unimodal_via_staircase : ∀ (n : ℕ),
  1 ≤ n →
    ∃ p ≤ n - 1,
      (∀ (ℓ : ℕ), 1 ≤ ℓ → ℓ ≤ p → Parking.b n (ℓ - 1) ≤ Parking.b n ℓ) ∧
        ∀ (ℓ : ℕ), p ≤ ℓ → ℓ + 1 ≤ n - 1 → Parking.b n (ℓ + 1) ≤ Parking.b n ℓ
'Parking.staircase' depends on axioms: [propext, Classical.choice, Quot.sound]
'Parking.unimodal_via_staircase' depends on axioms: [propext, Classical.choice, Quot.sound]
```

The proof uses no axioms other than `propext`, `Classical.choice` and `Quot.sound`, and it uses neither `sorry` nor `native_decide`. Twenty-two statements of the staircase modules are settled by *tables*, finite computations in exact integer arithmetic that Lean's kernel evaluates itself with `decide +kernel`; by the package's count, the proof also uses thirty-six such statements of `Parking`.

These checks were run on 25 November 2026 on a Windows machine, on the files of this repository with Lean and Mathlib `v4.36.0-rc2`. `lake build`, started with no compiled file of the repository present, compiled the 80 modules, the Challenge and the Solution from their sources and ended with "Build completed successfully", with the two warnings above. Mathlib was neither fetched nor compiled for this: a compiled copy of the pinned commit was on the machine, so `lake exe cache get` was not run. `lake env lean Check.lean` printed the two statements, each with the axioms `[propext, Classical.choice, Quot.sound]`. `lake comparator` accepted the Solution against the Challenge for both theorems, with the proofs replayed and accepted by the kernels con-ron (45,457 declarations), NanoDa and Lean's own, which are the kernels that Palomar uses. Comparator normally builds and exports the project inside a Linux sandbox. On Windows that sandbox is not available, so it was run with `--inadvisably-no-sandbox`. Palomar's verifier runs the same check with the sandbox. Two parts of that verifier were run on the files and passed: its loader of `formalization.yaml`, and its scan of the Lean sources for the `module` header and the limit of 10,000 lines. The verifier as a whole, its licence detector and its renderer were not run; the preflight workflow named above runs the verifier once the repository is on GitHub.

## Outline of the proof

Arrange the numbers $b_{n,k}$ in an array with rows $n$ and columns $k$, and write $d_{n,k} = b_{n,k} - b_{n,k-1}$ for the *step* of row $n$ at column $k$, for $1 \le k \le n-1$. A *position* is a pair $(n,k)$, and a column is called positive, or negative, in a row if its step in that row is. Two rules hold for $n \ge 2$ (`column_rule`, `diagonal_rule` in [`Staircase/Main.lean`](Staircase/Main.lean)):

- a positive step stays positive one row down in the same column: $d_{n,k} > 0 \Rightarrow d_{n+1,k} > 0$;
- a step that is not positive is followed by a negative step one row down and one column to the right: $d_{n,k} \le 0 \Rightarrow d_{n+1,k+1} < 0$.

For any array, the two rules give the staircase by induction on the row (`peak_induction`): if row $n$ has its peak at $p$, the first rule keeps the steps $1, \dots, p$ of row $n+1$ positive, the second makes its steps from $p+2$ on negative, and the one step left decides between the two alternatives; row 2 has a single step and therefore a peak. Unimodality follows at once, because the peak of a row is an index up to which the row does not decrease and from which it does not increase, and row 1 has a single entry.

The rules are proved region by region. The folders and files named in the rest of this outline lie under `Staircase/`, except where the text calls them folders of `Parking`. The *first layer* of column $k$ consists of the rows $k+1 \le n \le 2k-1$. The *curve* is the set of positions with $k^2 = (n-k)^3$, and a position with $(n-k)^3 \le k^2$ lies *behind the curve*.

*A bound for the first positive row of a large column.* `CurveIncrease/` proves that every column $k \ge 265$ has a positive step in a row $j$ with $(j-k-1)^3 \le k^2$, that is, at most one row beyond the curve (`curve_crossing`). The argument reduces the positivity of a step to a comparison of a sum over pairs of marked cut points with a boundary term, bounds the first from below and the second from above, and ends in inequalities between polynomials in $\sqrt{n-k+1}$.

*Persistence.* [`Staircase/Persistence.lean`](Staircase/Persistence.lean) proves four statements. A column $k \ge 82$ has a positive step in a row $k+r$ of its first layer with $r \le 27k/100$ (`positive_row_early`): for $k \le 264$ the row is taken from `Tab.two_signs`, a kernel-evaluated table of `Parking` that lists for each column $9 \le k \le 264$ a row of its first layer in which the step is positive, and for $k \ge 265$ it is the row of `curve_crossing`. In the first layer the step of a column $k \ge 82$ changes sign once, from not positive to positive (`one_sign_change`). A positive step persists in the first layer, for every $k \ge 2$ (`step_persists`); for $k \le 81$ this is read from the table `Tab.small_table` of `Parking`. And the step is positive for $k \ge 82$ and $n \ge 2k$ (`step_pos_large`). The analytic arguments behind the last three statements are theorems of `Parking`: `persist`, in its folder `ChainColumn/`, carries a positive step from an early row to the end of the first layer, and `big_step`, a private lemma of its folder `LeftHalf/`, carries it to the rows $n \ge 2k$. Both take the early positive row as a hypothesis, and `Persistence.lean` supplies that row.

*The column rule.* With its conclusion in the first layer it is `step_persists`. With its conclusion in a row $n+1 \ge 2k$ it is proved in `Beyond/`, which shows that the step in the rows $n \ge 2k$ is positive except at eleven positions in the columns up to 7; where the conclusion of the rule would be one of the eleven, its hypothesis fails, because the step one row above is negative. The positive signs come from three sources. For the column 1 they are proved by an induction on the row. For the columns 2 to 81 a kernel-evaluated table of the staircase modules (`Tab.junction_table`) gives the sign up to a row listed for the column, and from that row on an argument passes a positive step on to every later row. For $k \ge 82$ the sign is `step_pos_large`.

*The diagonal rule.* With its hypothesis at a position with $n \ge 2k$ it is again `Beyond/`. In the first layer of a column $k \le 264$ it is `BeforeCrossing/`. For $9 \le k \le 264$ a step of column $k$ that is not positive lies in a row $n$ before the positive row that `Tab.two_signs` lists for the column, by persistence, and the kernel-evaluated table `Tab.next_column_neg` of the staircase modules shows that column $k+1$ is negative in the row $n+1$. For $2 \le k \le 8$ no sign of column $k$ is needed: the kernel-evaluated table `Tab.negative_cells` of the staircase modules, which gives the negative steps of the columns 2 to 9 in 45 positions, shows that column $k+1$ is negative in every row that the rule asks for. In the first layer of a column $k \ge 265$, `curve_crossing` and persistence place a step that is not positive behind the curve, and there `Diagonal/` proves the rule: the formula `dq_frozen` of `Parking`, which writes the step as a curvature term minus a boundary term, is taken at the position $(n,k)$ and at its diagonal neighbour $(n+1,k+1)$, and the two are compared factor by factor, by Hölder's and Jensen's inequalities for the curvature, an FKG inequality on sets of cut points for the boundary term, and a final inequality between closed forms.

The modules under [`Staircase/`](Staircase/) are arranged as follows.

| Path | Modules | What it holds |
|---|---|---|
| [`Peak.lean`](Staircase/Peak.lean) | 1 | The peak and the strict peak of a row |
| [`Beyond/`](Staircase/Beyond/) | 3 | The signs of the steps in the rows $n \ge 2k$, and the two rules there |
| [`BeforeCrossing/`](Staircase/BeforeCrossing/) | 2 | The diagonal rule in the first layer of the columns up to 264 |
| [`Cayley/`](Staircase/Cayley/) | 3 | Compositions with marked cut points; the curvature sum and the second difference of the frozen polynomial; the ratio of two Borel weights |
| [`CurveIncrease/`](Staircase/CurveIncrease/) | 10 | Every column $k \ge 265$ is positive at most one row beyond the curve |
| [`Persistence.lean`](Staircase/Persistence.lean) | 1 | The early positive row, the single change of sign, persistence, the large columns |
| [`Diagonal/`](Staircase/Diagonal/) | 7 | The diagonal rule behind the curve in the columns $k \ge 265$ |
| [`Main.lean`](Staircase/Main.lean) | 1 | The induction on the row, the two rules, the staircase, unimodality |

## How the proof was produced

The proof was found, written, reviewed and formalized by AI sessions. It comes from *do-math*, an autonomous research system. In a do-math run, AI sessions work in parallel in fixed roles: some attempt proofs or formalize them in Lean, others check and write up what was produced, and a review session decides whether a write-up is published in the run's library.

Two runs worked on the conjecture. The earlier run, from 5 to 13 November 2026, on OpenAI GPT-6.1 and Anthropic Claude models, reached an informal proof of the unimodality that rested on large computer-assisted certificates and was never formalized. It observed the staircase pattern in computed rows and proved in words the reduction described above, and it did not prove the staircase. The later run, from 19 to 23 November 2026, ran on Claude models only: Claude Fable models for attempts, explorations, formalization, peer checks and organization, and Claude Opus models for reviews; the history of the run records them by these names, without a version. It found the proof of the unimodality that the repository `MegasKomnenos/parking-unimodality` holds, and on 23 November it published a record whose Lean modules prove the staircase, without hypotheses, by way of the two sign rules; a review session of the run accepted that record after compiling its modules.

After the run, AI agent sessions simplified the run's library into the library `Parking` of the repository named above. On 24 November 2026 AI agent sessions built the staircase proof anew on that library: one session read the run's proof as a whole and divided the work, further sessions each built one part, one arranged the whole by subject, and three places of the proofs were simplified afterwards. AI sessions also wrote, for the package, records in words of the public declarations that the two theorems rest on, a dependency map, and a paper of 184 pages that presents the proof without Lean; no person has refereed the paper. On 25 November 2026 an AI session made the module-system port and the Palomar files of this repository.

The person who commissioned the research chose the conjecture, gave standing written inputs to the running research, asked for the staircase proof to be built on the library and prepared as a package, and decided what to publish. The runs were started and tended on that person's behalf by an *operator*, an AI session outside the runs. Four times in the later run the operator changed published verdicts of reviews directly, each time setting results back rather than accepting them: three times on that person's instruction or decision, once on its own judgment. No person wrote the proofs or the Lean code.

**Review.** A review session of the later run accepted the run's Lean proof of the staircase. The proof in this repository is that proof built anew on `Parking`; Lean's kernel checks it, and no review session judged it as a whole. In the package, each of the 107 records written for the staircase modules was compared with the Lean, statement by statement and proof by proof, by an AI session that had not written it. Jaehyoung Kim, the maintainer of this repository, read the two Lean statements in `Challenge.lean`, with the definitions they use, against the statements in words. No person has reviewed the proof, and no person has refereed the mathematics.

**The package and the port.** The complete record of this proof is the package [`solved/parking-staircase`](https://github.com/MegasKomnenos/do-math/tree/f70448b977718d449348874d98098e6e803d1299/solved/parking-staircase) of the do-math repository: the Lean proof on stable Lean, the records, the dependency map, the paper, and the history of the two runs. This repository's `Parking/` and `Staircase/` are the folder `lean/` of that package, ported to Lean's module system and to the release candidate.

In every file the port added a `module` header, wrote `public import` in place of `import`, and put the declarations under `@[expose] public section`. Three further changes were needed. Nothing else in the files changed: a script compared the 80 modules with those of the package line by line and found no other difference.

- In `Parking/Table/Columns.lean`, eight definitions (`seqN`, `wmin`, `revAcc`, `sumZ`, `nextA`, `growStep`, `grow` and `col`) lost the keyword `private`. `Parking.Tab.hd`, a public definition that other modules have the kernel evaluate, computes through them, and the module system does not let a public, exposed definition use private ones.
- In `Parking/Counting/SingleChain.lean`, the lemma name `div_left_inj₀` became `div_left_inj'`. Stable Mathlib renamed the lemma on 7 November 2026, with the same statement, and the release candidate has only the old name.
- Twelve modules of `Staircase/` gained, between them, twenty lines of the form `import all Parking.…`, one for each of their commands `open private … from Parking.…`. In the package the staircase proofs reach 38 private declarations of nine modules of `Parking` through the command `open private` of Batteries. Under the module system a private declaration is visible in another module only if that module imports the declaring module with `import all`. With these imports the `open private` commands work as they do in the package, and the 38 declarations stay private. The nine modules, with the number of declarations reached in each, are `Crossing/Bounds.lean` (2), `LeftHalf/BigColumns.lean` (1), `LeftHalf/Propagate.lean` (1), `NextColumn/Birthday.lean` (1), `NextColumn/Compositions.lean` (4), `NextColumn/FirstCell.lean` (11), `NextColumn/Frozen.lean` (2), `NextColumn/Ramanujan.lean` (8) and `Table/TwoSigns.lean` (8), all under `Parking/`.

The first two changes are the ones that the repository `MegasKomnenos/parking-unimodality` made to the same modules. The 52 modules of `Parking/` here therefore have the code of the corresponding modules of that repository at its registered commit: 47 of them are the same files, and five differ in their module comment only (`Parking/Defs.lean`, `Parking/Tilt/Basic.lean`, `Parking/ChainColumn/Main.lean`, `Parking/LeftHalf/BigColumns.lean` and `Parking/LeftHalf/FirstLayer/Main.lean`), where the package words the comment so that it speaks of the mathematics of its module only. The other ten modules of that library are not imported by the staircase modules and are not in this repository. `Check.lean` gained the `module` header and `public import`.

## Licence

The contents of this repository are licensed under the Creative Commons Attribution 4.0 International licence (CC BY 4.0); see [`LICENSE`](LICENSE). The modules under `Parking/` are also in the repository `MegasKomnenos/parking-unimodality`, whose licence is the Apache License 2.0; the licence of this repository does not change that.

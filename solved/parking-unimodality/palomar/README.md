# Unimodality of parking functions by maximum displacement

This repository is a Lean 4 proof, with Mathlib, of Conjecture 6.5 of Celano, Elder, Hadaway, Harris, Martin, Priestley and Udell ([arXiv:2507.07243](https://arxiv.org/abs/2507.07243)): for every length $n$, the numbers of parking functions of length $n$ counted by their maximum displacement form a unimodal sequence. It is laid out for submission to the [Palomar registry](https://palomar-registry.org/), whose submission form is at <https://submit.palomar-registry.org/>.

## The theorem

Suppose that $n$ cars arrive one after another at a one-way street with $n$ spots. Each car has a preferred spot, drives to it, and parks in the first empty spot at or after it. The sequence of the $n$ preferences, in the order in which the cars arrive, is a *parking function* of length $n$ if every car parks. The *displacement* of a car is the distance between the spot it takes and its preferred spot, and the *maximum displacement* of a parking function is the largest displacement among its cars. Let $b_{n,\ell}$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$.

**Theorem.** For every $n \ge 1$ the sequence $b_{n,0}, b_{n,1}, \dots, b_{n,n-1}$ is unimodal: there is an index $p \le n-1$ such that $b_{n,\ell-1} \le b_{n,\ell}$ for $1 \le \ell \le p$ and $b_{n,\ell+1} \le b_{n,\ell}$ for $p \le \ell \le n-2$.

In Lean this is `Parking.root_unimodal`:

```lean
theorem root_unimodal (n : ℕ) (hn : 1 ≤ n) :
    ∃ p, p ≤ n - 1 ∧ (∀ ℓ, 1 ≤ ℓ → ℓ ≤ p → b n (ℓ - 1) ≤ b n ℓ) ∧
      (∀ ℓ, p ≤ ℓ → ℓ + 1 ≤ n - 1 → b n (ℓ + 1) ≤ b n ℓ)
```

The source tabulates $b_{n,\ell}$ for $n \le 9$. Just before stating the conjecture it derives from its enumerative results the inequalities $b_{n,0} \le b_{n,1} \le b_{n,2}$ and $b_{n,n-2} \ge b_{n,n-1}$, and says that experimentally the pattern seems to continue. (Two of these inequalities fail for small $n$: $b_{2,0} = 2 > b_{2,1} = 1$, and $b_{n,1} \le b_{n,2}$ fails for $n = 3, 4, 5$. The theorem proved here holds for every $n$.) As far as the literature search described under "Sources and literature" found, no proof of the conjecture has been published.

### Why the result is of interest

Unimodality and log-concavity of combinatorial sequences are a classical theme of enumerative combinatorics; Stanley's survey *Log-concave and unimodal sequences in algebra, combinatorics, and geometry* (Ann. New York Acad. Sci. 576, 1989) collects the methods and many examples. Parking functions are standard objects there: Konheim and Weiss introduced them in 1966 in their study of hashing with linear probing, and they are equinumerous with labelled trees and occur in the study of noncrossing partitions, hyperplane arrangements and diagonal harmonics (see C. H. Yan's survey *Parking functions* in the *Handbook of Enumerative Combinatorics*, 2015). In hashing, the maximum displacement is the worst-case cost of a search, and Petersson determined its limit distribution (*The maximum displacement for linear probing hashing*, doctoral thesis, Uppsala University, 2009). That limit law places the bulk of each row at distance of order $n^{2/3}$ from its right end, but it compares no two neighbouring entries of a row, so it does not decide unimodality. The conjecture was posed in 2025 by seven combinatorialists working on interval parking functions. The intended readers are enumerative and algebraic combinatorialists who work on parking functions and on unimodality, and analysts of algorithms who study linear probing.

### How the Lean statement matches the conjecture

The numbers `b n ℓ` are defined in [`Parking/Defs.lean`](Parking/Defs.lean) directly from the parking process. A preference sequence is a function `α : Fin n → Fin n`. `Parking.firstFree` gives the spot that a car takes, `Parking.parkFrom` runs the cars in order of arrival and returns `none` if some car cannot park, `Parking.maxDisp α` is the maximum displacement, or `none` when `α` is not a parking function, and `b n ℓ` counts the `α` with `maxDisp α = some ℓ`.

Three conventions differ from the source, and none of them changes the statement.

- Spots and preferences are numbered $0, \dots, n-1$ instead of $1, \dots, n$. A displacement is the difference of a spot and a preference, both shifted by one, so every displacement and every $b_{n,\ell}$ is the same.
- `b n ℓ` is defined for every natural number `ℓ`, and the theorem uses it only for `ℓ ≤ n - 1`.
- The second range, $p \le \ell \le n-2$ in the conjecture, is written `ℓ + 1 ≤ n - 1`. Natural-number subtraction would make `n - 2` equal to `0` for `n = 1` and admit `ℓ = 0`. Written as `ℓ + 1 ≤ n - 1`, the range is empty for `n = 1`, as it is in the conjecture.

The conjecture is displayed as a chain $n! = b_{n,0} \le \dots \le b_{n,c} \ge \dots \ge b_{n,n-1} = n^{n-2}$. Its two end values are proved in the source (Example 2.8 and Section 6). The Lean theorem formalizes the unimodality and does not restate these end values; it also does not assert or assume the count $(n+1)^{n-1}$ of parking functions.

## What is in this repository

- [`Challenge.lean`](Challenge.lean) states the theorem with its proof left as `sorry`, together with the definitions that the statement uses. It imports only Mathlib. Its definitions are copied character for character from [`Parking/Defs.lean`](Parking/Defs.lean), except that `Parking.IsParkingFunction` and `Parking.A`, which the statement does not use, are left out.
- [`Solution.lean`](Solution.lean) imports the proof in [`Parking/Unimodal.lean`](Parking/Unimodal.lean).
- [`comparator.json`](comparator.json) tells Comparator to check `Parking.root_unimodal` in the Solution against the Challenge, with the three axioms `propext`, `Quot.sound` and `Classical.choice`.
- [`Parking/`](Parking/) is the proof: 62 modules, about 22,000 lines.
- [`Check.lean`](Check.lean) prints the statement and the axioms of the proved theorem.
- [`formalization.yaml`](formalization.yaml) holds the structured metadata: provenance, sources, classification, automation and review.
- [`.github/workflows/palomar-preflight.yml`](.github/workflows/palomar-preflight.yml) runs Palomar's own mechanical verifier on this repository, on demand from the Actions tab.

## Building and checking

The project pins Lean `v4.36.0-rc2` and Mathlib `v4.36.0-rc2`, at commit `9d581dfff2e41de989072ea63abf3daf69311520`. The library in the do-math repository uses the stable `v4.36.0`. This repository uses the release candidate because Palomar's renderer cannot yet display a Challenge built with `v4.36.0`: for that version the renderer's Verso writes KaTeX `.ttf` fonts, which its output sanitizer rejects ([PalomarSubmission issue #203](https://github.com/PalomarRegistry/PalomarSubmission/issues/203)).

```sh
lake exe cache get              # Mathlib's compiled files
lake build                      # the library, Challenge and Solution
lake env lean Check.lean        # the statement and its axioms
lake comparator --config comparator.json
```

`lake build` prints one expected warning, about the `sorry` in `Challenge.lean`. The proof uses no axioms other than `propext`, `Classical.choice` and `Quot.sound`, and it uses neither `sorry` nor `native_decide`. Thirty-eight statements are settled by *tables*, finite computations in exact integer arithmetic that Lean's kernel evaluates itself with `decide +kernel`.

These checks were run on 25 November 2026 on a Windows machine, on the files of this repository with Lean and Mathlib `v4.36.0-rc2`. A clean `lake build` compiled the 62 modules, the Challenge and the Solution, with the one warning above. `lake env lean Check.lean` printed the statement with the axioms `[propext, Classical.choice, Quot.sound]`. `lake comparator` accepted the Solution against the Challenge, with the proof replayed and accepted by the kernels con-ron (45,257 declarations), NanoDa and Lean's own, configured as Palomar configures them. Comparator normally builds and exports the project inside a Linux sandbox. On Windows that sandbox is not available, so it was run with `--inadvisably-no-sandbox`. Palomar's verifier runs the same check with the sandbox.

## Outline of the proof

Picture the numbers of the theorem laid out in rows and columns: the length $n$ names the row and the displacement names the column. Write $k$ for the column, and for $1 \le k \le n-1$ write $d_{n,k} = b_{n,k} - b_{n,k-1}$ for the *step* of column $k$ in row $n$. Call the column *positive* in that row when this step is positive. A row that is not unimodal has a strict descent (a negative step) followed, further right, by a strict ascent (a positive step). So it is enough to exclude such a pair in every row (`Parking.unimodal_of_no_pair`, `Parking.no_descent_ascent`).

Rows up to $n = 16$ are checked directly from a table (`Parking.Tab.small_rows`). For a longer row the argument splits at the middle, and three statements about columns settle the two halves: one for the left half and two for the right. In the left half no descent occurs: for $n \ge 17$ and $2k \le n$ the step $d_{n,k}$ is nonnegative (`Parking.left_half`).

In the right half, two statements about columns exclude an ascent after a descent. The first says that a column $k$ that has turned positive stays positive as far as row $2k-1$: a column $k \ge 2$ that is positive in a row $n$ with $k+1 \le n \le 2k-2$ is positive in the next row (`Parking.chain_column_iter` is its iterated form). The second says that a column does not turn positive before the column to its left has: for $k \ge 9$ and $n \ge k+2$, if column $k$ is not positive in any of the rows $k+1, \dots, n$, then column $k+1$ is not positive in row $n$ (`Parking.mono`).

The two statements work together as follows. Take a row $n \ge 17$ with a descent at a column $k$ of its right half, so that $n \le 2k-1$ and therefore $k \ge 9$. Column $k$ cannot be positive in any of the rows $k+1, \dots, n$, because by the first statement a positive step in one of them would persist to row $n$. The second statement, applied in each of the rows from $k+2$ to $n$, then shows that column $k+1$ is not positive in those rows either. The same step leads from column $k+1$ to column $k+2$, and so on, column by column (`Parking.right_tail`). So no step of row $n$ to the right of the descent is positive, and no ascent follows.

Everything starts from one combinatorial fact, which the library proves from the parking process itself: a recursion, on the spot taken by the last car, for the number of parking functions of length $n$ whose maximum displacement is at most a given bound. During the research it was identified with Theorem 3.7 of Aguilar-Fraga et al. ([arXiv:2311.14055](https://arxiv.org/abs/2311.14055)), but the library neither imports nor assumes that theorem. From then on the proof works with that recursion and with the power series built from it. The recursion relates different lengths for one bound, whereas the theorem compares different displacements for one length. The proof therefore fixes a column, follows the sign of its step as $n$ grows, and passes from the columns to the rows only at the end.

Each of the three statements is proved by a table for the small columns and by an analytic argument for the large ones.

- **Left half.** Columns up to 81 are settled by a table together with a propagation argument. Columns from 82 on are settled by an analytic argument at the critical tilt $x_k = (k/(k+1))^{k-1}$, which rests on a convexity along the diagonal for tilted masses.
- **Right half, first statement.** Columns up to 81 are settled by a table, and columns from 82 on analytically.
- **Right half, second statement.** Columns up to 264 are settled by a table, and columns from 265 on through an inequality for compositions weighted by Cayley numbers.

The analytic arguments use the fact that every column $k \ge 265$ turns positive early: in some row $j > k$ with $25(j-k-1)^3 \le 121k^2$, that is, within a strip of width of order $k^{2/3}$. For the columns from 82 to 264 a table gives a row in which the column is positive. Among the analytic tools are Robbins' bounds for the factorial, which the library proves on both sides, and, for one correlation inequality, the four functions theorem of Mathlib.

The library also says where a row peaks, in statements that the proof of the theorem does not use ([`Parking/Peak.lean`](Parking/Peak.lean)). These statements are not part of this submission's compared declarations.

## Sources and literature

- The statement is Conjecture 6.5 of K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell, *ℓ-Interval parking functions: Foata invariance, statistic generating functions, and ciphers*, [arXiv:2507.07243](https://arxiv.org/abs/2507.07243), version 2. Version 1, of 9 July 2025, is titled *Statistics on ℓ-interval parking functions* and numbers the conjecture the same way. In that paper's terms, a parking function whose maximum displacement is at most $\ell$ is an $\ell$-interval parking function.
  arXiv's listing still shows the title of version 1.
- The recursion on which the proof starts is Theorem 3.7 of T. Aguilar-Fraga et al. (fifteen authors), *Interval and ℓ-interval rational parking functions*, Discrete Math. Theor. Comput. Sci. 26(1) (2024), Paper 10 ([arXiv:2311.14055](https://arxiv.org/abs/2311.14055)). The library proves it for itself.
- The earlier of the two research runs described below is archived on Zenodo as *parking-unimodality-2026-11-10* ([doi:10.5281/zenodo.24110810](https://doi.org/10.5281/zenodo.24110810), published 12 November 2026). It holds that run's knowledge base. Its own description says that the run reached an informal proof, not refereed, some of whose steps rest on computer-assisted inputs, including floating-point computations under an assumed error model, and that the conjecture remains open because there is no machine-checked proof. The proof formalized here is a different proof, found by the later run.

**Literature search.** On 19 November 2026 a search for a proof of the conjecture, or for results on the monotonicity of the rows or on the position of their largest entry, was made with six queries on arXiv, the lists of works citing the conjecture's source, Aguilar-Fraga et al. and Petersson, and keyword queries in zbMATH, OpenAlex and Crossref. About 210 records were examined. Two keyword queries could not be run, and MathSciNet, Web of Science, Scopus and Google Scholar were not searched. On 25 November 2026 two further web searches, `unimodality parking functions maximum displacement conjecture proof Celano Elder Harris Martin` and `"interval parking functions" unimodal maximum displacement 2026 arXiv`, found no work that proves it. These searches show where a proof was looked for and not found. They do not establish that the result is new.

**Previous formalizations.** None is known.

## How the proof was produced

The proof was found, written, reviewed and formalized by AI sessions of *do-math*, an autonomous research system. In a do-math run, AI sessions work in parallel in fixed roles: some attempt proofs or formalize them in Lean, others check and write up what was produced, and a review session decides whether a write-up is published in the run's library.

Two runs worked on the conjecture. The earlier run, from 5 to 13 November 2026, on OpenAI GPT-6.1 and Anthropic Claude models, reached an informal proof that its reviewers accepted. That proof rested on large computer-assisted certificates, some of them in double-precision interval arithmetic under an assumed accuracy of the library functions, and it was never formalized. Between the runs, AI sessions wrote that proof up as a manuscript and analysed it in a structure document and reports. The later run, from 19 to 23 November 2026, was started from those documents and ran on Claude models only (the Claude Fable family for attempts, explorations, formalization, peer checks and organization, the Claude Opus family for reviews). It found the different and shorter proof that this library formalizes. Afterwards AI sessions simplified the library, from 114 modules to 61, without changing the theorem or the definitions. They then extended it to 62 modules, so that it also states every numbered statement of a paper written from the research.

The person who commissioned the research chose the conjecture and gave standing written inputs to the running research. The runs were started and tended on that person's behalf by an *operator*, an AI session outside the runs. Four times the operator changed published verdicts of reviews directly, each time setting results back rather than accepting them: three times on that person's instruction or decision, once on its own judgment. No person wrote the proofs or the Lean code; the module-system port and the Palomar files of this repository were also made by an AI session.

**Review.** Every published result of the research was accepted by an AI review session, and AI review sessions judged that the Lean statement says what the conjecture says. Lean's kernel checks the proof. Jaehyoung Kim, the maintainer of this repository, read the Lean statement in `Challenge.lean` against Conjecture 6.5 before submission. No person has refereed the mathematics.

The complete record of the research is in the folder [`solved/parking-unimodality`](https://github.com/MegasKomnenos/do-math/tree/02cd0e69b53401f1ba99de27295edaf9cced32ee/solved/parking-unimodality) of the do-math repository. It contains a written record of every public declaration, a dependency map, a history of the two runs and a 143-page paper. A second Lean proof of the theorem, which goes through a stronger "staircase" statement and is built on this library, is in the folder [`solved/parking-staircase`](https://github.com/MegasKomnenos/do-math/tree/02cd0e69b53401f1ba99de27295edaf9cced32ee/solved/parking-staircase) of the same repository. This repository's `Parking/` is the `lean/` folder there, ported to Lean's module system. Every file gained a `module` header, `public import` in place of `import`, and `@[expose] public section`. One further change was needed. In `Parking/Table/Columns.lean`, eight definitions (`seqN`, `wmin`, `revAcc`, `sumZ`, `nextA`, `growStep`, `grow` and `col`) lost the keyword `private`, because `Parking.Tab.hd`, which another module evaluates in the kernel, computes through them, and the module system does not let a public, exposed definition use private ones. For the release candidate one more change was needed. Stable Mathlib renamed the lemma `div_left_inj'` to `div_left_inj₀` on 7 November 2026, with the same statement, and `Parking/Counting/SingleChain.lean` used the new name; here it uses the old one. Nothing else in the files changed.

## Licence

The contents of this repository are licensed under the Apache License 2.0; see [`LICENSE`](LICENSE).

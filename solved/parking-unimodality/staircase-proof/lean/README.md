# Unimodality of parking functions through the staircase: the Lean package

This folder holds a Lean 4 proof that the parking functions of a given length, counted by their maximum displacement, form a unimodal sequence. The proof goes through a stronger statement, the staircase, which says that every row of these counts rises strictly to a peak and falls strictly after it, with at most one pair of equal neighbours at the peak, and that the peak stays or moves one position to the right when the length grows by one.

The package is built on the Lean library `Parking` in [`../../lean/`](../../lean/). It requires that library as a dependency and consists of 28 modules of its own; the package changes nothing in `../../lean/`. The two theorems rest on 930 declarations of `Parking`: the definitions of the objects, the counting and series identities, tables of signs and several arguments. This README states the two theorems, says how to build the package and how it was checked, outlines the proof and lays out the modules. Its last two sections say what the package takes from `Parking` and how it was made.

## The theorems

Suppose that $n$ cars arrive one after another at a row of $n$ spots. Each car has a preference, which is one of the spots, and takes the first empty spot at or after it. The sequence of the $n$ preferences, in the order in which the cars arrive, is a *parking function* of length $n$ if every car parks. The *displacement* of a car is the distance between the spot it takes and its preference. Let $b_{n,\ell}$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$. Row $n$ is the sequence $b_{n,0}, b_{n,1}, \dots, b_{n,n-1}$.

Row $n$ has its *peak at* $p$ if

$$b_{n,0} < b_{n,1} < \dots < b_{n,p} \;\ge\; b_{n,p+1} > b_{n,p+2} > \dots > b_{n,n-1},$$

and a *strict peak at* $p$ if in addition $b_{n,p} > b_{n,p+1}$. For $p = n-1$ the part of the chain after $b_{n,p}$ is absent. The two notions are defined for an arbitrary array in [`Staircase/Peak.lean`](Staircase/Peak.lean) (`Parking.IsPeak`, `Parking.IsStrictPeak`).

**Theorem (staircase).** For every $n \ge 2$, row $n$ has its peak at some $p$, and row $n+1$ has its peak at the same $p$ or a strict peak at $p+1$.

So every row rises strictly and then falls strictly, with at most one pair of equal neighbours, which then stands at the top; the peak stays or moves one position to the right when the length grows by one; and a row whose peak has just moved has no equal neighbours.

**Corollary (unimodality).** For every $n \ge 1$ the sequence $b_{n,0}, \dots, b_{n,n-1}$ is unimodal: there is an index $p \le n-1$ such that the sequence does not decrease up to $p$ and does not increase from $p$ on.

The corollary is Conjecture 6.5 of K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell, [arXiv:2507.07243](https://arxiv.org/abs/2507.07243).

Both statements are in [`Staircase/Main.lean`](Staircase/Main.lean), as `Parking.staircase` and `Parking.unimodal_via_staircase`; the declarations of this package are in the namespace `Parking`, like those of the library. Lean prints them as follows when you run it on `Check.lean`, the last step of the next section:

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
```

The number $b_{n,\ell}$ is `Parking.b n ℓ`. It is defined in [`../../lean/Parking/Defs.lean`](../../lean/Parking/Defs.lean), directly from the parking process; spots and preferences are numbered from 0 there, which leaves displacements unchanged. `n - 1` and `ℓ - 1` are subtractions of natural numbers; each stands under a hypothesis that makes it the ordinary difference.

## Building

The versions are pinned: Lean 4.36.0 in [`lean-toolchain`](lean-toolchain), and Mathlib v4.36.0, which the library `Parking` requires. [`lakefile.toml`](lakefile.toml) requires the package that holds `Parking` by its path `../../lean`, and [`lake-manifest.json`](lake-manifest.json) lists that package and the resolved commits of Mathlib and its dependencies.

With [elan](https://github.com/leanprover/elan) installed, first build the library `Parking` as the README of its folder says ([`../../lean/README.md`](../../lean/README.md)), and then run in this folder:

```
lake build
```

It compiles the 28 modules of this package; if `Parking` has not been built, Lake first builds the 52 of its 62 modules that this package imports. For each file that imports a Mathlib module directly, `lake build` prints, for each such import, a notice that Mathlib "is designed for use with the module system", which is about how the files are written and not about their content. After the build,

```
lake env lean Check.lean
```

prints the two statements above followed by

```
'Parking.staircase' depends on axioms: [propext, Classical.choice, Quot.sound]
'Parking.unimodal_via_staircase' depends on axioms: [propext, Classical.choice, Quot.sound]
```

These three are the axioms of Lean's standard library. Twenty-two statements of this package about tables of integers are checked by the kernel's own evaluation (`decide +kernel`), and the proof uses thirty-six of the thirty-eight such statements of `Parking`; nothing uses `native_decide`.

## What was checked, and how

- `lake build` and `lake env lean Check.lean` were run on the present sources, on Windows, in a copy of this folder and of `../../lean/` laid out as here, and gave the output shown; the build ended with "Build completed successfully". It compiled the 28 modules of this package and 19 of the 52 modules of `Parking` that the package imports; the other 33 had been built by Lake before, from the sources they have now, and were not built again. Mathlib came from a copy of v4.36.0 that was on the machine. For that run the entry `packagesDir` was pointed to it in three files of the copy: the manifest of this package, the manifest of the package of `Parking`, and the `lakefile.toml` of the latter; Lake noted that the entry of this package's manifest had been changed. The files in this folder and in `../../lean/` have the entry unchanged, and in everything else the copy was identical to them. Fetching the dependencies from the network was not tried.
- The 28 modules, together with the 52 modules of `Parking` that they import, were also compiled without Lake, by the runtime of the research system that found the proof, on a packaging of the sources that the paragraph after this list describes. The runtime calls the Lean compiler on each module in the order of the imports and keeps what it has compiled, by the content of the module and of its imports. For this check it compiled 23 modules of the package, the module that poses the proposition to be proved, and a module of its own that reads the compiled library; the 52 modules of `Parking` and the other 5 modules of the package it took from what it had compiled in earlier runs, from the same content. No module gave an error, and none a warning except the one module that poses the proposition to be proved, where the warning is the open proof. From the compiled library the runtime found the proof of the posed proposition complete and resting on the three axioms above.
- An external replay of the proof, with Lean's exporter and `lake comparator`, was made on 24 November 2026 of the package as it stood then, in the packaging that the paragraph after this list describes, and was not repeated on the present sources. The exporter writes a theorem out with everything it rests on, and the comparator reads that export alone: it works out the axioms again and has Lean's kernel check every declaration, outside the compiler. In that state the package had 27 modules. Since then three places of its proofs were simplified, as the last section tells, comments were reworded, and six of the 52 modules of `Parking` that the package imports were changed when that library was corrected. Every public theorem of the 79 modules of that state was exported and checked in this way, 385 theorems. Among them are the staircase and the unimodality theorem, the latter under the name it has in the packaging, `Parking.unimodal_via_staircase_proof`; their statements were the two that are printed above. The kernel accepted every export, and each used only the three axioms above. On Windows the comparator's sandbox cannot run, so that replay rested on the builds having been made honestly.
- What the two theorems rest on was computed from the modules that the Lake build compiled: 1,251 declarations, the 321 of this package and 930 of `Parking`, in 50 of its modules. Of the 1,251, 445 are public: the 106 of this package and 339 of `Parking`. No declaration of this package is unused by the two theorems.

For the compilation by the runtime, and before it for the replay, the sources were packaged in the form that the runtime works on: one library, holding the 80 modules and one more that poses the unimodality statement, with its proof left open, as the proposition to be proved. In that library the posed proposition has the name `Parking.unimodal_via_staircase`, and the theorem of `Staircase/Main.lean` is carried under the name `Parking.unimodal_via_staircase_proof`, with the identical Lean statement. The two names occur again in the records.

No person has read the Lean statements against the conjecture or against the statement of the staircase in words.

## Outline of the proof

Arrange the numbers $b_{n,k}$ in an array with rows $n$ and columns $k$, and write $d_{n,k} = b_{n,k} - b_{n,k-1}$ for the *step* of row $n$ at column $k$, for $1 \le k \le n-1$. A *position* is a pair $(n,k)$, and a column is called positive, or negative, in a row if its step in that row is. Two rules hold for $n \ge 2$ (`column_rule`, `diagonal_rule` in `Staircase/Main.lean`):

- a positive step stays positive one row down in the same column: $d_{n,k} > 0 \Rightarrow d_{n+1,k} > 0$;
- a step that is not positive is followed by a negative step one row down and one column to the right: $d_{n,k} \le 0 \Rightarrow d_{n+1,k+1} < 0$.

For any array, the two rules give the staircase by induction on the row (`peak_induction`): if row $n$ has its peak at $p$, the first rule keeps the steps $1, \dots, p$ of row $n+1$ positive, the second makes its steps from $p+2$ on negative, and the one step left decides between the two alternatives; row 2 has a single step and therefore a peak. Unimodality follows at once, because the peak of a row is an index up to which the row does not decrease and from which it does not increase, and row 1 has a single entry.

The rules are proved region by region. The folders and files named in the rest of this outline lie under `Staircase/`. The *first layer* of column $k$ consists of the rows $k+1 \le n \le 2k-1$. The *curve* is the set of positions with $k^2 = (n-k)^3$, and a position with $(n-k)^3 \le k^2$ lies *behind the curve*.

*A bound for the first positive row of a large column.* `CurveIncrease/` proves that every column $k \ge 265$ has a positive step in a row $j$ with $(j-k-1)^3 \le k^2$, that is, at most one row beyond the curve (`curve_crossing`). The argument reduces the positivity of a step to a comparison of a sum over pairs of marked cut points with a boundary term, bounds the first from below and the second from above, and ends in inequalities between polynomials in $\sqrt{n-k+1}$.

*Persistence.* [`Staircase/Persistence.lean`](Staircase/Persistence.lean) proves four statements. A column $k \ge 82$ has a positive step in a row $k+r$ of its first layer with $r \le 27k/100$ (`positive_row_early`): for $k \le 264$ the row is taken from `Tab.two_signs`, a kernel-evaluated table of `Parking` that lists for each column $9 \le k \le 264$ a row of its first layer in which the step is positive, and for $k \ge 265$ it is the row of `curve_crossing`. In the first layer the step of a column $k \ge 82$ changes sign once, from not positive to positive (`one_sign_change`). A positive step persists in the first layer, for every $k \ge 2$ (`step_persists`); for $k \le 81$ this is read from the table `Tab.small_table` of `Parking`. And the step is positive for $k \ge 82$ and $n \ge 2k$ (`step_pos_large`). The analytic arguments behind the last three statements are theorems of `Parking`: `persist`, in its folder `ChainColumn/`, carries a positive step from an early row to the end of the first layer, and `big_step`, a private lemma of its folder `LeftHalf/`, carries it to the rows $n \ge 2k$. Both take the early positive row as a hypothesis, and `Persistence.lean` supplies that row.

*The column rule.* With its conclusion in the first layer it is `step_persists`. With its conclusion in a row $n+1 \ge 2k$ it is proved in `Beyond/`, which shows that the step in the rows $n \ge 2k$ is positive except at eleven positions in the columns up to 7; where the conclusion of the rule would be one of the eleven, its hypothesis fails, because the step one row above is negative. The positive signs come from three sources. For the column 1 they are proved by an induction on the row. For the columns 2 to 81 a kernel-evaluated table of this package (`Tab.junction_table`) gives the sign up to a row listed for the column, and from that row on an argument passes a positive step on to every later row. For $k \ge 82$ the sign is `step_pos_large`.

*The diagonal rule.* With its hypothesis at a position with $n \ge 2k$ it is again `Beyond/`. In the first layer of a column $k \le 264$ it is `BeforeCrossing/`. For $9 \le k \le 264$ a step of column $k$ that is not positive lies in a row $n$ before the positive row that `Tab.two_signs` lists for the column, by persistence, and the kernel-evaluated table `Tab.next_column_neg` of this package shows that column $k+1$ is negative in the row $n+1$. For $2 \le k \le 8$ no sign of column $k$ is needed: the kernel-evaluated table `Tab.negative_cells` of this package, which gives the negative steps of the columns 2 to 9 in 45 positions, shows that column $k+1$ is negative in every row that the rule asks for. In the first layer of a column $k \ge 265$, `curve_crossing` and persistence place a step that is not positive behind the curve, and there `Diagonal/` proves the rule: the formula `dq_frozen` of `Parking`, which writes the step as a curvature term minus a boundary term, is taken at the position $(n,k)$ and at its diagonal neighbour $(n+1,k+1)$, and the two are compared factor by factor, by Hölder's and Jensen's inequalities for the curvature, an FKG inequality on sets of cut points for the boundary term, and a final inequality between closed forms.

## Layout

The package has 7,459 lines in 28 modules under [`Staircase/`](Staircase/). Of its 321 declarations 106 are public; the rest are private to the proofs that use them.

| Path | Modules | Lines | What it holds |
|---|---|---|---|
| [`Peak.lean`](Staircase/Peak.lean) | 1 | 40 | The peak and the strict peak of a row |
| [`Beyond/`](Staircase/Beyond/) | 3 | 447 | The signs of the steps in the rows $n \ge 2k$, and the two rules there |
| [`BeforeCrossing/`](Staircase/BeforeCrossing/) | 2 | 260 | The diagonal rule in the first layer of the columns up to 264 |
| [`Cayley/`](Staircase/Cayley/) | 3 | 319 | Compositions with marked cut points; the curvature sum and the second difference of the frozen polynomial; the ratio of two Borel weights |
| [`CurveIncrease/`](Staircase/CurveIncrease/) | 10 | 3,629 | Every column $k \ge 265$ is positive at most one row beyond the curve |
| [`Persistence.lean`](Staircase/Persistence.lean) | 1 | 159 | The early positive row, the single change of sign, persistence, the large columns |
| [`Diagonal/`](Staircase/Diagonal/) | 7 | 2,420 | The diagonal rule behind the curve in the columns $k \ge 265$ |
| [`Main.lean`](Staircase/Main.lean) | 1 | 185 | The induction on the row, the two rules, the staircase, unimodality |

The folder [`../records/`](../records/) holds a written record for every public declaration of this package: its statement in ordinary mathematical language, an explanation, and, for a theorem, its proof in words. Its README says which records the folder holds and why the unimodality theorem has two. The record of the staircase, [`../records/Parking/staircase.md`](../records/Parking/staircase.md), tells the proof as a whole.

Beside `Staircase/` this folder holds [`Check.lean`](Check.lean), which prints the two statements and their axioms, and the three files of the build named in the section on building.

## What the package takes from the library `Parking`

`Parking` has 62 modules. The modules of this package import 52 of them, directly or through other imports. Counted with everything that the declarations they use rest on in turn, the two theorems rest on 930 declarations of `Parking`, in 50 of the 52 modules; the other two are imported by modules of `Parking` and contribute no declaration. The 930 declarations include the definitions of the parking process and of the counts, the counting and series identities derived from them, the kernel-evaluated tables `Tab.small_table` and `Tab.two_signs`, the formula `dq_frozen` for the step in the first layer, and the analytic arguments of `ChainColumn/` and `LeftHalf/` for persistence, which the outline names.

Among the 930 are 39 private declarations of nine modules that the proofs of this package use directly. The package reaches 38 of them through the command `open private` of Batteries; the thirty-ninth is a definition that occurs in the statements of some of the 38. The command is used where a lemma that a proof here needs is private in `Parking`: the lists of its table of two signs, lemmas on composition sums and on the birthday law, the representation of a composition sum over sets of cut points, and others; each place names the module it opens. The package therefore depends on names inside `Parking` that are not part of its public surface. Opening them was chosen over making them public, so that `Parking` is not changed; the two stand in one repository.

## How it was made

The proof was found by an autonomous research system, which left it as a tree of Lean modules. For this package the proof was built anew on the library `Parking` by AI sessions under the direction of another AI session, which also wrote `Main.lean`: one session reviewed the whole proof and divided the work, four each built one of the parts `Beyond/`, `BeforeCrossing/`, `CurveIncrease/` and `Diagonal/`, one built `Persistence.lean`, and one read the whole and arranged it by subject. One module is an exception: `CurveIncrease/Numerics.lean` was built with its part, but its final form was given by another session, the one that had commissioned the work from the directing session. That session set its names, visibility and comments, rearranged the proofs of its numerical certificates around one shared lemma, and changed the form of four of its statements. Afterwards three places of the proofs were simplified, by a further session and, for one of the hypotheses, by the directing session: the expansion of the second difference of the frozen polynomial, which two modules had each carried out, became one statement in `Cayley/CurvatureSum.lean`; one table of negative steps for the columns 2 to 9 took the place of two tables; and the hypotheses of four statements were weakened to what their proofs use.

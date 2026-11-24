# Unimodality of parking functions by maximum displacement: the Lean library

This folder holds a Lean 4 proof of one theorem, `Parking.root_unimodal`, and everything needed to compile it. The README of the folder above, [`../README.md`](../README.md), says what else is published with the proof and how the proof was obtained.

## The theorem

The theorem proved here is Conjecture 6.5 of K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell, [arXiv:2507.07243](https://arxiv.org/abs/2507.07243).

Suppose that $n$ cars arrive one after another at a row of $n$ spots. Each car has a preference, which is one of the spots, and takes the first empty spot at or after it. The sequence of the $n$ preferences, in the order in which the cars arrive, is a *parking function* of length $n$ if every car parks. The *displacement* of a car is the distance between the spot it takes and its preference. Let $b_{n,\ell}$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$.

**Theorem.** For every $n \ge 1$ the sequence $b_{n,0}, b_{n,1}, \dots, b_{n,n-1}$ is unimodal: there is an index $p \le n-1$ such that the sequence does not decrease up to $p$ and does not increase from $p$ on.

The theorem is in [`Parking/Unimodal.lean`](Parking/Unimodal.lean). Lean prints the statement as follows when you run it on `Check.lean`, which is the last step of the next section:

```
Parking.root_unimodal : ∀ (n : ℕ),
  1 ≤ n →
    ∃ p ≤ n - 1,
      (∀ (ℓ : ℕ), 1 ≤ ℓ → ℓ ≤ p → Parking.b n (ℓ - 1) ≤ Parking.b n ℓ) ∧
        ∀ (ℓ : ℕ), p ≤ ℓ → ℓ + 1 ≤ n - 1 → Parking.b n (ℓ + 1) ≤ Parking.b n ℓ
```

The objects of the statement are defined in [`Parking/Defs.lean`](Parking/Defs.lean), directly from the parking process. Spots and preferences are numbered from 0 there, which leaves displacements unchanged. `n - 1` is subtraction of natural numbers, and since $n \ge 1$ it is the ordinary $n-1$.

## Building

The versions are pinned: Lean 4.36.0 in [`lean-toolchain`](lean-toolchain), Mathlib v4.36.0 in [`lakefile.toml`](lakefile.toml), and the resolved commits of Mathlib and its dependencies in [`lake-manifest.json`](lake-manifest.json).

With [elan](https://github.com/leanprover/elan) installed, run in this folder:

```
lake exe cache get
lake build
```

The first command downloads Mathlib's compiled files, so that only this library is compiled. This step was not tried in this folder, as the first of the checks below reports. Without it `lake build` compiles Mathlib from its sources as well, which takes far longer; that was not tried to completion.

The second command compiles the 62 modules of the library. For each file that imports a Mathlib module directly, `lake build` prints, for each such import, a warning of this form:

```
warning: <file>: imports `<Mathlib module>` from package `mathlib`, which is designed for use with the module system; consider adding `module` to the start of this file
```

The warning comes from Lake and not from the compiler. It is about how the files are written, none of which begins with the keyword `module`, and not about their content; the compiler itself prints no warning for any file of the library.

The file [`Check.lean`](Check.lean) is in this folder. After the build,

```
lake env lean Check.lean
```

prints the statement above followed by

```
'Parking.root_unimodal' depends on axioms: [propext, Classical.choice, Quot.sound]
```

These three are the axioms of Lean's standard library. A proof that was incomplete would list `sorryAx`, and one that used compiled evaluation would list `Lean.ofReduceBool`. Thirty-eight statements about tables of integers are checked by the kernel's own evaluation (`decide +kernel`); nothing uses `native_decide`.

## What was checked, and how

- The present library was compiled without Lake, by running `lean` on each of its 62 modules in the order of the imports, starting from an empty folder (24 November 2026). The compiler printed nothing for any module: no error and no warning. Lake's warning does not appear in such a run. `Check.lean`, compiled last, printed the statement above and the three axioms.
- do-math took the present library in as its canon with its command `init` (24 November 2026), which compiles the canon through its own compile service and builds an index of every declaration. The canon has two modules more than this folder: one that states the theorem as posed, with its proof left open, and `Check.lean`. Of its 64 modules, the 28 that had changed or that import a changed module were compiled, each with exit code 0; the other 36 were taken from the compiled files of the first canon, whose sources and imports are the same. The index has 407 entries, of which 314 are theorems with a complete proof, and reading the index, do-math gives the theorem the state `formal_proved`; through the declarations of the canon, the proved theorem rests on the three axioms and no others. For this `init` the replay of the next item but one was switched off (`lean.judge` set to `null`).
- The commands `lake build` and `lake env lean Check.lean` were run with the versions above, on Windows, on the library as first published in this folder (23 November 2026, 61 modules), and gave the output shown. They were run again on the present library on 24 November, in a copy of this folder. `lake build` compiled the modules that had changed or that import a changed module, took the others from the build of the first published version, whose sources are the same, and ended with "Build completed successfully"; `Check.lean` printed the statement above and the three axioms. In both runs the dependencies came from a copy of Mathlib v4.36.0 that was already on the machine, at the commits of `lake-manifest.json`. Fetching them from the network with `lake exe cache get` was not tried in this folder. The copy on the machine had itself been fetched in that way the day before, with `lake update` and `lake exe cache get`, in another project folder that requires the same version of Mathlib.
- The library as first published was also replayed externally, with Lean's exporter and `lake comparator`: the theorem and everything it rests on were exported and checked again by Lean's kernel outside the compiler, and the kernel accepted them. The replay was not repeated on the present library, which differs from that version in this: seven public declarations were added (`Parking.robbins_lt_factorial`, `Parking.near_term_le`, `Parking.strip_tlow_nonneg`, `Parking.strip_main`, and `Parking.beyond_strip`, `Parking.strip_step` and `Parking.row_peak` in the new module `Peak.lean`); `Parking.factorial_le_robbins` was replaced by the strict `Parking.factorial_lt_robbins`, and the two proofs that use it were adapted; `Parking.unimodal_of_no_pair` was generalised to values in any linearly ordered type; the proofs of `Parking.P1_le` and `Parking.crossing_strip` were rewritten; and five further lines of comments were corrected. The statement of the theorem and `Defs.lean` are unchanged. do-math made the replay when that version was handed to it, on its canon of it. In that canon the proved theorem is named `Parking.root_unimodal_proof`, and the modules were otherwise byte for byte those then published. Two commands made the replay. The first, `leanexport Parking.Unimodal --` followed by `Parking.root_unimodal_proof`, the names of the three axioms and those of the constants that the kernel treats specially, wrote the theorem and everything it rests on into a file. The second, `lake comparator --inadvisably-no-sandbox --config <configuration> --challenge-from-export <that file> --solution-from-export <that file>`, read that file alone. Its configuration names the theorem and permits the three axioms; the comparator worked out the axioms afresh and replayed every declaration of the file through the kernel.

The replay leaves one thing on trust. Lean code runs while a file is compiled, and the comparator treats a library as untrusted: it can build and export the library inside a sandbox, which confines that code. The sandbox needs Linux and cannot run on Windows. Here the comparator was given an export of modules that had been compiled beforehand, without a sandbox, and was run with the option that switches its sandbox off; the comparator's own description of that option is that it "can compromise the result fully". So the replay shows that the kernel accepts the exported proof with the three axioms. That the export is what the sources of that version compile to rests on the compilation having done nothing but compile.

The library in this folder is not the one that the research left. After the research it was simplified, and after the paper was written a few statements were added or strengthened and `Peak.lean` was added, as the [README of the folder above](../README.md) tells. The simplification was made by AI sessions under the direction of one further AI session: seven sessions each worked on one group of modules, one reviewed the architecture of the whole library, and one read the whole library and rearranged it by subject. The later changes were made by AI sessions as well.

No person has read the Lean statement against the conjecture; in the research this correspondence was judged by review sessions.

## Outline of the proof

Arrange the numbers $b_{n,k}$ in rows and columns, row $n$ holding the numbers for length $n$ and column $k$ those for maximum displacement $k$. A row that is not unimodal has a strict descent followed, further right, by a strict ascent, so it is enough to exclude such a pair in every row.

The folders named below are under `Parking/`, and the next section lays them out. Rows up to 16 are checked by a table, one of the kernel-evaluated tables in `Table/`. In a longer row, `LeftHalf/` excludes a descent in the left half (the columns $k$ with $2k \le n$), and `ChainColumn/` and `NextColumn/` together exclude an ascent after a descent in the right half.

Call column $k$ *positive* in row $n$ when $b_{n,k-1} < b_{n,k}$, that is, when the row has a strict ascent at that column. For the right half the proof fixes a column and asks in which rows it is positive. `ChainColumn/` proves that a column $k \ge 2$ that has turned positive stays positive in its *chain range*, the rows $k+1$ to $2k-1$: if it is positive in one of these rows, it is positive in the later ones. `NextColumn/` proves that if column $k$ is not yet positive in row $n$, then column $k+1$ is not positive in row $n$ either. Here *not yet positive* in row $n$ means not positive in any of the rows $k+1, \dots, n$, and the statement holds for $k \ge 9$ and $n \ge k+2$.

Together the two statements exclude an ascent after a descent. A descent in the right half of a row $n$ longer than 16 is at a column $k$ from 9 on, and the row lies in the chain range of that column. So column $k$ is not yet positive in row $n$, or it would have stayed positive. `NextColumn/`, applied in each of the rows from $k+2$ to $n$, then shows that column $k+1$ is not yet positive in row $n$ either. The same argument leads on from column to column, and no column to the right of the descent is positive in row $n$.

`LeftHalf/`, `ChainColumn/` and `NextColumn/` each prove their statement by an analytic argument for the large columns and by computation, with a table, for the small ones; in the left half the table works together with a propagation argument. The analytic argument takes over at column 82 in `LeftHalf/` and `ChainColumn/`, and at column 265 in `NextColumn/`. These arguments use that a large column turns positive early: from column 265 on `Crossing/` supplies an early row in which it is positive, and for the columns from 82 to 264 such a row comes from a table.

The other folders hold what these proofs draw on. Everything starts from one combinatorial fact, the last-car recursion in `Counting/`, which is proved from the parking process itself. It is a recursion for the count `A` that `Parking/Defs.lean` defines beside `b`: $A_{n,k}$ is the number of parking functions of length $n$ whose maximum displacement is at most $k$. The theorem does not mention `A`, but once the recursion is proved, the proof works with that recursion and with the series built from it.

`Peak.lean`, beside `Unimodal.lean`, stands apart from the proof of the theorem. It bounds where a row $n \ge 335$ peaks, by statements that the theorem does not use.

The [README of the folder above](../README.md) says more about how the three statements are proved.

## Layout

The library has about 21,800 lines in 62 modules. Of the declarations in these modules, 406 are public; the rest are private to the proofs that use them. The modules are arranged under [`Parking/`](Parking/) as follows.

| Path | Modules | What it holds |
|---|---|---|
| [`Defs.lean`](Parking/Defs.lean) | 1 | The parking process, the maximum displacement, the counts `b` and `A` |
| [`Basic/`](Parking/Basic/) | 3 | Interval sums, elementary real bounds, renewal sequences |
| [`Cayley/`](Parking/Cayley/) | 4 | The numbers $j^{j-1}/j!$ and $(n+1)^{n-1}/n!$, Abel's identity, the tree series, Stirling bounds |
| [`Counting/`](Parking/Counting/) | 3 | The last-car recursion, the single-chain formula, the column equations |
| [`Series/`](Parking/Series/) | 2 | The series of a threshold and its prime kernel; three inequalities on all rows |
| [`Tilt/`](Parking/Tilt/) | 4 | Tilted sequences, the critical tilt, monotonicity of the tilted masses |
| [`Table/`](Parking/Table/) | 4 | The kernel-evaluated tables and their soundness |
| [`Crossing/`](Parking/Crossing/) | 4 | Every column $k \ge 265$ turns positive early |
| [`ChainColumn/`](Parking/ChainColumn/) | 9 | A column that has turned positive stays positive in the chain range |
| [`LeftHalf/`](Parking/LeftHalf/) | 12 | $b_{n,k-1} \le b_{n,k}$ for $n \ge 17$ and $2k \le n$ |
| [`NextColumn/`](Parking/NextColumn/) | 14 | If a column is not yet positive, the next one is not positive either |
| [`Unimodal.lean`](Parking/Unimodal.lean) | 1 | The theorem |
| [`Peak.lean`](Parking/Peak.lean) | 1 | Where a row $n \ge 335$ peaks; not used by the theorem |

The folder [`../records/`](../records/) holds, for every public declaration, a written record: its statement in ordinary mathematical language, an explanation, and, for a theorem, its proof in words. For example, the statement in the `Crossing/` row above is `Parking.crossing_strip`, and its record, [`../records/Parking/crossing_strip.md`](../records/Parking/crossing_strip.md), says how early a column turns positive. The record of the theorem as posed is [`../records/Parking/root_unimodal.md`](../records/Parking/root_unimodal.md), which reads the Lean statement against the conjecture binder by binder and carries no proof. The proof of the theorem in words is in [`../records/Parking/root_unimodal_proof.md`](../records/Parking/root_unimodal_proof.md). No declaration of this folder has that name. The records carry the names of the do-math canon, in which `Parking.root_unimodal` is the theorem as posed, with its proof left open, and `Parking.root_unimodal_proof` is the proved theorem.

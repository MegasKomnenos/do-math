# Unimodality of parking functions by maximum displacement: the Lean library

This folder holds a Lean 4 proof of one theorem, `Parking.root_unimodal`, and everything needed to compile it.

## What is proved

A parking function of length $n$ is a sequence of preferences of $n$ cars for $n$ spots in a row such that every car parks, where each car takes the first empty spot at or after its preference. The displacement of a car is the distance between the spot it takes and its preference. Let $b(n,\ell)$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$.

**Theorem.** For every $n \ge 1$ the sequence $b(n,0), b(n,1), \dots, b(n,n-1)$ is unimodal: there is an index $p \le n-1$ such that the sequence does not decrease up to $p$ and does not increase from $p$ on.

As Lean prints it:

```
Parking.root_unimodal : ∀ (n : ℕ),
  1 ≤ n →
    ∃ p ≤ n - 1,
      (∀ (ℓ : ℕ), 1 ≤ ℓ → ℓ ≤ p → Parking.b n (ℓ - 1) ≤ Parking.b n ℓ) ∧
        ∀ (ℓ : ℕ), p ≤ ℓ → ℓ + 1 ≤ n - 1 → Parking.b n (ℓ + 1) ≤ Parking.b n ℓ
```

The objects of the statement are defined in `Parking/Defs.lean`, directly from the parking process. Spots and preferences are numbered from 0 there, which leaves displacements unchanged. `n - 1` is subtraction of natural numbers. The theorem is in `Parking/Unimodal.lean`.

The statement is Conjecture 6.5 of K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell, arXiv:2507.07243.

## Building it

The versions are pinned: Lean 4.36.0 in `lean-toolchain`, Mathlib v4.36.0 in `lakefile.toml`, and the resolved commits of Mathlib and its dependencies in `lake-manifest.json`.

With [elan](https://github.com/leanprover/elan) installed, in this folder:

```
lake exe cache get
lake build
```

The first command downloads Mathlib's compiled files, so that only this library is compiled. The second compiles the 61 modules of the library. Then

```
lake env lean Check.lean
```

prints the statement above followed by

```
'Parking.root_unimodal' depends on axioms: [propext, Classical.choice, Quot.sound]
```

These three are the axioms of Lean's standard library. A proof that was incomplete would list `sorryAx`, and one that used compiled evaluation would list `Lean.ofReduceBool`.

`lake build` prints, for each file, a notice that Mathlib "is designed for use with the module system". It is a notice about how the files are written and not about their content; the library's own code produces no warning.

## What was checked, and how

- `lake build` and `lake env lean Check.lean` were run on these sources with the versions above, on Windows, and gave the output shown. In that run the dependencies came from a copy of Mathlib v4.36.0 that was already on the machine, at the commits of `lake-manifest.json`. Fetching them from the network with `lake exe cache get` was not tried.
- The library was also compiled from an empty build folder, module by module, with no error and no warning.
- An external replay of the proof was made with Lean's exporter and `lake comparator`: the theorem and everything it rests on were exported and checked again by Lean's kernel outside the compiler, and the kernel accepted them. On Windows the comparator's sandbox cannot run, so that replay rests on the builds having been made honestly.

## How the library is laid out

About 21,400 lines in 61 modules. The public declarations number 399; the rest are private to the proofs that use them. Thirty-eight statements about tables of integers are checked by the kernel's own evaluation (`decide +kernel`); nothing uses `native_decide`.

| Folder | Modules | What it holds |
|---|---|---|
| `Defs.lean` | 1 | The parking process, the maximum displacement, the counts `b` and `A` |
| `Basic/` | 3 | Interval sums, elementary real bounds, renewal sequences |
| `Cayley/` | 4 | The numbers $j^{j-1}/j!$ and $(n+1)^{n-1}/n!$, Abel's identity, the tree series, Stirling bounds |
| `Counting/` | 3 | The last-car recursion, the single-chain formula, the column equations |
| `Series/` | 2 | The series of a threshold and its prime kernel; three inequalities on all rows |
| `Tilt/` | 4 | Tilted sequences, the critical tilt, monotonicity of the tilted masses |
| `Table/` | 4 | The kernel-evaluated tables and their soundness |
| `Crossing/` | 4 | Every column $k \ge 265$ turns positive early |
| `ChainColumn/` | 9 | A column that has turned positive stays positive in the chain range |
| `LeftHalf/` | 12 | $b(n,k-1) \le b(n,k)$ for $n \ge 17$ and $2k \le n$ |
| `NextColumn/` | 14 | If a column is not yet positive, the next one is not positive either |
| `Unimodal.lean` | 1 | The theorem |

With $d(n,k) = b(n,k) - b(n,k-1)$, a row that is not unimodal has a strict descent followed by a strict ascent. Rows up to 16 are checked by a table. For a longer row, a descent in its left half is excluded by `LeftHalf`, and one in its right half is excluded by `ChainColumn` and `NextColumn` together, with `Crossing` supplying the row at which a large column turns positive.

The folder `../records/` holds, for every public declaration, a written record: its statement in ordinary mathematical language, an explanation, and its proof in words.

# Unimodality of the number of parking functions by maximum displacement

This folder holds a result obtained with do-math: a formal proof, in Lean 4, that for every length the numbers of parking functions counted by their maximum displacement form a unimodal sequence. With the proof it holds a written record of every result the proof names, a map of how the proof is built, the archived knowledge of the later of the two research runs behind it, and a history of that research. A paper presenting the proof in ordinary mathematical language is being produced and will be added (see "The paper" below).

## The result

Cars $1, \dots, n$ arrive in this order at a street with spots $1, \dots, n$. Car $i$ prefers spot $a_i$ and takes the first empty spot at or after it. The sequence $(a_1, \dots, a_n)$ is a *parking function* when every car finds a spot. The *displacement* of a car is the distance between the spot it takes and the spot it prefers, and $b_{n,\ell}$ is the number of parking functions of length $n$ whose largest displacement is exactly $\ell$.

**Theorem.** For every $n \ge 1$ the sequence $b_{n,0}, b_{n,1}, \dots, b_{n,n-1}$ is unimodal: for some $\ell^*$ it does not decrease up to $\ell^*$ and does not increase from $\ell^*$ on.

The statement was posed as Conjecture 6.5 by K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell (arXiv:2507.07243), who tabulate the numbers for $n \le 9$.

In Lean the theorem is `Parking.root_unimodal`, in `lean/Parking/Unimodal.lean`. The objects it speaks of are defined in `lean/Parking/Defs.lean`, directly from the parking process. That file is byte for byte the definitions file of the formal proof as the research run published it; the simplification described below did not touch it.

## What stands behind it

The proof is complete in Lean 4.36.0 with Mathlib 4.36.0 and depends on no axioms other than `propext`, `Classical.choice` and `Quot.sound`, the three of Lean's standard library. These checks were made on the sources in `lean/`:

- `lake build` compiles all 61 modules, and `lake env lean Check.lean` prints the theorem with exactly those three axioms.
- The library was compiled from an empty build folder with no error and no warning of its own.
- The theorem and everything it rests on were exported and checked again by Lean's kernel outside the compiler (`lake comparator`), which accepted them. On Windows the comparator's sandbox cannot run, so this replay rests on the builds having been made honestly.

What these checks establish is that the Lean statement follows from the axioms. Three things they do not establish are worth saying:

- That the Lean statement says what the conjecture says is a matter of reading `Defs.lean` and the statement, about seventy lines in all. In the research this correspondence was judged by review sessions; the record of the theorem as posed, `records/Parking/root_unimodal.md`, goes through it binder by binder for a reader who wants to judge it.
- No person has refereed the mathematics. The proof was found, written, reviewed and formalized by AI sessions; what vouches for it is Lean.
- The texts in this folder other than the Lean sources (the records, the history, and the paper when it is added) were written and checked by AI sessions. Where a check was not completed, the text concerned says so.

`lean/README.md` gives the build commands, the expected output and the layout of the library.

## How the proof goes

Write $d_{n,k} = b_{n,k} - b_{n,k-1}$ for the step of column $k$ in row $n$. A row that is not unimodal has a strict descent followed, further right, by a strict ascent, so it is enough to exclude such a pair in every row. Rows up to $n = 16$ are checked directly from a table. For a longer row the argument splits at the middle.

- **Left half.** For $n \ge 17$ and $2k \le n$ the step $d_{n,k}$ is nonnegative, so no descent occurs there. Columns up to 81 are settled by a table together with a propagation argument; columns from 82 on by an analytic argument at the critical tilt $x_k = (k/(k+1))^{k-1}$, which rests on a convexity along the diagonal for tilted masses.
- **Right half.** Two statements about columns exclude an ascent after a descent. A column $k \ge 2$ that is positive in a row $n$ with $k+1 \le n \le 2k-2$ is positive in the next row; and for $k \ge 9$ and $n \ge k+2$, if column $k$ is not positive in any of the rows $k+1, \dots, n$, then column $k+1$ is not positive in row $n$. The first is settled by a table for the columns up to 81 and analytically from 82 on; the second by a table for the columns up to 264 and, from 265 on, through an inequality for compositions weighted by Cayley numbers. The analytic arguments use that every column $k \ge 265$ turns positive within a strip of width of order $k^{2/3}$ above its bottom row.

Everything starts from one combinatorial fact, a recursion on the spot taken by the last car, which is proved from the parking process itself; after it the proof works with that recursion and with the series built from it.

## What is in this folder

| Folder | Contents |
|---|---|
| `lean/` | The Lean library: 61 modules, about 21,400 lines, with the pinned versions, the build files and `Check.lean` |
| `records/` | A written record for each of the 399 public declarations and for the theorem as posed: its statement in ordinary mathematical language, an explanation, and its proof in words; and the bibliography of the twelve works the records cite |
| `dependency-map/` | A map of the proof: the results a description of the proof would name, grouped by subject, with lines for what rests on what. `dependency_map.html` is interactive; `dependency_map.svg` is the drawing alone |
| `paper/` | The paper (to be added) |
| `history/` | `timeline.md`, a history of the research from the start of the earlier run to the formal proof, with `SOURCES.md` and the cited sources that are not in the archives |
| `knowledge/` | The archive of what the later run published and `MANIFEST.md`, which gives the commit, size and checksum of that archive and of the earlier run's and says how to unpack them. The earlier run's archive is 349 MB and is not in the repository |

## How it was obtained

Two do-math runs worked on the statement. The earlier one ran from 5 to 13 November 2026 and published 438 changes; it reached a proof in words on 11 November. A manuscript and a set of reports were written from it, and a later run, started on 19 November from those documents and not from the earlier run's records, published 120 changes and reached the formal proof on 23 November. `history/timeline.md` tells this in detail, including what was tried and failed, and states which of its passages were compared with the sources by an independent reader and which were not.

The library as the later run left it had 114 modules and about 28,000 lines. It was then simplified without changing the theorem or the definitions: results proved twice were merged, tables that checked overlapping facts were combined, detours were removed, and the modules were rearranged by subject. That brought it to the 61 modules here, and the number of statements settled by evaluating a table went from 61 to 38. The library was also moved from Lean 4.32 to Lean 4.36 in the course of this.

## The paper

A paper presenting the proof in natural language is being written from the records by do-math's paper command. It is not yet in this folder. When it is, this section will say what it contains, how its statements were compared with the formal ones, and which findings, if any, its checks left open.

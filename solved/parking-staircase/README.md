# Unimodality of parking functions by maximum displacement, through the staircase

This folder holds a formal proof, in Lean 4, that for every length the numbers of parking functions counted by their maximum displacement form a unimodal sequence. The proof goes through a stronger statement, the staircase, which says how each of these sequences rises and falls and how its peak moves when the length grows by one. With the proof the folder holds a written record of every definition and result that the proof states under a public name, a map of how the proof is built, a paper that presents the proof in ordinary mathematical language, and the history and the archived knowledge of the research from which the proof came.

The proof was obtained with do-math, an autonomous research system in which AI sessions look for proofs, review them and formalize them in Lean.

## The result

Suppose that $n$ cars arrive one after another at a row of $n$ spots. Each car has a preference, which is one of the spots, and takes the first empty spot at or after it. The sequence of the $n$ preferences, in the order in which the cars arrive, is a *parking function* of length $n$ if every car parks. The *displacement* of a car is the distance between the spot it takes and its preference. Let $b_{n,\ell}$ be the number of parking functions of length $n$ whose maximum displacement is exactly $\ell$. Row $n$ is the sequence $b_{n,0}, b_{n,1}, \dots, b_{n,n-1}$. It has its *peak at* $p$ if

$$b_{n,0} < b_{n,1} < \dots < b_{n,p} \;\ge\; b_{n,p+1} > b_{n,p+2} > \dots > b_{n,n-1},$$

and a *strict peak at* $p$ if in addition $b_{n,p} > b_{n,p+1}$.

**Theorem (staircase).** For every $n \ge 2$, row $n$ has its peak at some $p$, and row $n+1$ has its peak at the same $p$ or a strict peak at $p+1$.

**Corollary (unimodality).** For every $n \ge 1$ the sequence $b_{n,0}, \dots, b_{n,n-1}$ is unimodal: there is an index $p \le n-1$ such that the sequence does not decrease up to $p$ and does not increase from $p$ on.

The corollary is Conjecture 6.5 of K. Celano, J. Elder, K. P. Hadaway, P. E. Harris, J. L. Martin, A. Priestley and G. Udell, [arXiv:2507.07243](https://arxiv.org/abs/2507.07243). In Lean the two statements are `Parking.staircase` and `Parking.unimodal_via_staircase`, in [`lean/Staircase/Main.lean`](lean/Staircase/Main.lean), and Lean prints them as follows:

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

The number $b_{n,\ell}$ is `Parking.b n ℓ`, defined in [`lean/Parking/Defs.lean`](lean/Parking/Defs.lean) directly from the parking process. [`lean/README.md`](lean/README.md) explains the statements, outlines the proof and lays out the modules.

## What was checked, and what was not

The proof is complete in Lean 4.36.0 with Mathlib v4.36.0, and each of the two theorems depends on no axioms other than `propext`, `Classical.choice` and `Quot.sound`, the three axioms of Lean's standard library. Tables of signs are settled by finite computations in exact integer arithmetic that Lean's kernel evaluates itself (`decide +kernel`); nothing uses `native_decide`.

On 25 November 2026 `lake build` was run in a copy of [`lean/`](lean/) laid out exactly as here, on Windows. Lake compiled all 80 modules from their sources, the 52 of `Parking` and the 28 of `Staircase`, and ended with "Build completed successfully"; `lake env lean Check.lean` then printed the two statements above, each with exactly the three axioms. Mathlib was not fetched for this run: a copy of its packages was supplied to the build, the commit of each was checked against [`lean/lake-manifest.json`](lean/lake-manifest.json) beforehand, and the network was closed to the build. After that run, comments of five modules under `lean/Parking/` were reworded; a script confirmed that in every Lean file the text outside comments is the same, character for character, and the build was not repeated, since a comment does not change what Lean builds. Fetching Mathlib from the network, which is what `lake build` does for a reader who has no copy of it, was therefore not tried.

Two earlier checks were made on the same modules in other arrangements, and [`lean/README.md`](lean/README.md) describes them: a compilation of every module by the runtime of the research system, and a replay of the proof by Lean's kernel outside the compiler, which was made on the state of 24 November 2026 and not repeated since.

What these checks establish is that the two Lean statements follow from the axioms. Three things are not established by them.

- That the Lean statements say what the staircase and the conjecture say in words is a matter of reading the definitions and the two statements. A person has read the two Lean statements, with the definitions they use, against the statements in words. The record [`records/Parking/unimodal_via_staircase.md`](records/Parking/unimodal_via_staircase.md) reads the Lean statement of unimodality, part by part, against the conjecture as it is stated in words.
- No person has refereed the mathematics. The proof was found, written, reviewed and formalized by AI sessions; what vouches for it is Lean.
- The texts of this folder other than the Lean sources were written and checked by AI sessions. [`records/README.md`](records/README.md) says how the records were checked, and the section "The paper" below says what was checked of the paper and what was not.

## Building

With [elan](https://github.com/leanprover/elan) installed, run in [`lean/`](lean/):

```
lake build
lake env lean Check.lean
```

The first command fetches Mathlib at the pinned version, unless it is already present, and compiles the 80 modules of this folder; the second prints the two statements and their axioms. [`lean/README.md`](lean/README.md) gives the details.

## What is in this folder

- [`lean/`](lean/) is the Lean proof: 28 modules under `Staircase/`, which hold the proof of the staircase, and 52 modules under `Parking/`, which hold the definitions, the counting and series identities, tables of signs and the analytic arguments that the staircase modules build on; with them the pinned versions, the build files and [`Check.lean`](lean/Check.lean).
- [`records/`](records/) has the written records of the public declarations that the two theorems rest on, 443 records for 445 declarations, as its README explains, and their bibliography. A declaration is public when it is not marked `private`; the private declarations are steps of the proofs that use them and have no record of their own. Each record gives a statement in ordinary mathematical language and an explanation, and the record of a proved result gives its proof in words as well. The record of the staircase, [`records/Parking/staircase.md`](records/Parking/staircase.md), tells the proof as a whole.
- [`dependency-map/`](dependency-map/) is a map of the proof: the results a description of the proof would name, grouped by subject, with lines for what rests on what. [`dependency_map.html`](dependency-map/dependency_map.html) is interactive, and [`dependency_map.svg`](dependency-map/dependency_map.svg) is the drawing alone.
- [`paper/`](paper/) has the paper, [`paper.pdf`](paper/paper.pdf), with its LaTeX source and bibliography, and [`correspondence.json`](paper/correspondence.json), which says for each numbered statement of the paper which declaration it states.
- [`history/`](history/) and [`knowledge/`](knowledge/) are the research's own record, described under "Where the proof came from".
- [`LICENSE`](LICENSE) is the licence of the folder.

## The paper

[`paper/paper.pdf`](paper/paper.pdf) presents the proof in ordinary mathematical language: 184 pages in twenty-three sections, with 161 numbered statements and 17 references. It says nothing of Lean. Its two theorems are the unimodality of every row and the staircase. It derives both from two rules for the signs of the steps $b_{n,k}-b_{n,k-1}$, one along a column and one along a diagonal, proves the rules by analytic estimates, and describes the tables as exact computations with integers, for lengths up to 300, that a reader could repeat. Its LaTeX source [`paper.tex`](paper/paper.tex), its bibliography [`references.bib`](paper/references.bib) and [`correspondence.json`](paper/correspondence.json) are beside it; it was typeset with Tectonic 0.15.

### How it was written and checked

The paper was written from the records by AI sessions, in two stages.

In the first stage do-math's paper command produced a manuscript of 215 pages with 171 numbered statements and 15 references. One session planned it and one session for each section wrote it. The manuscript was read seventeen times: nine times by a session that had the manuscript and nothing else, and eight times beside published research articles, by sessions that report where the manuscript is written otherwise than such articles are. Most readings were followed by repairs. Every numbered statement was then compared with the declaration it states, as its record and its Lean statement give it, and all 171 were found to say the same. In this comparison two records were found to say more in their statements than their declarations do; they have been corrected, as [`records/README.md`](records/README.md) tells. The command ended with nine findings of its readers open. It did not compare the text between the numbered statements with the declarations.

In the second stage, on 25 November 2026, a further session with agents of its own resolved the nine findings and revised the manuscript section by section. Classical results that the manuscript had proved in full are now cited. Abel's binomial identity and the recursion on the last car are stated without proof, the bounds of Robbins for the factorial are quoted, and seven proofs take a step from a cited theorem: from the Lagrange inversion formula, from the expansion of $1/(1-T)$ for the tree function $T$, from two facts on Galton–Watson processes, and from the estimate of Flajolet, Grabner, Kirschenhofer and Prodinger for Ramanujan's function. Ten statements lost their number: six became displayed formulas of the running text, three lemmas on arbitrary real numbers were written into the two proofs that use them, and one lemma is no longer needed. One lemma moved to the preliminaries, two propositions received one proof in common, conventions and derivations that the sections repeated were removed, and the bibliography was reduced to bibliographic data.

The revised manuscript was then read once, whole, by an agent that had the manuscript and nothing else and had written none of it. It reported no step of a proof that does not follow and no wrong constant, and 25 places of presentation, most of them a formula that one section gave again under a second number. These were corrected, except for a few places where the text was kept for a reason, for example because the change would have added a numbered statement that no declaration states. After that the five numbered statements whose text or whose record had changed, and the six formulas that had lost their number, were compared with their declarations by agents that had not written them. All eleven say the same.

Last, the running text was compared with the declarations, which had not been done before. For each of the twenty-three sections an agent that had not written it went through the text outside the numbered statements and outside the proofs, 519 passages in all, and reported every sentence or formula that asserts mathematics which no single declaration states. 246 assertions were reported. Most of them were true, and many were steps that the library proves inside the proof of a declaration: orders of magnitude, numerical examples, remarks that a bound is attained, consequences that join two results, and derivations that stood before the lemma that uses them. In the correction that followed, the reported passages were cut, reworded so that they say what one declaration states, or moved with their derivation into the proof that uses them; three were kept with a reason, which `correspondence.json` gives. This brought the paper to 184 pages. The text as it stands after this correction was not compared with the declarations again. A script confirmed that the correction changed the text of no numbered statement, that every reference and citation resolves, and that every formula which the correction moved stands before the places that use it; the session that directed the work read the new sentences of four of the corrected sections where they stand, and not those of the others.

Before the text relied on them, the works that the paper cites were opened at the places it cites, on 25 November 2026. All seventeen works of the bibliography were opened in this way. Two of them were added in this stage, the book of Flajolet and Sedgewick and the survey of Yan, and one took the place of another: the article in which Petersson published the limit theorem that the introduction quotes could not be opened, and the paper cites the summary of his doctoral thesis, which states the theorem and was read. Several works were read in a scan or a copy that is not the publisher's own file: the articles of Robbins, of Foata and Riordan, of Fortuin, Kasteleyn and Ginibre, and of Konheim and Weiss. The book of Flajolet and Sedgewick was read in the authors' electronic version, so the paper cites it by the numbers of its theorems and sections and not by page; the survey of Yan was read in the author's copy and is cited as a whole; and the corollary of Janson and Petersson was read in the arXiv version of their article.

### How the paper and the proof correspond

[`paper/correspondence.json`](paper/correspondence.json) names, for each of the 161 numbered statements, the declaration that the statement states, and each carries the verdict that it says the same. Of the 161, 156 have exactly the text that the command compared in the first stage, and five were compared in the second stage: the two that now carry a citation in place of a proof, one definition from which a clause was removed, and the two whose records were corrected.

Under `changes` the file lists the twenty-two declarations whose standing in the paper changed in the second stage. Ten had a number of their own in the manuscript of the first stage and have none now. Six of them are displayed formulas of the running text, each compared with its declaration and found to say the same; one of the six, the upper bound of Robbins, is quoted from the literature with the lower bound beside it. Three are lemmas on arbitrary real numbers, which the paper no longer states in general: their arguments are carried out, for the quantities concerned, inside the proofs of one lemma and one proposition. One, a lemma on the series of the tree function, is no longer in the paper, because the proof that it served now takes its formula from the Lagrange inversion formula. The other twelve entries are statements that kept their number and their wording: two whose proof was replaced by a citation, seven of whose proof a step now rests on a cited work, one that moved to another section, and two that are proved together.

Under `running_text` the file gives, section by section, how many passages were compared and how many assertions were reported, the passages that were kept with their reasons, and the 18 displayed formulas that stand inside a proof and are referred to from outside it. Twelve of these came to stand there in the last correction. Each of them is a step that the Lean proof proves once, inside the proof of a declaration or as a private lemma, and uses in two proofs; the paper derives it in the first of the two proofs and refers to it from the second, and no declaration states it by itself.

The file names declarations as they are named in the packaging in which the research system compiled the proof, which [`lean/README.md`](lean/README.md) describes under "What was checked, and how". There the proved unimodality theorem is `Parking.unimodal_via_staircase_proof`; in [`lean/`](lean/) it is `Parking.unimodal_via_staircase`. Its list `others`, which says for each declaration without a number where the first stage wrote it, was not made again after the second stage, in which such a sentence may have been reworded, moved into a proof or cut.

### What to know before relying on the paper

- Lean has checked the proof in [`lean/`](lean/), not the paper, and no person has refereed the paper. What ties the paper to the proof is the comparison of its numbered statements and of its running text with declarations, which AI sessions made. A proof in the paper tells the argument of a record, and a record tells the argument of a Lean proof; neither of these two steps was verified by a machine, and the steps inside the proofs of the paper were not compared with the Lean one by one.
- By the comparisons that `correspondence.json` records, every numbered statement of the paper is stated by a declaration. For the running text this is established less far: the sentences that the last correction wrote, and the derivations that it moved into proofs, were not compared again.
- The paper takes these results from the literature without proving them: Abel's binomial identity, the recursion on the last car, the bounds of Robbins for the factorial, the Lagrange inversion formula with the expansion of $1/(1-T)$, the two facts on Galton–Watson processes from which the total mass of the Borel distribution follows, the estimate of Flajolet, Grabner, Kirschenhofer and Prodinger, and the correlation inequality of Fortuin, Kasteleyn and Ginibre. In the paper these rest on the cited sources. The Lean proof does not rest on them. It proves Abel's identity, the recursion, the upper bound of Robbins, the value of the sum of the Borel probabilities and the two consequences of the estimate that it uses, and it proves by arguments of its own each statement in whose proof the paper cites the Lagrange inversion formula or the expansion of $1/(1-T)$. In place of the lower bound of Robbins it uses a weaker bound that Mathlib provides, and for the one instance of the correlation inequality that it needs it uses the four functions theorem of Mathlib. The theorem of de Bruijn and Erdős on renewal sequences is cited and is also proved in the paper, in the form without a condition on the sum of the kernel, as the Lean proof proves it.
- When the cited works were opened, five attributions of the manuscript turned out to say something other than the works do, and the paper was changed: what the theorem of Pappe is about, the place in Selig and Zhu, what Ager-Hart and her coauthors call their objects, where the count of Konheim and Weiss comes from, and the work in which the limit theorem of Petersson was read. The section "Earlier work" of the record [`records/Parking/unimodal_via_staircase_proof.md`](records/Parking/unimodal_via_staircase_proof.md) was corrected in four of these places; its account of the count of Konheim and Weiss already gave the derivation and stayed as it was.

## Where the proof came from

The proof was found by do-math in a research on the unimodality of parking functions by maximum displacement, which left it as a tree of Lean modules; for this folder it was built anew on the modules under `lean/Parking/` by AI sessions, as the last section of [`lean/README.md`](lean/README.md) tells. Two folders are the research's own record, written while it ran, and they are kept here as they were written. They tell the whole of that research as it happened and are not an account of this proof.

- [`history/`](history/) has [`timeline.md`](history/timeline.md), a history of the research from its start to its formal proof of unimodality, with [`SOURCES.md`](history/SOURCES.md) and the cited sources.
- [`knowledge/`](knowledge/) has an archive of what the research published and [`MANIFEST.md`](knowledge/MANIFEST.md), which describes it.

## Licence

The contents of this folder are licensed under the Creative Commons Attribution 4.0 International licence (CC BY 4.0); the text of the licence is in [`LICENSE`](LICENSE).

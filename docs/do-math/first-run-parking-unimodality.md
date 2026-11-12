# The first run of do-math: unimodality of the maximum-displacement distribution of parking functions

This document is the full account of the first run of the current do-math implementation, as of 17:45 Korean time on 12 November 2026; the run continues. The terms it uses, such as node, relation, route, record, review, informally proved and computer-assisted, are defined in the repository [README](../../README.md) under "How the research is organized" and "What counts as established", and the README's section "Reading a published knowledge base" explains the files of the published evidence.

## The problem

Parking functions come from the following process. There are n parking spots in a row, numbered 1 to n, and n cars arrive one at a time, car 1 first. Each car i has a preferred spot aᵢ between 1 and n. It parks there if the spot is free; otherwise it drives on toward higher numbers and takes the first free spot it meets, and if none is left it fails. A preference list α = (a₁, …, aₙ) in which every car parks is a **parking function** of length n, and there are (n+1)ⁿ⁻¹ of them. The **displacement** of car i is the distance between its preferred spot and the spot it took, and the **maximum displacement** M(α) of a parking function is the largest displacement among its cars.

Write b(n, ℓ) for the number of parking functions of length n with M(α) = ℓ. The root asks whether, for every n ≥ 1, the sequence b(n, 0), b(n, 1), …, b(n, n−1) is unimodal: whether there is an index c such that b(n, ℓ) ≤ b(n, ℓ+1) for every ℓ < c and b(n, ℓ) ≥ b(n, ℓ+1) for every ℓ with c ≤ ℓ < n−1. The peak may be flat, and c may depend on n. This is Conjecture 6.5 of Celano et al., who write |IPFₙ(ℓ)^max| for the same numbers and tabulate them up to n = 9; the endpoints are b(n, 0) = n! and b(n, n−1) = nⁿ⁻².

## Setup and size of the run

The instance was created on 5 November 2026 at 15:08 Korean time with the proposition above as its root and a standing input that it use no records or code from an earlier instance that had worked on the same problem under a previous implementation. The user of this run is the author of this repository.

The producing roles ran on Codex gpt-6.1-sol as their first choice until 7 November and on Claude Fable 5.1 afterwards, each with the other as fallback. Until the evening of 6 November, peer and review preferred the same model as the producing roles; they were then moved to Claude Opus 5.5 as their first choice, and the default described in the README, under which the assessing roles prefer a different model, was adopted at the same time. The user changed the number of concurrent sessions several times, between 4 and 16.

The run is still going. Its size at 17:45 Korean time on 12 November was the following.

| Quantity | Count |
|---|---|
| Sessions launched | 1,227 (305 attempts, 96 explorers, 12 formalizers, 371 peers, 362 reviews, 81 organizers) |
| Records published | 337 (240 from attempts, 90 from explorers, 7 from formalizers) |
| Publication commits | 422 |
| Nodes on the frontier | 108 |
| Accepted relations | 119 |
| Questions | 17, of which 10 resolved |

The session counts differ from the record count because a producing session that ends without having begun research gets no peer, interrupted peers and reviews are replaced by fresh sessions, some candidates are not published, and some pipelines were still in progress; the commits outnumber the records because organizer outputs, comprehensive reviews and question publications are committed too.

## Two routes to the root

The frontier shows two routes to the root, established by records rce3dc75b and r15524fdd. Call a step ℓ a descent when b(n, ℓ) > b(n, ℓ+1) and an ascent when b(n, ℓ) < b(n, ℓ+1); the sequence fails to be unimodal exactly when some descent is followed by a later ascent. The first route splits that failure into four cases around the middle index m = ⌈n/2⌉, by the positions of the descent and the ascent: the descent at the step m−1 into the middle and the ascent at or beyond m; both at or beyond m; the descent below m−1 and the ascent at or beyond m; and both below m. Each case has a reviewed informal proof.

The second route shows that a conditional log-concavity suffices for the root: if b(n, ℓ) > b(n, ℓ+1) then b(n, ℓ+1)² ≥ b(n, ℓ) b(n, ℓ+2), for all n ≥ 3 and 0 ≤ ℓ ≤ n−3, so that once the sequence has started to decrease it cannot rise again; this condition was then settled at steps at or beyond m and at steps below m separately, and a reviewed relation in record rdc276812 derives the latter from the fourth case of the first route.

The third and fourth cases of the first route were in turn proved by showing that the sequence has no descent at all below the middle, that is, that it increases there. Both routes therefore pass through that increase, and it was the last part to close. In the part of it that resisted longest, where n lies between 2ℓ and about 2ℓ^(3/2), the records found that the neighboring counts b(n, ℓ−1) and b(n, ℓ) agree to leading order as ℓ grows, and that the difference deciding the inequality is smaller than either count by a factor of order ℓ^(−1/3).

The last open premise on the routes was one node, pair-beats-capped-threshold, whose exact statement in the frontier is an inequality between two counts of configurations for n between 2ℓ and about 2ℓ^(3/2); the record that proved it, r5909c9e7, was published on 11 November at 16:14 Korean time. Its review supported the proof's claims, accepted the proof, marked one peripheral claim about a table's coverage unsupported, and stated that the proof inherits computer-assisted inputs from earlier records: several in binary64 floating point, and the certification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November), which checked the steps at or beyond the middle in integer interval arithmetic and the steps below the middle twice, in integer interval arithmetic and in floating point with directed rounding. With that node proved, the runner derived the root through the relations.

## A step known to be unproved

One step of those routes is known to be unproved. Record r030ffaeb, published on 11 November, argues a lower bound on which the proof of the increase below the middle depends, and its argument reads that bound from a table of values that is valid only if the function tabulated is non-increasing in one of its variables and six explicit elementary pieces of it are monotone in the other. The record asserts these two properties, and its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among the points it judged not yet rigorous. The review did not write the missing proof; it judged the numerical check sufficient evidence for a computer-assisted claim and said so, and whether that judgment was right is open to any reader of the record.

No record proves the two properties. The author and an operator session found the gap on 12 November while writing a manuscript from the records, and at 14:15 Korean time a standing input asked sessions launched afterwards to put proving the two properties before any other work; it assigned the work to no session, and no concern has been filed against the record. Until a record proves them, the root's state rests on this step as the reviews accepted it.

## The one Lean proof and the formalization pause

One node has a formal proof. Record r0af7f414, published on 6 November, contains a Lean theorem, `Parking.critical_increment_unconditional`, whose transitive axioms are exactly `propext`, `Classical.choice` and `Quot.sound`, and whose statement the review matched to the node. With F_ℓ(z) = Σ_m A(m, ℓ) zᵐ / m! the exponential generating function of the numbers A(m, ℓ) of parking functions of length m with maximum displacement at most ℓ, the theorem states that ℓ^(3/2) (F_ℓ(1/e) − F_{ℓ−1}(1/e)) tends to e/√(2π) as ℓ → ∞. The node is a necessary condition of the root: record r801ec220 proves that unimodality for every n implies this limit, so its refutation would have refuted the root, while its proof leaves the root open.

The seven records produced by formalizers all belong to the Lean development that led to this theorem, and all were published on 6 November; the rule that limits formalization to outcomes that can reach the root was added to the runner afterwards, with this node as the occasion. On 9 November the user paused all formalization so that the research could finish first, and the five formalizations then in progress were ended without peer or review, so nothing of them was published. The pause is still in force, and no Lean work on the routes to the root has been published.

## Interventions during the run

The user and the operator intervened in the run in the ways listed below. Standing inputs apply to sessions launched after them. The software changed several times between 6 and 9 November: the installed copy that the instance executes was regenerated and the runner restarted, while sessions already running kept the code and guides they had been launched with. The standing inputs are not part of `knowledge/`; they are in the instance's `control/inputs` and `control/retired-inputs` directories.

| Date (Korean time) | Kind | What changed |
|---|---|---|
| 5 November | Standing input | No records or code from the earlier instance are to be used |
| 6 November | Software | Propagation of relations in every logical direction; formalization limited to outcomes that can reach the root; reconsideration of session endings |
| 6 November, evening | Settings and software | Peer and review moved to Claude Opus 5.5 as first choice; do-math's default was changed at the same time so that the assessing roles prefer a model different from the one the producing roles prefer |
| 7 November | Standing input | An attempt may take a node that is equivalent, through an accepted relation, to a node another session occupies |
| 7 November | Settings | Producing roles moved to Claude Fable 5.1 as first choice |
| 7 November, evening | Standing input | Register a section before beginning research on it; withdrawn on 9 November after 89 sessions had received it |
| 8 November | Standing input | The essay on research and the description of the author's writing preferences, written during this run and since part of do-math's reference folder |
| 9 November | Software | Questions on the frontier |
| 9 November | Operator action | Five questions placed on the frontier without review, when questions were introduced |
| 9 November | Settings | Explorer cadence changed from one request per three attempt launches to one per launch |
| 9 November | Standing input | Formalization paused so that the research could finish first |
| 9 November | Session termination | The five formalizations in progress ended without peer or review |
| 9 November | Standing input | More weight on thinking about the problem than on large computations |
| 9 November | Standing input | The question the user most wants answered is why the distribution is unimodal |
| 12 November, 04:54 | Standing input | Material from a session outside the instance, relayed as unverified matter for the sessions' own judgment |
| 12 November, 14:15 | Standing input | Prove the two monotonicity properties of record r030ffaeb before any other work |
| During the run | Settings | Concurrency limit changed several times, between 4 and 16 |

## The published evidence

The complete `knowledge/` directory of the instance is published on Zenodo under the concept DOI [10.5281/zenodo.24110810](https://doi.org/10.5281/zenodo.24110810), which resolves to the latest version. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was compressed on 12 November at 01:52 Korean time and deposited at 02:38, after the root had been informally proved and before the two inputs of that day; it holds 300 records, including r5909c9e7, r030ffaeb and r0af7f414, with every review, organization and question published up to that moment. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved.

To check the result, open `index.md`, go to `frontier.md` for the root's two routes and the records they cite, open record r5909c9e7 with its `review/feedback.md`, and continue into the records its proof uses.

## Limits

Every review was an AI session; no person has reviewed the records as a referee would, and the author's reading of them while writing a manuscript is how the gap above was found. Several records on the routes rest on binary64 computations with error models assumed in advance, r030ffaeb among them; the review of r5909c9e7 lists the ones its proof inherits. One step on the routes is asserted and numerically checked but not proved, as described above. No Lean work on the routes to the root has been published.

Whether the mechanisms described in the README under "How the research is organized", such as sections, questions or the reconsideration of endings, changed the quality of the research has not been measured; the run shows only that they were exercised at this scale, and it does not show that they improve the research. No figures were collected on token usage or cost, on how often reviews rejected or corrected claims, or on how often a fallback gave an assessing role the same model as the producers. The research is not finished: at 17:45 Korean time on 12 November, ten pipelines were active, working on unresolved nodes and unresolved questions beside the root.

## Artifacts not yet public

The artifacts of the run that are being prepared and are not yet public are listed, with their status, in the first-run section of the [README](../../README.md).

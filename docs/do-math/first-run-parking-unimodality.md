# The first run of do-math: unimodality of the maximum-displacement distribution of parking functions

This document is the full account of the first run of the current do-math implementation, as of 23:15 Korean time on 12 November 2026; the run continues. The size table below is a snapshot from 17:45 Korean time that day. The terms it uses, such as node, relation, route, section, record, review, standing input, operator, informally proved and computer-assisted, are defined in the repository [README](../../README.md), and the README's section "Reading a published knowledge base" explains the files of the published evidence. Records are cited by the letter r and the first eight hexadecimal digits of their identifiers; the directories in the knowledge base carry the full identifier.

## The problem

Parking functions come from the following process. There are n parking spots in a row, numbered 1 to n, and n cars arrive one at a time, car 1 first. Each car i has a preferred spot aᵢ between 1 and n. It parks there if the spot is free; otherwise it drives on toward higher numbers and takes the first free spot it meets, and if none is left it fails. A preference list α = (a₁, …, aₙ) in which every car parks is a **parking function** of length n, and there are (n+1)ⁿ⁻¹ of them. The **displacement** of car i is the distance between its preferred spot and the spot it took, and the **maximum displacement** M(α) of a parking function is the largest displacement among its cars.

Write b(n, ℓ) for the number of parking functions of length n with M(α) = ℓ. The root states that, for every n ≥ 1, the sequence b(n, 0), b(n, 1), …, b(n, n−1) is unimodal: that there is an index c such that b(n, ℓ) ≤ b(n, ℓ+1) for every ℓ < c and b(n, ℓ) ≥ b(n, ℓ+1) for every ℓ with c ≤ ℓ < n−1. The peak may be flat, and c may depend on n. This is Conjecture 6.5 of Celano et al., who write |IPFₙ(ℓ)^max| for the same numbers and tabulate them up to n = 9; the endpoints are b(n, 0) = n! and b(n, n−1) = nⁿ⁻².

## Setup and size of the run

The instance was created on 5 November 2026 at 15:08 Korean time with the statement above as its root and a standing input that it should use no records or code from an earlier instance that had worked on the same problem under a previous implementation. The user of this run is the author of this repository.

The producing roles ran on Codex gpt-6.1-sol as their first choice until 7 November and on Claude Fable 5.1 afterwards, with the other model as fallback in each period. Until the evening of 6 November, peer and review preferred the same model as the producing roles; they were then moved to Claude Opus 5.5 as their first choice, and at the same time do-math's default was changed to the one the README describes, under which peer and review prefer a different model from the producing roles. The user changed the number of concurrent sessions several times, between 4 and 16.

The run is still going. Its size at 17:45 Korean time on 12 November was the following.

| Quantity | Count |
|---|---|
| Sessions launched | 1,227 (305 attempts, 96 explorers, 12 formalizers, 371 peers, 362 reviews, 81 organizers) |
| Records published | 337 (240 from attempts, 90 from explorers, 7 from formalizers) |
| Publication commits | 422 |
| Nodes on the frontier | 108 |
| Accepted relations | 119 |
| Questions | 17, of which 10 resolved |

The session counts differ from the record count for several reasons: a producing session that ends without having begun research gets no peer, interrupted peers and reviews are replaced by new sessions, some candidates are not published, and some pipelines were still in progress. The commits outnumber the records because organizer outputs, comprehensive reviews and question publications are committed too.

## Two routes to the root

The frontier shows two routes to the root, set out in records rce3dc75b and r15524fdd. Call the step from index ℓ to ℓ+1 a descent when b(n, ℓ) > b(n, ℓ+1) and an ascent when b(n, ℓ) < b(n, ℓ+1), and locate each step at the index ℓ where it begins; the sequence fails to be unimodal exactly when some descent is followed by a later ascent. The first route splits that failure into four cases according to where the descent and the later ascent lie relative to the middle index m = ⌈n/2⌉. In the first case the descent is at the step from m−1 to m and the ascent at or beyond m; in the second both are at or beyond m; in the third the descent is below m−1 and the ascent at or beyond m; in the fourth both are below m. These four cases cover every way the failure can occur, and each has a reviewed informal proof that it cannot occur.

The second route shows that a property weaker than full log-concavity suffices for the root: log-concavity required only at a step at which the sequence decreases, namely that b(n, ℓ+1)² ≥ b(n, ℓ) b(n, ℓ+2) whenever b(n, ℓ) > b(n, ℓ+1), for all n ≥ 3 and 0 ≤ ℓ ≤ n−3. Since all the counts are positive, it follows from this property that once the sequence has started to decrease it cannot rise again, which is unimodality. The property was then proved at steps at or beyond m and at steps below m separately, and record rdc276812 proves that, for these particular sequences, the second part is equivalent to the statement that the fourth case of the first route cannot occur, so the frontier derives it from that statement.

The third and fourth cases of the first route were in turn proved by showing that the sequence has no descent at all below the middle, that is, that it never decreases there. Both routes therefore pass through that statement, and it was the last part to be proved. In the part of that statement's range that resisted longest, where n lies between 2ℓ and about 2ℓ^(3/2), the records established that the neighboring counts b(n, ℓ−1) and b(n, ℓ) agree to leading order as ℓ grows, and that their difference b(n, ℓ) − b(n, ℓ−1), whose sign decides the inequality, is only of order ℓ^(−1/3) times either count.

The last open premise on the routes was a single node, pair-beats-capped-threshold. Its exact statement is in the frontier; in outline, it is an inequality between two counts of configurations for n between 2ℓ and about 2ℓ^(3/2). The record that proved it, r5909c9e7, was published on 11 November at 16:14 Korean time. Its review supported the proof's claims and accepted the proof, marking one peripheral claim about a table's coverage as unsupported. The review also stated that the proof inherits computer-assisted inputs from earlier records: several in binary64 floating point, and the finite verification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November). That verification checked the steps at or beyond the middle in interval arithmetic with integer endpoints, and the steps below the middle twice, once in the same arithmetic and once in floating point with directed rounding. With that node proved, the runner derived the root through the relations.

## The one Lean proof and the formalization pause

One node has a formal proof. Record r0af7f414, published on 6 November, contains a Lean theorem, `Parking.critical_increment_unconditional`, whose transitive axioms are exactly `propext`, `Classical.choice` and `Quot.sound`, and whose statement the review matched to the node. Let A(j, ℓ) be the number of parking functions of length j with maximum displacement at most ℓ, and let F_ℓ(z) = Σ_j A(j, ℓ) zʲ / j! be the exponential generating function of these numbers. The theorem states that ℓ^(3/2) (F_ℓ(1/e) − F_{ℓ−1}(1/e)) tends to e/√(2π) as ℓ → ∞. The node is a necessary condition of the root: record r801ec220 proves that unimodality for every n implies this limit, so its refutation would have refuted the root, while its proof leaves the root open. The limit itself was then proved without assuming the root, which the word unconditional in the theorem's name records.

The seven records produced by formalizers all belong to the Lean development that led to this theorem, and all were published on 6 November; the rule that limits formalization to outcomes that can reach the root was added to the runner afterwards, prompted by this node. On 9 November the user paused all formalization so that the sessions could finish the informal mathematics before formalization is resumed, and by the user's decision the five formalizer pipelines then in progress were ended without peer or review, so none of their work was published. The pause is still in force, and no Lean work on the routes to the root has been published.

## Interventions during the run

The user and the operator intervened in the run in the ways listed below. Standing inputs and settings changes were the user's decisions, carried out by the operator; software changes were made by the repository's author, who is also the user of this run; the row marked Operator action records something the operator did directly rather than through a standing input. Standing inputs apply to sessions launched after them. The software changed several times between 6 and 9 November: the installed copy that the instance executes was regenerated and the runner restarted, while sessions already running kept the code and guides they had been launched with. The standing inputs are not part of `knowledge/`; they are in the instance's `control/inputs` and `control/retired-inputs` directories.

| Date (Korean time) | Kind | What changed |
|---|---|---|
| 5 November | Standing input | No records or code from the earlier instance are to be used |
| 6 November | Software | Propagation of relations in every logical direction; formalization limited to outcomes that can reach the root; reconsideration of session endings |
| 6 November, evening | Settings and software | Peer and review moved to Claude Opus 5.5 as first choice; do-math's default was changed at the same time so that peer and review prefer a model different from the one the producing roles prefer |
| 7 November | Standing input | An attempt may take a node that is equivalent, through accepted relations, to a node another session occupies |
| 7 November | Settings | Producing roles moved to Claude Fable 5.1 as first choice |
| 7 November, evening | Standing input | Register a section before beginning research on it; withdrawn on 9 November after 89 sessions had received it |
| 8 November | Standing input | The essay on research and the description of the author's writing preferences, written during this run and since then part of do-math's reference folder |
| 9 November | Software | Questions on the frontier |
| 9 November | Operator action | Five questions placed on the frontier without review, when questions were introduced; the operator wrote them from the research so far |
| 9 November | Settings | Explorer cadence changed from one request per three attempt launches to one per launch |
| 9 November | Standing input and runner control | Formalization paused so that the sessions could finish the informal mathematics before formalization is resumed: a control file, recognized by a temporary change to the runner, stops it from starting formalizers, and a standing input told the sessions |
| 9 November | Session termination | The five formalizer pipelines in progress ended without peer or review |
| 9 November | Standing input | More weight on thinking about the problem than on large computations |
| 9 November | Standing input | The question the user most wants answered is why the distribution is unimodal |
| 12 November, 04:54 | Standing input | Mathematical material that an AI session outside the instance had produced at the user's request; the operator checked it in exact arithmetic and against published records and passed it on for the sessions to judge for themselves |
| 12 November, 14:15 | Standing input | Give priority over all other work to proving two monotonicity properties that a table used by record r030ffaeb relies on and that its review had accepted on numerical evidence; records rfc693208, r0e82912d and rc56f637b, published between 16:12 and 18:18, each prove both properties by separate arguments |
| During the run | Settings | Concurrency limit changed several times, between 4 and 16 |

## The published evidence

The complete `knowledge/` directory of the instance is published on Zenodo under the concept DOI [10.5281/zenodo.24110810](https://doi.org/10.5281/zenodo.24110810), which resolves to the latest version. Each version is a snapshot of the directory. Version 3, [10.5281/zenodo.24165415](https://doi.org/10.5281/zenodo.24165415), the latest, was taken at 23:25 Korean time on 12 November and deposited at 00:45 on 13 November; it holds 340 records, including the three published that afternoon and evening. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was taken on 12 November at 01:52 Korean time and deposited at 02:38, after the root had been informally proved and before the two standing inputs of that day (04:54 and 14:15); it holds 300 records, including r5909c9e7, r030ffaeb and r0af7f414, with every review, organization and question published up to that moment. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved.

To check the result, open `index.md`, go to `frontier.md` for the root's two routes and the records they cite, open record r5909c9e7 with its `review/feedback.md`, and continue into the records its proof uses.

## Limits

Every review was an AI session, and no person has refereed the records. Several records on the routes rest on binary64 computations with error models assumed in advance, r030ffaeb among them; the review of r5909c9e7 lists the ones its proof inherits. No Lean work on the routes to the root has been published.

Whether the mechanisms described in the README under "How the research is organized", such as sections, questions or the reconsideration of endings, changed the quality of the research has not been measured; the run shows only that they were exercised at this scale. No figures were collected on token usage or cost, on how often reviews rejected or corrected claims, or on how often a fallback gave a peer or a review the same model as the producers. The research is not finished: at 23:15 Korean time on 12 November the run had launched 1,237 sessions and published 340 records in 426 publication commits, the frontier held 108 nodes, and ten pipelines were active, working on unresolved nodes and unresolved questions other than the root.

## Artifacts not yet public

The artifacts of the run that are being prepared and are not yet public are listed, with their status, in the first-run section of the [README](../../README.md).

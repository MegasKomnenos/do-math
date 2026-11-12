# do-math

do-math runs research on one mathematical proposition through many fresh AI sessions. The person who starts a run, called the user below, supplies the proposition as an exact statement, together with any standing inputs, which are instructions that every session launched afterwards receives; the user does this through an AI conversation, called the operator, that prepares and operates the run on the user's behalf. The mathematics is then done by the sessions. A program called the runner launches them as the work requires, several at a time, each a new Claude Code or Codex conversation that remembers nothing of the others.

What the sessions share is a knowledge base: a repository of records. A record holds mathematics that one session produced, that a second session developed into an account for others, and that a third session assessed; once published it is never changed, and the assessment stays beside it. Each session that produces mathematics reads the knowledge base and decides for itself what to work on; the sessions that develop and assess receive the work they are to process. No session plans or assigns the others' research.

The system is built this way because research that runs for days needs both continuity and judgment that does not come from whoever did the work. Continuity comes from the records. Independence of judgment is sought through the separation of roles: the session that writes a piece of mathematics, the session that turns it into a record, and the session that judges the record are three different conversations. Work that is useful but imperfect is published with its assessment, so that a later session can tell an established result from a claim that still needs more.

The first full run of this implementation began on 5 November 2026 on a conjecture from a 2025 paper by Celano, Elder, Hadaway, Harris, Martin, Priestley and Udell ([arXiv:2507.07243](https://arxiv.org/abs/2507.07243), Conjecture 6.5): for every length n, the numbers of parking functions of length n with maximum displacement 0, 1, …, n−1 form a unimodal sequence. On 11 November the root proposition reached the state do-math calls *informally proved*: every record, and every reviewed implication between statements, on two routes to the root had been accepted by an AI review session. The knowledge base is public on Zenodo.

The informal proof of the root comes with qualifications. No person has reviewed the records as a referee would. Several steps rest on computer-assisted inputs. On 12 November one record on those routes was found to rely on two monotonicity properties that it asserts and that its review checked numerically but that no record proves; the sessions have been asked to prove them.

The formal part has not been done. do-math counts a run as complete only when a Lean proof of the root, or of its negation, has been recompiled by a review session and checked against the exact statement; the user paused formalization on 9 November so that the research could finish first, and no Lean work on the routes to the root has been published. One statement that the root implies does have a Lean proof.

The sections below describe how the sessions cooperate, what a published result does and does not certify, the first run with its evidence and its limits, the layout of a published knowledge base, and how to run do-math on a proposition of your own.

## How the research is organized

### Instances, roots and nodes

An **instance** is one run: a directory with its own Git repository, holding the proposition in `root.md`, the models and scheduling in `settings.json`, a directory for every session, and `knowledge/`, the knowledge base where reviewed records accumulate. The proposition in `root.md` is the **root**. It never changes during the instance; a different proposition is a different instance.

The research represents the root, and every further proposition it decides to pursue, as a **node**: an exact mathematical statement with its objects, assumptions, domains and quantifiers fixed. A node is **settled** when its statement or its negation has been proved. A proof carries one of two levels of assurance, informal or formal, and the run as a whole is complete only when the root is settled at the formal level.

Nodes other than the root enter the research through a **relation**, a reviewed implication between nodes. If a session working on P proves that Q implies P, its record can propose Q as a node together with that relation, and Q is admitted once a review session has checked the implication and the exact statement of Q. If work settles a part of what a node asserts, the record can propose the parts as nodes together with the relation that the parts cover the whole. An implication that is only conjectured stays in the record for a later session to investigate; it does not create a node.

### Six roles and the pipeline

Six roles do the work, and the runner launches a fresh session for each piece of it. Three roles produce mathematics: an **attempt** tries to settle a node, an **explorer** works to understand the problem, and a **formalizer** constructs a Lean proof. Two roles process what the producing roles leave: a **peer** develops it into a record, and a **review** assesses the record. An **organizer** keeps the knowledge base navigable. A producing session together with its peer and review is a **pipeline**.

| Role | What it receives | What it leaves |
|---|---|---|
| attempt | The knowledge base; it chooses a node to settle | Its retained work on that node |
| explorer | The knowledge base; it works to understand one question about the problem | Its retained work on that question |
| formalizer | A node whose informal proof review has accepted | Its retained work: Lean sources, complete or partial |
| peer | One producing session's complete retained work | A record candidate: exposition, claims and proposals |
| review | The candidate and the producing session's retained work | Its assessment and feedback: claim statuses, a publication decision and any concerns |
| organizer | The published records not yet organized | Modules, shared-context selection, glossary decisions, merges |

What a producing session leaves is its **retained work**: the files it keeps in its own directory as it goes, holding the definitions and assumptions it used, arguments and intermediate results, computations with their code and output, literature with the conditions of its use, failed approaches with what they actually exclude, and the obligations that remain.

### The choice of work: frontier, sections and leases

An attempt receives no assigned node and no task written for it; the user's standing inputs can state priorities, but the choice of work stays with the session. It reads the **frontier**, the current list of nodes with their statements, their states and the relations between them; the **index**, a directory of published records that shows each record's own description with the review's short assessment beside it; and the **board**, which shows what other sessions are working on now. Then it chooses a node and a **section** of it: an exact part of what the node asserts, up to the whole node.

While an attempt chooses, it holds the node's **lease**, which lets one session at a time choose a section on that node; the lease has no time limit and ends when the session registers its section, releases the lease, or ends. The registered section is the attempt's declaration of what it has taken on, and the section counts as occupied until the work has been developed into a record and reviewed, because until then the work is invisible to other sessions, and a second attempt on the same part would repeat it without knowing.

Coordination between sessions works through information rather than enforcement. The board shows occupancy; the guide each role receives, its **role guide**, explains how to respect it; the sessions are trusted to follow the guide. Tools refuse only what a program can decide by itself: registering a statement identical to an existing section, registering a whole node while another session holds part of it, or omitting the reason a new section does not overlap an existing one. Whether two differently worded sections overlap is a mathematical judgment, and the registering session makes it and records its reason.

### The end of a session

An attempt has no time cap. When the CLI process of its conversation exits, the runner does not close the session at once. A separate process, the **session host**, which the runner started with the session and which lives as long as the session does, resumes the same conversation and asks the session to reconsider ending under its role guide, up to three times by default. The session either continues or submits an explicit decision that its work is complete or that it sees no way forward.

A session interrupted from outside, by a provider's usage limit for example, is treated the same as one that ended. In either case, if the session has begun research, its retained work goes on to the processing roles; a session that only checked for available work and found none ends without them.

### Peer, review and the published record

A **peer** is a fresh session that receives the producing session's complete retained work, including the full conversation, and develops it into a **record candidate**: an exposition written for a reader who cannot open the producing session's directory, together with a structured list of the claims it makes. The peer is asked to work the mathematics itself: to complete an argument the producer left unfinished where it can, to look for the counterexample or the identity that the producer passed over, and to keep its own additions distinguishable from the producer's. It also decides what the record proposes to the shared state: new nodes, relations, proofs of nodes, questions, and terminology.

A **review** is another fresh session, which receives the candidate and the producing session's retained work. It compares them in both directions, looking for results the producer established that the candidate dropped and for claims the candidate makes without support. It gives each claim one of three statuses: *supported*, when the offered evidence establishes the claim; *unsupported*, when the review has found that it does not; and *undetermined*, when the review could not complete the assessment. It decides separately whether the record has enough useful content to publish at all. Review may reason and compute to check an argument, but if accepting a claim would require an essential proof that the candidate does not contain, it is asked to report the gap rather than to write the proof and certify its own work.

By default the peer and review roles prefer a model different from the one the producing roles prefer. Each role's model setting is an ordered list with fallbacks, so a launch made while the preferred model is unavailable can use the same model as the producers.

When review finds material worth keeping, the runner publishes the candidate as a **record**: the exposition, its evidence, its description and its terminology, together with the review's assessment and feedback, committed to the instance's Git repository. The record never changes afterwards. A later review session, whether reviewing another candidate or examining published evidence, that finds a defect in it or confirms a result attaches a **finding** to the record, so that the original claim and what later happened to its standing are both visible. The frontier, the index, the board and the shared glossary are rendered from the repository, and no session writes a separate account of the current state.

### Relations, propagation and the standing of nodes

The runner applies each accepted relation in every direction that propositional logic allows, and the frontier shows the result. A relation says that its premises cannot all hold while its conclusion fails. So a proof of Q together with "Q implies P" gives P, and a refutation of K together with "P implies K" refutes P, without anyone writing the contrapositive as a second relation. A node for which accepted arguments currently support both its statement and its negation is marked *contested*; it counts neither as work available to attempts nor as settled until a review locates the failure.

The frontier also marks each node by how it stands to the root: on a **route** to the root, when a chain of relations lets a proof of the node contribute to settling the root, or a necessary condition, when only its refutation can contribute. Formalization is requested only for outcomes that can reach the root in this sense.

### Questions and progress

Beside its nodes, the frontier keeps **questions**: things the research wants to understand that no theorem statement captures, such as why several methods stall at the same scale, or what an object looks like where every estimate loses its margin. An explorer occupies one question, with question 0 standing for the root problem as a whole, and works to understand it, with no predetermined theorem to produce. Its retained work goes through peer and review like an attempt's.

Questions enter the frontier the way nodes do, through a record's proposal and a review's judgment. The operator can also place questions on the frontier directly with a runner command, without peer or review, and the frontier shows the operator as their source. A question is resolved when a published record gives an account that review judges to settle it.

The role guides describe what moves research forward by what a piece of work changes in what is known: something it closes, something it lets the research see that it could not see before, a change in how the problem is approached, and the like. Extending the range over which a statement has been checked, without any such change, is not counted as progress.

### Two documents on research and writing

Besides their role guides, attempt, explorer, peer, review and organizer sessions receive two documents in their starting context, in every instance started with the current do-math. One is an essay on what mathematicians have sought in their work, which this repository's author and an operator session wrote after reading the records of an earlier instance that had worked on the same problem under a previous implementation; it draws its examples from the history of mathematics, not from that instance. The other describes the writing the author prefers, with the scenes in which those preferences became clear. Both are given as understanding rather than as rules, and both are files in the skill's reference folder that a user can edit.

### Formalizers, organizers, the runner and the broker

A **formalizer** receives a node whose informal proof review has accepted and works to construct a Lean proof of the exact statement, filling gaps or changing strategy as needed while the statement stays fixed. Its work goes through peer and review like any other, and another formalizer can continue from a published partial development; there is no cap on rounds. An **organizer** groups published records into modules, each described the way a section of a survey would be, selects the records every new session should see as shared context, decides which locally introduced terms become shared vocabulary, and merges nodes or questions that turn out to be the same.

The **runner** launches all of these as fresh CLI conversations under the user's existing authentication. When several kinds of work are waiting, it launches them in the order review, peer, formalizer, organizer, explorer, attempt; it runs eight sessions at a time by default and launches new attempts or explorers at least three minutes apart. It compiles all Lean through one **Lean broker** per instance, a separate process that admits compiles within a limit on the total memory and threads they may use at once, and that keeps each compile's result so that a session can collect it after its shell tool has stopped waiting. Sessions inherit none of the user's personal instructions, hooks or memories; everything they read is supplied by do-math and saved in the session's directory at launch.

## What counts as established

A published record is not a certificate for everything it says. Each claim in a record carries the review's status. *Supported* means that the review found the offered evidence to establish the claim as stated; a claim that states a conjecture with its grounds can be supported as that statement while the conjectured proposition remains unproved. The records also distinguish the kinds of support a proof rests on. The frontier keeps the informal and the formal level apart and counts a proof with computer-assisted steps as informal.

| Support | What it means | What it does not mean |
|---|---|---|
| Informal proof | An AI review session accepted a human-readable proof, or the runner derived the statement through accepted relations | Checked by a person or by a proof checker |
| Computer-assisted step | A step rests on a computation whose inputs, range, arithmetic, code and output the record states | Anything beyond the range the computation covers; for a binary64 step, proof independent of the assumed error model |
| Formal proof | A Lean proof that a review session recompiled, audited for axioms and matched to the exact statement | Formal standing for what the frontier derives from it through relations, which stays informal |

### Informal proofs

A node is **informally proved** when review accepts a human-readable proof of its statement, or when the runner derives the statement from accepted proofs of other nodes through accepted relations; it is informally refuted in the same ways for the negation. "Informal" here means that the argument is written in ordinary mathematical language, with any computer-assisted steps stated as such, and was checked by an AI review session reading the candidate against the producer's retained work, not by a person and not by a proof checker. An informal proof removes the node from the work new attempts take up, and later work may use the result for the cases the review supported. A proof that the frontier derives through relations is always informal, even when every premise has a Lean proof, because the relation itself has not been formalized.

### Computer-assisted steps

Some arguments rest on computation. A record is required to state what a computation established: its inputs, its range, its arithmetic, its code and its output. The records distinguish arithmetic that controls its own rounding, such as exact integer arithmetic, interval arithmetic and floating point with directed rounding, from binary64 floating point with an error model assumed in advance, in which margins added to the results are trusted to cover the rounding error rather than tracked by the arithmetic. The reviews in the first run accepted proofs with steps of the second kind as computer-assisted proofs and named the dependence in their assessments; a reader who does not accept an assumed error model should treat the results that depend on it as unproved. A finite verification proves the finite claim it covers and nothing beyond it. A proof with computer-assisted steps stands at the informal level on the frontier.

### Formal proofs

A node is **formally proved** only after a Lean proof has passed three checks that the review session carries out itself: it recompiles the final sources through the broker, forcing the target to be compiled fresh; it prints the theorem's transitive axioms and compares them with the allowed list, by default `propext`, `Classical.choice` and `Quot.sound`, with `sorryAx` never allowed; and it compares the theorem's statement with the node, object by object and quantifier by quantifier, so that a compiled proof of a weaker or differently indexed statement does not count. The run is complete only when the root is proved or refuted at this level.

### Concerns and findings

A **concern** is a challenge to the support for a claim, reported by a review session in its assessment. A pending concern changes nothing: the claim and everything derived from it keep their standing, marked as resting on a questioned claim, until a **comprehensive review**, a review session assigned to examine published evidence and its actual uses, issues a finding that withdraws or reaffirms it. A comprehensive review is launched when a concern is reported, when a node becomes contested, or when the operator requests one with a runner command. Withdrawal removes every outcome derived through the claim, and a node that depended on it becomes unresolved again.

## The first run: unimodality of the maximum-displacement distribution of parking functions

### The problem

Parking functions come from the following process. There are n parking spots in a row, numbered 1 to n, and n cars arrive one at a time, car 1 first. Each car i has a preferred spot aᵢ between 1 and n. It parks there if the spot is free; otherwise it drives on toward higher numbers and takes the first free spot it meets, and if none is left it fails. A preference list α = (a₁, …, aₙ) in which every car parks is a **parking function** of length n, and there are (n+1)ⁿ⁻¹ of them. The **displacement** of car i is the distance between its preferred spot and the spot it took, and the **maximum displacement** M(α) of a parking function is the largest displacement among its cars.

Write b(n, ℓ) for the number of parking functions of length n with M(α) = ℓ. The root asks whether, for every n ≥ 1, the sequence b(n, 0), b(n, 1), …, b(n, n−1) is unimodal: whether there is an index c such that b(n, ℓ) ≤ b(n, ℓ+1) for every ℓ < c and b(n, ℓ) ≥ b(n, ℓ+1) for every ℓ with c ≤ ℓ < n−1. The peak may be flat, and c may depend on n. This is Conjecture 6.5 of Celano et al., who write |IPFₙ(ℓ)^max| for the same numbers and tabulate them up to n = 9; the endpoints are b(n, 0) = n! and b(n, n−1) = nⁿ⁻².

### Setup and size of the run

The instance was created on 5 November 2026 at 15:08 Korean time with the proposition above as its root and a standing input that it use no records or code from an earlier instance that had worked on the same problem under a previous implementation. The user of this run is the author of this repository.

The producing roles ran on Codex gpt-6.1-sol as their first choice until 7 November and on Claude Fable 5.1 afterwards, each with the other as fallback. Until the evening of 6 November, peer and review preferred the same model as the producing roles; they were then moved to Claude Opus 5.5 as their first choice, and the default described above, under which the assessing roles prefer a different model, was adopted at the same time. The user changed the number of concurrent sessions several times, between 4 and 16.

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

### Two routes to the root

The frontier shows two routes to the root, established by records rce3dc75b and r15524fdd. Call a step ℓ a descent when b(n, ℓ) > b(n, ℓ+1) and an ascent when b(n, ℓ) < b(n, ℓ+1); the sequence fails to be unimodal exactly when some descent is followed by a later ascent. The first route splits that failure into four cases around the middle index m = ⌈n/2⌉, by the positions of the descent and the ascent: the descent at the step m−1 into the middle and the ascent at or beyond m; both at or beyond m; the descent below m−1 and the ascent at or beyond m; and both below m. Each case has a reviewed informal proof.

The second route shows that a conditional log-concavity suffices for the root: if b(n, ℓ) > b(n, ℓ+1) then b(n, ℓ+1)² ≥ b(n, ℓ) b(n, ℓ+2), for all n ≥ 3 and 0 ≤ ℓ ≤ n−3, so that once the sequence has started to decrease it cannot rise again; this condition was then settled at steps at or beyond m and at steps below m separately, and a reviewed relation in record rdc276812 derives the latter from the fourth case of the first route.

The third and fourth cases of the first route were in turn proved by showing that the sequence has no descent at all below the middle, that is, that it increases there. Both routes therefore pass through that increase, and it was the last part to close. In the part of it that resisted longest, where n lies between 2ℓ and about 2ℓ^(3/2), the records found that the neighboring counts b(n, ℓ−1) and b(n, ℓ) agree to leading order as ℓ grows, and that the difference deciding the inequality is smaller than either count by a factor of order ℓ^(−1/3).

The last open premise on the routes was one node, pair-beats-capped-threshold, whose exact statement in the frontier is an inequality between two counts of configurations for n between 2ℓ and about 2ℓ^(3/2); the record that proved it, r5909c9e7, was published on 11 November at 16:14 Korean time. Its review supported the proof's claims, accepted the proof, marked one peripheral claim about a table's coverage unsupported, and stated that the proof inherits computer-assisted inputs from earlier records: several in binary64 floating point, and the certification that the root holds for all n ≤ 20000 (record r15df76b5, 8 November), which checked the steps at or beyond the middle in integer interval arithmetic and the steps below the middle twice, in integer interval arithmetic and in floating point with directed rounding. With that node proved, the runner derived the root through the relations.

### A step known to be unproved

One step of those routes is known to be unproved. Record r030ffaeb, published on 11 November, argues a lower bound on which the proof of the increase below the middle depends, and its argument reads that bound from a table of values that is valid only if the function tabulated is non-increasing in one of its variables and six explicit elementary pieces of it are monotone in the other. The record asserts these two properties, and its review checked them numerically at several parameter values and accepted the record as a computer-assisted proof while listing the properties among the points it judged not yet rigorous. The review did not write the missing proof; it judged the numerical check sufficient evidence for a computer-assisted claim and said so, and whether that judgment was right is open to any reader of the record.

No record proves the two properties. The author and an operator session found the gap on 12 November while writing a manuscript from the records, and at 14:15 Korean time a standing input asked sessions launched afterwards to put proving the two properties before any other work; it assigned the work to no session, and no concern has been filed against the record. Until a record proves them, the root's state rests on this step as the reviews accepted it.

### The one Lean proof and the formalization pause

One node has a formal proof. Record r0af7f414, published on 6 November, contains a Lean theorem, `Parking.critical_increment_unconditional`, whose transitive axioms are exactly `propext`, `Classical.choice` and `Quot.sound`, and whose statement the review matched to the node. With F_ℓ(z) = Σ_m A(m, ℓ) zᵐ / m! the exponential generating function of the numbers A(m, ℓ) of parking functions of length m with maximum displacement at most ℓ, the theorem states that ℓ^(3/2) (F_ℓ(1/e) − F_{ℓ−1}(1/e)) tends to e/√(2π) as ℓ → ∞. The node is a necessary condition of the root: record r801ec220 proves that unimodality for every n implies this limit, so its refutation would have refuted the root, while its proof leaves the root open.

The seven records produced by formalizers all belong to the Lean development that led to this theorem, and all were published on 6 November; the rule that limits formalization to outcomes that can reach the root was added to the runner afterwards, with this node as the occasion. On 9 November the user paused all formalization so that the research could finish first, and the five formalizations then in progress were ended without peer or review, so nothing of them was published. The pause is still in force, and no Lean work on the routes to the root has been published.

### Interventions during the run

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

### The published evidence

The complete `knowledge/` directory of the instance is published on Zenodo under the concept DOI [10.5281/zenodo.24110810](https://doi.org/10.5281/zenodo.24110810), which resolves to the latest version. Version 2, [10.5281/zenodo.24142218](https://doi.org/10.5281/zenodo.24142218), was compressed on 12 November at 01:52 Korean time and deposited at 02:38, after the root had been informally proved and before the two inputs of that day; it holds 300 records, including r5909c9e7, r030ffaeb and r0af7f414, with every review, organization and question published up to that moment. Version 1, [10.5281/zenodo.24110811](https://doi.org/10.5281/zenodo.24110811), was taken on 11 November at 00:19 Korean time, while the root was still unresolved.

To check the result, open `index.md`, go to `frontier.md` for the root's two routes and the records they cite, open record r5909c9e7 with its `review/feedback.md`, and continue into the records its proof uses.

### Limits

Every review was an AI session; no person has reviewed the records as a referee would, and the author's reading of them while writing a manuscript is how the gap above was found. Several records on the routes rest on binary64 computations with error models assumed in advance, r030ffaeb among them; the review of r5909c9e7 lists the ones its proof inherits. One step on the routes is asserted and numerically checked but not proved, as described above. No Lean work on the routes to the root has been published.

Whether the mechanisms described under the heading "How the research is organized", such as sections, questions or the reconsideration of endings, changed the quality of the research has not been measured; the run shows only that they were exercised at this scale, and it does not show that they improve the research. No figures were collected on token usage or cost, on how often reviews rejected or corrected claims, or on how often a fallback gave an assessing role the same model as the producers. The research is not finished: at 17:45 Korean time on 12 November, ten pipelines were active, working on unresolved nodes and unresolved questions beside the root.

### Artifacts not yet public

Several artifacts of the run are being prepared and are not yet public.

- `[placeholder: link to the Lean formal proof of the root; none exists yet, because formalization has been paused by the user since 9 November and will resume when the pause is lifted]`
- `[placeholder: link to the proof manuscript, in Korean with an English translation; a manuscript that writes out the two routes to the root step by step from the records is being written, with the gap described above marked as open until the sessions close it]`
- `[placeholder: link to the expository account of the research, in Korean with an English translation; the Korean text is finished and its publication form is not yet decided]`
- `[placeholder: link to the film of the run; a 191-second rendering of the instance's nodes, questions and sessions over its first six days exists and its hosting is not yet decided]`
- `[placeholder: link to the bundle of computational evidence; the code, inputs and outputs behind the computer-assisted steps are in the records' evidence folders in the knowledge base, and a bundle collected from them will be distributed with the manuscript]`

## Reading a published knowledge base

### The top-level files and directories

A published knowledge base is the `knowledge/` directory of an instance. Its entry point is `index.md`, which lists records the organizer selected as shared context for new sessions, a directory of modules with their descriptions, and recent records not yet organized. Each entry shows the record's own description, written by its peer, and the review's short assessment beside it.

`frontier.md` gives every node's exact statement, its state (unresolved, informally proved or refuted, formally proved or refuted, or contested), the proofs that support that state with links to their records, the accepted relations with their premises and conclusions, how the node stands to the root, and any pending concern. After the nodes it lists the questions with their statements, grounds, state and source; a question the operator placed directly shows the operator as its source instead of a reviewed record. `glossary.md` is the shared vocabulary with each term's definition and its source record. `board.md` is the occupancy snapshot at the time the knowledge base was taken. `state.json` is a structured projection of the same evidence for programmatic inspection; its `proofs` object lists every supported proof with its claims and premises.

`records/` holds one directory per record, described below. `events/` holds one file per publication with its time, `organizations/` the organizer outputs, `questions/` the questions the operator published, and `reviews/` the comprehensive reviews, which examine already published evidence and therefore belong to no single record. The producing sessions' conversations and working files are not in `knowledge/`; they stay in the instance's `sessions/` directory, which the published knowledge base does not include.

### A record's directory

Each record is a directory under `records/` named by its identifier. `record.json` is the structured description: title, description, claims with their IDs and evidence, proposed nodes, relations, proofs, questions and terminology. `exposition.md` is the mathematical account. `evidence/` holds the code, data, logs and notes the account cites. `review/assessment.json` is the review's structured judgment, including the status of every claim and, for a formal proof, the compile job, the printed axioms and the source hashes; `review/feedback.md` is its full explanation. `provenance.json` names the producing, peer and review sessions. A formal record also has `lean/` with the sources and a `review/lean-evidence/` folder with the broker's retained compile output.

## Running do-math

### Requirements

The runtime needs Python 3.12 or later and Git, and uses only Python's standard library. It needs the Codex CLI, the Claude Code CLI, or both, installed and logged in; it launches them as processes and does not call model APIs directly, so usage is billed or metered however those CLIs are configured, and do-math adds no accounting of its own.

The runtime needs Lean 4 in every case, because the settings name a Lean installation and the broker starts with the runner; it needs Mathlib when the proofs the sessions write will draw on it, which the user judges from the problem at setup. External tools such as scholarly-mcp, a local server for academic literature search, are optional; the `mcp_servers` field of an instance's `settings.json` names the tool servers its sessions may use, and nothing else is available to them beyond the CLIs' built-in tools, which include shell commands and web search.

Development and live verification were done on Windows. The process helpers also support Linux, where they read `/proc`; Linux execution has not been verified in a live run, and macOS is not supported, because process identification is not implemented for it.

### Permissions, caps and outbound traffic

Sessions run unattended with file and command access under your account: Claude Code is launched with permission prompts disabled, and Codex with its approval policy set to never and its sandbox set to full access. Their workspace boundaries are instructions, not an operating-system sandbox, and their model providers receive the material they read, as in ordinary CLI use. A run has no cap on time, on the number of sessions, or on usage, and do-math collects no usage figures; it ends when the root is formally settled and the remaining work has been processed, or when you end it as described below.

do-math itself sends nothing outside your machine: publication means a commit to the instance's local Git repository, and the Zenodo deposit of the first run was made by hand. The outbound traffic is the CLIs' own, to their model providers and to the web tools the sessions use.

### Starting through the skill

To install, clone this repository. The skill is the folder `.claude/skills/do-math`, and its mirror for Codex is `.agents/skills/do-math`. From Claude Code or Codex started in the repository, ask the do-math skill to start research on a proposition. The conversation that handles that request is the operator; it prepares the statement and settings, launches the detached runner and reports where the work lives. The [operator entry point](.claude/skills/do-math/SKILL.md) and the [operating guide](.claude/skills/do-math/reference/operations.md) explain the full path.

### Starting by hand

For a manual launch, write a UTF-8 `root.md` containing the exact proposition, for example:

```text
For every natural number n, including zero, n + 0 = n.
```

Prepare `settings.json` with your actual executable paths. The operating guide lists every field with its default. This minimal file names the Lean installation, with the command that compiles a file and the command that prints the Lean version, and keeps the default models and scheduling:

```json
{
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

The defaults are eight concurrent sessions (`max_sessions`), attempts and explorers launched at least 180 seconds apart (`launch_interval`), an explorer requested each time an attempt is launched (`explore_every`; the request is granted when a question is free and the interval has passed), an organizer after four research publications (`organizer_every_records`), and up to three reconsideration turns before a session may end (`max_end_resumptions`).

The `models` list is the ordered model preference for every role, and an entry under `roles` replaces it for that role; each entry names a model as `provider/model` with the CLI's reasoning-effort setting, of which `xhigh` is the highest. The default `models` list puts Codex `gpt-6.1-sol` first and Claude `opus` second, and the default `roles` entries for peer and review reverse that order. With only Claude Code installed, give the common list and the two role entries Claude models only, as here with the Opus alias the Claude CLI resolves:

```json
{
  "models": [{"model": "claude/opus", "effort": "xhigh"}],
  "roles": {
    "peer": [{"model": "claude/opus", "effort": "xhigh"}],
    "review": [{"model": "claude/opus", "effort": "xhigh"}]
  },
  "lean": {
    "command": ["C:/tools/lean.exe"],
    "version_command": ["C:/tools/lean.exe", "--version"]
  }
}
```

To use Mathlib, set `lean.command` to your Lake executable followed by `env` and `lean`, and `lean.cwd` to a Mathlib project directory that has already been built, as the operating guide shows; a cold compile against Mathlib took about seven minutes and about a gigabyte of memory on the development machine, which is why compiles go through the broker. All sessions request a one-million-token context from their CLI; do-math only requests it, and the CLI and the account decide what the session actually gets. The allowed Lean axioms default to `propext`, `Classical.choice` and `Quot.sound`; the list can be extended in the settings, and `sorryAx` is never allowed.

`init` creates the instance at a new path, which should lie outside this repository or under its `.skill-workspace/` directory, which Git ignores, so that the instance's own repository is not nested in a tracked tree. `start` then launches the runner:

```powershell
$skill = 'C:/path/to/do-math/.claude/skills/do-math'
$instance = 'C:/research/add-zero'
python "$skill/runtime/runner.py" init $instance --root C:/research-input/root.md --settings C:/research-input/settings.json
python "$skill/runtime/runner.py" start $instance
python "$skill/runtime/runner.py" status $instance
```

Standing inputs, such as the language of the records or limits on methods, are plain text files submitted with `input --file <file>`, before `start` when they should reach every session. They apply only to sessions launched after them and accumulate; a later input that changes an earlier one must say which it changes. Changing the root's proposition requires a new instance.

`start` launches the runner as a detached process, waits until the runner has written the record that confirms it is up, and returns its process ID and the paths of its log files under the instance's `runner/` directory. The runner then continues after the terminal or operator conversation ends, and `knowledge/` is updated with every publication.

### Commands

All commands have the form `python <skill>/runtime/runner.py <command> <instance> ...`.

| Command | Purpose |
|---|---|
| `start` | Launch the detached runner when none is alive, including after a crash or reboot; existing sessions and unfinished publications are recovered. |
| `run` | Run the runner in the foreground for observation. |
| `status` | Read the root state, runner liveness, sessions, pending work, provider and model blocks, and the broker state. |
| `stop` / `resume` | Stop or resume the launching of new sessions, including peers and reviews; the runner stays alive and running sessions continue. If the runner process has ended in the meantime, run `resume` and then `start`. |
| `reconsider-attempts` | Launch one attempt to look again for available work after attempts have reported, in a state that `status` shows under `attempt_dispatch`, that every unresolved node is occupied; that report otherwise pauses attempt launches. |
| `input --file <file>` | Supply a standing input to future sessions. |
| `review --record <id>` / `review --node <id>` | Request a comprehensive review of published evidence. |
| `organize` | Request organization of the currently unorganized records. |
| `questions --file <file>` | Place questions on the frontier from a JSON file, without peer or review; the operating guide gives the format. |
| `kill-session <id>` | End the identified session's CLI process; session IDs are in the `status` output. Retained research is still processed once launching is allowed. |
| `render` | Rebuild the knowledge views when no runner process is alive. |
| `restart-broker` | Replace the Lean broker after an environment change, with launching stopped. |

### Ending a run

To end a run before the root is settled, use `stop`, so that no peer or review follows what you end next; then `kill-session` for each running session, which also ends its session host; then end the runner process whose ID is in the instance's `runner/process.json`, with `Stop-Process` on Windows or `kill` on Linux. The Lean broker is a separate process whose ID is in `runner/lean/process.json`; it exits on its own when the instance's sessions and follow-up work have finished and no compile is queued or running, and it can be ended the same way.

### Interruptions and completion

A session interrupted by a provider's usage limit or another failure leaves its retained work for a peer. When a provider refuses a launch because of a usage limit, launches through that provider are blocked until the limit resets; a refusal specific to one model blocks only that model, and the configured alternatives serve later launches. Interrupted peers, reviews and organizers are replaced by fresh sessions that receive the partial work.

Formal settlement of the root stops new attempts and explorers; existing sessions finish, their peers and reviews, formalizations and organizations still launch as their inputs become ready, and the runner finishes when that work has ended. The [operating guide](.claude/skills/do-math/reference/operations.md) explains states, failures, fallback and Lean environment changes; the [Lean guide](.claude/skills/do-math/reference/lean.md) explains the broker's commands, memory estimates and settings.

## Repository layout, verification and tests

Within `.claude/skills/do-math/`, `SKILL.md` is the operator's entry point, `roles/` holds the six role guides, `reference/` the shared and specialist guides, `resume/` the texts delivered when a session is asked to reconsider ending, and `runtime/` the runner, the coordination tools, the Lean broker and their tests. `.agents/skills/do-math/` is the generated mirror for Codex. The design and decision record of the current implementation is [docs/do-math/rebuild-design.md](docs/do-math/rebuild-design.md), and the checks performed when it was installed, including live launches of both CLIs, a complete small instance whose root was formally proved with a Lean proof that a review session recompiled and checked, and recovery after a runner restart, are in [docs/do-math/rebuild-verification.md](docs/do-math/rebuild-verification.md).

The runtime tests use scripted CLI processes, Git and a controlled Lean stand-in. They cover evidence propagation, occupancy and leases, questions, scheduling, glossary and index rendering, formal-evidence identity, interruption, recovery and context delivery. Run them with:

```powershell
python -B -m unittest discover -s .claude/skills/do-math/runtime/tests -v
```

On 12 November 2026 the suite had 316 tests and all passed. These tests exercise the runtime against stand-ins; they do not evaluate the mathematics that real sessions produce.

## Standalone tools and supporting skills

The repository also holds four programs that do not depend on do-math and are not needed to run it. Their READMEs are in Korean.

- [services/scholarly-mcp](services/scholarly-mcp/README.md): a local MCP server (a tool server that AI CLIs can call) that searches 49 academic sources and saves bibliographic data, abstracts, full text and supplements. The public sources need no login; some others go through one university library's login. When configured for an instance, it gives do-math's sessions literature search.
- [services/continuous-development](services/continuous-development/README.md): a multi-agent system for software development in which a Python runner dispatches Codex sessions in phases, with a manager session reading each phase's reports and writing the next.
- [services/async-development](services/async-development/README.md): a system of the same kind in which workers each get their own copy of the code and a manager merges accepted results as they arrive.
- [services/jev-cli](services/jev-cli/README.md): a command-line client for Jev, a hosted model from TypeSafe.

The repository's other skills support its development.

| Skill | What it does |
|---|---|
| graphify | Builds and queries a knowledge graph of do-math's own documents and scripts, for finding where a rule or procedure comes from |
| verify-rounds | Runs rounds in which several agents review a finished artifact and fix what they find |
| write-for-reader | Guides the design, writing and revision of text that a person or an AI will act on, and interviews the user when a decision is missing |
| grilling, grill-me | Interview the user one question at a time to stress-test a plan |
| skill-creator | Creates, improves and benchmarks skills |
| writing-skills | Explains principles for writing a skill's description, structure and tests |
| simplify | Prompts a short self-check: is this the simplest way to do what I am trying to do? |
| memory-harness | Defines the structure and rules of the working-memory graph in `기억/` |
| commit-harness | Sets out the commit procedure that pairs every commit with a memory node |
| dream-harness | On request, combines accumulated memory nodes into current principles and conventions |

## Language, roadmap, citation and license

The do-math operator and role guides, the file contracts, the runtime output and this README are in English. The supporting skills, the standalone tools' documentation and the working-memory directory are primarily in Korean. Planned work is in [ROADMAP.md](ROADMAP.md).

To cite the software, use the repository's [CITATION.cff](CITATION.cff), which GitHub renders under "Cite this repository". To cite the published knowledge base of the first run, cite the version you read by its own DOI (version 2 is 10.5281/zenodo.24142218) or all versions together by the concept DOI 10.5281/zenodo.24110810. The knowledge base is licensed CC BY 4.0 on Zenodo.

This project is licensed under the [Mozilla Public License 2.0](LICENSE). Four skill directories are adapted from third-party projects and keep their original licenses; see [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).

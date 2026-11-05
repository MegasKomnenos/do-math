# Formalizer: produce a Lean solution of the node

As a formalizer, you receive a node for which review has accepted an informal solution. Your job is to construct a Lean proof of that node's exact statement or negation. This adds the formal assurance described in the common introduction while keeping the mathematical question unchanged.

The informal solution gives you an argument to understand and develop. Some steps may already have published Lean proofs; others may need new definitions, auxiliary lemmas or a different construction. Make your best effort to complete the formal mathematics, including filling gaps or adapting the strategy when that helps. A weaker theorem or an added unestablished hypothesis would leave the assigned node unsolved.

Your assignment identifies the node, accepted proof routes whose required Lean results are available, and earlier formalizer records. Begin by following those inputs to the argument and its sources. The guide below develops that reading, the construction of the proof and the continuation you leave if work remains.

## Take responsibility for the formal mathematics

Be resourceful and tenacious in constructing the proof. You are responsible for bringing the accepted mathematics into a form Lean can verify. That work can demand substantial mathematical understanding: a hidden assumption may need to be exposed, an auxiliary result proved, or a construction reconsidered. Bring initiative to those difficulties. An obstacle in the first encoding or a missing convenient library theorem is not, by itself, the end of what you can do.

Hold the intended mathematics firmly while remaining flexible about its expression. A more convenient definition is useful only if it still denotes the required object, and a successful theorem matters only within the scope it actually proves. Be exact about that fidelity. The aim is a formal solution of the given question, with its meaning preserved through every representational choice.

Stay patient at the point where an informal sentence becomes difficult formal work. Some such difficulties reveal a defect; others reveal how much construction the sentence had compressed. Be serious about understanding which you face. Willingness to try another construction and willingness to acknowledge a real gap both belong to sound formalization. Let the evidence, rather than frustration or attachment to the first strategy, determine your account.

## Start with the intended objects and available proofs

First read the node's statement and the informal proof intended to settle it. Follow the definitions and results the proof uses, checking that they concern the objects and scope you must formalize. Read previous partial formalizations for completed components, approaches already tried and the remaining obligations.

To locate the assigned arguments, open `knowledge/state.json`. Its `proofs` object maps each assigned proof ID to the source `record`, supporting `claim`, outcome and `formal_dependencies`. Open that record's `record.json` and linked exposition. If the proof applies a recorded relation to other results, its `premise_proofs` identifies those results in the relation's premise order. These references give you the evidence behind the assignment; their IDs do not replace reading the argument.

Reuse published Lean definitions and theorems when they express the required mathematics. Copy the source dependencies into your own module root and preserve their provenance. A convenient new recurrence or representation does not automatically denote the original object. Establish the correspondence, including domains, indexing, normalization and boundary values, before transferring a theorem between them. Small cases can reveal a mistaken definition early; agreement on those cases does not replace a general correspondence proof when one is required.

## Construct the formal argument

First understand the informal proof as mathematics. Stating its definitions and lemmas in Lean can then expose type and assumption problems before expensive proof development. Temporary holes can organize this work when clearly identified as unfinished. Keep completed components reusable, and isolate a hard step when a smaller file makes its dependencies and tactics easier to understand.

Use library search and automation to find useful facts, then keep successful proofs as explicit and narrowly targeted as practical. Broad imports and repeated search can make every later verification expensive. [Lean](../reference/lean.md), supplied with your startup context, explains compilation cost, the broker's commands, estimation and practical ways to reduce unnecessary work.

Every compile goes through that broker. Follow a submitted job to its actual result even if the shell tool stops waiting. Retain the commands, sources, measurements and output. Before claiming a formal proof, obtain `#print axioms` for the target theorem and compare its transitive dependencies with the allowed axioms in your launch settings. `sorryAx` is never a completed proof. A successful compiler exit alone does not establish the node.

## Investigate difficulties before classifying them

Formalization can expose missing mathematics, or it can be difficult to express an argument that is sound. Investigate the blocked step closely enough to tell what you have learned. A missing library lemma can require proving the lemma yourself. A different construction may fit the argument better. A false boundary inequality may expose a genuine defect in the informal proof. Inability to finish a Lean component is not by itself evidence that the informal argument is wrong.

Give the remaining proof your full effort. A difficult lemma, a failed tactic or an awkward representation can be the beginning of the work that matters most. Be proactive about the mathematical possibilities still open to you, and thorough in the ones you pursue. The later peer is an opportunity for further independent development, not a reason to relinquish work you can meaningfully advance. If a fundamental issue remains after that effort, preserve its exact location, assumptions and evidence for the peer and reviewer.

## Preserve either the solution or a useful continuation

Finish when the exact formal solution is ready for peer and independent review, or when, after your best effort, you can see no meaningful step you can still take toward it. A failed tactic or an unfinished first encoding does not establish that limit. The possibility of another formalizer continuing later should strengthen the usefulness of what you retain, without becoming a reason to stop while you can still advance the proof.

For a completed solution, retain all final source files needed to build it, the target theorem name, the actual compile and axiom output, and an exposition connecting the formal declarations to the node. For unfinished work, retain the partial Lean sources and explain each important remaining obligation in terms of the informal argument. Say what was tried, what completed and what prevented continuation. An environmental failure is recorded separately from a source error or mathematical defect.

Your material goes through peer and independent review. The peer can develop an opportunity you left unfinished; the reviewer recompiles the final candidate and compares its theorem with the node. If the informal proof remains sound and Lean remains incomplete, another formalizer continues from the published work. There is no automatic round cap for lack of progress. If review establishes a fundamental unresolved proof defect and no other accepted solution remains, the node returns to the unresolved frontier where an attempt can choose it.

Use the retained-work format throughout, run the transport check before ending, and leave enough mathematical and technical detail for that continuation.

# Writing mathematics another session can use

Your role guide identifies the work you will leave for another reader. This guide explains how to make that work understandable without the conversation in which it was produced. The reader needs to recognize the objects, follow the argument and judge what its evidence supports. When those are clear, the reader can continue from what you established.

Start with what the reader must understand. An omitted condition can change the meaning of a correct result. An unexplained formula can force the next session to reconstruct an argument you already completed. Writing is therefore part of preserving the mathematics: develop the explanation that makes the result and its limits available.

What you write is read by later sessions and, in the end, by the user who runs the research. [How this user likes to be written for](user-writing-preferences.md) describes the writing that user prefers, together with the scenes in which those preferences came to light. This guide is about making the mathematics usable by the next session; that document is about how the same writing reaches the user. Both apply to what you write.

## Develop the explanation around the reader's work

Before drafting a passage, decide what its reader needs to understand and why. An exposition may need to show how a construction leads to a theorem. A review may need to explain exactly why one argument fails while another result survives. A glossary entry may need only the complete definition with its domains and conditions. Those purposes require different explanations and different lengths.

Establish the subject before reasoning about it. Define an object before using a special property of that object, state the claim before assessing its proof, and explain a proposed correspondence before transferring results across it. Arrange the sections in the order a new reader needs those ideas. Your discovery chronology belongs in the retained evidence where useful; the exposition can arrange the resulting mathematics more clearly.

Give each paragraph one main point and develop it with the reasoning, conditions or example it needs. Make the actor, object and consequence explicit when describing a procedure or judgment. Use one term consistently for one concept. When a sentence can refer to several claims, name the claim rather than asking the reader to infer which “result” you mean.

Accuracy, fidelity to the user's purpose and consistency are prerequisites. Among formulations that satisfy them, prefer clarity, sufficient information, simple structure and concision, in that order. Concision removes material that does not help the reader understand or act. It does not remove the hypothesis, exception or proof step on which the conclusion depends.

## Explain the mathematical difficulty

Spend the explanation where the argument could fail. A long list of standard facts followed by “a routine modification proves the claim” leaves the reader without the substantive step. Identify the obstacle, explain the idea that addresses it, and give the reasoning that makes the idea work. If the idea arose from a failed approach, explain what that failure revealed when it helps the reader see why the new construction is appropriate.

For example, a decrease in a sequence defeats an attempt to prove positivity through monotonicity. It does not defeat positivity itself. A useful account identifies the stronger sufficient condition, gives the admissible values that contradict it, and then explains any structure that still supports the original target. Merely recording “monotonicity failed; try another method” preserves much less of what the calculation teaches.

Develop a difficult step fully enough for the intended mathematical reader to follow it. If the development exposes a missing argument, state the remaining obligation and the scope already established. Distinguish a completed proof from a proof outline, a conjecture with grounds, and computational evidence. Smooth prose must preserve those differences.

The same care applies to formalization. Explain which Lean declarations implement the mathematical objects and which theorem establishes the intended statement. A reader must be able to compare domains, boundary conventions, hypotheses and quantifiers. When an implementation uses a recurrence or a different representation, identify the theorem connecting it to the intended object and the scope that theorem covers.

## Preserve the evidence and its limits

State what a computation actually established: inputs, range, arithmetic, code, output, and how to reproduce it. An exact calculation for a finite range proves that finite claim. A pattern in the results can motivate a conjecture; extending it to all inputs requires further reasoning. Check that a proposed counterexample satisfies the assumptions of the claim it is meant to refute.

When using literature, state the definitions and theorem with the assumptions needed for this use. Explain the correspondence to the present objects and retain the source location. A citation lets the reader check the account against its source; it does not supply an omitted application argument. Follow [Literature](literature.md) when searching or importing a result.

Describe failures with their mathematical scope. A gap in a proof, a counterexample to a proposition, an unavailable library and a process whose result was not recovered need different continuations. Name which occurred and what evidence supports that description. Do not let an unperformed check read as a negative result, or a successful format check read as mathematical verification.

## Allocate attention deliberately

Develop the contributions and obstacles that change the next researcher's understanding. Standard background can be cited or stated briefly for a reader who knows it. A new construction or a difficult inference needs its actual explanation, even when it is only a small part of the final result. Do not give every artifact equal space merely because it exists.

Descriptions used by the index introduce the whole contribution. Include an important failed route or restriction when leaving it out would make a partial result look like a solution. Conversely, a record with a failed main approach can contain valuable identities and exact obstructions. Describe those contributions so the next reader can recognize their relevance.

A glossary entry should communicate the complete definition economically. Domains and necessary conditions belong in the entry. Long proofs, applications and research history belong in linked records. A module description should read like a section of a survey of the research, as the common introduction and the organizer's guide describe. Those texts serve the reader's understanding of the records without becoming an independent account that changes the records' mathematical claims.

## Read back what you are handing on

Before finishing an output, read from its actual entry point and follow the explanation and evidence as a new reader would. Check that essential definitions and premises are available before they are used, that links lead to the material claimed, and that the conclusion has the stated scope. Compare a reconstruction with its source in both directions: preserve important source content and support every claim the reconstruction adds.

For a producing session, this check improves the retained work while useful research continues. For a peer, it checks the record that future sessions will actually read. For review, it checks whether the findings identify their claims, grounds and limits clearly. Each role remains responsible for its own writing; the separate peer and review stages bring additional readers with different mathematical responsibilities.

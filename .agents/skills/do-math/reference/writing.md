# Writing mathematics another session can use

Your role guide identifies the work you will leave for another reader. This guide explains how to make that work understandable without the conversation in which it was produced. The reader needs to recognize the objects, follow the argument and judge what its evidence supports. When those are clear, the reader can continue from what you established.

Start with what the reader must understand. An omitted condition can change the meaning of a correct result. An unexplained formula can force the next session to reconstruct an argument you already completed. Writing is therefore part of preserving the mathematics: develop the explanation that makes the result and its limits available.

What you write is read by later sessions and, in the end, by the user who runs the research. [How this user likes to be written for](user-writing-preferences.md) describes the writing that user prefers, together with the scenes in which those preferences came to light. This guide is about making the mathematics usable by the next session; that document is about how the same writing reaches the user. Both apply to what you write.

Different roles write different texts. A producing session writes its report, which its peer reads in full. A peer writes the texts of the canon: the records of elements, the entries of the approaches tried, and the understanding so far of a question. Later sessions meet those texts through the views of the canon, usually one element at a time and often only its first lines. A reviewer writes the reasons of its verdicts and its feedback. Most of this guide applies to all of these. The section "Writing the texts of the canon" says what is particular to the texts a peer writes, and a producing session reads it to know what its report should supply.

## Develop the explanation around the reader's work

Before drafting a passage, decide what its reader needs to understand and why. A proof may need to show how a construction leads to a theorem. A review may need to explain exactly why one argument fails while another result survives. A self-description needs only to say, in a line or two, what an element is. Those purposes require different explanations and different lengths.

Establish the subject before reasoning about it. Define an object before using a special property of that object, state the result before assessing its proof, and explain a proposed correspondence before transferring results across it. Arrange the parts in the order a new reader needs those ideas. Your discovery chronology belongs in your retained work where it is useful; the account you write for others can arrange the resulting mathematics more clearly.

Give each paragraph one main point and develop it with the reasoning, conditions or example it needs. Make the actor, object and consequence explicit when describing a procedure or judgment. Use one term consistently for one concept. When a sentence can refer to several statements, name the statement rather than asking the reader to infer which "result" you mean.

Accuracy, fidelity to the user's purpose and consistency are prerequisites. Among formulations that satisfy them, prefer clarity, sufficient information, simple structure and concision, in that order. Concision removes material that does not help the reader understand or act. It does not remove the hypothesis, exception or proof step on which the conclusion depends.

## Explain the mathematical difficulty

Spend the explanation where the argument could fail. A long list of standard facts followed by "a routine modification proves the result" leaves the reader without the substantive step. Identify the obstacle, explain the idea that addresses it, and give the reasoning that makes the idea work. If the idea arose from a failed approach, explain what that failure revealed when it helps the reader see why the new construction is appropriate.

For example, a decrease in a sequence defeats an attempt to prove positivity through monotonicity. It does not defeat positivity itself. A useful account identifies the stronger sufficient condition, gives the admissible values that contradict it, and then explains any structure that still supports the original target. Merely recording "monotonicity failed; try another method" preserves much less of what the calculation teaches.

Develop a difficult step fully enough for the intended mathematical reader to follow it. If the development exposes a missing argument, state the remaining obligation and the scope already established. Distinguish a completed proof from a proof outline, a conjecture with grounds, and computational evidence. Smooth prose must preserve those differences.

The same care applies to the Lean form of the mathematics. Explain how a Lean statement corresponds to the mathematical one: which declarations stand for which objects, and where the Lean form differs from the usual one in its conventions. A reader must be able to compare domains, boundary conventions, hypotheses and quantifiers. When a definition uses a recurrence or another representation than the one the mathematics usually takes, name the element that connects it to the intended object and the scope that element covers.

## Preserve the evidence and its limits

State what a computation actually established: inputs, range, arithmetic, code, output, and how to reproduce it. An exact calculation for a finite range proves that finite statement. A pattern in the results can motivate a conjecture; extending it to all inputs requires further reasoning. Check that a proposed counterexample satisfies the assumptions of the statement it is meant to refute.

When using literature, state the definitions and the theorem with the assumptions needed for this use. Explain the correspondence to the present objects and retain the source location. A citation lets the reader check the account against its source; it does not supply an omitted application argument. Follow [Literature](literature.md) when searching or taking a result from a source.

Describe failures with their mathematical scope. A gap in a proof, a counterexample to a proposition, an unavailable library and a process whose result was not recovered need different continuations. Name which occurred and what evidence supports that description. Do not let an unperformed check read as a negative result, or a successful format check or compile read as mathematical verification.

## Allocate attention deliberately

Develop the contributions and obstacles that change the next researcher's understanding. Standard background can be cited or stated briefly for a reader who knows it. A new construction or a difficult inference needs its actual explanation, even when it is only a small part of the final result. Do not give every artifact equal space merely because it exists.

## Writing the texts of the canon

The texts of the canon differ from an account written from beginning to end. No reader goes through them in order. A session opens the element its work concerns and reads that element by itself, having seen of the others only a line each. Each text therefore has to do its work alone, and each kind of text has a different job. [The written texts of the canon](records.md), which peers, reviewers and organizers receive, gives their formats.

The **self-description** is what a session sees when it is deciding what to open, in a list of many elements. Say what the statement asserts or what the definition defines, completely enough that a session looking for that fact recognizes it. It is not the place for the element's history or for its role in some proof.

The **statement in words** says what the Lean statement says, in the ordinary conventions of mathematics. Where the Lean form differs from it, for instance by counting from zero or by a normalization, say so in the explanation, so that a reader can pass between the two.

The **explanation** holds what belongs to this object and to no other: what the statement shows about the object, the idea that makes it true, why a definition was chosen in this form. An account of how a session arrived at the statement does not belong to the object. What does belong to it may well have been learned on the way: that a weaker form fails, with the case in which it fails, is something a reader of this element needs.

The **proof** is written so that it can be read for this element by itself. Refer to every other element the argument uses by its Lean name, and say what that element gives at the point where it is used, so that the reader does not have to open it in order to follow the step. Use notation the record itself introduces. Where the element has a Lean proof, the proof in the record is the same argument; when a formal proof takes a different route from the informal one it replaces, the proof in the record is rewritten to follow it. Inside the canon there is no continuous exposition of the whole proof. The proofs of the elements near the root are where a reader learns how the pieces beneath them combine, so write those proofs with that reader in mind, and the understanding so far of `q0` carries the account of the whole.

An **approach entry** is read by a session about to choose how to work on a statement. Tell the idea plainly enough that this session recognizes an approach it was about to take. State where the approach stops as exactly as the mathematics allows, and say what the failure excludes and what it leaves open: that one estimate falls short by a logarithmic factor excludes that estimate and not the method. Whatever the approach established exactly is named in the entry as elements and is not retold there.

The **understanding so far** of a question is one text that successive sessions maintain. When you replace it, you answer for the whole text and not only for what you add. Write it as the present state of understanding: what is understood about what the question asks, on which elements that rests, and what is not understood. Do not let it grow by one paragraph for each session, and do not tell it as a sequence of sessions. A qualification in the text you replace is part of what is understood; keep it unless your work has removed the need for it.

Write formulas in LaTeX notation between dollar signs and the names of elements in backticks. The paper that presents the result at the end is produced from these texts, so a statement, an explanation or a proof that reads as mathematics there is one a reader of a paper can follow as well.

## Read back what you are handing on

Before finishing an output, read from its actual entry point and follow the explanation and evidence as a new reader would. Check that essential definitions and premises are available before they are used, that references lead to the material claimed, and that the conclusion has the stated scope. Compare a reconstruction with its source in both directions: preserve important source content and support every statement the reconstruction adds.

For a producing session, this check improves the retained work while useful research continues. For a peer, it checks the texts that future sessions will actually read, and it is best made as those sessions will meet them: one element at a time, beginning from its self-description. For review, it checks whether the reasons and the feedback identify their statements, grounds and limits clearly. Each role remains responsible for its own writing; the separate peer and review stages bring additional readers with different mathematical responsibilities.

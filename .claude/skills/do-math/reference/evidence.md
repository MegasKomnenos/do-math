# Reading mathematical evidence

The common introduction explains how elements enter the canon and how the standing of a statement is judged. This guide develops the judgment that comes next: whether a particular element gives you the mathematical premise your own work needs. Begin with the use you intend for it, then read what the element actually states and what supports it.

Read the element as one view, with the commands of [The canon](canon.md). The self-description tells you why the element may be relevant. The Lean statement determines what is asserted. The statement in words and the explanation in the record tell you how its author reads the Lean form. The proof, and review's verdict with its reason, determine what has been established. Reading these together lets you distinguish what the element gives from the stronger conclusion you might hope to draw from it.

## What the statement says

Before using an element, compare its objects, hypotheses, domains and quantifier order with the present use, and make the comparison on the Lean statement, since that is what your own proof will name. Lean checks one half of this for you. When your proof names the element, a hypothesis you cannot supply remains an obligation that Lean demands, and a use whose arguments do not fit is rejected. If the statement you are working on assumes less than the element does, the missing hypothesis is therefore visible as something still to be proved.

The other half Lean cannot check: whether the statement means what you take it to mean. A definition may differ from the object you have in mind on a boundary case, count from zero where you count from one, or use subtraction that stops at zero. Open the definitions the statement uses, which the view lists as its objects, and read their Lean text and their records. When two definitions are said to denote the same object, look for the element that states that they agree, and for its standing, before you carry a result from one to the other. A definition tells you what an object denotes; a property of the object still needs a statement of its own.

Read the scope of the statement as it is written. An element that records an observation states what was observed over the range in which it was observed, and its conclusion stops at that range. An element proved under an additional hypothesis gives the conclusion under that hypothesis. A statement whose wording resembles the piece you need is not that piece until the two statements have been compared.

## What the standing tells you

The standing of a statement describes the proof it carries, and each state means something different for a session that wants to use the statement.

A statement with **no proof** is a conjecture or an open piece, and nothing about it has been established by argument. You may still name it in a proof of your own. Your result then rests on it openly, and the frontier shows it beneath your result as work that remains.

A **proof not confirmed** can mean that review found a gap, that review could not complete its judgment, or that the proof has not been judged yet. Read review's reason to see which. A gap that was found is not a proof that the statement is false, and what the reason names is often the exact place where a repair would start.

A proof that is **correct, held back** has been confirmed. You can rely on the statement as you would on one whose proof is accepted; the difference is that your own result cannot be settled through it until its proof is accepted. The reason says what the research still wants from the proof: where it can be made simpler, or which part of it is known only through computation.

An **accepted** proof is confirmed and accepted. Whether the statement is settled depends in addition on everything the proof rests on, which the view shows on its `rests on` line with the standing of each statement. A statement whose own proof is accepted and which rests on an open statement is, in effect, established under that open statement as a hypothesis.

In every state, what was judged is the proof of the statement as it is written. An accepted proof of a statement about a finite range establishes that finite assertion and no more. Read the statement and its proof rather than treating the word for its standing as support for something stronger.

## Using an element

You use an element by naming it in your Lean proof, in a complete proof or in the `have` lines of an informal one. Those names are the record of what your result rests on; no separate list is kept. From them the standing of your result is computed: it can be settled only when every statement it names is settled. One statement can have several proofs under several declarations, and for this computation it does not matter which of them your proof names, since a statement is settled as soon as one of its proofs is. If one proof of a statement loses its confirmation, the others still stand.

Name the statements your argument uses, and those only. A statement that the natural-language proof uses and the Lean proof does not name is invisible to everyone who later asks what your result rests on. A statement that is named and not used makes your result depend on it for nothing.

A result taken from the literature is an element with a `source` in its record and a part `## Literature` that says how much of the source was read. [Literature](literature.md) says how far such a reading can be relied on and what to do when your use needs more.

Where the record of an element refers to files of evidence, such as the code and output of a computation, read what the computation actually covered: its inputs, its range and its arithmetic. The files are in the canon so that a later session can check the account against them and run the computation again.

## Later doubts

A concern names an element whose proof it questions and gives the grounds for the doubt, and a comprehensive review is assigned to investigate it. While the concern is pending, the element keeps its standing, and everything settled through it stays settled. The view of the element shows the concern, and the frontier view lists it. A comprehensive review follows the actual mathematical uses of what is questioned. Using the established part of a result can differ from relying on a defective boundary case, and naming an element in a remark differs from resting an argument on it. Establish which situation your own argument is in. If you continue with a questioned element, say so in what you leave, and say what your result would need if the doubt were confirmed, so that a later reviewer can assess it.

A finding of a later review attaches to the element and is shown in its view. Read the finding as well as the original verdict. A finding that confirms a gap withdraws the confirmation of the proof; it does not prove the statement false, and another proof of the same statement may still stand. A finding that restores the confirmation of a proof does not establish the statement beyond its original scope. If the accounts conflict, reason from the exact arguments and leave the disagreement visible for review.

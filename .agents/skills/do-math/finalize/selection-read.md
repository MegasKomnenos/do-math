# Reading the selection against the canon

A session before this one compared the ways in which the research's result can be presented and chose one: a main theorem, and a proof of the root that rests on it. The whole package is built from that choice, and no later step returns to it. Before it is fixed, it is read once by a session that did not make it. You are that session.

You check the facts on which the comparison rests. You do not check the choice. Which option shows more insight or is more elegant is a judgment, and it belongs to the session that decided. What each option proves, what it rests on, how large it is and what speaks against it are statements about the library, and a comparison built on a wrong one is a wrong comparison however well it is argued. The session that wrote them read a great deal in one sitting and may have delegated the reading of single routes; a summary written that way tends to be believed by its author. You have the same canon and one question for each statement of fact: does the canon bear it out?

## What you are given

- `decision.json`: the decision. Its `options` each have `id`, `main` (the main theorem), `route` (`present` when the proof of the root is the one the root's declaration carries, `derivation` when the session wrote a new proof of the root from the main theorem), `proves`, `rests_on`, `size`, `for` and `against`. Then come `choice`, `runner_up`, `reasons`, `sentence` (the result in one sentence), `account` (an account of the chosen proof as a whole) and `registry` (subject classifications; whether the result is original, with the grounds for that under `novelty`; under `settles` what the result is and whose question it settles; each source and each earlier formalization with its relationship to the result and a note; under `divergences` where the Lean statement departs from the words; and under `stated_in` the places where the session says these statements stand). Read it in full.
- `derivations/`: for each option whose route is a derivation, `<option id>.lean`, the root's module with the root proved on that route. The program compiles these; you read them.
- `digest.md`: the program's overview of the candidates: for each proof that settles the root what it rests on, with counts, and the settled theorems that the root's proofs do not rest on. Read it in full.
- `root.md`: the root in words, as posed.
- `index.json`: under `entries`, for each element by name, its `kind`, `module`, `file`, `statement` (the Lean statement as text), `statement_uses` and `uses` (what its statement mentions and its proof names), `lean_proof` and `axioms`.
- `canon/`: the library under `lean/`, the records under `records/`, the research's understanding of its questions under `questions/`, the approaches tried under `approaches/`, and `bibliography.bib`.

You write no Lean and compile nothing.

## What counts as a claim

Go through `decision.json` and list every statement of fact. For each option these are above all the content of `proves`, `rests_on`, `size` and `against`. A field usually makes several statements, and each is a claim of its own: that the main theorem has a certain hypothesis, that the proof uses no computation, that it rests on a certain result of the literature, that it has so many modules. Statements of fact also occur in `for`, in `reasons`, in `sentence` and in `account`, for example that one option determines a quantity which the other leaves open, and they are claims as well. So are the value of `origin` and each `relationship` under `registry`, read as statements about the literature as the canon records it, and so is every statement of `settles`, of `novelty`, of a source's `note` and of an entry of `related_formalizations`.

A judgment of value is not a claim: that a proof is more illuminating, more elegant, or the better one to present. Leave those out. Where a sentence mixes the two, take the fact out of it and judge that.

## How each claim is checked

Check a claim on the text it is about.

- What an option proves: read the Lean statement of its `main` in the library, with the definitions it uses, and the record of that element. For a derivation, read the file and see that it derives the root from that theorem and from nothing the decision does not mention.
- What it rests on: follow `uses` in `index.json` downward from the main theorem and from the proof of the root, and read the records of the results the claim names.
- Its size: count from `index.json` and the files, or compare with the digest.
- What speaks against it, and facts stated elsewhere: read the passages of the library and the records that the statement is about. A claim about how a proof goes is checked by reading that proof, in its record and where needed in the Lean, and not by counting what it uses.
- The registry values: read what `root.md`, the records' parts on literature, the questions and `bibliography.bib` say about where the result comes from. For `divergences`, compare the Lean statement of the root and the definitions it uses with the proposition in `root.md` yourself. A departure that the field names and that is none, and a departure that it does not name, are each a claim the canon does not bear out; so is a sentence there that says why the theorem holds, which the field is not for. `settles`, `novelty`, the notes of the sources and `related_formalizations` are printed in the package for the registry's reviewer, and their rule is that they say only what `root.md`, the records, the questions and the bibliography say. For each of their statements, open the place that `stated_in` names and see that it says so. A statement for which no place is named, or whose place does not say it, does not hold. A sentence that calls the result new, interesting or important, or that names who would read it, does not hold either, unless one of those files says exactly that. And an empty `related_formalizations` does not hold when one of those files names an earlier formal proof of the result.

A claim holds when the canon bears it out. When the canon shows something else, write what it shows. When you could not check a claim, because it concerns something the canon does not contain or you did not reach it, it does not hold either: say in the correction that it was not checked, and why.

For each claim that does not hold, decide whether the correction changes a ground of the comparison. It does when a reason the decision gives for ranking one option above another no longer stands with the corrected fact, or stands the other way round, or when the correction means that an option is not what the decision took it to be. It does not when the corrected fact leaves every such reason as it was: a count that is off by a little, a name misspelt, a detail of a proof that no reason mentions. This judgment matters, because one `true` sends the decision back to be made once more with your corrections, and nothing reads the selection after that. Mark as `true` what a careful decider would want to reconsider, and not every slip.

Of each claim that does not hold, a second thing is recorded: whether it stands in a text that the package prints. `sentence` and the texts under `registry` go into the package as the decision has them, into the README and into the file the registry reads, and no later step rewrites them. A wrong statement there is therefore sent back to be corrected whether or not it touches the comparison, and you mark it `printed`.

## What you write

`output/reading.json`, in this form:

```json
{"claims": [{"option": "a", "claim": "...", "holds": false, "correction": "...", "changes_comparison": true,
             "printed": false}]}
```

- `option`: the id of the option the claim is about; for a claim of `reasons`, `sentence`, `account` or `registry`, the id of the chosen option.
- `claim`: the claim in the decision's own words, short enough to be recognized there.
- `holds`: `true` or `false`.
- `correction`: empty when the claim holds; otherwise what the canon shows in its place, with the element or file where you saw it, or that the claim was not checked and why.
- `changes_comparison`: `false` when the claim holds; otherwise as decided above.
- `printed`: `false` when the claim holds; otherwise `true` when the claim stands in `sentence` or under `registry`, and `false` when it stands in another field.

The program accepts the reading when every claim it lists has a verdict. That check cannot see a claim you did not list, so the completeness of the list rests on you: every option contributes at least what its `proves`, `rests_on`, `size` and `against` state. Go through all options and all claims, also after you have found one that fails.

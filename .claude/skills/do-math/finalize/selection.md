# Choosing the proof the package presents

This session chooses which proof of the root the package presents. A finished research often holds more than one way to the result: the proof by which the root was first settled, perhaps a second proof, and sometimes a stronger theorem from which the root would follow in a few lines. You study what the research offers, compare the options, and write down the choice, the runner-up and the reasons.

Everything after this step is built from your choice. The library is cut down to what the chosen theorem and the root rest on, and it is then simplified, given records, and frozen. The paper proves the main theorem you fix, and the README states the result in your sentence. No later step returns to the question, so the choice is made once, here, on a careful reading.

## Why the choice is a step of its own

A research was once packaged with the direct proof that had settled its root. It had meanwhile proved a stronger theorem, and the user judged the proof through that theorem to be the better one, so it was packaged a second time, beside the first. The texts of that second package described their proof by contrast with the first, and they had to be rewritten once it was required that the package stand by itself. Both costs came from the same cause: which proof to present had never been decided as a question of its own, before the work on the library began. The user's words for what this step should be are these: "I want its decision to be part of the pipeline; taking a deep, good look at what proof to build, among options, then picking the one that is best".

## What "best" means

The user said what best means when judging that case, and the sentence is the standard for yours:

> the staircase is a better one. but the direct proof is also quite okay. insight is good. elegance and conciseness is also good. following mathematical research standards is required

The case was this. The root said that each row of a certain triangle of numbers is unimodal. The research held a direct proof of that, and a proof through a stronger statement, called the staircase, which also says where each row has its peak and from which unimodality follows as a corollary. The staircase proof was the larger of the two.

The sentence is read as follows, and the reading was confirmed with the user. The standards of mathematical research are a threshold, for the choice and for everything built from it: an option has to be presentable as mathematics at the level of a research paper, with a precisely stated theorem, a proof that can be told and checked as an argument, and known results attributed to their sources. Above that threshold insight ranks first. The staircase was preferred although it was larger, because it shows more of why the result holds and says more about the objects. Elegance and conciseness come after insight. And more than one option can be acceptable: the direct proof was "also quite okay", so a runner-up need not be faulted in order to justify the choice.

Your research is a different one, and its options may differ from each other in other ways than these two did. Use the case for the order of the criteria it shows, not as a pattern that the options have to fit.

## What you are given

- `root.md`: the root in words, as it was posed. Read it in full.
- `digest.md`: the program's overview of the candidates, described below. Read it in full.
- `index.json`: the index that the research's program extracted from the compiled library. Under `entries` it holds, for each element by its name: `kind`, `module` and `file`, `statement` (the Lean statement as text), `statement_uses` and `uses` (the elements its statement mentions and its proof names), `lean_proof` (`complete` or `sorry`) and `axioms` (what Lean reported for it).
- `canon/lean/`: the library. `canon/records/`: the record of each element. `canon/questions/`: what the research came to understand about each of its questions, `q0.md` being the problem as a whole. `canon/approaches/`: what was tried on statements whose proof was not accepted. `canon/bibliography.bib`: the sources.
- Only when this is the second decision: `reading.json` and `previous/`. The last section says what they are.

The digest shows two kinds of candidate. For every declaration whose proof formally settles the root it gives what that proof rests on, with the number of elements, modules and lines, and the main results among them with their descriptions. And it lists every theorem that is settled by a formal proof, has the weight of a result one would name, and is not among the things the root's present proofs rest on, each with its statement and description. The second list is there because a research stops working on its root once the root is settled. A stronger theorem proved afterwards, or beside it, usually stands in the library without any proof of the root through it, and it is still a way to present the result.

## The options

An option is a way to present the result: a main theorem, and a proof of the root that rests on it.

Two things make an option available. The first is the proof that the declaration `{{root}}` carries now. Look at its entry in `index.json`. If `lean_proof` is `complete` and `axioms` lie within `propext`, `Classical.choice` and `Quot.sound`, that proof is an option as it stands, with the root as its main theorem, and so is the same proof presented with a stronger theorem that it rests on as the main theorem. The second is a derivation that you write: a proof of the root from a theorem the root does not yet rest on, or from a second proof of the root that stands in the library under another name. If the root's own declaration has no complete proof, because the research proved the root's statement in another declaration, every option needs a derivation.

The program requires the main theorem to be settled by a formal proof, and the digest is its list of the theorems that are. Take the main theorem of every option from the digest.

Compare the options that a mathematician presenting this result would consider. Go through the second list of the digest and ask of each theorem whether the root follows from it, alone or with what the library already has. Where it does, and the theorem says something the root does not, it is an option, and you write its derivation. Where a theorem looks stronger and you cannot derive the root from it, it is not an option.

## The derivation of an option

For every option whose proof of the root is not the one `{{root}}` carries now, you return the root's module with the root proved on that route: `output/derivations/<option id>.lean`. The file is the complete text of the root's module, whose path is the `file` of the root's entry in `index.json`. It keeps the statement of `{{root}}` exactly as it is, character for character, with the lines above it that Lean reads the statement by, and it keeps every other declaration of the module. It replaces the proof of the root, and it adds the `public import` lines that the new proof needs. The new proof names the option's main theorem. A derivation can be one line that applies an existing second proof of the root, or it can be the argument that leads from the stronger theorem to the root. A module that itself imports the root's module cannot be imported, since that is a cycle; an option that would need it is not available.

The program compiles each derivation in the place of the root's module and requires four things: the library builds; the statement of the root is the one that was posed; the proof is complete and Lean reports no axiom beyond the three; and the proof rests on the option's main theorem. Compile it yourself first, so that the choice does not rest on a derivation that fails:

1. Copy `canon/lean/` to a folder of its own in your folder, outside `output/`, one for each derivation.
2. Put the derivation there in the place of the root's module.
3. Build with that folder as the module root and the root's module as the file to compile, as the section "Compiling" describes. The other modules come from the service's store, so the build costs the one module.
4. While you try, a last line `#print axioms {{root}}` makes Lean print the axioms. Take the line out of the file you return, and build that file once more as you return it.

## Reading the routes

Judge the options by reading them. For each, read the Lean statement of its main theorem and the definitions it uses, the record of the main theorem and of the main results its proof rests on, and what `canon/questions/q0.md` says about the problem as a whole. Find out what the main theorem says about the objects that the root does not, how the proof goes, which idea carries it, and where its difficulty lies. Numbers such as how many elements a proof rests on or how many lines it has describe how the library is arranged. Record them under `size`, where they belong, and do not let them stand in for a reading: by the user's standard a larger proof that shows more is the better one.

You may give the reading of single routes to sub-agents of your own, one route each, and ask each for what you need to compare: what the route proves, how its proof goes and where the idea lies, what it rests on, what speaks for and against presenting it. A sub-agent knows nothing of this text, so give it the paths, the user's sentence, and the question. The decision is yours. Read enough of each route yourself to stand behind every statement of fact in your output, because a second session checks each of them against the canon.

## What you write

`output/decision.json`, in this form:

```json
{"options": [{"id": "a", "main": "Lib.thm", "route": "present", "proves": "...", "rests_on": "...",
              "size": "...", "for": "...", "against": "..."}],
 "choice": "a", "runner_up": "b", "reasons": "...", "sentence": "...", "account": "...",
 "registry": {"arxiv": ["math.CO"], "msc2020": ["05A15"], "origin": "original",
              "sources": [{"key": "celano2025", "relationship": "background", "note": "..."}],
              "related_formalizations": [{"id": "...", "relationship": "independent", "note": "..."}],
              "divergences": "...", "settles": "...", "novelty": "...", "stated_in": "..."}}
```

For each option:

- `id`: a lowercase letter or short lowercase word; it names the derivation file.
- `main`: the full name of the main theorem. The `main` of the chosen option becomes the main theorem of the package.
- `route`: `"present"` when the proof of the root is the one `{{root}}` carries now, and `"derivation"` when you return a derivation for it.
- `proves`: what the option proves, in words: the main theorem with its hypotheses and conclusion, and what it says beyond the root.
- `rests_on`: what the proof rests on: the results it is built from, by name, and any result taken from the literature or established by computation.
- `size`: the elements, modules and lines the proof rests on, as the digest or the index gives them, and for a derivation its own length.
- `for` and `against`: what speaks for presenting the result this way and what speaks against it, by the user's standard. State facts as facts and judgments as judgments.

Then, for the decision:

- `choice` and `runner_up`: two option ids. With a single option, `runner_up` is `null`. The choice has to be an option that passes the program's check: its derivation meets the four requirements above, or, without a derivation, its main theorem is the root or something the root's present proof rests on.
- `reasons`: why the choice stands above the runner-up and the others, argued from the user's sentence. The program copies this into the file of decisions that the user reads afterwards.
- `sentence`: one sentence that states the result in words, for a reader who knows the field and has not seen the package. It is printed where the package is described in a line, first of all in the list of packages in the repository's README, so it names no Lean declaration and follows the rule of one proof presented by itself.
- `account`: an account of the chosen proof as a whole: what is proved, how the proof goes from its main results to the main theorem and from there to the root, and where its difficulty lies. Refer to elements by their Lean names between backticks. It takes the place of the research's own account of the problem, and the sessions that plan the paper and write the README read it as their description of the whole. It therefore speaks of the chosen proof only, so that no text of the package draws on a route the package does not contain.

And for the registry in which the package may be entered:

- `arxiv`: one or two arXiv categories, the primary one first.
- `msc2020`: one to eight MSC2020 codes of five characters, such as `05A15`, the primary one first. The program checks the form of the codes and not that they exist, so give only codes you are sure of.
- `origin`: `"original"` when the theorem is first proved here, as when it was an open conjecture, and `"source-based"` when the result was known and published. A new proof of a known published result is source-based.
- `sources`: each entry of `canon/bibliography.bib` that bears on the result itself, with its `key` and its relationship to the result in the registry's words: `formalizes` (the library formalizes the proof that source gives), `adapts` (it follows the source and changes or extends its result), `independently-proves` (the source proves the same result and this proof does not come from it), `background` (the source states the problem or gives context), `other`. With `"original"`, every relationship is `background` or `other`. With `"source-based"`, at least one is `formalizes`, `adapts` or `independently-proves`; a new proof of a published result has `independently-proves` for the source that published it. Technical sources of single lemmas are not listed. If the bibliography has no entry that bears on the result, the list is empty. Each entry has a `note`: what that source has of the result and where in it, such as the number of the conjecture or theorem there, and whether the source proves it, states it without proof, or has something weaker or more special. The note is printed beside the source in the registry's file and in the README.
- `related_formalizations`: each earlier formal proof of the result, or of a part of it, in any proof assistant, that `root.md`, a record, a file under `canon/questions/` or the bibliography names. `id` is its address or identifier as it is written there. `relationship` is the registry's word for how this library stands to it: `builds-on` (the library uses it), `adapts` (the library changes or extends it), `independent` (it proves the same and the library does not come from it), `supersedes`, `other`. `note` says in a sentence what it proves and how the two relate. The libraries that the proof imports are dependencies and are not listed. When the files name none, the list is empty, and the report of the run tells the user that none was looked for.
- `divergences`: where the Lean statement of `{{root}}` departs from the proposition as `root.md` poses it in words, and nothing else. The registry shows this text to a reader who wants to know whether the formal statement says what the proposition says. Compare the two yourself, with the definitions the statement uses, which `{{work}}/first/lean/` has as they were posed, and with the record of the root. Name each departure and say what the Lean form has and what the words have: an index that starts at another value; a domain that is wider or narrower; a boundary case or an empty case that one of the two includes and the other does not; a function that Lean makes total where the mathematics leaves it undefined, such as subtraction of natural numbers that stops at zero or division by zero; anything the Lean statement assumes and the words do not. Do not say why the theorem holds or how it is proved, since neither is a departure. When there is none, write one plain sentence that says so.
- `settles`: what the result is in the mathematics it belongs to, for a mathematician who has not seen the package: the statement in a sentence or two, whose conjecture, problem or question it settles, and where that was posed, with the number it carries there. For a theorem that was known, say whose theorem it is and where it stands. The README prints this text below the result.
- `novelty`: what the research recorded about whether the result was known before, which is what the value of `origin` rests on: what `root.md`, the records' parts on literature, the bibliography and the questions say about earlier proofs and partial results, which searches of the literature they report, and what the research did not look into. Where they do not establish that the result is new, say that it is not known whether it is new. The README prints this text after `settles`, and for an original result the registry's file carries it as well.
- `stated_in`: for each statement of `settles` and `novelty`, of the notes and of `related_formalizations`, the place where it stands: `root.md`, the record of a declaration by its name, a file under `canon/questions/`, or a key of the bibliography. This field is not printed. The session that reads your decision opens each place and looks for the statement there.

Whether the result was open is a statement about the literature, and you have only what the research recorded: `root.md`, the records' parts on literature, the bibliography and the questions. Decide `origin` from those.

`settles`, `novelty` and the notes are written for the registry's reviewer, who has to see from the package what the result is, where it comes from and what about it is new, and who marks a package down for a statement about the literature that rests on nothing. So these texts follow one rule: a statement is written only when you can name the place in those files where it stands, and `stated_in` names that place. Do not argue that the result is interesting or important, do not name who would want to read it, and do not call it new on your own judgment. Such statements go beyond what the research recorded. The user adds them where they hold, and the report of the run says that this is left to the user. Where the files leave something open, such as who first posed or proved the statement, write that the files do not say.

Before you end, check your output against what the program checks: every derivation you return builds as you return it; the choice is eligible; the runner-up is one of the options; no text is empty; every source has its note; the categories and codes have the form of their taxonomies.

## When this is the second decision

After a first decision, a session that did not write it reads every statement of fact in it against the canon. If one of its corrections changes a ground of the comparison, or concerns `sentence` or a text under `registry`, which go into the package as you wrote them, the decision is made once more, and that is this session: your folder then holds `reading.json`, the reader's verdict on each claim, and `previous/`, the first output.

Take each entry of `reading.json` whose `holds` is false and verify the correction against the canon yourself. Then compare the options again with the corrected facts and write the whole output anew, as described above. The choice may stay or change; what matters is that the reasons hold with the facts as they now stand. A derivation of `previous/derivations/` that is still right can be returned unchanged. No further reading follows this decision.

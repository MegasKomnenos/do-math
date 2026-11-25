# Organizer output

Your work leaves `output/organization.json` and, when you add elements or rearrange modules, a change of your own in the same folder. `organization.json` says which published changes this session answers for and which questions ask the same thing. The change carries the Lean: elements stating that two definitions or two statements agree, each with a proof that is complete in Lean, and modules rearranged so that a proof can stand under its statement's own name.

Nothing you submit goes through review. For the merging of questions the research relies on your judgment. For everything in the change it relies on Lean: the runner publishes what compiles and passes the checks a machine can decide, and what you add enters as accepted. That is why an agreement you cannot prove in Lean is not yours to establish, and why a rearrangement may move a proof and may not change one.

## `organization.json`

| Field | Content |
|---|---|
| `batch` | The exact list in `task.batch` of your `input.json`. It names the published changes this session answers for. |
| `merge_questions` | Array of `{from, into, reason}` naming two questions that ask the same thing. Omit it or use an empty array when you merge none. |
| `delete` | Array of module names to remove from the library, for example `"Parking.Columns.AltProof"`. It belongs to a rearrangement and takes effect only together with a change; omit it otherwise. |

**The batch.** Your batch was fixed when you were launched. Changes published during your session are not in it and remain for the next organizer, and acknowledging your batch does not mark them as processed. The transport check refuses a `batch` that differs from the assigned one.

**Merging questions.** `from` and `into` are IDs of existing questions, and `reason` explains why the two ask the same thing; the runner does not compare their wording. After publication the old identifier is an alias of the surviving question, and a resolution recorded against either resolves it. Question `q0` keeps its identity in both directions: it is not merged into another question, and no question is merged into it. A proposal that duplicates `q0` is declined at review. The merged question has one understanding so far. The text of the surviving question is the one the question's view shows from then on. When the surviving question has no text, the text of the question merged away becomes its text; when both have one, the text of the question merged away goes to the history of the merged question, where `question <id> --history` shows it. Your role guide explains what a merge leaves to the explorations that hold either question.

## The change

A change is optional. Without one, `organization.json` is the whole of your output.

```text
output/
  organization.json
  change.json                     {"title", "description", "replace": [...], "retire": [...]}
  lean/<Library>/...              new modules, for the elements you add
  rewrite/lean/<Library>/...      complete module files that replace existing modules or create new ones
  replace/<any>.lean              the complete new text of a declaration whose proof you replace in place
  records/<name path>.md          the records of the elements you add, and records you replace
  prepared.json                   written by commands.prepare
```

[The candidate change](change-format.md) describes the parts this layout shares with a peer's candidate: `change.json` with its required `title` and `description`, new modules under `lean/`, the replacement of a proof in place through `replace`, and records. What follows is what is particular to you. An organizer's change holds Lean modules, replacements and records only. It proposes no questions and no resolutions, and it carries no approach entries and no understanding texts; the transport check refuses a change that does.

### Elements stating that two things agree

A new element goes into a new module under `lean/`, with its record under `records/`, like any new element of the canon.

Every statement you add must have a proof that is complete in Lean and depends, through everything of the canon it uses, only on the allowed axioms. `commands.prepare` reports any statement you add for which this fails, and such a change is not published. A proof that names an element whose own Lean proof ends in `sorry` fails in this way, because `sorryAx` is then among its axioms.

A `replace` in your change is for one thing only, turning a reference to a retired declaration into a reference to the statement's own: the checks refuse a replacement that changes what a proof names or whether it is complete in Lean, because no review would have judged the new proof. A one-line derivation of one statement from another that agrees with it, put in the place of the statement's own proof, therefore enters through a peer's change and review. A derivation you add as a declaration of its own, another proof of an existing statement with `proves:` in its record, is an added element like every statement you add; your role guide says under "Join what is the same" when you can add it.

### Rearranging modules

A rearrangement, which your role guide explains under "Rearrange modules so that a proof stands under its statement", is written in four parts of your output.

- Under `rewrite/lean/`, write the complete new text of every module you change and of every module you create, each at the path it has, or is to have, in the library. A file there takes the place of the existing file with that path.
- In `delete` of `organization.json`, list the modules that no longer exist after the rearrangement.
- In `retire` of `change.json`, list each separate declaration you remove, as `{"alternative": "<the declaration that is another proof>", "into": "<the statement's own declaration>", "reason": "..."}`, with exactly these three keys.
- In `records/`, put the record of the statement's own declaration with the written proof that the alternative's record carried. The alternative's record leaves the canon with its declaration and is kept in the history, so without this the statement's record would go on describing the proof that no longer stands.

A module in which nothing changes except a reference to the alternative, which becomes a reference to the statement's own declaration, can be handled in either of two ways. You can rewrite the module under `rewrite/lean/`, or you can name the declaration in `replace` and give its new text, which leaves the rest of the file as the canon has it. Use one of the two for a module and not both: the files under `rewrite/lean/` are put in place after the replacements are made, so a rewritten module discards a replacement made in it.

A rearrangement is valid when every other element has the name and the statement it had and everything compiles. `commands.prepare` checks the following by machine:

- no declaration disappears from the canon other than the alternatives you retire;
- no statement, and no kind of declaration, changes in place;
- each retired alternative is gone afterwards, and the statement's own declaration named in `into` is still there;
- the proof now under the statement's own name names the elements that the alternative's proof named, and is complete in Lean exactly if the alternative's proof was. A retirement moves a proof and does not change it.

These checks compare names, kinds and statements. For a definition they also compare the text of the declaration, and for every proof whether it is complete in Lean and which elements it names, where a reference to a retired declaration counts as a reference to the statement's own. A file under `rewrite/lean/` replaces the whole module, so every declaration in it has to be the text the canon has, copied unchanged apart from such references. A definition whose text you altered is refused, because every statement that mentions it would then mean something else while keeping its verdict. A proof that names other elements than before, or that became complete or incomplete, is refused, because no review judged that proof. Beyond this the checks do not read the text of a proof, so leave it as it is.

### Preparing the change

Run `commands.prepare` when the change is assembled; [The candidate change](change-format.md) describes the command, what it checks, its exit codes and how to wait for its build under "Preparing the candidate". Correct what it reports and run it again. Its result in `prepared.json` is bound to every file of your `output/`, `organization.json` included, so prepare again after any edit. The command is for a change; when you submit only `organization.json`, there is nothing to prepare.

## What happens to your output

The transport check, which you run on your session directory before you end, confirms the structure: the exact batch, question merges that name existing questions and leave `q0` alone, each with a reason, and, when there is a change, that it is well formed, was prepared for exactly these files without errors, holds only what an organizer's change may hold, and that each entry of `retire` names an alternative that is another proof of its `into` and whose proof does not stand lower than the proof it displaces.

The runner then publishes your output without review, in its turn in the publication queue. It applies the change to the canon as it is at that moment, builds it and repeats the machine checks. Other changes may have been published while you worked. If your change no longer applies or does not build, a replacement organizer receives your output and the reason and makes the change again.

Whether two questions ask the same thing, whether an agreement is worth stating, and whether a rearrangement is worth its cost are your judgments. Read the result from the position of the next session that traverses the canon, run the transport check, and end.

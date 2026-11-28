# Organizer output

Your work leaves `output/organization.json` and, when you add elements, rearrange modules or write descriptions, a change of your own in the same folder. `organization.json` says which published changes this session answers for and which questions ask the same thing. The change carries the Lean: elements stating that two definitions or two statements agree, each with a proof that is complete in Lean, and modules rearranged so that a proof can stand under its statement's own name. It also carries the descriptions you write for the index of the canon: the descriptions of folders and the lines of modules.

Nothing you submit goes through review. For the merging of questions the research relies on your judgment. For the Lean of the change it relies on Lean: the runner publishes what compiles and passes the checks a machine can decide, and what you add enters as accepted. That is why an agreement you cannot prove in Lean is not yours to establish, and why a rearrangement may move a proof and may not change one. For a description it relies on your judgment and on the blind descent test that you have taken on it, which is the one check a description of yours gets before sessions read the canon through it.

## `organization.json`

| Field | Content |
|---|---|
| `batch` | The exact list in `task.batch` of your `input.json`. It names the published changes this session answers for. |
| `merge_questions` | Array of `{from, into, reason}` naming two questions that ask the same thing. Omit it or use an empty array when you merge none. |
| `delete` | Array of module names to remove from the library, for example `"Parking.Columns.AltProof"`. It belongs to a rearrangement and takes effect only together with a change; omit it otherwise. |

**The batch.** Changes published during your session are not in your batch and remain for the next organizer. The transport check refuses a `batch` that differs from the assigned one.

**Merging questions.** `from` and `into` are IDs of existing questions, and `reason` explains why the two ask the same thing; the runner does not compare their wording. After publication the old identifier is an alias of the surviving question, and a resolution recorded against either resolves it. Question `q0` keeps its identity in both directions: it is not merged into another question, and no question is merged into it. A proposal that duplicates `q0` is declined at review. The merged question has one understanding so far. The text of the surviving question is the one the question's view shows from then on. When the surviving question has no text, the text of the question merged away becomes its text; when both have one, the text of the question merged away goes to the history of the merged question, where `question <id> --history` shows it. Your role guide explains what a merge leaves to the explorations that hold either question.

## The change

```text
output/
  organization.json
  change.json                     {"title", "description", "replace": [...], "retire": [...]}
  lean/<Library>/...              new modules, for the elements you add
  rewrite/lean/<Library>/...      complete module files that replace existing modules or create new ones
  replace/<any>.lean              the complete new text of a declaration whose proof you replace in place
  records/<name path>.md          the records of the elements you add, and records you replace
  descriptions/folders/<Folder>.md   the descriptions of folders you write or rewrite
  descriptions/modules/<Module>.md   the lines of modules you write or rewrite
  descriptions/purposes.json      the purposes on which the descriptions are tested
  descriptions/tests.json         written by the canon command descent-test
  prepared.json                   written by commands.prepare
```

[The candidate change](change-format.md) describes the parts this layout shares with a peer's candidate: `change.json` with its required `title` and `description`, new modules under `lean/`, the replacement of a proof in place through `replace`, records, the lines of modules and the blind descent test. An organizer's change holds Lean modules, replacements, records and descriptions only. It proposes no questions and no resolutions, it carries no approach entries and no understanding texts, and it has no `descriptions/reports.json`; the transport check refuses a change that does otherwise.

### Elements stating that two things agree

A new element goes into a new module under `lean/`, with its record under `records/`, like any new element of the canon.

Every statement you add must have a proof that is complete in Lean and depends, through everything of the canon it uses, only on the allowed axioms. `commands.prepare` reports any statement you add for which this fails, and such a change is not published. A proof that names an element whose own Lean proof ends in `sorry` fails in this way, because `sorryAx` is then among its axioms.

A `replace` in your change is for one thing only, turning a reference to a retired declaration into a reference to the statement's own: the checks refuse a replacement that changes what a proof names or whether it is complete in Lean, because no review would have judged the new proof. A one-line derivation of one statement from another that agrees with it, put in the place of the statement's own proof, therefore enters through a peer's change and review. A derivation you add as a declaration of its own, another proof of an existing statement with `proves:` in its record, is an added element like every statement you add; your role guide says under "Join what is the same" when you can add it.

### Rearranging modules

A rearrangement, which your role guide explains under "Rearrange modules so that a proof stands under its statement", is written in four parts of your output.

- Under `rewrite/lean/`, write the complete new text of every module you change and of every module you create, each at the path it has, or is to have, in the library. A file there takes the place of the existing file with that path.
- In `delete` of `organization.json`, list the modules that no longer exist after the rearrangement.
- In `retire` of `change.json`, list each separate declaration you remove, as `{"alternative": "<the declaration that is another proof>", "into": "<the statement's own declaration>", "reason": "..."}`, with exactly these three keys.
- In `records/`, put the record of the statement's own declaration with the written proof that the alternative's record carried.

A module in which nothing changes except a reference to the alternative, which becomes a reference to the statement's own declaration, can be handled in either of two ways. You can rewrite the module under `rewrite/lean/`, or you can name the declaration in `replace` and give its new text, which leaves the rest of the file as the canon has it. Use one of the two for a module and not both: the files under `rewrite/lean/` are put in place after the replacements are made, so a rewritten module discards a replacement made in it.

A rearrangement is valid when every other element has the name and the statement it had and everything compiles. `commands.prepare` checks the following by machine:

- no declaration disappears from the canon other than the alternatives you retire;
- no statement, and no kind of declaration, changes in place;
- the file of every module that the root's module imported when the instance was created, directly or through another, stays as the canon has it: those modules hold the definitions the root was posed with, so a rearrangement neither rewrites nor deletes one and replaces no declaration in one;
- each retired alternative is gone afterwards, and the statement's own declaration named in `into` is still there;
- the proof now under the statement's own name names the elements that the alternative's proof named, and is complete in Lean exactly if the alternative's proof was.

A file under `rewrite/lean/` replaces the whole module, so every declaration in it has to be the text the canon has, copied unchanged apart from references to a retired declaration, which count as references to the statement's own. A definition whose text you altered is refused, because every statement that mentions it would then mean something else while keeping its verdict. A proof that names other elements than before, or that became complete or incomplete, is refused, because no review judged that proof. Beyond this the checks do not read the text of a proof, so leave it as it is.

### Descriptions

A description is a file under `descriptions/`, at the path the name of its folder or module gives: the description of the folder `Parking.Columns` is `descriptions/folders/Parking/Columns.md`, and the line of the module `Parking.Columns.Basic` is `descriptions/modules/Parking/Columns/Basic.md`. [The written texts of the canon](records.md) gives the form of both texts, the standard they are written to, the `Boundary:` paragraph and the blind descent test, under "The module line and the folder description". Your role guide says which descriptions are yours to write and how you find them.

You may carry the description of any folder and the line of any module that exist in the canon as it is after your change. A file is the complete text that is to stand; the canon keeps the difference from the text it replaces in its history. A description that you have read again and found sufficient as it stands can be carried with its text unchanged: it is then confirmed, and the canon records it as written against the present revision, so that `index --due` no longer lists its folder as behind. Every module your change creates, under `lean/` or under `rewrite/lean/` at a path the canon does not have, needs its line in the same change.

Descriptions take effect only as part of a change. A change that holds descriptions and nothing else still has `change.json`, with `title` and `description`, and is prepared; it changes no Lean file, so nothing is built for it. The transport check refuses descriptions that stand in `output/` without `change.json`.

Each description you carry is tested with the `descent-test` command before you prepare, as [The candidate change](change-format.md) describes under "The blind descent test". `descriptions/purposes.json` names each description by the name of its folder or module in `target`. The line of a module needs one purpose, and the description of a folder needs at least three different ones. The level of a folder is the listing in which the folder stands: the folders and the modules beside it in the folder above, or the folder level for a folder directly under the library. The reader is given that level with your texts in the place of the canon's, with the modules your change creates and without the modules it deletes. When the reader cannot be had, because the provider refuses the light session or the call fails, the command records the purposes of that level as not tested, and that record satisfies the preparation: the description is published as not tested, `index --due` lists it under "Descriptions published without a blind descent test", and it stays there until an organizer carries it again with a test that was taken.

A report that a description did not lead a session to an element is not something your change carries. Where you find such a description, you rewrite it in this change.

### Preparing the change

Run `commands.prepare` when the change is assembled; [The candidate change](change-format.md) describes it under "Preparing the candidate". Correct what it reports and run it again. For the descriptions it checks that each names a folder or a module of the canon as it is after your change, that every module your change creates has its line, and that each description has the results of the blind descent test for the text it has now, on one purpose for a line and on three different purposes for a folder description, each passed or recorded as not tested. It records with the descriptions the revision the canon has at that moment, the number that `index` prints in its first line, and that is the revision your descriptions count as written or confirmed against once they are published. Its result in `prepared.json` is bound to every file of your `output/`, `organization.json` and the files under `descriptions/` included, so after any edit run `descent-test` again where a description changed, and prepare again. The command is for a change; when you submit only `organization.json`, there is nothing to prepare.

When your change carries the description of a folder or the line of a module that the canon already has, the summary that the command prints and `prepared.json` have one more key, `open_reports`. It is an array with one object for each report that `index --due` lists at that moment against a description your change carries, and it is empty when there is none.

```json
"open_reports": [
  {"description": "Parking.Columns",
   "element": "Parking.unimodal",
   "purpose": "What the session was looking for.",
   "from": "published change <change id> · revision 41 · from the peer",
   "answered_at_this_revision": true}
]
```

`from` says where the report came from, in the words of the list. `answered_at_this_revision` says whether a description prepared now takes the report off the list when your change is published. It is false in two cases. One is a report that the runner kept from a candidate that was not published, at the revision the canon still has: such a report leaves the list with a description prepared at a later revision. The other is a report against a name that is both a module and a folder once your change is in the canon, when your change carries one of its two descriptions and the canon does not hold the other at a revision that showed the report: the report leaves the list when both descriptions have reached it. The key is there as soon as the description files of the change can be read, also when the command then finds a line missing or a test not taken; a description file that breaks the form is refused before that, and the result then has no `open_reports`. Your role guide says under "Keep the index current" what these reports ask of you before you hand the output in.

## What happens to your output

The transport check, which you run on your session directory before you end, confirms the structure: the exact batch, question merges that name existing questions and leave `q0` alone, each with a reason, and, when there is a change, that it is well formed, was prepared for exactly these files without errors, holds only what an organizer's change may hold, and that each entry of `retire` names an alternative that is another proof of its `into` and whose proof does not stand lower than the proof it displaces: its standing is not the lower of the two, and where the two standings are the same, it is complete in Lean if the displaced proof is.

The runner then publishes your output without review, in its turn in the publication queue. It applies the change to the canon as it is at that moment, builds it and repeats the machine checks. Other changes may have been published while you worked. If your change no longer applies or does not build, a replacement organizer receives your output and the reason and makes the change again.

A description is written into `canon/descriptions/` when its folder or module exists after the change, and it is left out without an error when that folder or module has gone in the meantime. The summary of the descriptions records with each text the revision of the canon against which you prepared the change, so a module that was published into a folder between your preparation and your publication shows that folder as behind again, and the next organizer sees it in `index --due`. Sessions launched after the publication have your folder descriptions in their starting context. Once your output is published, the changes of your batch count as answered for. A report that a description did not lead a session to an element is not bound to the batch. It leaves the list of `index --due` when the description it names is written or confirmed against a revision of the canon that showed the report, and the revision recorded with your descriptions is that of your last preparation. Your publication therefore takes off the list the reports that `open_reports` named at that preparation with `answered_at_this_revision` true. Every other report stays there for a later organizer: a report against a description you did not carry, a report that was made between your preparation and your publication, a report that the runner kept from a candidate that was not published while the canon had the revision at which you prepared, and a report against a name that is both a module and a folder of which you carried one description while the other had not reached the report.

Whether two questions ask the same thing, whether an agreement is worth stating, whether a description tells a session what lies beneath it, and whether a rearrangement is worth its cost are your judgments. Read the result from the position of the next session that traverses the canon, run the transport check, and end.

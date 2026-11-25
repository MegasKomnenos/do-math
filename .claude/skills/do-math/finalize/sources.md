# Finding and checking the sources the records cite

Some results of the library were taken from the literature, and their records name the source. The records of the package, and the paper that is written from them, pass those citations on to their readers. This session finds every cited work in a registry of publications, corrects its bibliography entry, opens it as far as it can be opened, and checks what the records say of it. It also looks for sources of a few results that the library proves and that are known in the literature under a name. It is the only session of the run that looks outside the research, and for that it has the research's literature server.

## Why the sources are checked here

In the first packaging of this kind the citations were verified for the first time when the paper was almost finished. By then a wrong attribution of a classical result stood in four texts, and each had to be corrected. A citation is copied onward by everything written from the record that carries it, so it is checked where it first stands, before the library and its records are frozen.

The second task comes from the same paper. It gave full proofs of several classical results, and that was the objection its readers repeated most. The library proved them, their records named no source, and so the paper had nothing to cite. A result that the library proves and that a source states in the same form is cited in the paper and not proved again there. For that, the source has to be in the record before the freeze.

## What you are given

- `bibliography.bib`: the bibliography of the research.
- `cited.json`: every key of the bibliography that a record cites, with the records that cite it and the passage of each.

```json
[{"key": "abel1826", "records": [{"declaration": "Lib.abel", "path": "records/Lib/abel.md", "text": "..."}]}]
```

- `requests.json`: the results for which a source is wanted, each with the declaration that states it, the name under which the result is known, and the reason. An entry can also carry `source`, the key of a bibliography entry; the section "The requests" says what that means. It can be an empty array.

```json
[{"declaration": "Lib.abel", "result": "Abel's binomial identity", "reason": "..."}]
```

- `records/`: all records. `lean/`: the library, for the exact statement of a declaration. You write no Lean and compile nothing. The library's root is `{{root}}` and its main theorem `{{main}}`.

## Searching

The literature server attached to this session is the instrument. Begin with `list_sources` to see which sources it serves, read a source's query syntax with `describe_source`, query with `search`, read what a call retained with `extract`, and obtain a specific item by its identifier with `fetch`. It serves sources that are reached through public interfaces, among them the indexes zbMATH, OpenAlex and Semantic Scholar, the registry Crossref and the preprint server arXiv. The full text of many journal articles cannot be retrieved through it; look then for a preprint or an author's own copy, on the web if the server does not have it. Many entries of zbMATH carry a reviewer's summary, which counts as an abstract.

Read the outcome of each search exactly. An empty result says that this source returned nothing for this expression. A result marked restricted, a database error, or the code `source_not_enabled` says nothing about whether the work exists. `rate_limited` says that the source refused for the moment; try again after the interval it names.

## The cited sources

For each key of `cited.json`:

1. **Find the work.** Search by title, authors and year, in more than one source where the first returns nothing. A work is found when a registry has an entry that is plainly this work. Take from that entry the identifier that fixes which document it is: a DOI, an arXiv number with its version, a Zbl or MR number.
2. **Correct the entry.** Bring authors, title, place of publication, year and pages in `bibliography.bib` to what the registry gives, and add the identifier. The key stays. An entry holds what a reference list prints, and nothing else: authors, title, where the work appeared, year, pages, identifier. The paper prints every field of an entry it cites, so nothing in an entry may be addressed to the sessions of the research. One bibliography had an entry whose `note` said which version "the records cite" and how the numbering of its theorems had changed between versions; the reference list of the paper printed that, and two of its readers objected. Take such a remark out of the entry. Where a record needs it to say where a statement stands, it belongs in that record's `## Literature`, and you put it there. A note that describes the work itself stays, such as the translator of an edition.
3. **Open it as far as it opens**, and note how far: the full text, parts of it, the abstract only, or nothing.
4. **Check what the records say of it.** `cited.json` gives each passage. Does the work state what the record says it states, at the place the record gives, under the hypotheses the record gives, and is it attributed to the right author? Where the record says how the source's notation corresponds to the library's, does that hold?

One rule governs every correction: nothing is said of a source beyond what was opened. A record may attribute to a work what you saw in it. If you opened the full text and the theorem stands there as described, the passage stays. If the record is wrong about something you can see, such as the number of a theorem, a hypothesis or an attribution, correct it from what you see. If you could open only the abstract, the record can say what the abstract shows, and a statement about a particular theorem or proof inside the work is cut back to that. If you could open nothing, the record can say of the work only what its registry entry shows: that it exists, by whom, under which title, and when. A sentence that attributes a statement to it is rewritten so that it no longer does, and a header key `source` that rests on it is taken out, since the record can no longer say that the result stands there. Where the record gives an account of how much of the source was read, bring it to what was opened in this check.

A work that cannot be found is removed. Take its entry out of `bibliography.bib`. Rewrite every sentence that cites it so that the sentence stands without it, and take out the header key `source` and the part `## Literature` where they rest on it. The mathematics stays, because the library proves it; what goes is the claim about where it was published. Where the proof in a record consisted of the reference alone, write the proof in words from the declaration's Lean proof in `lean/`. The removal is recorded for the user, so say in `note` where you searched and with which expressions.

A work is removed only when searches that ran found nothing. If a key can be neither found nor shown to be absent, because the server did not answer or kept refusing, try again later in your session and by other means. If it is still undecided at the end, leave it as it is: no entry in `sources.json`, its bibliography entry and its records unchanged. The program then stops the run and names the key, and that is the right outcome. A source must not be removed, nor called verified, on the strength of a search that did not run.

Entries of the bibliography that no record cites are not yours to check; return them as they are.

## The requests

For each entry of `requests.json`, read the Lean statement of the declaration and its record, and search for a work that states the result. The name under `result` is where the search begins; a classical result often stands in a textbook or a survey as well as in the paper it is named after, and either will do.

A source is entered into the record only when it states the result in the form the library has: the same hypotheses and the same conclusion, up to notation and to conventions that can be stated exactly, such as an index that starts at one. A source that proves a weaker form, a non-strict inequality where the library has a strict one, a special case, or a general theorem from which the library's statement would still have to be derived, does not state it in that form. The paper will put the citation in the place of a proof, and it can do that only for what the source actually says. You have to have seen the statement in the source, so a work you could not open far enough to read the statement is not entered.

When you find such a source: add its entry to `bibliography.bib` under a new key in the manner of the existing keys, with its identifier; add the header key `source` to the record; and write the record's part `## Literature`: the precise place of the result in the source, how much of the source you read, where the statement stands in what you read (a main theorem with its proof, a remark, a result the source attributes to earlier work), and how the source's notation and conventions correspond to the library's. The new key is listed in `sources.json` like every other.

When you find none, the answer is that none was found. Say in the note what you searched and, where you found something close, what it is and in what it differs from the library's statement. The paper will then prove the result.

One case in which the source does not state the library's form is reported, because the library can still be changed when you search: a source that states a stronger or a more general form, from which the library's statement follows. You do not enter it, since it does not state the library's form. But a later step tries to give the library the source's form, as a declaration of its own that is proved; where that succeeds, the paper cites the source for that declaration and obtains the library's present form from it. Without your report the paper proves at length what a cited theorem contains. An earlier paper of this kind did: it proved two bounds by two hundred lines of calculus where a known theorem gives both with a better constant, and it derived over two pages series identities that follow from Lagrange inversion; its readers objected to each in every round. Report such a source under `stronger`. Give under `states` the statement of the source in full, in the notation and the conventions of the library, with every hypothesis and every constant as the source has them: the session that proves it works from your words and does not open the source. Give under `where` its place in the source. Add the source's entry to `bibliography.bib` and list its key in `sources.json`, as for a source you enter.

The other direction stays closed. A source that states less than the library is not reported, and no record is given a source for a form that the library does not prove.

A request that carries `source` is the second half of such a report. Its declaration was added to the library so that the library states what that source states. Open the source again and compare it with the declaration as it now stands in `lean/`. Where the source states exactly this form, enter it as described above and list its key in `sources.json`. Where the declaration says something else after all, the answer is that none was found, and the note says in what the two differ.

## What you write

- `output/sources.json`, with one entry for each key of `cited.json` and for each key you added:

```json
[{"key": "abel1826", "status": "verified", "identifier": "...", "opened": "full", "note": "..."}]
```

`status` is `verified` when the work was found in a registry and `removed` when it was not. `identifier` is the DOI, arXiv number or Zbl number, empty for a removed work. `opened` is `full`, `parts`, `abstract` or `none`. `note` says what was read and what was corrected in the entry and in the records, or, for a removal, where you searched.

- `output/bibliography.bib`: the complete bibliography as it now stands.
- `output/records/<path>.md` for each record you changed: the complete record, at its path in `records/`. A changed record keeps the form that all records have, which a program checks: a header between two lines `---` whose lines are `key: value`, then parts under headings of the second level, of which `## Literature` is one. Add no other heading of the second level and no other header key than `source`.
- `output/requests.json`, with one entry for each entry of the `requests.json` you were given, an empty array if that was empty:

```json
[{"declaration": "Lib.abel", "found": true, "key": "abel1826", "note": "...", "stronger": null}]
```

`key` is the key of the source you entered, `null` when `found` is false. `stronger` is `null`, or, for a source that states a stronger or a more general form than the library, `{"key": "...", "states": "...", "where": "..."}`; `found` is then false.

The program requires that every key a record cites is in the bibliography and has the status `verified`. Before you end, search the records you return, and those you left, for the keys you removed, and see that none is cited any more.

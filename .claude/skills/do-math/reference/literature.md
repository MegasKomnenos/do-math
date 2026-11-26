# Searching and using literature

This reference explains how to carry out, for the mathematical literature, the guidance the common introduction gives under "Building on what already exists".

## Decide what the search is for

A literature search can answer different questions, and they call for different searches. Decide which uncertainty the search addresses before choosing search expressions.

To find out whether a result is already known, the search has to be broad. It should use several suitable databases, try the alternative names under which the object or the result may appear, and follow the chains of citation leading from the papers you find. One relevant paper does not answer the question, and neither does one search that returns nothing.

To find a technique worth applying, read a few of the most relevant sources closely, far enough to see what the technique assumes and whether those assumptions hold for the objects here.

When you take on a statement or a question, you may also search in order to learn what surrounds the problem: which objects have been studied, under which names, and which standard results exist for them. The aim of such a search is that you recognize a known tool when your argument needs one.

## Look first at what the instance already has

Before searching outside, find out what earlier sessions of this instance have already obtained. Every source the canon uses has an entry in `canon/bibliography.bib`, and a text search of that file for an author's name or a title shows whether a paper is already there. A result taken from a source is an element whose record names the source's key in its header and says, in its `## Literature` part, how much of the source was read; a text search of `canon/records/` for the key finds those elements.

Where a record gives the reference under which the scholarly tool retained a source, you can read that source with `extract` without retrieving it again. A source that an earlier session confirmed can be used at the depth its record states. If your use needs more than was read, for example the proof where only the statement was read, go to the source for that part and say so.

Look also in the imported library. Mathlib contains a large part of classical mathematics, and a result it already has is used directly in a proof, by the library's name for it, without a citation and without an element.

## Search

The instance's literature tool is scholarly-mcp. When it is attached to your session, use it first. Begin with `list_sources` to see which sources it serves, and read a source's query syntax and capabilities with `describe_source`. Then use `search` to query the source and `fetch` to obtain a specific item by its identifier. The server retains large results and returns a reference to each; passing that reference to `extract` reads records, fields or pages from what the call retained.

Sessions receive the sources that are reached through public interfaces. Among them are the indexes zbMATH, OpenAlex and Semantic Scholar, the registry of publications Crossref and the preprint server arXiv. Sources that require an institutional login are not offered to sessions, so MathSciNet cannot be searched and the full text of many journal articles cannot be retrieved; a request for such a source is answered with the code `source_not_enabled`, which says nothing about whether the work exists. When you need a paper that can be reached only through such a source, look for a preprint or an author's own copy. If there is none, note the paper as not read, and say what you relied on in its place, for example the abstract or another paper's account of it.

When the question is whether a result is known, include zbMATH. Many of its entries carry a summary written by a reviewer, and its entries carry a subject classification and links to cited and citing works; it covers published mathematics more completely than a preprint server or a general search engine does. Follow both the works a useful paper cites and the later works that cite it, when that helps to establish coverage or to locate a development.

Web search and the pages of preprint servers and authors supplement this, and they are what you use when the scholarly tool is not attached or a source is unavailable through it.

Interpret the outcome of each search exactly. An empty result says that this source returned nothing for this expression. A result marked restricted, or a database error, says nothing about whether the work exists. A result with the code `rate_limited` says that the source refused the request for the moment because too many requests had reached it from this machine, which other sessions share; try again after the interval the result names, or later. Any assertion that something is new, or absent from the literature, must be bounded by the sources and the search scope actually examined.

## Keep a log of the search

Keep a search log as you go, in a file under `work/literature/`. Its purpose is that someone who reads it, the peer and the reviewer of your work first of all, can tell what was searched and what was not. A log that serves that purpose says:

- the question the search was meant to answer;
- each search made: the source or tool, the expression exactly as submitted, and what came back, including searches that returned nothing, were restricted or failed;
- each source read: its identifier and location, the artifact reference when the scholarly tool retained it, and what was read there, down to the theorem or equation numbers confirmed;
- what could not be read or was not consulted, such as a paper behind an access barrier or a scanned document without a text layer;
- what was not searched for, when a reader might otherwise assume it was.

The form is a recommendation and nothing checks it.

The log stays in your session's working files, which later sessions cannot open. What later sessions need therefore goes into the canon: the bibliography entry and the `## Literature` part described in the next section, and, wherever a record says that something is new or not in the literature, the scope of the search behind that statement.

## A result from the literature in the canon

A result that you take from a source and use enters the canon as an element, like any other result. Its statement is written in Lean, in terms of the instance's own definitions, and its record carries what a later reader needs in order to rely on it. A producing session leaves this material in its report, and the peer writes the element, its record and the bibliography entry into the candidate.

The statement is where a citation most often goes wrong. The source states its theorem for its own objects and in its own conventions, and the Lean statement speaks of the instance's definitions. Retain the source's definitions, its exact statement and its assumptions, and explain how its notation and conventions correspond to the objects here. A theorem remembered from an abstract or taken from a secondary account needs confirmation against the source before it can support anything. A citation lets a reader check your account against its source; it does not supply an application argument you left out.

The record of such an element has the following beyond what every record has.

- The header key `source` gives the key of the source's entry in the bibliography.
- The `## Literature` part gives the precise location of the result in the source, how much of the source was read, and where the statement stands in what was read: whether it is a main theorem with a proof, a remark stated without proof, or a result the source attributes to earlier work. For how much was read, say whether it was the full text, named parts or the abstract only, and whether you read the proof of what you use or only its statement. When the scholarly tool retained the item, give the reference it returned as well, so that a later session can read the same copy.
- The `## Proof` part is what makes the statement count as having a proof. For a cited result it says that the proof is the one in the source and where it is found, and it gives the argument that leads from the source's statement to the Lean statement wherever the two are not literally the same. If you worked the proof through, write it out. If only the statement was read, say so here as well; review judges the element on what was read.

A `## Literature` part might read:

```markdown
## Literature

[AuthorAuthor2003], Theorem 4.3. Retained by the scholarly tool as <reference>.

Read: sections 2 and 4 of the arXiv version (v2) in full, including the proof of Theorem 4.3; the journal version was not seen.

Theorem 4.3 is the main result of section 4 and is proved there. The paper indexes its sequence from 1 and this library from 0, so the paper's $a_n$ is `Small.a (n - 1)`.
```

The note on what was read matters as much as the identifiers. It tells a later session whether it can rely on your reading for its own use or has to go to the source, and it tells a reviewer what your confirmation covered.

The bibliography entry is a BibTeX entry in the candidate's `bibliography.bib`. Give the authors, the title, where the work appeared and the year, and the identifiers that fix which document it is: a DOI, an arXiv number together with its version, an MR or Zbl number.

The entry holds what a reference list prints, and nothing addressed to the sessions of the research. When a paper is written from the canon, the bibliography goes into it as it stands, and the paper's list of references prints the fields of a cited entry that its style knows, `note` among them. A remark in such a field on which version the records cite, or on how the numbering of a source's theorems changed between versions, would be printed there too. Such a remark belongs in the `## Literature` part of the record, which already says what was read and where the statement stands in the source. A note that describes the work itself, such as the translator of an edition, is part of the entry.

```bibtex
@article{AuthorAuthor2003,
  author  = {A. Author and B. Author},
  title   = {Title of the paper},
  journal = {Journal},
  volume  = {12},
  year    = {2003},
  pages   = {45--67},
  doi     = {<DOI>},
  eprint  = {<arXiv number>v2},
  note    = {Zbl <number>}
}
```

The wording and arrangement shown inside the `## Literature` part and the choice of BibTeX fields are recommendations; the same information arranged otherwise serves equally well. The parts and header keys of the record are those [The written texts of the canon](records.md) fixes. A source the bibliography already lists keeps its entry, and you cite it by its existing key.

A cited result that the root comes to rest on is under the same final requirement as every other statement: before the research is complete, it needs a complete Lean proof. A deep theorem that the imported library does not contain therefore brings with it the work of proving it in Lean later. That is no reason to avoid a result the argument needs, and it is a reason to prefer, between two results that serve equally, the one the imported library has or the one whose proof is within reach.

The literature of the problem itself belongs in the canon too, although no proof uses it: the work that poses the root, or another statement the research took from the literature, and the earlier results on that statement. Each such work has an entry in the bibliography, and the record of the statement, which for the problem itself is the record of the root, says in its `## Literature` part what the work has of the statement, such as that it poses it or proves a case or a weaker form of it, and how much of the work was read, citing the work by its key in square brackets as the example above does. The record receives no header key `source` for such a work: that key marks a result taken from its source, which the paper cites and does not prove. A producing session leaves what it read in its report, and the peer enters it in a record that replaces the present one. The reason is the paper that is written from the canon once the root is settled. It cites only works of the bibliography, says of a work no more than a record says was read and adds nothing from memory, and no later step looks for where a problem comes from, so what no session read and entered is missing from that paper. How far to read into the history of a problem remains your judgment, as with every search.

Distinguish checking a transcription from checking a calculation based on it. A correct calculation with a wrongly transcribed recurrence still concerns the wrong recurrence. Preserve what was checked and what remains unavailable. Respect the constraints on access to a source and on quoting from it; a faithful mathematical account can explain the needed definitions and argument in your own words with a precise citation.

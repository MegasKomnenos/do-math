# Searching and using literature

You should actively look for earlier work you can use, and cite it, instead of building everything again yourself. The common introduction gives this guidance and its reasons under "Building on what already exists". This reference explains how to carry it out: what a search is for, where to look first, how to search, what to keep from a search, and how to cite what you use.

## Decide what the search is for

A literature search can answer different questions, and they call for different searches. Decide which uncertainty the search addresses before choosing search expressions.

To find out whether a result is already known, the search has to be broad. It should use several suitable databases, try the alternative names under which the object or the result may appear, and follow the chains of citation leading from the papers you find. One relevant paper does not answer the question, and neither does one search that returns nothing.

To find a technique worth applying, read a few of the most relevant sources closely, far enough to see what the technique assumes and whether those assumptions hold for the objects here.

When you take up a node or a question, you may also search in order to learn what surrounds the problem: which objects have been studied, under which names, and which standard results exist for them. The aim of such a search is that you recognize a known tool when your argument needs one.

## Look first at what the instance already has

Before searching outside, find out what earlier sessions of this instance have already obtained. Published records that used literature list their sources, often with the identifier of each and with a note of how much of it was read. The general index and its modules lead to those records, and a text search of `knowledge/records/` for an author's name or a title finds the rest.

In an earlier run three papers were each searched for by three different sessions working separately. Where a record gives the reference under which the scholarly tool retained a source, you can read that source with `extract` without retrieving it again. A source that an earlier record confirmed can be used at the depth that record states. If your use needs more than it read, for example the proof where only the statement was read, go to the source for that part and say so.

## Search

The instance's literature tool is scholarly-mcp. When it is attached to your session, use it first. Begin with `list_sources` to see which sources it serves, and read a source's query syntax and capabilities with `describe_source`. Then use `search` to query the source, `extract` to read records, fields or pages from what a call retained, and `fetch` to obtain a specific item by its identifier. The server retains large results and returns a reference to each; you read a retained result by passing its reference to `extract`.

Sessions receive the sources that are reached through public interfaces. Among them are the indexes zbMATH, OpenAlex and Semantic Scholar, the registry of publications Crossref and the preprint server arXiv. Sources that require an institutional login are not offered to sessions. In practice this means that MathSciNet cannot be searched and that the full text of many journal articles cannot be retrieved; a request for such a source is answered with the code `source_not_enabled`, which says nothing about whether the work exists. When you need a paper that can be reached only through such a source, look for a preprint or an author's own copy. If there is none, record the paper as not read, and say what you relied on in its place, for example the abstract or another paper's account of it.

When the question is whether a result is known, include zbMATH. Many of its entries carry a summary written by a reviewer, and its entries carry a subject classification and links to cited and citing works; it covers published mathematics more completely than a preprint server or a general search engine does. Follow both the works a useful paper cites and the later works that cite it, when that helps to establish coverage or to locate a development.

Web search and the pages of preprint servers and authors supplement this, and they are what you use when the scholarly tool is not attached or a source is unavailable through it.

Interpret the outcome of each search exactly. An empty result says that this source returned nothing for this expression. A result marked restricted, or a database error, says nothing about whether the work exists. A result with the code `rate_limited` says that the source refused the request for the moment because too many requests had reached it from this machine, which other sessions share; try again after the interval the result names, or later. Any claim that something is new, or absent from the literature, must be bounded by the sources and the search scope actually examined.

## Keep a record of the search

Keep a search log as you go, in a file under `work/literature/`. Its purpose is that someone who reads it, the peer and the reviewer of your work first of all, can tell what was searched and what was not. A log that serves that purpose says:

- the question the search was meant to answer;
- each search made: the source or tool, the expression exactly as submitted, and what came back, including searches that returned nothing, were restricted or failed;
- each source read: its identifier and location, the artifact reference when the scholarly tool retained it, and what was read there, down to the theorem or equation numbers confirmed;
- what could not be read or was not consulted, such as a paper behind an access barrier or a scanned document without a text layer;
- what was not searched for, when a reader might otherwise assume it was.

The form is a recommendation and nothing checks it. It follows a log that one peer session of an earlier run kept without being asked.

The log stays in your session's working files, which later sessions cannot open. What later sessions need therefore goes into the record: the list of sources described in the next section, and, wherever the record claims that something is new or not in the literature, the scope of the search behind that claim.

## Cite what you use

For a result you use, retain its definitions, its exact statement and assumptions, the argument needed to apply it here, and the bibliographic entry with a precise location in the source. Explain how its notation and conventions correspond to the objects of this research. A theorem remembered from an abstract or taken from a secondary account needs confirmation against the source before it can support a stronger claim. A citation lets a reader check your account against its source; it does not supply an application argument you left out.

In the record's list of sources, give for each entry the authors, the title, where it appeared and the year, the identifiers that fix which document it is, and how much of it you read. Useful identifiers are a DOI, an arXiv number together with its version, and an MR or Zbl number. When the scholarly tool retained the item, give the reference it returned as well, so that a later session can read the same copy. For how much was read, say whether it was the full text, named parts or the abstract only, and whether you read the proof of what you use or only its statement. An entry might read:

```text
[AB] A. Author, B. Author, Title of the paper, Journal 12 (2003) 45-67. doi:<DOI>; arXiv:<number>v2; Zbl <number>.
     Retained: <reference returned by the scholarly tool>.
     Read: sections 2 and 4 of the arXiv version in full, including the proof of Theorem 4.3; the journal version not seen.
```

The note on what was read matters as much as the identifiers. It tells a later session whether it can rely on your reading for its own use or has to go to the source, and it tells a reviewer what your confirmation covered. This form is also a recommendation; a record that gives the same information in another arrangement serves equally well.

Distinguish checking a transcription from checking a calculation based on it. A correct calculation with a wrongly transcribed recurrence still concerns the wrong recurrence. Preserve what was checked and what remains unavailable. Respect the constraints on access to a source and on quoting from it; a faithful mathematical account can explain the needed definitions and argument in your own words with a precise citation.

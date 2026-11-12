The diagram shows one pipeline and the organizer's loop. Every box except the knowledge base and the record is a session that the runner launches as a fresh conversation; the arrows carry files from one session to the next, and no two sessions converse.

```mermaid
flowchart LR
  KB["knowledge base: frontier, index, board, records"]
  P["producing session: attempt, explorer or formalizer"]
  PR["peer"]
  RV["review"]
  REC["record with its assessment"]
  ORG["organizer"]
  KB -- "read; an attempt or explorer chooses its own work, a formalizer receives a node whose informal proof review has accepted" --> P
  P -- "retained work" --> PR
  P -- "retained work" --> RV
  PR -- "record candidate" --> RV
  RV -- "publish, with claim statuses" --> REC
  REC --> KB
  KB -- "records not yet organized" --> ORG
  ORG -- "modules, shared context, glossary" --> KB
```

# Zenodo v2 (10.5281/zenodo.24142218) 설명문 초안

아래 텍스트를 Zenodo 기록의 Description 칸에 붙인다. Zenodo는 HTML 서식을 받으므로 문단 사이 빈 줄은 유지된다. 그 아래에 Keywords와 Related identifiers에 넣을 값을 적었다.

## Description

This archive is the `knowledge/` directory of a do-math research instance: the records that a run of autonomous mathematical research published, together with the views derived from them. do-math runs research on one proposition through many fresh AI sessions that share no conversation. Each piece of work is produced by one session, developed into a record by a second session that reads everything the first left behind, and assessed by a third session that compares the record with the originals. Published records never change; later judgments attach to them. Every judgment in this archive was made by AI sessions, and no person has reviewed its records. The software, its design record and a description of these files are at https://github.com/MegasKomnenos/do-math.

The instance worked on Conjecture 6.5 of Celano, Elder, Hadaway, Harris, Martin, Priestley and Udell (arXiv:2507.07243): for every length n, the numbers of parking functions of length n with maximum displacement 0, 1, …, n−1 form a unimodal sequence. The run started on 5 November 2026. This version was compressed on 12 November 2026 at 01:52 Korean time and deposited at 02:38 Korean time (11 November, 17:38 UTC); it holds 300 records. On 11 November at 16:14 Korean time the root proposition had reached the state do-math calls informally proved: every record and relation on two routes from proved statements to the root had been accepted by an AI review session. That state has qualifications. Several steps rest on computer-assisted inputs in binary64 floating point with error models assumed in advance, which the reviews name. One record on the routes (r030ffaebcd164eb492cc4215ce1c2e56) relies on two monotonicity properties that it asserts and that its review checked numerically but that no record in this version proves; after this version was taken, the instance was asked to prove them. The root has no Lean proof: the user paused formalization on 9 November so that the research could finish first. One necessary condition of the root has a Lean proof whose axioms are exactly propext, Classical.choice and Quot.sound (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7). Version 1 of this record was taken on 11 November at 00:19 Korean time, while the root was still open.

To read the archive, extract it and open `index.md`, which lists the records with each record's own description and the review's assessment beside it. `frontier.md` gives every node's exact statement, its state, the proofs behind that state and the accepted relations between nodes; the root is listed first with its two routes. `glossary.md` is the shared vocabulary. Each record is a directory under `records/` holding `record.json` (claims and proposals), `exposition.md` (the mathematics), `evidence/` (code, data, logs), `review/assessment.json` and `review/feedback.md` (the independent assessment) and `provenance.json`. The record that proved the last open premise on the routes to the root is `records/r5909c9e73b34492cbe5e197cf65c02e8`. `state.json` is a structured projection of the same evidence. The standing conditions the user supplied to the run and the sessions' own conversations are not part of `knowledge/`; the repository's README summarizes the conditions.

## Keywords

parking functions; maximum displacement; unimodality; combinatorics; autonomous research; multi-agent system; large language models; Lean 4; Mathlib; do-math

## Related identifiers

| Relation | Identifier | Type |
|---|---|---|
| Is compiled by | https://github.com/MegasKomnenos/do-math | URL |
| References | arXiv:2507.07243 | arXiv |

(v1과의 판본 관계는 Zenodo가 이미 보유한다.)

## 사용자가 확인할 것

- 압축 시각 01:52 KST는 인스턴스 루트의 `knowledge.7z`(크기가 v2와 같은 341,293,992바이트)의 수정 시각이고, 02:38 KST는 Zenodo API의 `created` 값이다. 두 시각 사이에 게시 사건은 없다.
- 기록 수 300은 게시 사건 시각이 01:52 KST 이하인 기록을 센 값이다.
- "Is compiled by" 대신 "Is supplemented by"나 "Is derived from"을 쓸 수도 있다. DataCite 어휘에서 소프트웨어가 자료를 만든 관계는 "IsCompiledBy"가 가장 가깝다.
- 저장소 README가 공개된 뒤에 붙이면 링크가 바로 작동한다.

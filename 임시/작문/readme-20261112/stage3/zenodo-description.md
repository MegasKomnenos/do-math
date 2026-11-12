# Zenodo v3 설명문 초안 (흐름 개정판)

아래 텍스트를 Zenodo 기록(v3)의 Description 칸에 붙인다. Zenodo는 HTML 서식을 받으므로 문단 사이 빈 줄은 유지된다. 압축 시각(23:25 KST, 인스턴스 루트 `knowledge.7z`의 수정 시각 23:25:51)과 기록 수(340, 게시 사건 시각이 압축 시각 이하인 기록)는 채웠고, 기탁 시각 하나가 자리 표시자로 남아 있다. 그 아래에 Keywords와 Related identifiers에 넣을 값을 적었다.

## Description

This archive is the complete knowledge base of one run of autonomous mathematical research. The run worked on Conjecture 6.5 of Celano, Elder, Hadaway, Harris, Martin, Priestley and Udell (arXiv:2507.07243): for every length n, the numbers of parking functions of length n with maximum displacement 0, 1, …, n−1 form a unimodal sequence. It started on 5 November 2026 and was carried out entirely by AI sessions, using the do-math system described at the end of this text. The archive holds every result the run published, each with the independent assessment it received, together with the index, the frontier (the list of statements the research tracked, with their states) and the glossary derived from them. This version is a snapshot taken on 12 November 2026 at 23:25 Korean time and deposited on 13 November at 00:45 Korean time (12 November, 15:45 UTC); it holds 340 records. Version 2 was a snapshot taken on 12 November at 01:52 Korean time with 300 records, and version 1 a snapshot taken on 11 November at 00:19 Korean time, while the conjecture was still unresolved.

On 11 November at 16:14 Korean time the conjecture reached the state that do-math calls informally proved. The term is do-math's own, and it means less than the words may suggest: along the two chains of implications that lead from statements proved in earlier records to the conjecture itself, every record had passed review and every implication had been accepted by an AI review session. The two chains are not independent confirmations; both pass through one statement, that the sequence never decreases over the steps below its middle index, in the exact range the frontier states. No person has refereed the records. Several steps rest on computer-assisted inputs: a finite verification that the conjecture holds for all n ≤ 20000, and binary64 floating-point computations with error models assumed in advance, in which the rounding error is covered by preset margins rather than tracked by the arithmetic. The reviews name these steps, the conjecture's informal proof depends on them, and a reader who does not accept such an error model should treat the conjecture as unproved. The conjecture has no machine-checked proof: the user, the person who started the run, paused formalization in Lean 4 on 9 November so that the sessions could finish the informal mathematics before formalization is resumed. One statement that the conjecture implies does have a Lean 4 proof, whose axioms are exactly propext, Classical.choice and Quot.sound, the three standard axioms of Lean's logic, with no unproved assumption left (record r0af7f414c9ea4bc5847ce2e9f6d0c6a7); that proof leaves the conjecture itself open.

To read the archive, extract it and open `index.md`, which lists the records chosen as orientation for new sessions, the groups (called modules) into which records were sorted, and the records not yet sorted, each with its own description and the review's short assessment beside it. `frontier.md` lists the nodes, that is, the exact statements the research tracked, with the conjecture first among them; for each node it gives the state, the proofs behind that state and the accepted implications to other nodes, and for the conjecture it shows the two chains of implications mentioned above, which the frontier calls routes. `glossary.md` is the shared vocabulary. Each record is a directory under `records/` holding `record.json` (claims and proposals), `exposition.md` (the mathematics), `evidence/` (code, data, logs), `review/assessment.json` and `review/feedback.md` (the assessment) and `provenance.json`. The record that proved the last open statement on those routes is `records/r5909c9e73b34492cbe5e197cf65c02e8`. `state.json` holds the same information in structured form. Three things are not part of the archive: the standing inputs, that is, the instructions the user gave to the sessions during the run; the sessions' working files, against which the reviews checked the drafts; and the sessions' conversations. The repository's first-run document (docs/do-math/first-run-parking-unimodality.md) lists the inputs.

The run was produced by do-math, a system in which many AI sessions work together to prove or refute a single mathematical statement. The sessions have no contact with one another: each is a new conversation that knows nothing of the others, and work passes between them only as files. Every record here is the work of three sessions in turn. One worked on the problem, trying to prove or refute a statement, to understand some feature of the problem, or to turn an already reviewed proof into a formal proof in Lean 4, a proof assistant; a second read everything the first left behind and developed it into a draft record; a third checked that draft against the first session's files and assessed every claim in it. Records that the third session judged worth keeping were published in the knowledge base, each with its assessment, including any claims the assessment did not support; every later session read them. Published records were never changed; later assessments were recorded beside them. The software, its design record and a description of these files are at https://github.com/MegasKomnenos/do-math.

## Keywords

parking functions; maximum displacement; unimodality; combinatorics; autonomous research; multi-agent system; large language models; Lean 4; Mathlib; do-math

## Related identifiers

| Relation | Identifier | Type |
|---|---|---|
| Is compiled by | https://github.com/MegasKomnenos/do-math | URL |
| References | arXiv:2507.07243 | arXiv |

(v1·v2와의 판본 관계는 Zenodo가 이미 보유한다.)

## 사용자가 확인할 것

- v3는 기록 24165415, DOI 10.5281/zenodo.24165415, `created` 2026-11-12T15:45:38Z(13일 00:45 KST), 파일 349,034,614바이트(인스턴스 루트의 `knowledge.7z`와 같다). 세 값을 모두 채웠다.
- 세 기록의 게시 시각(KST, 12일): rfc69320 16:12, r0e82912d 17:36, rc56f637b 18:18. 압축 시각이 18:18 이후이므로 셋이 모두 들어 있다.
- "Is compiled by" 대신 "Is supplemented by"나 "Is derived from"을 쓸 수도 있다. DataCite 어휘에서 소프트웨어가 자료를 만든 관계는 "IsCompiledBy"가 가장 가깝다.

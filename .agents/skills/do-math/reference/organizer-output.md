# Publishing organization decisions

Your organization decisions describe how the published mathematics should be found and recognized. The module layout and shared-context selection determine the reading paths through the index. Glossary dispositions and node merges determine which names or identifiers refer to the same shared objects.

Write these decisions in `output/organization.json`. The runner uses them to render the index and glossary while preserving every published mathematical account and its description. Supply the complete intended layout, so the file states what the organization should be after your work. The disposition arrays then record the specific glossary and identity changes that accompany it.

| Field | Content |
|---|---|
| `batch` | The exact list from your assignment. It identifies the publications this session processes. |
| `modules` | Array of `{id, title, description, records}`. `records` lists published research record IDs. A record may appear in several modules. |
| `shared_context` | Published research record IDs to display in the general index as shared context. |
| `promote` | Published local term IDs to promote permanently, written `<publication-id>/<term-id>`. |
| `refuse` | Current global candidate IDs to remove from the global glossary. |
| `merge_terms` | Array of `{keep, others, reason}`. Keep the primary entry's definition and append other entries' names and aliases. |
| `merge_nodes` | Array of `{from, into, reason}` identifying duplicate node statements. |
| `glossary` | Optional local definitions introduced in your own explanation, in the record's local entry format. |

Use empty arrays for operations not needed. Module IDs use letters, digits, `_` and `-`, beginning with a letter or digit, and must differ even without letter case. They become files under `knowledge/index/`. Supply titles and descriptions as readable text; the runner supplies links and record assessments.

An optional local glossary entry has `id`, `name`, `definition`, and optional `symbol`. The definition includes the domains and conditions needed to interpret your explanation. Use an empty array when you introduce no terminology. [Record format](record-format.md) explains introduced and inherited terminology in more detail.

Carry forward the existing layout as appropriate and place every record in the assigned batch into shared context or at least one module. Publications arriving later stay unfiled unless your complete layout places them as well; acknowledging your batch does not mark those later arrivals as processed. The next automatic organizer is due after four unprocessed research publications by default. Organizer outputs and separate comprehensive reviews do not count toward that threshold.

A global term ID refers to its published local definition. Promotion retains that definition. Refusal applies only to candidates; permanent membership survives merges. If a permanent entry merges into a candidate primary, the surviving primary becomes permanent. New writing then uses that primary name and recognizes the merged names as aliases.

Node merges preserve references through aliases. Explain the mathematical identity in `reason`; the runner does not establish identity by comparing strings. If both original nodes are occupied, both preexisting attempts continue against the merged identity.

The runner checks IDs, references, permissible dispositions and the exact batch. You judge whether the grouping helps readers, a term deserves shared status, and definitions or statements are actually identical. Read the resulting arrangement from that perspective, run the check command on your own session directory, and end.

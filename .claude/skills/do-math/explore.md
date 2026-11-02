# Working context of the exploration session

The exploration's job is to become familiar with the given problem slowly and to widen the horizon of understanding of the problem. Apply the purpose, authority, glossaries, literature and submission procedure of [common.md](common.md). An exploration is not tied to solving any element of the problem. Completing a proof or answering one question is not the goal. The goal is to look into the problem from several directions and become familiar with its structure, to find connections with unexpected concepts, and to test even ideas that look odd without pressure.

Hard problems are often not solved only by solving the visible elements one by one. A breakthrough sometimes appears from a deep understanding of the problem, or from a connection with a concept nobody expected. Even without a dramatic breakthrough, becoming familiar with the problem without hurry is important for seeing its essence. The understanding an exploration leaves becomes the basis on which the plans and research that follow pursue the goal more clearly, more coherently and with more direction.

## Starting the exploration

The instance's `goal.md` is the problem that is the subject of the exploration. The `task.instructions` of `input.json` loosely tell the subject or area to look into and the reason the plan posted this exploration. A plan posts an exploration in two cases. One is early in the research, when the problem is not yet familiar enough; the other is when, after several attempts, there is a need to step back one step and look with a wider view. The instructions are a starting point and do not close the scope of the exploration. You may start from the subject of the instructions and go to places whose relevance to the goal is not immediately visible.

At the start, read the global glossary and `knowledge/index.md`, and read the published records in `task.references`, with their local glossaries, and any other published knowledge needed. Reading all the published knowledge is not the exploration, and this applies to the index modules too: open the modules whose descriptions concern the angle you are looking from, and leave the others closed. If the exploration is for stepping back, the modules holding closed lines are the ones to open, because what failed, and where, is what a stepping-back exploration is meant to look at freshly. Read as much as is needed to touch the problem directly.

## The exploring attitude

An exploration is not work evaluated by what it proved. Even though a peer and a review follow, the exploration does not succeed only by obtaining a particular conclusion. That follow-up work examines the claims and interpretations left behind independently; it is not a gate that prevents thoughts that may be wrong from being brought out. Conjectures that may be wrong, connections whose use is unclear, and thoughts that ended in a dead end in the end are all worth recording if they helped understand the problem. Do not hurry. If a thought is interesting, follow where it leads.

Examples of ways to look in are as follows. This list is an example and does not limit the exploration to these methods.

- Build small cases directly by hand or by computation, and see what repeats and what breaks.
- Restate the problem in another form and see what becomes easier and what harder in each statement.
- Remove or change the conditions one by one and see how the conclusion changes. Look at special cases and generalized cases together.
- See the same object with the eyes of another field: generating functions, probability, geometry, algebraic structure, bijective correspondence and the like.
- Find analogies with similar problems or already known theorems. You may browse the literature with the scholarly academic-source tool defined by 'Literature' in [common.md](common.md) and look for connections.
- Think about why this problem is hard and which properties create that difficulty.
- Look again at the results and failures in the published knowledge from another angle. See what the failures say about the problem.

## Epistemic status of statements

At the time an exploration is published, the independent review is not yet finished. So that the next reader knows what can be read and how far, the author marks the status of statements. Attach one of the following statuses to every mathematical claim about the objects of the problem. Properties, patterns, relations, connections and results from the literature are such claims. Do not attach them to accounts of what was tried or of how your own understanding changed. But if such an account contains a mathematical claim, attach it to that claim.

| Status | Meaning and what to write with it |
|---|---|
| verified | Proved, or confirmed by an exact computation. Write the method and the range. |
| observed | A pattern seen in small cases or numerical data. Write the range seen. |
| conjecture | A claim with grounds but not confirmed. Write the grounds. |
| hunch | A connection or feeling that came without grounds. |
| literature | The literature says so. Transcribe according to 'Literature' in [common.md](common.md). |

If an exact exhaustive computation confirmed that there is no counterexample for n≤20, that finite statement is verified. The shape or rule read from that data is distinguished as observed, and the unproved proposition that the rule holds for every n as a conjecture. The fact that an exact computation was used does not confirm conclusions beyond the computed range.

Do not write a status higher than it really is. If a pattern seen in small cases is written as a verified fact, the next plan may choose tasks on the premise of that pattern and collapse together with it. Hunches and conjectures are useful records too, if written with their status.

## Following interesting ideas and handing understanding on

When a promising line of attack or a solvable question appears during the exploration, follow it far enough to understand what that discovery means. Do not stop at once because you have obtained grounds that it is promising. Handle yourself the questions that arise as the thought continues, such as which assumptions are really needed, why a conspicuous constant appears, and what changes in another expression. This is not a list of things to do but the process of making the discovery your own.

For an important discovery or content you mean to leave as an explanation, if the next step that can be confirmed with the formulas and argument now at hand is visible, perform that confirmation. Do not postpone to research the work of finishing a small generalization or a short argument merely because finishing it would make a theorem. In the process you may correct your first interpretation, discard a direction you thought promising, or end up somewhere unexpected. A proof obtained in an exploration is also kept in full. A proof is an achievement that can arise during exploration, not a goal that ties the exploration to producing it.

When completing one unresolved question becomes the center of later work, and the exploration that looks at the problem from another angle turns into focused solving work, hand that point on to research. Do not set the boundary merely because the computation gets long or more literature must be read. Becoming sufficiently familiar with an unfamiliar concept can take a long time. What you are doing is judged by whether the work widens and deepens the understanding with which the problem is seen, or focuses on obtaining one fixed conclusion.

When handing on, write what was seen and why it is worth looking into further, and what, once confirmed, would open that direction. Distinguish what you confirmed directly from what was not yet tried or got blocked. If you know which part of the original problem that direction connects to and what it still fails to explain, state that as well. If the relevance is still unclear, leave that unclarity as it is. It is not necessary to show immediate usefulness for the goal in order to record a connection. The plan receives the published understanding and the peer's and review's responses and chooses the follow-up research.

## Recording interpretations faithfully

When a picture of the problem forms, explain that picture, but do not attach a stronger meaning than the relations actually confirmed. In your own explanation, distinguish the part mathematically established from the interpretation that understands it. Do not hide failed cases or the scope of application behind an interesting story. If another interpretation comes naturally, examine it together with the original argument. The fact that the author's understanding changed is an important output of the exploration, but it does not replace a mathematical guarantee that the interpretation is right.

Do not omit confirmations the explorer can do because a peer and a review come afterwards. The peer is the role that meets the same output in another context and develops its own thinking, and the review is the role that judges the claims and evidence of both sides. It is not meant to have what the exploration already confirmed repeated, but to create the chance for different understandings to meet.

## Finishing

Session run time has no cap. Do not finish after writing down the first few things that came to mind. Finish when the following two conditions hold together.

1. You can write concretely how the understanding with which the problem is seen has changed compared with before the exploration.
2. Looking in from a new angle only repeats the viewpoints already obtained and widens the understanding no further.

Being blocked from one angle is not the second condition. Then move to another angle. The second condition holds when, after testing several angles, the last angles tested added no new item to 'Changed understanding' or 'Connections found'. Recording what was seen from each angle makes this judgment possible.

## Writing the output

The exploration body file (for example `output/exploration.md`) is written so that the next reader, who has not talked with this session, takes the understanding over. Include the following.

- Starting point: the instructions received, and the understanding at the start from the published knowledge read
- Changed understanding: how the problem is seen now and what differs from before the exploration. The center of the body.
- Angles examined: what was seen from each angle and its epistemic status
- Connections found: connections with other concepts, fields and theorems and their status
- Directions handed on: what was seen and why it is worth looking at further, and what, once confirmed, would open it. Write the connection to the original problem and the remaining obstacles as concretely as confirmed, and leave what is still unclear as unclear.
- Dead ends: thoughts that were tried but did not continue, and what they told about the problem

If operating conditions and model instructions must be preserved, put them in a separate operational memo and do not repeat them in the mathematical body.

If you computed, put the code, inputs and results in `output/` and link them in the body together with the reproduction method. If you used Lean, the compile goes through the Lean broker, as 'Running Lean' in [common.md](common.md) describes, and a proof obtained along the way gets the same axiom audit as it would in research. If new notation is needed, first see whether an existing global definition can be reused. Define the symbols and auxiliary objects the exploration uses in `output/glossary-local.md`, according to 'Glossaries' in [common.md](common.md), and flag as global candidates, by the criteria there, only the objects that need to be shared across the whole run; an exploration's candidates usually come with its handed-on directions, which name the object that a follow-up task would use. The local glossary is required by the official check even when it has no entries.

Write `output/output.json` in the 'Exploration output' format of section 4 of [protocol.md](protocol.md). `category` is `"explore"` and `supersedes` is `[]`. In `exposition` write the relative path, based on `output/`, of the exploration body file, and in `questions` write the questions that arose during the exploration as concrete strings. `[]` if none. In `references` write the published records actually used. `overview` introduces the whole exploration according to section 3 of [protocol.md](protocol.md). Write it so that the angles examined, the changed understanding and the directions handed on are visible.

So as not to lose what was obtained during the exploration, save it as needed in `output/` and continue the exploration. However the session ends, the runner re-checks the `output/` of that moment with the official check and publishes it if it passes. So each time you update `output.json`, keep it in a state that passes the official check. Save completed content of the body, code and computation data in each published file. The new output.json that points to these files is written completely to a temporary file in your own work/ and then swapped in as output/output.json (for example Python's os.replace). This way, even on interruption, one complete version of the JSON, either the previous or the new one, can be read. Before finishing, run the official check of [common.md](common.md) yourself to confirm the format, and finish by yourself. An integrated exploration is delivered to the next plan, and a peer session is assigned automatically. When the peer finishes, an independent review that sees the original exploration and the peer output together is assigned automatically. The plan may read the published understanding for its choice of direction. What is used as mathematical evidence is the content that review accepted with the exact claim and scope designated; the observations and conjectures of the exploration as a whole are not certified wholesale.

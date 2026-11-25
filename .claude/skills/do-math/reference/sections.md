# Sections: choosing and registering what you take on

The common introduction explains sections, their occupancy, the element's lease and the division of a statement under "Seeing work that is still underway: the board". Attempts and peers are the roles that register sections, and this guide gives what they need in order to do it.

## Stating a section

Every section is stated as precisely as the statement itself, and the statement implies it. Settling a section therefore asks for no more than the statement does, and settling sections that together cover all its requirements settles the statement. Several attempts can thus work on one statement at the same time without repeating each other. A section divides the statement and not the method: two attempts applying different techniques to the same part would still be proving the same results.

A statement that is not implied by the statement of the element is not a part of that element, even when proving it would suffice. For a statement asserting that a sequence rises to a single peak and then falls, monotonicity on either side of a chosen index, rising up to that index and falling after it, would prove the statement. When it is not known whether the peak lies at that index, the statement does not imply this monotonicity. An attempt that decides to pursue such a statement registers it as what it is: a statement of its own, not yet in the canon, given in Lean and in words together with the element it is aimed at. Registering it makes it visible. Two attempts that hold different elements and aim at the same intermediate statement can then see each other on the board, which a division into sections cannot show.

## Breadth, and the moment of registration

The breadth of a section follows the work you actually intend to do. An idea that could settle the whole statement calls for the whole statement; an approach to one regime calls for that regime. There is no merit in taking a small part for its own sake. A pattern that appears only across the whole problem may resolve many parts at once, and an attempt pursuing it needs the whole statement.

An attempt registers its section once it has decided what to pursue, and then does its research inside that section, because work that is not registered is invisible to other sessions, which may repeat it without knowing. Registering early has a cost as well. A boundary chosen before the shape of the difficulty is understood tends to follow what looks manageable rather than what the mathematics suggests, and it then fixes what counts as settled. When the shape is not yet clear, a breadth set by the approach you intend serves the research better than one set by the range you expect to cover. Understanding gained later can still be acted on, because you can register a further section when the mathematics calls for it.

Taking responsibility for a section does not limit the knowledge you can use to work on it. Results about other sections or other statements may provide a definition, an argument or a useful comparison. You can read those results and use them without taking on the problems they concern.

Your work may also develop beyond the section you first chose. You can register a further available section and pursue it alongside the sections you already hold, which remain yours. You therefore do not need to reserve additional parts in advance merely because you may need them later or want to consult results about them. An attempt's role guide develops the tradeoff between using its accumulated understanding and leaving useful work for another researcher.

## Choosing under the lease

While you hold the lease of an element, no other section can appear on the element, so the sections you read are the sections you have to respect. Registering your section ends your lease and lets the next waiting session choose, and a further section is chosen through the lease again. A statement whose own proof is accepted and which is not settled, because of what that proof rests on, can still be taken, and a statement of your own that would give it by another route is registered there.

The registration tool refuses what it can decide by itself, namely an identical statement, any conflict with a section that covers the whole element, and missing reasons. Two sections overlap when both ask for the same requirement in the same case. Sections covering the same cases but different required conditions do not overlap, and neither do sections asking for the same condition in different cases. Whether two differently stated sections overlap is a mathematical judgment, and it is yours. A registration therefore records, for every section other sessions hold on that element, your reason that the two sections are disjoint. Disjoint sections can still use each other's established results.

## The commands

Attempts and peers register sections with four commands. Replace `<element>` with the declaration name and `<file>` with a file path. Sections and leases attach to the statement, so if you name a declaration that is another proof of a statement, the commands act on the statement's own declaration, and their responses name it.

The commands count sections by pipeline: the sections registered by the producing session whose work a peer takes over, and by any earlier peer it replaces, are the peer's own. Where the descriptions below speak of sections, or a whole element, that another session holds, they mean those of another pipeline. Your own pipeline's sections need no reasons, and they do not prevent you from registering the whole element unless your pipeline already holds it whole.

1. `commands.lease` takes the element's lease if no other session holds it. A refusal exits with code 1, records nothing and returns the reason, the current holder, the waiting sessions and the element's sections. The lease is also refused for a definition, for a statement that is settled, contested or refuted, and while another session holds the whole element.
2. `commands.wait` joins the element's queue and returns with exit code 0 once the lease is yours. When its timeout passes first, it exits with code 124 and reports your place; the place is kept, so run the command again to keep waiting. It refuses with exit code 1, giving up your place on the element, when the element is a definition, when the statement is settled, contested or refuted, or when another session holds the whole element, whether that is already so when you start waiting or happens while you wait; the response says which. A session stands in one lease relation at a time: taking or waiting for another element gives up its place here.
3. `commands.section` registers a section while you hold the lease, and registering ends the lease. The file is JSON in one of the three forms below. Give a reason for every section other sessions hold on the element; the lease response lists them with their IDs. The tool refuses an identical statement, a whole-element registration while other sessions hold sections, and missing reasons. A refusal records nothing and keeps your lease, so you can correct the request. It also refuses a statement that has become settled, contested or refuted, or that another session now holds whole, when that changed while you held the lease; the response says which, and the remedy is then to release the lease rather than correct the request.
4. `commands.release` gives up the lease, or your place in the queue, without registering. Use it as soon as you decide not to take a section on that element. A lease has no time limit: until you register, release or end your session, everyone waiting for the element waits for you.

A section request takes one of three forms:

```json
{"whole": true}
```

```json
{"statement": "<the exact part of what the element asserts that you take on>",
 "reasons": {"<section ID>": "<why your section does not overlap it>"}}
```

```json
{"new": {"lean": "<a Lean statement that is not yet in the canon>",
         "statement": "<the same statement in words>"},
 "reasons": {"<section ID>": "<why your section does not overlap it>"}}
```

The first takes the whole of the statement. The second takes an exact part of it. The third registers a statement you have formulated yourself, on the element it is aimed at. `reasons` is needed only when other sessions hold sections on the element.

A registered section cannot be withdrawn, so register it once you have decided to pursue it. The transport check accepts a candidate that replaces the proof of an element only when its pipeline holds a section on that statement.

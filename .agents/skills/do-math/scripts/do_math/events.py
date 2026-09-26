"""Public events: preserve the parent's facts and number only new records."""


def event_rows(value):
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError("events must be a record list")
    return value


def check_sequence(rows, cursor=None):
    """The published numbering rule: ``event_seq`` runs 1..n in list order.

    ``cursor``, when given, is the runtime ``event_cursor`` and must equal n.
    Reading a snapshot and assigning new numbers both end with this check.
    """
    numbers = [row.get("event_seq") for row in rows]
    if any(type(number) is not int for number in numbers) or numbers != list(range(1, len(rows) + 1)):
        raise ValueError("published event sequence is not contiguous")
    if cursor is not None and cursor != len(rows):
        raise ValueError("event cursor differs from published events")


class EventPublisher:
    @staticmethod
    def assign_sequences_in_place(runtime, *, published_events=None):
        """Validate event history and assign sequence fields on the supplied runtime.

        ``published_events`` maps IDs to the parent's rows. The parent was read
        or published under the same contract, so its numbering already follows
        :func:`check_sequence` and is not checked again here. An error can
        leave this runtime partially numbered; callers apply this to their own
        candidate copy.
        """
        previous = published_events or {}
        if "events" not in runtime and not previous and not runtime.get("pending_events"):
            return
        events = runtime.setdefault("events", [])
        rows = event_rows(events)
        pending = runtime.get("pending_events", [])
        if not isinstance(pending, list):
            raise ValueError("pending_events must be a list")
        # This is the planner's unconsumed-event queue, not unpublished objects.
        if any(not isinstance(ref, str) for ref in pending) or len(set(pending)) != len(pending):
            raise ValueError("pending_events requires distinct event references")
        ids = [row.get("id") for row in rows]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError("event IDs must be distinct")
        if set(previous) - set(ids):
            raise ValueError("published events cannot be removed")
        if set(pending) - set(ids):
            raise ValueError("pending_events references unknown event")
        next_sequence = len(previous)
        for row in rows:
            identifier = row["id"]
            if "event_seq" in row and (type(row["event_seq"]) is not int or row["event_seq"] < 1):
                raise ValueError("invalid event sequence")
            if identifier in previous:
                old = previous[identifier]
                if {k: v for k, v in row.items() if k != "event_seq"} != {k: v for k, v in old.items() if k != "event_seq"}:
                    raise ValueError("published event content cannot be rewritten")
                if row.get("event_seq", old["event_seq"]) != old["event_seq"]:
                    raise ValueError("published event sequence cannot be rewritten")
                row["event_seq"] = old["event_seq"]
            else:
                next_sequence += 1
                if row.get("event_seq", next_sequence) != next_sequence:
                    raise ValueError("new event sequence must be contiguous")
                row["event_seq"] = next_sequence
        # Published rows keep their numbers and new rows follow them, so the
        # result is 1..n in list order exactly when no published row moved.
        check_sequence(rows)
        runtime["event_cursor"] = next_sequence

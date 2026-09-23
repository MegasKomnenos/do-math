"""Public events: preserve the parent's facts and number only new records."""
from copy import deepcopy


def event_rows(value):
    if isinstance(value, dict):
        rows = list(value.values())
        if any(not isinstance(row, dict) or key != row.get("id") for key, row in value.items()):
            raise ValueError("event map key and id differ")
        return rows
    if not isinstance(value, list) or any(not isinstance(row, dict) for row in value):
        raise ValueError("events must be a record list or map")
    return value


class EventPublisher:
    @staticmethod
    def prepare(instance, runtime, parent_last_seq=0, published_sequences=None, *, published_events=None):
        """Return detached candidates; the repository supplies complete parent facts."""
        instance, runtime = deepcopy(instance), deepcopy(runtime)
        EventPublisher.assign_sequences_in_place(runtime, parent_last_seq, published_sequences,
                                                published_events=published_events)
        return instance, runtime

    @staticmethod
    def assign_sequences_in_place(runtime, parent_last_seq=0, published_sequences=None, *, published_events=None):
        """Validate event history and assign sequence fields on the supplied runtime.

        An error can leave this runtime partially numbered. Callers requiring an
        unchanged original use prepare(), or apply this to their own candidate copy.
        """
        previous = published_events or {}
        if previous:
            numbers = sorted(row["event_seq"] for row in previous.values())
            if numbers != list(range(1, len(previous) + 1)):
                raise ValueError("parent event sequence is not contiguous")
            parent_last_seq = numbers[-1]
        if type(parent_last_seq) is not int or parent_last_seq < 0:
            raise ValueError("invalid parent event sequence")
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
        next_sequence = parent_last_seq
        for row in rows:
            identifier = row["id"]
            if identifier in previous:
                old = previous[identifier]
                if {k: v for k, v in row.items() if k != "event_seq"} != {k: v for k, v in old.items() if k != "event_seq"}:
                    raise ValueError("published event content cannot be rewritten")
                if row.get("event_seq", old["event_seq"]) != old["event_seq"]:
                    raise ValueError("published event sequence cannot be rewritten")
                row["event_seq"] = old["event_seq"]
            elif published_events is None and row.get("event_seq", parent_last_seq + 1) <= parent_last_seq:
                # Standalone sequence-only API; repository never uses this weaker boundary.
                if published_sequences is not None and published_sequences.get(identifier) != row["event_seq"]:
                    raise ValueError("published event sequence cannot be rewritten")
            else:
                next_sequence += 1
                if row.get("event_seq", next_sequence) != next_sequence:
                    raise ValueError("new event sequence must be contiguous")
                row["event_seq"] = next_sequence
        if previous:
            old_order = [row["event_seq"] for row in rows if row["id"] in previous]
            if old_order != sorted(old_order):
                raise ValueError("published event order cannot be changed")
            if [row["event_seq"] for row in rows] != list(range(1, len(rows) + 1)):
                raise ValueError("new events must follow published event order")
        runtime["event_cursor"] = next_sequence

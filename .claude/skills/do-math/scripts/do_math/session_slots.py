"""Cross-process local execution slots shared by engine and scheduled operator.

SQLite serializes admission, while OS locks identify live owners. Slot records
are retained after release. A disappeared owner releases a started session only
after its named Windows Job is observed empty/absent. Unknown lifetime stays held.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid


def _lock(path: Path):
    stream = path.open("a+b")
    if path.stat().st_size == 0:
        stream.write(b"0"); stream.flush()
    stream.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        stream.close()
        return None
    return stream


def _unlock(stream):
    if stream is None:
        return
    stream.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(stream.fileno(), fcntl.LOCK_UN)
    stream.close()


class SessionSlots:
    def __init__(self, workspace: Path, instance_id: str, *, observer=False):
        self.root = Path(workspace) / "session-slots" / instance_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.owner = None if observer else uuid.uuid4().hex
        self.owner_lock = _lock(self.root / (self.owner + ".lock")) if self.owner else None
        self.path = self.root / "slots.sqlite3"
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS limits (pool TEXT, model TEXT, capacity INTEGER NOT NULL, PRIMARY KEY(pool,model))")
            db.execute("CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, pool TEXT, model TEXT, owner TEXT, state TEXT, process TEXT, created REAL, ended REAL, reason TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS provider_waits (provider TEXT PRIMARY KEY, generation INTEGER NOT NULL, state TEXT NOT NULL, retry_at REAL, evidence TEXT, probe_owner TEXT, probe_started_at REAL, attempts INTEGER NOT NULL)")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def configure(self, limits: dict):
        with self._db() as db:
            db.execute("DELETE FROM limits")
            db.executemany("INSERT INTO limits VALUES(?,?,?)", [(p, m, n) for p, row in limits.items() for m, n in row.items()])

    def _reconcile(self, db):
        owners = {}
        for row in db.execute("SELECT * FROM sessions WHERE state != 'ended'").fetchall():
            if row["owner"] == self.owner and row["state"] != "stopping":
                continue
            if row["owner"] not in owners:
                probe = _lock(self.root / (row["owner"] + ".lock"))
                owners[row["owner"]] = probe is None
                _unlock(probe)
            if owners[row["owner"]] and row["state"] != "stopping":
                continue
            identity = json.loads(row["process"]) if row["process"] else None
            ended = identity is None  # on_started is acknowledged before the suspended Job resumes.
            if identity and identity.get("job_name"):
                from .windows_job import named_job_empty
                ended = named_job_empty(identity["job_name"]) is True
            if ended:
                db.execute("UPDATE sessions SET state='ended', ended=?, reason='owner disappeared; local lifetime reconciled' WHERE id=?", (time.time(), row["id"]))
                db.execute("UPDATE provider_waits SET state='waiting', probe_owner=NULL, probe_started_at=NULL WHERE state='checking' AND probe_owner=?", (row["id"],))

    def acquire(self, execution_id: str, pool: str, model: str, *, provider: str | None = None,
                enforce_capacity: bool = True, current_time: float | None = None) -> bool:
        if self.owner is None:
            raise ValueError("a read-only slot observer cannot reserve a session")
        with self._db() as db:
            self._reconcile(db)
            previous = db.execute("SELECT * FROM sessions WHERE id=?", (execution_id,)).fetchone()
            if previous:
                raise ValueError("session IDs are single-use")
            current = time.time() if current_time is None else current_time
            gate = db.execute("SELECT * FROM provider_waits WHERE provider=?", (provider,)).fetchone() if provider else None
            if gate and (gate["state"] == "checking" or (gate["state"] == "waiting" and gate["retry_at"] > current)):
                self.admission_reason = "provider_limit"
                return False
            if enforce_capacity:
                limit = db.execute("SELECT capacity FROM limits WHERE pool=? AND model=?", (pool, model)).fetchone()
                used = db.execute("SELECT count(*) FROM sessions WHERE pool=? AND model=? AND state != 'ended'", (pool, model)).fetchone()[0]
                if limit is None or used >= limit[0]:
                    self.admission_reason = "capacity"
                    return False
            db.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?,?)", (execution_id, pool, model, self.owner, "starting", None, current, None, None))
            if gate and gate["state"] == "waiting":
                db.execute("UPDATE provider_waits SET state='checking', probe_owner=?, probe_started_at=? WHERE provider=?",
                           (execution_id, current, provider))
            self.admission_reason = None
            return True

    def provider_result(self, execution_id: str, provider: str, *, failure: dict | None = None,
                        response_observed: bool = True, current_time: float | None = None,
                        initial_seconds: float = 300, maximum_seconds: float = 7200) -> dict:
        """Only an owned invocation can record a limit or finish its own probe."""
        from .provider_wait import retry_time
        current = time.time() if current_time is None else current_time
        with self._db() as db:
            reservation = db.execute("SELECT owner FROM sessions WHERE id=?", (execution_id,)).fetchone()
            if not reservation or reservation[0] != self.owner:
                raise ValueError("provider result has no owned invocation")
            row = db.execute("SELECT * FROM provider_waits WHERE provider=?", (provider,)).fetchone()
            if failure is not None:
                if failure.get("kind") != "provider_limit" or failure.get("provider") != provider:
                    raise ValueError("provider failure identity differs from admission")
                attempts = (1 if row is None or row["state"] == "available" else
                            row["attempts"] + int(row["state"] == "checking" and row["probe_owner"] == execution_id))
                retry_at = retry_time(failure, attempts, current, initial_seconds, maximum_seconds)
                if row and row["state"] == "waiting":
                    retry_at = max(retry_at, row["retry_at"])
                db.execute("INSERT OR REPLACE INTO provider_waits VALUES(?,?,?,?,?,?,?,?)",
                           (provider, row["generation"] + 1 if row else 1, "waiting", retry_at,
                            json.dumps({**failure, "execution_id": execution_id}), None, None, attempts))
            elif row and row["state"] == "checking" and row["probe_owner"] == execution_id:
                if response_observed:
                    db.execute("UPDATE provider_waits SET state='available', retry_at=NULL, probe_owner=NULL, probe_started_at=NULL, attempts=0 WHERE provider=?", (provider,))
                else:
                    retry_at = retry_time({}, row["attempts"] + 1, current, initial_seconds, maximum_seconds)
                    db.execute("UPDATE provider_waits SET state='waiting', retry_at=?, probe_owner=NULL, probe_started_at=NULL, attempts=attempts+1 WHERE provider=?", (retry_at, provider))
            result = db.execute("SELECT * FROM provider_waits WHERE provider=?", (provider,)).fetchone()
            return self._provider_view(result, current) if result else {"provider": provider, "state": "available", "generation": 0}

    @staticmethod
    def _provider_view(row, current):
        from .provider_wait import utc
        return {"provider": row["provider"], "generation": row["generation"], "state": row["state"],
                "retry_at": utc(row["retry_at"]), "due": row["state"] == "waiting" and row["retry_at"] <= current,
                "evidence": json.loads(row["evidence"]) if row["evidence"] else None,
                "probe_owner": row["probe_owner"], "probe_started_at": utc(row["probe_started_at"]),
                "attempts": row["attempts"]}

    def provider_snapshot(self, *, current_time: float | None = None) -> dict:
        from .provider_wait import utc
        current = time.time() if current_time is None else current_time
        with self._db() as db:
            self._reconcile(db)
            return {"observed_at": utc(current), "path": str(self.path),
                    "providers": {row["provider"]: self._provider_view(row, current)
                                  for row in db.execute("SELECT * FROM provider_waits")}}

    def started(self, execution_id: str, identity: dict):
        with self._db() as db:
            changed = db.execute("UPDATE sessions SET state='running', process=? WHERE id=? AND owner=? AND state='starting'",
                                 (json.dumps(identity), execution_id, self.owner)).rowcount
            if changed != 1:
                raise ValueError("session start has no owned reservation")

    def release(self, execution_id: str, *, reason="local runner returned after termination"):
        with self._db() as db:
            row = db.execute("SELECT process FROM sessions WHERE id=? AND owner=?", (execution_id, self.owner)).fetchone()
            if not row:
                return False
            identity = json.loads(row[0]) if row and row[0] else None
            if identity and identity.get("job_name"):
                from .windows_job import named_job_empty
                if named_job_empty(identity["job_name"]) is not True:
                    db.execute("UPDATE sessions SET state='stopping', reason='local Job termination unconfirmed' WHERE id=?", (execution_id,))
                    return False
            db.execute("UPDATE sessions SET state='ended', ended=?, reason=? WHERE id=? AND owner=?",
                       (time.time(), reason, execution_id, self.owner))
            # A probe without a classified response is retryable, never success.
            db.execute("UPDATE provider_waits SET state='waiting', retry_at=?, probe_owner=NULL, probe_started_at=NULL WHERE state='checking' AND probe_owner=?",
                       (time.time() + 300, execution_id))
            return True

    def snapshot(self) -> dict:
        with self._db() as db:
            self._reconcile(db)
            result = {"work": {}, "operations": {}}
            for row in db.execute("SELECT * FROM limits"):
                result[row["pool"]][row["model"]] = {"limit": row["capacity"], "used": 0, "execution_ids": []}
            for row in db.execute("SELECT * FROM sessions WHERE state != 'ended'"):
                cell = result[row["pool"]].setdefault(row["model"], {"limit": 0, "used": 0, "execution_ids": []})
                cell["used"] += 1
                cell["execution_ids"].append(row["id"])
            for values in result.values():
                for cell in values.values():
                    cell["available"] = max(0, cell["limit"] - cell["used"])
            return result

    def close(self):
        _unlock(self.owner_lock)
        self.owner_lock = None

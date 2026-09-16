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

    def acquire(self, execution_id: str, pool: str, model: str) -> bool:
        if self.owner is None:
            raise ValueError("a read-only slot observer cannot reserve a session")
        with self._db() as db:
            self._reconcile(db)
            previous = db.execute("SELECT * FROM sessions WHERE id=?", (execution_id,)).fetchone()
            if previous:
                raise ValueError("session IDs are single-use")
            limit = db.execute("SELECT capacity FROM limits WHERE pool=? AND model=?", (pool, model)).fetchone()
            used = db.execute("SELECT count(*) FROM sessions WHERE pool=? AND model=? AND state != 'ended'", (pool, model)).fetchone()[0]
            if limit is None or used >= limit[0]:
                return False
            db.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?,?)", (execution_id, pool, model, self.owner, "starting", None, time.time(), None, None))
            return True

    def started(self, execution_id: str, identity: dict):
        with self._db() as db:
            changed = db.execute("UPDATE sessions SET state='running', process=? WHERE id=? AND owner=? AND state='starting'",
                                 (json.dumps(identity), execution_id, self.owner)).rowcount
            if changed != 1:
                raise ValueError("session start has no owned reservation")

    def release(self, execution_id: str, *, reason="local runner returned after termination"):
        with self._db() as db:
            row = db.execute("SELECT process FROM sessions WHERE id=? AND owner=?", (execution_id, self.owner)).fetchone()
            identity = json.loads(row[0]) if row and row[0] else None
            if identity and identity.get("job_name"):
                from .windows_job import named_job_empty
                if named_job_empty(identity["job_name"]) is not True:
                    db.execute("UPDATE sessions SET state='stopping', reason='local Job termination unconfirmed' WHERE id=?", (execution_id,))
                    return False
            db.execute("UPDATE sessions SET state='ended', ended=?, reason=? WHERE id=? AND owner=?",
                       (time.time(), reason, execution_id, self.owner))
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

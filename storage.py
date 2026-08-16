"""Local persistence layer for RAGNAROC-UI.

Default backend is SQLite at data/ragnaroc.db (override with RAGNAROC_DB).
Set RAGNAROC_STORAGE=dynamo with standard AWS credentials in the environment
(AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY / AWS_DEFAULT_REGION) to use the
original DynamoDB tables instead. Credentials are never stored in code.

Operations used by the app:
    log_run(creator, exp_name)
    list_trial_names(creator) -> [name, ...]
    trial_exists(creator, name) -> bool
    get_trial(creator, name) -> dict | None
    save_trial(creator, name, runtime, canvas, mask, stim_types, vis_objs, overwrite)
"""

import json
import os
import sqlite3
from datetime import datetime

_DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ragnaroc.db")


class SqliteBackend:
    def __init__(self, path=None):
        self.path = path or os.environ.get("RAGNAROC_DB", _DEFAULT_DB)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS trials (
                       creator    TEXT NOT NULL,
                       name       TEXT NOT NULL,
                       runtime    INTEGER,
                       canvas     INTEGER,
                       mask       INTEGER,
                       stim_types TEXT,
                       vis_objs   TEXT,
                       updated_at TEXT,
                       PRIMARY KEY (creator, name)
                   )"""
            )
            conn.execute(
                """CREATE TABLE IF NOT EXISTS runs (
                       id       INTEGER PRIMARY KEY AUTOINCREMENT,
                       creator  TEXT,
                       exp_name TEXT,
                       ts       TEXT
                   )"""
            )

    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def log_run(self, creator, exp_name):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO runs (creator, exp_name, ts) VALUES (?, ?, ?)",
                (str(creator), str(exp_name), datetime.now().isoformat()),
            )

    def list_trial_names(self, creator):
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT name FROM trials WHERE creator = ? ORDER BY name", (str(creator),)
            ).fetchall()
        return [row["name"] for row in rows]

    def trial_exists(self, creator, name):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM trials WHERE creator = ? AND name = ?", (str(creator), str(name))
            ).fetchone()
        return row is not None

    def get_trial(self, creator, name):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM trials WHERE creator = ? AND name = ?", (str(creator), str(name))
            ).fetchone()
        if row is None:
            return None
        return {
            "creator": row["creator"],
            "name": row["name"],
            "runtime": int(row["runtime"]) if row["runtime"] is not None else None,
            "canvas": int(row["canvas"]) if row["canvas"] is not None else None,
            "mask": int(row["mask"]) if row["mask"] is not None else None,
            "stim_types": json.loads(row["stim_types"] or "[]"),
            "vis_objs": json.loads(row["vis_objs"] or "[]"),
        }

    def save_trial(self, creator, name, runtime, canvas, mask, stim_types, vis_objs, overwrite=False):
        if not overwrite and self.trial_exists(creator, name):
            return False
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO trials
                       (creator, name, runtime, canvas, mask, stim_types, vis_objs, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(creator),
                    str(name),
                    int(runtime),
                    int(canvas),
                    int(mask),
                    json.dumps(stim_types),
                    json.dumps(vis_objs),
                    datetime.now().isoformat(),
                ),
            )
        return True


class DynamoBackend:
    """Original DynamoDB backend; requires boto3 and AWS credentials in the environment."""

    def __init__(self):
        import boto3  # imported lazily so boto3 stays an optional dependency

        from boto3.dynamodb.conditions import Key

        self._key = Key
        self._db = boto3.resource("dynamodb")

    def log_run(self, creator, exp_name):
        self._db.Table("ragnaroc-runs").put_item(
            Item={"creator": str(creator), "exp-name": str(exp_name), "date": str(datetime.now())}
        )

    def list_trial_names(self, creator):
        response = self._db.Table("ragnaroc-trial-names").query(
            KeyConditionExpression=self._key("creator").eq(creator)
        )
        return [item["name"] for item in response["Items"]]

    def trial_exists(self, creator, name):
        response = self._db.Table("ragnaroc-trial-names").get_item(
            Key={"name": name, "creator": creator}
        )
        return "Item" in response

    def get_trial(self, creator, name):
        response = self._db.Table("ragnaroc-trials").query(
            KeyConditionExpression=self._key("name").eq(name) & self._key("creator").eq(creator)
        )
        if not response["Items"]:
            return None
        item = response["Items"][0]
        return {
            "creator": item["creator"],
            "name": item["name"],
            "runtime": int(item["runtime"]) if item.get("runtime") is not None else None,
            "canvas": int(item["canvas"]) if item.get("canvas") is not None else None,
            "mask": int(item["mask"]) if item.get("mask") is not None else None,
            "stim_types": json.loads(json.dumps(item["stimulus-types"], default=float)),
            "vis_objs": json.loads(json.dumps(item["visual-objects"], default=float)),
        }

    def save_trial(self, creator, name, runtime, canvas, mask, stim_types, vis_objs, overwrite=False):
        from decimal import Decimal

        if not overwrite and self.trial_exists(creator, name):
            return False
        self._db.Table("ragnaroc-trials").put_item(
            Item={
                "creator": str(creator),
                "name": str(name),
                "runtime": int(runtime),
                "canvas": int(canvas),
                "mask": int(mask),
                "stimulus-types": json.loads(json.dumps(stim_types), parse_float=Decimal),
                "visual-objects": json.loads(json.dumps(vis_objs), parse_float=Decimal),
            }
        )
        self._db.Table("ragnaroc-trial-names").put_item(
            Item={"creator": str(creator), "name": str(name)}
        )
        return True


def _make_backend():
    if os.environ.get("RAGNAROC_STORAGE", "").lower() == "dynamo":
        return DynamoBackend()
    return SqliteBackend()


_backend = None


def _get_backend():
    global _backend
    if _backend is None:
        _backend = _make_backend()
    return _backend


def log_run(creator, exp_name):
    return _get_backend().log_run(creator, exp_name)


def list_trial_names(creator):
    return _get_backend().list_trial_names(creator)


def trial_exists(creator, name):
    return _get_backend().trial_exists(creator, name)


def get_trial(creator, name):
    return _get_backend().get_trial(creator, name)


def save_trial(creator, name, runtime, canvas, mask, stim_types, vis_objs, overwrite=False):
    return _get_backend().save_trial(creator, name, runtime, canvas, mask, stim_types, vis_objs, overwrite)

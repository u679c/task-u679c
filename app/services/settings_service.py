import os
import sqlite3
from typing import List

DEFAULT_TASK_TYPES = ["需求", "bug", "其他"]
DEFAULT_STATUSES = ["待开始", "等待评审", "进行中", "已完成"]


def _sanitize_types(types: List[str]) -> List[str]:
    seen = set()
    cleaned: List[str] = []
    for raw in types:
        name = (raw or "").strip()
        if not name:
            continue
        if name == "无":
            continue
        if name in seen:
            continue
        seen.add(name)
        cleaned.append(name)
    return cleaned


def _sanitize_statuses(statuses: List[str]) -> List[str]:
    seen = set()
    cleaned: List[str] = []
    for raw in statuses:
        name = (raw or "").strip()
        if not name:
            continue
        if name == "无状态":
            continue
        if name in seen:
            continue
        seen.add(name)
        cleaned.append(name)
    return cleaned


class SettingsService:
    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or os.path.join(os.getcwd(), "app_settings.db")
        self._ensure_db()

    def get_task_types(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "select name from task_types order by position asc, name asc"
            ).fetchall()
        return [row[0] for row in rows]

    def set_task_types(self, types: List[str]) -> List[str]:
        cleaned = _sanitize_types(types)
        with self._connect() as conn:
            self._save_types(conn, cleaned)
        return cleaned

    def get_statuses(self) -> List[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "select name from statuses order by position asc, name asc"
            ).fetchall()
        return [row[0] for row in rows]

    def set_statuses(self, statuses: List[str]) -> List[str]:
        cleaned = _sanitize_statuses(statuses)
        with self._connect() as conn:
            self._save_statuses(conn, cleaned)
        return cleaned

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                create table if not exists task_types (
                    name text primary key,
                    position integer not null
                )
                """
            )
            conn.execute(
                """
                create table if not exists statuses (
                    name text primary key,
                    position integer not null
                )
                """
            )
            cur = conn.execute("select count(*) from task_types")
            count = cur.fetchone()[0]
            if count == 0:
                self._save_types(conn, DEFAULT_TASK_TYPES)
            cur = conn.execute("select count(*) from statuses")
            count = cur.fetchone()[0]
            if count == 0:
                self._save_statuses(conn, DEFAULT_STATUSES)

    def _save_types(self, conn, types: List[str]) -> None:
        conn.execute("delete from task_types")
        for index, name in enumerate(types):
            conn.execute(
                "insert into task_types (name, position) values (?, ?)",
                (name, index),
            )

    def _save_statuses(self, conn, statuses: List[str]) -> None:
        conn.execute("delete from statuses")
        for index, name in enumerate(statuses):
            conn.execute(
                "insert into statuses (name, position) values (?, ?)",
                (name, index),
            )

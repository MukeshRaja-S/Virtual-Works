"""SQLite schema and small repository helpers for the five mini-apps."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DB_PATH = Path(__file__).resolve().parent / "app.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL CHECK(length(trim(content)) > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS coffee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    votes INTEGER NOT NULL DEFAULT 0 CHECK(votes >= 0)
);
CREATE TABLE IF NOT EXISTS quote_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote TEXT NOT NULL,
    author TEXT NOT NULL,
    viewed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    available INTEGER NOT NULL DEFAULT 1 CHECK(available IN (0, 1))
);
"""

SEED_COFFEE = [
    ("Flat White", "Velvety espresso with micro-foam and a smooth finish."),
    ("Cappuccino", "Bold espresso, airy foam, and a dusting of cocoa."),
    ("Cold Brew", "Slow-steeped, chocolatey, and naturally low in acidity."),
    ("Pour Over", "Bright, precise, and layered with a clean finish."),
]
SEED_TEAM = [
    ("Maya Chen", "Product Design", 1),
    ("Jordan Ellis", "Engineering", 1),
    ("Samira Patel", "Customer Success", 0),
    ("Leo Martins", "Marketing", 1),
]


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def db() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with db() as connection:
        connection.executescript(SCHEMA)
        if connection.execute("SELECT COUNT(*) FROM coffee").fetchone()[0] == 0:
            connection.executemany("INSERT INTO coffee(name, description) VALUES (?, ?)", SEED_COFFEE)
        if connection.execute("SELECT COUNT(*) FROM team_members").fetchone()[0] == 0:
            connection.executemany("INSERT INTO team_members(name, role, available) VALUES (?, ?, ?)", SEED_TEAM)


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(row) for row in rows]

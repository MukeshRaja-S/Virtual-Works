from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, HttpUrl

from models import db, init_db, rows_to_dicts

BASE_DIR = Path(__file__).resolve().parent
app = FastAPI(title="Five Apps Workspace", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class NoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class ProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    bio: str = Field(min_length=1, max_length=500)
    image_url: HttpUrl | None = None


class QuoteCreate(BaseModel):
    quote: str = Field(min_length=1, max_length=1000)
    author: str = Field(min_length=1, max_length=200)


class AvailabilityUpdate(BaseModel):
    available: bool


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


# Task 1: Quick Notes
@app.get("/api/notes")
def list_notes() -> list[dict[str, Any]]:
    with db() as connection:
        rows = connection.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC").fetchall()
    return rows_to_dicts(rows)


@app.post("/api/notes", status_code=201)
def create_note(payload: NoteCreate) -> dict[str, Any]:
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Note cannot be blank")
    with db() as connection:
        cursor = connection.execute("INSERT INTO notes(content) VALUES (?)", (content,))
        row = connection.execute("SELECT id, content, created_at FROM notes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


# Task 2: Profile Card Generator
@app.post("/api/profile-card")
def create_profile_card(payload: ProfileCreate) -> dict[str, Any]:
    return {
        "name": payload.name.strip(),
        "bio": payload.bio.strip(),
        "image_url": str(payload.image_url) if payload.image_url else None,
        "initials": "".join(part[0] for part in payload.name.strip().split()[:2]).upper(),
    }


# Task 3: Coffee Ratings
@app.get("/api/coffee")
def list_coffee() -> list[dict[str, Any]]:
    with db() as connection:
        rows = connection.execute("SELECT id, name, description, votes FROM coffee ORDER BY id").fetchall()
    return rows_to_dicts(rows)


@app.post("/api/coffee/{coffee_id}/vote")
def vote_for_coffee(coffee_id: int) -> dict[str, Any]:
    with db() as connection:
        cursor = connection.execute("UPDATE coffee SET votes = votes + 1 WHERE id = ?", (coffee_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Coffee item not found")
        row = connection.execute("SELECT id, name, description, votes FROM coffee WHERE id = ?", (coffee_id,)).fetchone()
    return dict(row)


# Task 4: Quote Generator and history
FALLBACK_QUOTES = [
    {"quote": "Great things are done by a series of small things brought together.", "author": "Vincent van Gogh"},
    {"quote": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
    {"quote": "What we think, we become.", "author": "Buddha"},
]


@app.get("/api/quotes/random")
async def random_quote() -> dict[str, Any]:
    quote_data: dict[str, str] | None = None
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("https://dummyjson.com/quotes/random")
            response.raise_for_status()
            data = response.json()
            quote_data = {"quote": str(data["quote"]), "author": str(data["author"])}
    except (httpx.HTTPError, KeyError, TypeError, ValueError):
        with db() as connection:
            seen = connection.execute("SELECT COUNT(*) FROM quote_history").fetchone()[0]
        quote_data = FALLBACK_QUOTES[seen % len(FALLBACK_QUOTES)]

    with db() as connection:
        cursor = connection.execute(
            "INSERT INTO quote_history(quote, author) VALUES (?, ?)",
            (quote_data["quote"], quote_data["author"]),
        )
        row = connection.execute(
            "SELECT id, quote, author, viewed_at FROM quote_history WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return dict(row)


@app.post("/api/quotes/history", status_code=201)
def save_quote(payload: QuoteCreate) -> dict[str, Any]:
    with db() as connection:
        cursor = connection.execute(
            "INSERT INTO quote_history(quote, author) VALUES (?, ?)",
            (payload.quote.strip(), payload.author.strip()),
        )
        row = connection.execute(
            "SELECT id, quote, author, viewed_at FROM quote_history WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return dict(row)


@app.get("/api/quotes/history")
def quote_history() -> list[dict[str, Any]]:
    with db() as connection:
        rows = connection.execute(
            "SELECT id, quote, author, viewed_at FROM quote_history ORDER BY id DESC LIMIT 10"
        ).fetchall()
    return rows_to_dicts(rows)


# Task 5: Team Availability
@app.get("/api/team")
def list_team() -> list[dict[str, Any]]:
    with db() as connection:
        rows = connection.execute("SELECT id, name, role, available FROM team_members ORDER BY id").fetchall()
    return [{**dict(row), "available": bool(row["available"])} for row in rows]


@app.patch("/api/team/{member_id}")
def update_availability(member_id: int, payload: AvailabilityUpdate) -> dict[str, Any]:
    with db() as connection:
        cursor = connection.execute(
            "UPDATE team_members SET available = ? WHERE id = ?", (int(payload.available), member_id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Team member not found")
        row = connection.execute("SELECT id, name, role, available FROM team_members WHERE id = ?", (member_id,)).fetchone()
    return {**dict(row), "available": bool(row["available"])}

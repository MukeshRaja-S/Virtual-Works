# Five Apps Workspace

A single FastAPI + SQLite project containing five small applications in one responsive dashboard:

1. **Quick Notes** — saves notes to SQLite and refreshes the note list.
2. **Profile Card Generator** — posts name, bio, and optional image URL and renders a card.
3. **Coffee Rating** — seeded coffee items with persistent vote counts.
4. **Quote Generator** — fetches a random quote server-side from `dummyjson.com`, stores it in quote history, and falls back to local quotes if the external service is unavailable.
5. **Team Availability** — seeded team members with PATCH-based availability toggles.

## Project structure

```text
Virtual-Works/
├── task1_quick_notes/             # Task 1 documentation
├── task2_profile_card/            # Task 2 documentation
├── task3_coffee_rating/           # Task 3 documentation
├── task4_quote_generator/         # Task 4 documentation
├── task5_team_availability/       # Task 5 documentation
├── main.py                        # Shared FastAPI app and all API routes
├── models.py                      # Shared SQLite schema and seed data
├── requirements.txt
├── README.md
├── app.db                         # Created automatically on first startup
└── static/
    ├── index.html                 # Single-page dashboard
    ├── styles.css                 # Responsive visual design
    └── script.js                  # Vanilla JS API client and UI events
```

Each task now has its own top-level folder, while the five applications continue to use the shared backend and dashboard. This keeps the repository organized like a multi-task assignment without duplicating the server code.

## Run locally

Python 3.10+ is recommended.

```bash
cd fastapi-five-apps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open <http://127.0.0.1:8000>. The SQLite database and its tables are initialized automatically at startup. To reset all data, stop the server and remove `app.db`, then start it again.

## API routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` / `POST` | `/api/notes` | List or create notes |
| `POST` | `/api/profile-card` | Return a formatted profile card payload |
| `GET` | `/api/coffee` | List coffee items and votes |
| `POST` | `/api/coffee/{coffee_id}/vote` | Increment one coffee item's votes |
| `GET` | `/api/quotes/random` | Fetch, persist, and return a random quote |
| `GET` | `/api/quotes/history` | Return the 10 most recently viewed quotes |
| `POST` | `/api/quotes/history` | Persist a supplied quote |
| `GET` | `/api/team` | List team members and availability |
| `PATCH` | `/api/team/{member_id}` | Update one member's boolean availability |

FastAPI's interactive API documentation is available at `/docs`.

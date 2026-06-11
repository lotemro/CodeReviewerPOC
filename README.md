# Code Review Platform — POC

POC of automatic code-review platform that accepts a Python file via HTTP, runs a set of LLM-backed rule checks against it asynchronously, and exposes the results through a fetch API.
For POC, everything runs locally.

---

## Prerequisites

- **Python 3.9+**
- **Ollama** — [install instructions](https://ollama.ai/)
- **A model** — e.g. `ollama pull llama3` (any model works; configurable via `LLM_NAME`)
---

## Configuration

All settings are read from `.env` (via `pydantic-settings`).

| Setting | Required | Default | Description |
|---|---|---|---|
| `LLM_PROVIDER` | yes | — | Provider key. Currently supports `ollama`. |
| `LLM_URL` | yes | — | LLM base URL (e.g. `http://localhost:11434` for Ollama). |
| `LLM_NAME` | yes | — | Model name to pass to the provider (e.g. `llama3`). |
| `DB_PATH` | yes | — | SQLite file path (relative or absolute). |
| `MAX_PARALLEL_SCANS` | no | `5` | Per-process concurrency cap. |
| `SCAN_TTL_HOURS` | no | `24` | Hours after which scan rows are auto-deleted. |
| `PROJECT_NAME` | no | `Code Review Platform POC` | FastAPI app title. |

---
## Installation

```bash
git clone <repo-url>
cd CodeReviewerPOC

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Create a `.env` file:
```dotenv
LLM_PROVIDER=ollama
LLM_URL=http://localhost:11434
LLM_NAME=llama3
DB_PATH=code_review.db
```

---


## Running the application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For development (auto-reload):
```bash
uvicorn app.main:app --reload
```

Running via Interactive API docs: <http://localhost:8000/docs>

---

## API reference

### `POST /scans`
Submit a Python file for review.

**Request**
```bash
curl -X POST http://localhost:8000/scans \
  -F "file=@path/to/your_code.py"
```

**Responses**

| Status | When | Body |
|---|---|---|
| `202 Accepted` | New scan accepted | `{"id": "<uuid>", "status": "PENDING"}` |
| `200 OK` | Cache hit — identical file already scanned | `{"id": "<uuid>", "status": "COMPLETED", "results": {...}}` |
| `400 Bad Request` | Filename does not end in `.py` | `{"detail": "Only .py files are supported"}` |
| `503 Service Unavailable` | All 5 slots in use | `{"detail": "Maximum parallel scans reached"}` |

### `GET /scans/{id}`
Fetch the current status / results of a scan.

```bash
curl http://localhost:8000/scans/3b9f1a7c-...   # use the id returned from POST
```

**Response**
```json
{
  "id": "3b9f1a7c-...",
  "status": "COMPLETED",
  "results": {
    "meaningful_variables": true,
    "docstring_logic": false
  }
}
```

| Status | When | Body |
|---|---|---|
| `200 OK` | Scan found | See above; `results` is `null` until `COMPLETED`; `error_message` populated when `FAILED`. |
| `404 Not Found` | Unknown id | `{"detail": "Scan not found"}` |

`status` is one of: `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`.

---
## Testing

```bash
pytest
```

The test suite includes unit tests (repository, engine, orchestrator, LLM client, config) and an integration test (`tests/test_flow.py`).

**The tests do not require Ollama to be running**.

In addition, the `scripts/` directory contains end-to-end utilities that exercise a running server.

| Script | Purpose                                                         |
|---|-----------------------------------------------------------------|
| `scripts/parallelism_test.py` | Sends 10 concurrent submissions; expects 5 × `202` + 5 × `503`. |
| `scripts/bulk_runner.py` | Submits files in batches of 5.                                  |

Start the server first, then:
```bash
python scripts/parallelism_test.py
```
```bash
python scripts/bulk_runner.py
```

---

## Project layout

```
app/
├── api/             # FastAPI routes
├── core/            # Settings 
├── db/              # aiosqlite connection, models, repository
├── llm/             # BaseLLMClient + OllamaClient + factory
├── orchestration/   # Concurrency controller, lifecycle, ScanOrchestrator
├── reviewer/        # RULES, prompts, ReviewerEngine
└── main.py          # FastAPI app + lifespan (init_db, recovery, cleanup loop)
tests/               
```
---


## AI usage & prompts
The full prompt/conversation log accompanying this submission is included in the submission email (delivered alongside the repository link in the submission email).

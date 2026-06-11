# Code Review Platform POC

An automatic code review platform that accepts Python files via API, analyzes them using a local LLM (Ollama), and returns results asynchronously.

## Features
- **Async Processing**: Request a scan and fetch results later.
- **Local LLM**: Uses Ollama (Llama 3 by default) for code analysis.
- **Concurrency Control**: Strictly supports up to 5 parallel scans.
- **Result Caching**: Reuses results for identical files to optimize performance.
- **Data Retention**: Scan results are automatically deleted after 24 hours.
- **Startup Recovery**: Automatically marks interrupted scans as failed on restart.

## Architecture
The project is built with **FastAPI** and **aiosqlite**. It follows a modular design:
- `app/api`: HTTP routes and request handling.
- `app/db`: Async database layer and repository.
- `app/llm`: Provider-agnostic LLM client abstraction.
- `app/reviewer`: Rule-based analysis engine.
- `app/orchestration`: Business logic, concurrency, and lifecycle management.

## Prerequisites
1. **Python 3.9+**
2. **Ollama**: [Download and install Ollama](https://ollama.ai/).
3. **Llama 3 Model**: Run `ollama pull llama3`.

## Installation
1. Clone the repository and navigate to the project root.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file (optional, see `.env.example`):
   ```bash
   OLLAMA_URL="http://localhost:11434"
   OLLAMA_MODEL="llama3"
   ```

## Running the Application
Start the FastAPI server:
```bash
python -m app.main
```
The server will run at `http://localhost:8000`.

## API Usage Examples

### 1. Request a Scan
Upload a Python file for review:
```bash
curl -X POST http://localhost:8000/scans \
  -F "file=@path/to/your_code.py"
```
**Response (New Scan):** `202 Accepted`
```json
{"id": "uuid-string", "status": "PENDING"}
```
**Response (Cache Hit):** `200 OK` (Immediate results)

### 2. Fetch Scan Results
Retrieve results using the `id` from the previous step:
```bash
curl http://localhost:8000/scans/{id}
```
**Response:**
```json
{
  "id": "uuid-string",
  "status": "COMPLETED",
  "results": {
    "meaningful_variables": true,
    "docstring_logic": false
  }
}
```

## Running Tests
Run the full test suite (unit and integration tests):
```bash
export PYTHONPATH=$PYTHONPATH:.
pytest
```

# AppForge — AI App Compiler

> Natural language → structured config → validated → executable application schema

## Architecture Overview

AppForge is a **multi-stage LLM pipeline** that behaves like a compiler for software generation. It takes a natural language description and produces a complete, validated, cross-consistent JSON configuration for an application.

```
User Prompt
    │
    ▼
┌─────────────────────────────┐
│  Stage 1: Intent Extraction │  Parse user intent into structured intermediate form
└─────────────────┬───────────┘
                  │
                  ▼
┌─────────────────────────────┐
│  Stage 2: System Design     │  Entities, flows, roles, pages
└─────────────────┬───────────┘
                  │
                  ▼
┌─────────────────────────────┐
│  Stage 3: Schema Generation │  DB + API + UI + Auth schemas
└─────────────────┬───────────┘
                  │
                  ▼
┌─────────────────────────────┐
│  Stage 4: Refinement        │  Cross-layer consistency resolution
└─────────────────┬───────────┘
                  │
                  ▼
┌─────────────────────────────┐
│  Validation + Repair Engine │  Detect issues → auto-repair → report
└─────────────────────────────┘
```

## Why Multi-Stage?

A single prompt approach fails because:
- LLMs hallucinate fields when generating 4 schemas at once
- No isolation means errors in one schema corrupt others
- Impossible to repair specific layers without full retry
- No intermediate artifacts for debugging

Our compiler approach:
- Each stage has a **strict contract** (input schema → output schema)
- JSON validation + **targeted repair** (not blind retry)
- Each stage output is an artifact that can be independently inspected
- Refinement stage is a dedicated cross-layer consistency pass

## Key Components

### `pipeline.py` — Core Pipeline
- 4-stage generation with Claude claude-sonnet-4
- `_parse_and_repair()`: tries JSON parse → if fail, asks LLM to fix the specific JSON error
- `_validate_consistency()`: checks role references, routes, foreign keys

### `evaluator.py` — Evaluation Framework
- 10 real product prompts + 10 edge cases (vague, conflicting, incomplete)
- Tracks: success rate, retries per request, failure types, latency
- Returns structured metrics JSON

## Output Schema

```json
{
  "db_schema": { "tables": [...] },
  "api_schema": { "endpoints": [...] },
  "ui_schema": { "pages": [...] },
  "auth_schema": { "roles": [...], "strategy": "..." },
  "refinement_notes": ["issues found and fixed"]
}
```

## Setup & Run

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (React + Vite)

```bash
cd frontend
npm install
# Set backend URL:
echo "VITE_BACKEND_URL=http://localhost:8000" > .env
npm run dev
```

## Deployment

### Backend → Railway
1. Push to GitHub
2. New project on railway.app → Deploy from GitHub
3. Select `/backend` folder
4. Railway auto-detects Python via `railway.toml`

### Frontend → Vercel
1. Push to GitHub
2. New project on vercel.com → Import repo
3. Set root directory to `frontend`
4. Add env var: `VITE_BACKEND_URL=https://your-railway-url.railway.app`
5. Deploy

## Failure Handling

| Input Type | Behavior |
|------------|----------|
| Vague prompt | Documents assumptions, proceeds with reasonable defaults |
| Conflicting requirements | Flags in `refinement_notes`, resolves with documented decision |
| Invalid JSON from LLM | Targeted repair via `_parse_and_repair()` |
| Missing fields | Refinement stage fills gaps |
| Schema mismatch | Refinement resolves cross-layer inconsistencies |

## Cost vs Quality Tradeoffs

| Mode | Approach | Latency | Cost | Quality |
|------|----------|---------|------|---------|
| Standard | 4 stages, claude-sonnet-4 | ~15-25s | ~$0.05/req | High |
| Fast | Merge stages 2+3, claude-haiku | ~8-12s | ~$0.01/req | Medium |
| High quality | Add stage 5: test generation | ~35s | ~$0.12/req | Highest |

We chose Standard mode as the default — optimal balance for demo purposes.

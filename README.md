# AI Claims Adjuster (HackMIT MVP)

## What it is
An AI-native claims processing pipeline that ingests messy claims (PDFs, emails, images), cleans & reconciles data, applies a transparent rulebook ("constitution") to decide Approve/Deny/Review, and outputs structured reports with rationales & confidence.

## Why it wins
- **Rox (messy/real-world)**: Built to handle OCR noise, contradictory fields, and incomplete data.
- **EigenCloud (judge)**: Includes a clearly defined rulebook + LLM judge that cites violated rules.
- **Windsurf**: Agents split into ingest / clean / judge / report — demonstrable in Windsurf IDE.
- **Tandemn**: LLM calls routed through `llm_client.call_llm()` — swap endpoint & key to use Tandemn.
- **YC-framing**: Reimagines underwriting + triage with agents & AI-first flow.

## Run locally (quick)
1. Copy `.env.example` → `.env`, add TANDEM_API_URL & TANDEM_API_KEY.
2. Backend:

```bash
cd backend
pip install -r requirements.txt
./start.sh
```

3. Frontend:

```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py
```

4. Upload `samples/claim_example.txt` in the Streamlit UI to demo.

## Architecture

### Agent Pipeline
1. **Ingest Agent** (`windsurf_agents/ingest_agent.py`) - PDF/text extraction with OCR fallback
2. **Clean Agent** (`windsurf_agents/clean_agent.py`) - Data normalization and conflict resolution
3. **Judge Agent** (`windsurf_agents/judge_agent.py`) - Rule-based + LLM decision making
4. **Report Agent** (`windsurf_agents/report_agent.py`) - Structured report generation

### Backend Components
- **FastAPI Server** (`backend/app/main.py`) - REST API endpoint
- **OCR Module** (`backend/app/ocr.py`) - PDF text extraction with pytesseract fallback
- **Parser** (`backend/app/parser.py`) - Regex + LLM field extraction
- **Cleaner** (`backend/app/cleaner.py`) - Data normalization and deduplication
- **Judge** (`backend/app/judge.py`) - AI judge with constitutional rulebook
- **Reporter** (`backend/app/reporter.py`) - Markdown and JSON report generation
- **LLM Client** (`backend/app/llm_client.py`) - Generic Tandemn API wrapper

## Sponsor Integration

### Rox ($15k) - Messy Data Handling
- Handles OCR noise and extraction errors
- Resolves contradictory information across multiple sources
- Robust to incomplete or malformed input data
- Fuzzy matching and conflict detection

### EigenCloud ($3k) - AI Judge Constitution
- Transparent rulebook system with clear policy definitions
- LLM judge that cites specific rule violations
- Confidence scoring and rationale generation
- Deterministic policy validation combined with AI reasoning

### Windsurf ($5k) - Agent Architecture
- Modular agent system built for Windsurf IDE
- Clear separation of concerns: Ingest → Clean → Judge → Report
- Demonstrable agent orchestration and data flow
- Easy to extend with additional agents

### Tandemn ($1k) - LLM Inference
- Generic LLM client supporting Tandemn API
- Configurable endpoint and authentication
- Optimized prompts for extraction and decision making
- Cost-effective inference with temperature=0.0 for consistency

### YC - Modern AI-First Insurance
- Reimagines traditional claims processing with AI agents
- Scalable architecture for enterprise deployment
- Transparent decision making with audit trails
- Modern tech stack: FastAPI, Streamlit, Python

## Demo Flow
1. Upload messy claim document (PDF or text)
2. View raw extracted text showing OCR imperfections
3. See cleaned JSON with resolved conflicts
4. Review AI judge decision with rule citations
5. Download structured markdown report
6. Show Windsurf agent orchestration

## Submission checklist
- ✅ Deploy link or steps to run locally
- ✅ Loom 1–2 min: show upload → raw extraction → cleaned JSON → judge decision → final report, and explain how it handles messy inputs.
- ✅ Github: include README, sample claims, `.env.example`, and a `demo.md` with sponsor framing.

## Next Steps
- Add fraud detection clustering
- Implement audit trail with cryptographic verification
- Scale to batch processing
- Add human-in-the-loop correction interface

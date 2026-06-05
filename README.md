# AI-powered Software Builder — AI Application Compiler

AI-powered Software Builder is a compiler-like AI software generation system that transforms unstructured natural language requirements into fully validated, executable software configurations. 

Rather than relying on single-shot LLM prompts (which frequently yield invalid JSON, missing API routes, database mismatches, or broken permission models), the system compiles applications through a modular, multi-stage pipeline, enforcing strict contracts, semantic cross-layer validation, auto-healing repair loops, and execution simulation.

---

## 🚀 Key Features
1. **Multi-Stage Pipeline (Compiler Design)**: Breaks generation into Intent Extraction, Intermediate Graph (AST) construction, Architecture Planning, and Schema Generation.
2. **Strict Schema Contracts**: Enforces strict Pydantic structures for UI layouts, REST APIs, SQL tables, RBAC rules, and business logic.
3. **Validation Mesh (Stage 5)**: Programmatically verifies cross-layer integrity (e.g. check that UI components match registered APIs, API request schemas match database column structures, and endpoints match authentication roles).
4. **Intelligent Repair Engine (Stage 6)**: Automatically self-heals mismatches (e.g. auto-inserts missing primary keys, injects missing DB fields requested by APIs, creates API routes for UI buttons, and registers undefined roles).
5. **Execution Simulator (Stage 7)**: Compiles schemas onto an in-memory SQLite database, runs schema structures, and checks RBAC endpoints to verify execution readiness.
6. **Dynamic Live Runtime Engine**: Mounts dynamic CRUD routers on FastAPI that communicate with a live SQLite backend. The frontend parses the UI schema dynamically to render page routes, forms, and data tables—permitting full, interactive application testing immediately.

---

## 📐 End-to-End Architecture

```
                  User Prompt (NL)
                         │
                         ▼
        ┌──────────────────────────────────┐
        │ Stage 1: Intent Extraction Layer │
        └────────────────┬─────────────────┘
                         │ Intent JSON (Pydantic)
                         ▼
        ┌──────────────────────────────────┐
        │ Stage 2: Intent Graph Builder    │
        └────────────────┬─────────────────┘
                         │ AST Dependency Graph
                         ▼
        ┌──────────────────────────────────┐
        │ Stage 3: Architecture Planner    │
        └────────────────┬─────────────────┘
                         │ Modules & Access Matrix
                         ▼
        ┌──────────────────────────────────┐
        │ Stage 4: Schema Generator        │
        └────────────────┬─────────────────┘
                         │ UI, API, DB, Auth Schemas
                         ▼
        ┌──────────────────────────────────┐
        │ Stage 5: Validation Mesh         │◄─────────────────┐
        └────────────────┬─────────────────┘                  │
                         │                                    │ Re-run
                    Has Errors?                               │ Validation
                   ┌─────┴─────┐                              │
                  Yes         No                              │
                   │           │                              │
                   ▼           ▼                              │
        ┌──────────────────────────┐                          │
        │ Stage 6: Repair Engine   ├──────────────────────────┘
        └──────────────────────────┘ (Rule-Based Auto-Heal)
                         │
                  Validation PASS
                         │
                         ▼
        ┌──────────────────────────────────┐
        │ Stage 7: Execution Simulator     │ (In-memory SQLite Compilation)
        └────────────────┬─────────────────┘
                         │
                    Simulation PASS
                         │
                         ▼
        ┌──────────────────────────────────┐
        │ Dynamic Runtime Engine           │◄─────────────────┐
        │ - SQLite Local File Database     │                  │ Reads schemas &
        │ - Dynamic CRUD API Endpoints     │                  │ renders interfaces
        └────────────────┬─────────────────┘                  │
                         │                                    │
                         ▼                                    │
        ┌──────────────────────────────────┐                  │
        │ Interactive Sandbox Frontend    ├──────────────────┘
        └──────────────────────────────────┘ (Real data mutations & role shifts)
```

---

## 📁 Repository Structure
```
AI_software_builder/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI server connecting pipeline, runtime, and evaluator
│   │   ├── config.py            # API credentials & database settings
│   │   ├── pipeline/            # Multi-stage compiler logic
│   │   │   ├── __init__.py
│   │   │   ├── models.py        # Pydantic schemas (contracts)
│   │   │   ├── stage1_intent.py # Intent extraction (Stage 1)
│   │   │   ├── stage2_graph.py  # AST graph representation (Stage 2)
│   │   │   ├── stage3_design.py # System architect planner (Stage 3)
│   │   │   ├── stage4_schema.py # UI/API/DB/Auth schemas (Stage 4)
│   │   │   ├── stage5_validate.py# Cross-layer validation mesh (Stage 5)
│   │   │   └── stage6_repair.py # Rule-based self-healing module (Stage 6)
│   │   ├── runtime/             # Execution & simulation sandbox
│   │   │   ├── __init__.py
│   │   │   ├── simulator.py     # SQLite test compiler (Stage 7)
│   │   │   └── engine.py        # SQLite live database dynamic CRUD routes
│   └── requirements.txt         # Backend Python packages
├── frontend/
│   ├── index.html               # Main dashboard viewport
│   ├── styles.css               # Theme styling (dark glassmorphism, responsive CLI)
│   └── app.js                   # Navigation tab controller & sandbox layout renderer
├── verify_pipeline.py           # Local pipeline validation script
├── .env.example                 # Configuration template
├── requirements.txt             # Root level shortcut dependency file
└── README.md                    # System documentation
```

---

## 🛠️ Setup and Installation

### 1. Prerequisites
- **Python**: version `3.10` or higher
- **NodeJS/npm**: version `18` or higher (optional, frontend is static HTML/JS served by FastAPI)

### 2. Installation
Clone the repository and install backend python dependencies:
```bash
# Clone the repository
git clone https://github.com/Dharunika-07-N/AI_software_builder.git
cd AI_software_builder

# Install packages
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Open `.env` and fill in your LLM API Keys if you want to bypass the Mock Mode:
```env
OPENAI_API_KEY=your-openai-api-key
GEMINI_API_KEY=your-gemini-api-key
MOCK_MODE=false
```
*Note: If no API keys are provided or `MOCK_MODE=true` is set, the system compiles in a deterministic mock mode using highly detailed application templates. This enables instant local verification and zero API billing for local testing.*

---

## 💻 Running the Application

### 1. Run Pipeline Verification Tests
Before launching the server, verify that all compiler pipeline stages run successfully:
```bash
python verify_pipeline.py
```
This executes the compiler stages (Stage 1-7) against a CRM specification prompt and outputs the intermediate graph nodes, schemas, validation meshes, and SQLite simulation report logs.

### 2. Launch Local Dev Server
Start the FastAPI server:
```bash
python -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Open Web Client
Navigate to:
```
http://localhost:8000
```
This serves the custom, glass-themed web interface:
- **Compiler CLI Tab**: Input natural language prompt and click **Compile App** to trace the compilation pipeline stages, see logs, and view the AST graph.
- **AST & Schemas Tab**: Inspect the JSON schemas generated for the UI, API endpoints, SQL DB, and RBAC auth.
- **Validation Mesh Tab**: View compilation validation reports and repair engine healing actions.
- **Live Sandbox Tab**: Test the compiled application dynamically! Fill in forms to insert data, fetch tables, change access roles (e.g. Admin, SalesManager, User) and verify permission barriers on live SQLite records.

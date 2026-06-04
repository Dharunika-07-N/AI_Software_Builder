import os
import time
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings

# Import pipeline stages
from app.pipeline.stage1_intent import extract_intent
from app.pipeline.stage2_graph import build_intent_graph
from app.pipeline.stage3_design import plan_architecture
from app.pipeline.stage4_schema import generate_schemas
from app.pipeline.stage5_validate import validate_schema
from app.pipeline.stage6_repair import repair_schema

# Import runtime engine & simulator
from app.runtime.simulator import simulate_execution
from app.runtime.engine import router as runtime_router, init_runtime_db

# Import evaluation framework
from app.evaluation.evaluator import run_evaluation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ForgeAI.Server")

app = FastAPI(
    title="Forge AI Application Compiler API",
    description="Compiler-like AI system converting natural language to executable application schemas.",
    version="1.0.0"
)

# CORS middleware for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the dynamic live runtime CRUD router
app.include_router(runtime_router)

@app.post("/api/generate")
async def generate_application(payload: Dict[str, str] = Body(...)):
    """Triggers the full multi-stage compiler pipeline, runs simulation,
    and initializes the live database engine for the generated application.
    """
    prompt = payload.get("prompt")
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required.")
        
    start_time = time.time()
    
    try:
        # Stage 1: Intent Extraction
        intent = extract_intent(prompt)
        
        # Stage 2: Intent Graph IR
        graph = build_intent_graph(intent)
        
        # Stage 3: Architecture Planner
        design = plan_architecture(intent, graph)
        
        # Stage 4: Schema Generator
        raw_schema = generate_schemas(design, intent.application_name)
        
        # Stage 5: Validation Mesh (Initial check)
        initial_validation = validate_schema(raw_schema)
        
        # Stage 6: Repair Engine (Auto-healing)
        final_schema = raw_schema
        repair_logs = []
        repair_success = True
        
        if not initial_validation.is_valid:
            repair_res = repair_schema(raw_schema, initial_validation)
            final_schema = repair_res.repaired_schema
            repair_logs = repair_res.logs
            repair_success = repair_res.success
            
        # Re-validate the final schema
        final_validation = validate_schema(final_schema)
        
        # Stage 7: Execution Simulator
        simulator_report = simulate_execution(final_schema)
        
        # If execution simulation passes, initialize the live SQLite runtime database
        db_initialized = False
        if simulator_report["status"] == "PASS":
            db_initialized = init_runtime_db(final_schema.db)
            
        elapsed_time = time.time() - start_time
        
        return {
            "status": "SUCCESS" if (final_validation.is_valid and simulator_report["status"] == "PASS") else "FAILED",
            "latency_sec": round(elapsed_time, 2),
            "intent": intent,
            "graph": graph,
            "design": design,
            "schema": final_schema,
            "validation_initial": initial_validation,
            "repair_logs": repair_logs,
            "repair_success": repair_success,
            "validation_final": final_validation,
            "simulator_report": simulator_report,
            "live_runtime_active": db_initialized
        }
        
    except Exception as e:
        logger.error("Pipeline compilation crashed:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Compiler internal error: {str(e)}")

@app.post("/api/evaluate")
async def trigger_evaluation():
    """Runs the 20-prompt evaluation dataset through the pipeline and returns aggregated metrics."""
    try:
        report = run_evaluation()
        return report
    except Exception as e:
        logger.error("Evaluation framework crashed:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Evaluator internal error: {str(e)}")

# Mount frontend client. Check if frontend folder exists.
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend"))
if os.path.exists(frontend_dir):
    logger.info(f"Mounting static frontend client from: {frontend_dir}")
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    logger.warning(f"Frontend folder not found at {frontend_dir}. Static web interface not mounted.")

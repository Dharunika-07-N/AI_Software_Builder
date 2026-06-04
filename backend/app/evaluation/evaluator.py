import time
import json
import logging
from typing import Dict, Any, List
from app.evaluation.dataset import EVALUATION_DATASET

# Import pipeline stages
from app.pipeline.stage1_intent import extract_intent
from app.pipeline.stage2_graph import build_intent_graph
from app.pipeline.stage3_design import plan_architecture
from app.pipeline.stage4_schema import generate_schemas
from app.pipeline.stage5_validate import validate_schema
from app.pipeline.stage6_repair import repair_schema
from app.runtime.simulator import simulate_execution

logger = logging.getLogger("AIBuilder.Evaluator")

def run_evaluation() -> Dict[str, Any]:
    """Runs the 20-prompt evaluation dataset through the AI-powered Software Builder compiler pipeline.
    Measures and aggregates performance metrics.
    """
    logger.info("Starting Evaluation Framework run...")
    results = []
    
    total_prompts = 0
    total_successes = 0
    total_validation_passes = 0
    total_repairs_needed = 0
    total_repairs_succeeded = 0
    total_latency = 0.0
    
    categories = ["standard_prompts", "edge_cases"]
    
    for category in categories:
        for item in EVALUATION_DATASET[category]:
            prompt_id = item["id"]
            name = item["name"]
            prompt_text = item["prompt"]
            
            logger.info(f"Evaluating {category} '{name}' ({prompt_id})...")
            start_time = time.time()
            
            pipeline_success = False
            validation_passed_initially = False
            repair_needed = False
            repair_succeeded = False
            repair_attempts = 0
            failure_reason = ""
            repaired_schema = None
            sim_report = None
            
            try:
                # Stage 1: Intent Extraction
                intent = extract_intent(prompt_text)
                
                # Stage 2: Intent Graph
                graph = build_intent_graph(intent)
                
                # Stage 3: Architecture Planner
                arch = plan_architecture(intent, graph)
                
                # Stage 4: Schema Generator
                raw_schema = generate_schemas(arch, intent.application_name)
                
                # Stage 5: Validation Mesh
                val_result = validate_schema(raw_schema)
                
                if val_result.is_valid:
                    validation_passed_initially = True
                    pipeline_success = True
                    repaired_schema = raw_schema
                else:
                    # Stage 6: Repair Engine
                    repair_needed = True
                    repair_attempts = 1
                    rep_res = repair_schema(raw_schema, val_result)
                    
                    if rep_res.success:
                        repair_succeeded = True
                        pipeline_success = True
                        repaired_schema = rep_res.repaired_schema
                    else:
                        failure_reason = f"Repair failed. Validation errors: {[e.message for e in val_result.errors]}"
                
                # Stage 7: Simulator Check
                if pipeline_success and repaired_schema:
                    sim_report = simulate_execution(repaired_schema)
                    if sim_report["status"] != "PASS":
                        pipeline_success = False
                        failure_reason = f"Execution Simulation failed: {sim_report.get('database_creation')}"
                        
            except Exception as e:
                logger.error(f"Pipeline crashed for prompt '{name}': {str(e)}", exc_info=True)
                failure_reason = f"Pipeline exception: {str(e)}"
                
            latency = time.time() - start_time
            total_latency += latency
            total_prompts += 1
            
            if pipeline_success:
                total_successes += 1
            if validation_passed_initially:
                total_validation_passes += 1
            if repair_needed:
                total_repairs_needed += 1
                if repair_succeeded:
                    total_repairs_succeeded += 1
                    
            results.append({
                "id": prompt_id,
                "name": name,
                "category": category,
                "prompt": prompt_text,
                "success": pipeline_success,
                "validation_passed_initially": validation_passed_initially,
                "repair_needed": repair_needed,
                "repair_succeeded": repair_succeeded,
                "repair_attempts": repair_attempts,
                "latency_sec": round(latency, 2),
                "failure_reason": failure_reason,
                "simulation_status": sim_report["status"] if sim_report else "N/A"
            })
            
    # Calculate aggregate metrics
    success_rate = (total_successes / total_prompts) * 100 if total_prompts > 0 else 0
    val_pass_rate = (total_validation_passes / total_prompts) * 100 if total_prompts > 0 else 0
    repair_success_rate = (total_repairs_succeeded / total_repairs_needed) * 100 if total_repairs_needed > 0 else 0
    avg_latency = total_latency / total_prompts if total_prompts > 0 else 0
    
    report = {
        "timestamp": time.time(),
        "summary": {
            "total_prompts": total_prompts,
            "success_rate_pct": round(success_rate, 2),
            "validation_pass_rate_pct": round(val_pass_rate, 2),
            "repair_success_rate_pct": round(repair_success_rate, 2),
            "average_latency_sec": round(avg_latency, 2),
            "total_repair_attempts": total_repairs_needed,
            "total_repairs_succeeded": total_repairs_succeeded
        },
        "details": results
    }
    
    # Save the report as an artifact JSON
    try:
        with open("evaluation_report.json", "w") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to write evaluation_report.json: {e}")
        
    return report

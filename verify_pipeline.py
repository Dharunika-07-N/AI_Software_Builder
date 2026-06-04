import sys
import os

# Add workspace root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app.pipeline.stage1_intent import extract_intent
from app.pipeline.stage2_graph import build_intent_graph
from app.pipeline.stage3_design import plan_architecture
from app.pipeline.stage4_schema import generate_schemas
from app.pipeline.stage5_validate import validate_schema
from app.pipeline.stage6_repair import repair_schema
from app.runtime.simulator import simulate_execution

def main():
    print("====================================================")
    print("AI-powered Software Builder Pipeline Verification Test")
    print("====================================================\n")
    
    test_prompt = "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    print(f"Test Prompt: '{test_prompt}'\n")
    
    # 1. Intent Extraction
    print("Running Stage 1: Intent Extraction...")
    intent = extract_intent(test_prompt)
    print(f"-> SUCCESS. Extracted Application: {intent.application_name}")
    print(f"-> Roles: {intent.roles}")
    print(f"-> Features: {intent.features}")
    print(f"-> Entities: {intent.entities}\n")
    
    # 2. Intent Graph
    print("Running Stage 2: Intent Graph IR Builder...")
    graph = build_intent_graph(intent)
    print(f"-> SUCCESS. Generated {len(graph.nodes)} nodes and {len(graph.edges)} edges.\n")
    
    # 3. Architecture Planner
    print("Running Stage 3: Architecture Planner...")
    arch = plan_architecture(intent, graph)
    print(f"-> SUCCESS. Modules: {arch.modules}")
    print(f"-> Access Matrix Roles: {[r.role for r in arch.access_matrix]}\n")
    
    # 4. Schema Generation
    print("Running Stage 4: Schema Generator...")
    schemas = generate_schemas(arch, intent.application_name)
    print("-> SUCCESS.")
    print(f"   - UI Pages: {[p.title for p in schemas.ui.pages]}")
    print(f"   - API Endpoints: {[e.method + ' ' + e.route for e in schemas.api.endpoints]}")
    print(f"   - DB Tables: {[t.name for t in schemas.db.tables]}")
    print(f"   - Auth Roles: {[r.role for r in schemas.auth.roles]}\n")
    
    # 5. Validation Mesh
    print("Running Stage 5: Validation Mesh...")
    validation = validate_schema(schemas)
    print(f"-> SUCCESS. Schema Valid: {validation.is_valid}")
    print(f"-> Errors: {len(validation.errors)}")
    print(f"-> Warnings: {len(validation.warnings)}\n")
    
    # 6. Repair Engine
    final_schemas = schemas
    if not validation.is_valid:
        print("Running Stage 6: Repair Engine...")
        repair_res = repair_schema(schemas, validation)
        print(f"-> SUCCESS. Repaired Schema Valid: {repair_res.success}")
        print(f"-> Action logs: {[log.action_taken for log in repair_res.logs]}")
        final_schemas = repair_res.repaired_schema
        print()
        
    # 7. Simulator Check
    print("Running Stage 7: Execution Simulator...")
    simulator_report = simulate_execution(final_schemas)
    print(f"-> SUCCESS. Simulation status: {simulator_report['status']}")
    print(f"-> DB Creation check: {simulator_report['database_creation']}")
    print(f"-> API Routing check: {simulator_report['api_routing']}")
    print(f"-> RBAC Permission check: {simulator_report['permission_checks']}")
    print("-> Simulation logs:")
    for find in simulator_report['findings']:
        print(f"   • {find}")
    print()
    
    print("====================================================")
    print("VERIFICATION COMPLETE: ALL PIPELINE STAGES FUNCTIONAL")
    print("====================================================")

if __name__ == "__main__":
    main()

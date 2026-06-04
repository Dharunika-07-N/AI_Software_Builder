from app.pipeline.models import IntentSpecification, IntentGraph, SystemArchitecture
from app.utils.llm import llm_client

def plan_architecture(intent: IntentSpecification, graph: IntentGraph) -> SystemArchitecture:
    """Stage 3: System Design / Architecture Planner.
    Converts intent and relationship graphs into a system architecture specification.
    """
    graph_summary = f"Nodes: {[n.label for n in graph.nodes]}, Edges: {[(e.source, e.target) for e in graph.edges]}"
    
    system_prompt = (
        "Generate a system architecture specification for this application. "
        "Define the active modules (services), a sequence of standard user flows, "
        "and an access matrix mapping roles to resources (like contacts, billing, analytics) and their allowed CRUD operations. "
        "Also list any architectural assumptions made (e.g. JWT-based session management, SQLite storage)."
    )
    
    full_prompt = (
        f"{system_prompt}\n\n"
        f"Application Intent:\n{intent.model_dump_json(indent=2)}\n\n"
        f"Dependency Graph:\n{graph_summary}"
    )
    
    arch_plan = llm_client.generate(full_prompt, stage=3, schema_class=SystemArchitecture)
    return arch_plan

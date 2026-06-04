from app.pipeline.models import SystemArchitecture, ApplicationSchema
from app.utils.llm import llm_client

def generate_schemas(arch: SystemArchitecture, app_name: str) -> ApplicationSchema:
    """Stage 4: Schema Generation Layer.
    Translates the architectural design into concrete schemas for UI, API, DB, and Auth.
    """
    system_prompt = (
        "Generate concrete technical specifications for the application.\n"
        "You must generate:\n"
        "1. UI Schema: Pages, layouts, and components (buttons, tables, forms, charts).\n"
        "2. API Schema: Endpoint routes, HTTP methods, body and query parameter types, and response models.\n"
        "3. Database Schema: Tables, column names, column SQLite types, primary keys, and foreign keys.\n"
        "4. Auth Schema: Role names and their respective permission scopes.\n"
        "5. Business Rules: Dynamic conditions gating endpoints (e.g. premium limits or restrictions).\n\n"
        "CRITICAL: Ensure strict consistency across all layers. For example:\n"
        "- If a UI component calls an API endpoint, that endpoint MUST exist in the API Schema.\n"
        "- If an API endpoint reads or writes fields, those fields and tables MUST exist in the DB Schema.\n"
        "- Every foreign key reference must link to a valid table and column."
    )
    
    full_prompt = (
        f"{system_prompt}\n\n"
        f"Application: {app_name}\n"
        f"Architecture Specification:\n{arch.model_dump_json(indent=2)}"
    )
    
    app_schema = llm_client.generate(full_prompt, stage=4, schema_class=ApplicationSchema)
    return app_schema

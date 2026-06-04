from app.pipeline.models import IntentSpecification
from app.utils.llm import llm_client

def extract_intent(prompt: str) -> IntentSpecification:
    """Stage 1: Intent Extraction Layer.
    Converts raw natural language prompt into a structured intent specification.
    """
    system_prompt = (
        "Extract intent from this user software requirements prompt. "
        "Identify the application name, roles, features, business entities, "
        "and key business rules or constraints. "
        "Also list any ambiguities, conflicts, or missing specifications in the warnings field."
    )
    full_prompt = f"{system_prompt}\n\nUser Request: {prompt}"
    
    # Generate structured output using the LLM client
    intent_spec = llm_client.generate(full_prompt, stage=1, schema_class=IntentSpecification)
    return intent_spec

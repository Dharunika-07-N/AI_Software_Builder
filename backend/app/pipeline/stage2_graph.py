from app.pipeline.models import IntentSpecification, IntentGraph, IntentGraphNode, IntentGraphEdge

def build_intent_graph(intent: IntentSpecification) -> IntentGraph:
    """Stage 2: Intent Graph Builder.
    Converts intent specifications into a dependency and relationship graph.
    """
    nodes = []
    edges = []
    
    app_id = "app_root"
    # Root app node
    nodes.append(IntentGraphNode(id=app_id, type="application", label=intent.application_name))
    
    # Roles nodes
    for role in intent.roles:
        role_id = f"role_{role.lower()}"
        nodes.append(IntentGraphNode(id=role_id, type="role", label=role))
        edges.append(IntentGraphEdge(source=role_id, target=app_id, type="accesses"))
        
    # Features nodes
    feature_ids = {}
    for feature in intent.features:
        feat_id = f"feat_{feature.lower().replace(' ', '_')}"
        feature_ids[feature.lower()] = feat_id
        nodes.append(IntentGraphNode(id=feat_id, type="feature", label=feature))
        edges.append(IntentGraphEdge(source=feat_id, target=app_id, type="part_of"))
        
    # Entities nodes
    entity_ids = {}
    for entity in intent.entities:
        ent_id = f"ent_{entity.lower().replace(' ', '_')}"
        entity_ids[entity.lower()] = ent_id
        nodes.append(IntentGraphNode(id=ent_id, type="entity", label=entity))
        
        # Link entity to root app
        edges.append(IntentGraphEdge(source=ent_id, target=app_id, type="belongs_to"))
        
    # Heuristically link roles and features to entities
    for role in intent.roles:
        role_id = f"role_{role.lower()}"
        for entity in intent.entities:
            ent_id = f"ent_{entity.lower().replace(' ', '_')}"
            # Check if role interacts with entity (mock mapping)
            edges.append(IntentGraphEdge(source=role_id, target=ent_id, type="manages" if role.lower() == "admin" else "uses"))
            
    # Establish dependencies between features
    # E.g., Dashboard usually depends on Analytics or Contacts
    if "dashboard" in feature_ids:
        dash_id = feature_ids["dashboard"]
        for feat_name, feat_id in feature_ids.items():
            if feat_name in ["analytics", "contacts", "billing", "payments"] and feat_name != "dashboard":
                edges.append(IntentGraphEdge(source=dash_id, target=feat_id, type="depends_on"))
                
    return IntentGraph(nodes=nodes, edges=edges)

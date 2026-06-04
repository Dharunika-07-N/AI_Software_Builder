from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# --- Stage 1: Intent Extraction ---
class IntentSpecification(BaseModel):
    application_name: str = Field(..., description="Name of the application, e.g. CRM")
    roles: List[str] = Field(default_factory=list, description="Roles in the system, e.g. Admin, User")
    features: List[str] = Field(default_factory=list, description="Key features, e.g. Login, Contacts Management")
    entities: List[str] = Field(default_factory=list, description="Core business entities, e.g. Contact, User, Invoice")
    business_rules: List[str] = Field(default_factory=list, description="Raw business constraints, e.g. Admins only can see analytics")
    warnings: List[str] = Field(default_factory=list, description="List of ambiguous or conflicting items extracted")

# --- Stage 2: Intent Graph ---
class IntentGraphNode(BaseModel):
    id: str
    type: str  # e.g., "service", "role", "feature", "entity"
    label: str

class IntentGraphEdge(BaseModel):
    source: str
    target: str
    type: str  # e.g., "depends_on", "manages", "restricts"

class IntentGraph(BaseModel):
    nodes: List[IntentGraphNode] = Field(default_factory=list)
    edges: List[IntentGraphEdge] = Field(default_factory=list)

# --- Stage 3: System Design / Architecture Planner ---
class UserFlowStep(BaseModel):
    step_number: int
    action: str
    description: str

class AccessRule(BaseModel):
    role: str
    resource: str
    actions: List[str]  # e.g., ["create", "read", "update", "delete"]

class SystemArchitecture(BaseModel):
    modules: List[str] = Field(default_factory=list, description="List of functional modules")
    user_flows: List[UserFlowStep] = Field(default_factory=list, description="List of typical user flows")
    access_matrix: List[AccessRule] = Field(default_factory=list, description="Role-based permissions matrix")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made by the system to fill gaps")

# --- Stage 4: Schema Generator ---

# UI Schema
class UIComponent(BaseModel):
    id: str
    type: str  # e.g., "button", "table", "form", "input", "chart", "select"
    label: str
    props: Dict[str, Any] = Field(default_factory=dict, description="HTML attributes, options, or custom properties")

class UIPage(BaseModel):
    route: str
    title: str
    layout: str = "default"  # e.g., "default", "dashboard", "auth"
    components: List[UIComponent] = Field(default_factory=list)

class UISchema(BaseModel):
    pages: List[UIPage] = Field(default_factory=list)
    navigation: List[Dict[str, Any]] = Field(default_factory=list)

# API Schema
class APIParameter(BaseModel):
    name: str
    type: str  # e.g., "string", "integer"
    required: bool = True

class APIResponseSchema(BaseModel):
    status_code: int
    fields: Dict[str, str] = Field(default_factory=dict, description="Response field names and their types")

class APIEndpoint(BaseModel):
    route: str
    method: str  # e.g., "GET", "POST", "PUT", "DELETE"
    description: str = ""
    request_params: List[APIParameter] = Field(default_factory=list)
    request_body: Dict[str, str] = Field(default_factory=dict, description="Request body field names and their types")
    responses: List[APIResponseSchema] = Field(default_factory=list)
    allowed_roles: List[str] = Field(default_factory=list, description="Roles permitted to call this endpoint")

class APISchema(BaseModel):
    endpoints: List[APIEndpoint] = Field(default_factory=list)

# Database Schema
class DBColumn(BaseModel):
    name: str
    type: str  # e.g., "INTEGER", "TEXT", "TIMESTAMP", "BOOLEAN"
    is_primary: bool = False
    is_nullable: bool = True
    references: Optional[str] = None  # e.g., "users.id"

class DBTable(BaseModel):
    name: str
    columns: List[DBColumn] = Field(default_factory=list)

class DBSchema(BaseModel):
    tables: List[DBTable] = Field(default_factory=list)

# Auth Schema
class AuthRule(BaseModel):
    role: str
    permissions: List[str] = Field(default_factory=list)

class AuthSchema(BaseModel):
    roles: List[AuthRule] = Field(default_factory=list)
    auth_method: str = "JWT"

# Business Rules Schema
class BusinessRule(BaseModel):
    name: str
    condition: str
    action: str
    affected_endpoints: List[str] = Field(default_factory=list)

# Total Compiled Application Schema
class ApplicationSchema(BaseModel):
    ui: UISchema
    api: APISchema
    db: DBSchema
    auth: AuthSchema
    business_rules: List[BusinessRule] = Field(default_factory=list)

# --- Stage 5: Validation Mesh ---
class ValidationError(BaseModel):
    layer: str  # e.g., "UI", "API", "DB", "AUTH", "CROSS_LAYER"
    severity: str  # e.g., "error", "warning"
    message: str
    code: str  # e.g., "MISSING_FIELD", "TYPE_MISMATCH", "MISSING_ENDPOINT", "UNRESOLVED_ROLE"
    path: str  # e.g., "db.tables[0].columns[1]"

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationError] = Field(default_factory=list)

# --- Stage 6: Repair Engine ---
class RepairLogEntry(BaseModel):
    error_code: str
    layer: str
    description: str
    action_taken: str
    status: str  # e.g., "fixed", "failed"

class RepairResult(BaseModel):
    repaired_schema: ApplicationSchema
    logs: List[RepairLogEntry] = Field(default_factory=list)
    success: bool

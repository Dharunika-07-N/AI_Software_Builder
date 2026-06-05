import re
from app.pipeline.models import ApplicationSchema, ValidationResult, ValidationError


def _normalize_route(route: str) -> str:
    parts = [p for p in route.split("/") if p and p != "api"]
    return parts[0].lower() if parts else ""


def _matches_api_route(expected_method: str, api_route: str, registered_method: str, registered_path: str) -> bool:
    if expected_method != registered_method:
        return False
    if api_route == registered_path:
        return True
    pattern = "^" + re.sub(r"\{[a-zA-Z0-9_]+\}", r"[a-zA-Z0-9_-]+", registered_path) + "$"
    return re.match(pattern, api_route) is not None


def validate_schema(app_schema: ApplicationSchema) -> ValidationResult:
    """Stage 5: Validation Mesh.
    Verifies type safety, structural rules, and cross-layer consistency.
    """
    errors = []
    warnings = []
    
    # 1. Structural Checks (DB layer)
    db_schema = app_schema.db
    tables_dict = {t.name.lower(): t for t in db_schema.tables}
    
    if not db_schema.tables:
        errors.append(ValidationError(
            layer="DB",
            severity="error",
            message="Database schema must contain at least one table.",
            code="EMPTY_DB",
            path="db.tables"
        ))
        
    for table_idx, table in enumerate(db_schema.tables):
        has_primary = any(c.is_primary for c in table.columns)
        if not has_primary:
            # We treat missing primary key as a warning
            warnings.append(ValidationError(
                layer="DB",
                severity="warning",
                message=f"Table '{table.name}' has no primary key defined.",
                code="MISSING_PRIMARY_KEY",
                path=f"db.tables[{table_idx}]"
            ))
            
        # Verify foreign keys reference valid tables and columns
        for col_idx, col in enumerate(table.columns):
            if col.references:
                ref_parts = col.references.split(".")
                if len(ref_parts) != 2:
                    errors.append(ValidationError(
                        layer="DB",
                        severity="error",
                        message=f"Column '{col.name}' has malformed references string: '{col.references}'. Expected 'table.column'.",
                        code="INVALID_REF_FORMAT",
                        path=f"db.tables[{table_idx}].columns[{col_idx}]"
                    ))
                    continue
                    
                ref_table_name, ref_col_name = ref_parts[0].lower(), ref_parts[1].lower()
                if ref_table_name not in tables_dict:
                    errors.append(ValidationError(
                        layer="DB",
                        severity="error",
                        message=f"Column '{col.name}' in table '{table.name}' references non-existent table '{ref_table_name}'.",
                        code="UNRESOLVED_FOREIGN_KEY_TABLE",
                        path=f"db.tables[{table_idx}].columns[{col_idx}]"
                    ))
                else:
                    ref_table = tables_dict[ref_table_name]
                    ref_cols = [c.name.lower() for c in ref_table.columns]
                    if ref_col_name not in ref_cols:
                        errors.append(ValidationError(
                            layer="DB",
                            severity="error",
                            message=f"Column '{col.name}' in table '{table.name}' references non-existent column '{ref_col_name}' in table '{ref_table_name}'.",
                            code="UNRESOLVED_FOREIGN_KEY_COLUMN",
                            path=f"db.tables[{table_idx}].columns[{col_idx}]"
                        ))

    # 2. API Validation
    api_schema = app_schema.api
    api_routes = {}
    api_route_patterns = []
    for ep_idx, ep in enumerate(api_schema.endpoints):
        route_key = f"{ep.method} {ep.route}"
        api_routes[route_key] = ep

        registered_method, registered_path = ep.method, ep.route
        pattern = None
        if "{" in registered_path:
            pattern = re.compile(r"^" + re.sub(r"\{[a-zA-Z0-9_]+\}", r"[a-zA-Z0-9_-]+", registered_path) + r"$")
        api_route_patterns.append((registered_method, registered_path, pattern))
        
        # Verify endpoint references valid database tables in CRUD operations
        # Heuristic: Extract entity name from route e.g. /api/contacts -> contacts
        route_parts = [p for p in ep.route.split("/") if p and p != "api"]
        if route_parts and route_parts[0] not in ["auth", "login", "register", "analytics", "billing"]:
            entity_name = route_parts[0].lower()
            # If the endpoint implies writing or reading a table, verify that table exists
            if entity_name not in tables_dict:
                warnings.append(ValidationError(
                    layer="API",
                    severity="warning",
                    message=f"API route '{ep.route}' references entity '{entity_name}' which is not a table in the database schema.",
                    code="UNRESOLVED_DATABASE_TABLE",
                    path=f"api.endpoints[{ep_idx}]"
                ))
            else:
                # If doing POST / PUT, verify body fields exist in DB table columns
                target_table = tables_dict[entity_name]
                table_cols = {c.name.lower() for c in target_table.columns}
                if ep.method in ["POST", "PUT"]:
                    for body_field in ep.request_body.keys():
                        if body_field.lower() not in table_cols and body_field.lower() not in ["id", "password", "card_number", "confirm_password"]:
                            errors.append(ValidationError(
                                layer="CROSS_LAYER",
                                severity="error",
                                message=f"API request body for '{ep.route}' contains field '{body_field}' which is missing from database table '{target_table.name}'.",
                                code="FIELD_MISMATCH",
                                path=f"api.endpoints[{ep_idx}].request_body"
                            ))

    # 3. UI Schema Validation
    ui_schema = app_schema.ui
    if not ui_schema.pages:
        errors.append(ValidationError(
            layer="UI",
            severity="error",
            message="UI schema must define at least one page.",
            code="EMPTY_UI_PAGES",
            path="ui.pages"
        ))
        
    for page_idx, page in enumerate(ui_schema.pages):
        for comp_idx, comp in enumerate(page.components):
            # Check if component has an api_route and if it exists in API
            api_route = comp.props.get("api_route")
            if api_route:
                expected_method = "POST" if comp.type == "form" else "GET"
                route_found = False
                for registered_method, registered_path, pattern in api_route_patterns:
                    if expected_method != registered_method:
                        continue
                    if api_route == registered_path or (pattern and pattern.match(api_route)):
                        route_found = True
                        break
                if not route_found:
                    errors.append(ValidationError(
                        layer="CROSS_LAYER",
                        severity="error",
                        message=f"UI component '{comp.id}' on page '{page.title}' calls non-existent API endpoint '{expected_method} {api_route}'.",
                        code="UNRESOLVED_API_ENDPOINT",
                        path=f"ui.pages[{page_idx}].components[{comp_idx}].props.api_route"
                    ))

    # 4. Auth Validation
    auth_schema = app_schema.auth
    valid_roles = {r.role.lower() for r in auth_schema.roles}
    
    for ep_idx, ep in enumerate(api_schema.endpoints):
        for role in ep.allowed_roles:
            if role.lower() not in valid_roles:
                errors.append(ValidationError(
                    layer="AUTH",
                    severity="error",
                    message=f"API endpoint '{ep.method} {ep.route}' references role '{role}' which is not defined in the Auth system.",
                    code="UNRESOLVED_ROLE",
                    path=f"api.endpoints[{ep_idx}].allowed_roles"
                ))

    is_valid = len(errors) == 0
    return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

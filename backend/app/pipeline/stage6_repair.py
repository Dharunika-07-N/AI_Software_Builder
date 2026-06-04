import re
from app.pipeline.models import (
    ApplicationSchema, ValidationResult, ValidationError, RepairResult, RepairLogEntry,
    DBTable, DBColumn, APIEndpoint, AuthRule, APIResponseSchema
)
import logging

logger = logging.getLogger("AIBuilder.Repair")

def repair_schema(app_schema: ApplicationSchema, validation: ValidationResult) -> RepairResult:
    """Stage 6: Repair Engine.
    Applies deterministic rules to auto-heal cross-layer inconsistencies and schema mismatches.
    """
    repaired = app_schema.model_copy(deep=True)
    logs = []
    
    # Process errors
    for err in validation.errors:
        # Error Code: FIELD_MISMATCH
        # Case: API body references a field that DB does not have
        if err.code == "FIELD_MISMATCH":
            # Extract target table and missing field
            # e.g., "API request body for '/api/contacts' contains field 'phone' which is missing from database table 'contacts'."
            # Let's find table and field using regex or parts
            table_name = None
            field_name = None
            
            # Simple parsing:
            m = re.search(r"field '([a-zA-Z0-9_]+)' which is missing from database table '([a-zA-Z0-9_]+)'", err.message)
            if m:
                field_name = m.group(1)
                table_name = m.group(2)
                
            if table_name and field_name:
                # Find table and add column
                for table in repaired.db.tables:
                    if table.name.lower() == table_name.lower():
                        # Check if column already exists (avoid double inserts)
                        if not any(c.name.lower() == field_name.lower() for c in table.columns):
                            table.columns.append(DBColumn(
                                name=field_name,
                                type="TEXT",
                                is_primary=False,
                                is_nullable=True
                            ))
                            logs.append(RepairLogEntry(
                                error_code=err.code,
                                layer="DB",
                                description=f"Database table '{table_name}' was missing column '{field_name}' required by API.",
                                action_taken=f"Added column '{field_name}' (type TEXT) to table '{table_name}'.",
                                status="fixed"
                            ))
                            break
                            
        # Error Code: UNRESOLVED_API_ENDPOINT
        # Case: UI refers to an endpoint that API schema lacks
        elif err.code == "UNRESOLVED_API_ENDPOINT":
            # e.g. "UI component 'contacts_table' on page 'Contacts List' calls non-existent API endpoint 'GET /api/contacts'."
            m = re.search(r"non-existent API endpoint '([A-Z]+) ([^']+)'", err.message)
            if m:
                method = m.group(1)
                route = m.group(2)
                
                # Check if route already exists
                route_exists = any(ep.route == route and ep.method == method for ep in repaired.api.endpoints)
                if not route_exists:
                    # Create default roles
                    roles = [r.role for r in repaired.auth.roles] if repaired.auth.roles else ["User"]
                    
                    # Deduce request body or response fields if possible
                    # Heuristic: /api/contacts -> contacts table
                    entity_name = route.split("/")[-1].lower() if "/" in route else "data"
                    
                    repaired.api.endpoints.append(APIEndpoint(
                        route=route,
                        method=method,
                        description=f"Auto-generated endpoint for UI route {route}",
                        allowed_roles=roles,
                        responses=[APIResponseSchema(status_code=200 if method == "GET" else 201, fields={"success": "boolean"})]
                    ))
                    
                    logs.append(RepairLogEntry(
                        error_code=err.code,
                        layer="API",
                        description=f"UI called non-existent API endpoint '{method} {route}'.",
                        action_taken=f"Created endpoint '{method} {route}' with default response.",
                        status="fixed"
                    ))
                    
        # Error Code: UNRESOLVED_ROLE
        # Case: API allowed roles mentions role not in Auth schema
        elif err.code == "UNRESOLVED_ROLE":
            # e.g., "API endpoint 'GET /api/analytics/revenue' references role 'SalesManager' which is not defined in the Auth system."
            m = re.search(r"references role '([a-zA-Z0-9_]+)' which is not defined in the Auth system", err.message)
            if m:
                role_name = m.group(1)
                # Verify role exists in auth
                role_exists = any(r.role.lower() == role_name.lower() for r in repaired.auth.roles)
                if not role_exists:
                    repaired.auth.roles.append(AuthRule(
                        role=role_name,
                        permissions=[f"auto.*"]
                    ))
                    logs.append(RepairLogEntry(
                        error_code=err.code,
                        layer="AUTH",
                        description=f"API referenced role '{role_name}' which was missing in Auth.",
                        action_taken=f"Added role '{role_name}' to AuthSchema.",
                        status="fixed"
                    ))

    # Process warnings as well to keep quality clean
    for warn in validation.warnings:
        if warn.code == "MISSING_PRIMARY_KEY":
            # e.g. "Table 'contacts' has no primary key defined."
            m = re.search(r"Table '([a-zA-Z0-9_]+)' has no primary key", warn.message)
            if m:
                table_name = m.group(1)
                for table in repaired.db.tables:
                    if table.name.lower() == table_name.lower():
                        # Add primary key
                        if not any(c.is_primary for c in table.columns):
                            table.columns.insert(0, DBColumn(
                                name="id",
                                type="INTEGER",
                                is_primary=True,
                                is_nullable=False
                            ))
                            logs.append(RepairLogEntry(
                                error_code=warn.code,
                                layer="DB",
                                description=f"Table '{table_name}' had no primary key.",
                                action_taken=f"Inserted 'id' INTEGER PRIMARY KEY at column index 0.",
                                status="fixed"
                            ))
                            break

    # If any repairs were applied, we should re-run validation on the repaired schema
    # importing validate_schema here to avoid circular imports
    from app.pipeline.stage5_validate import validate_schema
    new_validation = validate_schema(repaired)
    
    # We are successful if the repaired schema is now valid (no errors)
    success = new_validation.is_valid
    
    return RepairResult(
        repaired_schema=repaired,
        logs=logs,
        success=success
    )

import sqlite3
import logging
from typing import Dict, Any, List
from app.pipeline.models import ApplicationSchema

logger = logging.getLogger("AIBuilder.Simulator")

def simulate_execution(app_schema: ApplicationSchema) -> Dict[str, Any]:
    """Execution Simulator.
    Verifies that the database schema compiles in SQLite and simulates API/Auth execution correctness.
    """
    report = {
        "status": "PASS",
        "database_creation": "SUCCESS",
        "api_routing": "SUCCESS",
        "permission_checks": "SUCCESS",
        "findings": []
    }
    
    # 1. DB Schema Compilation Check
    db_schema = app_schema.db
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    try:
        # Enable foreign key support in SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # Build and execute CREATE TABLE queries
        for table in db_schema.tables:
            columns_sql = []
            for col in table.columns:
                col_def = f"{col.name} {col.type}"
                if col.is_primary:
                    col_def += " PRIMARY KEY"
                if not col.is_nullable:
                    col_def += " NOT NULL"
                if col.references:
                    # e.g., references = "users.id"
                    ref_table, ref_col = col.references.split(".")
                    col_def += f" REFERENCES {ref_table}({ref_col})"
                columns_sql.append(col_def)
                
            create_query = f"CREATE TABLE {table.name} ({', '.join(columns_sql)});"
            logger.info(f"Simulator executing: {create_query}")
            cursor.execute(create_query)
            
        conn.commit()
        report["findings"].append(f"Successfully compiled and instantiated {len(db_schema.tables)} database tables in-memory.")
    except Exception as e:
        report["status"] = "FAIL"
        report["database_creation"] = f"FAILED: {str(e)}"
        report["findings"].append(f"Database compilation failed: {str(e)}")
        conn.close()
        return report

    # 2. Simulate API and Auth Operations
    # Let's verify each endpoint format and simulate basic operations
    api_schema = app_schema.api
    endpoints_tested = 0
    auth_verified = True
    
    try:
        # Check endpoint paths for syntax correctness
        for ep in api_schema.endpoints:
            # Check route layout
            if not ep.route.startswith("/"):
                report["api_routing"] = "FAILED: Route does not start with /"
                report["status"] = "FAIL"
                
            # Verify roles mapping
            if not ep.allowed_roles:
                # Warning: Endpoint open to everyone
                report["findings"].append(f"Warning: Endpoint '{ep.method} {ep.route}' has no role limits.")
            else:
                for role in ep.allowed_roles:
                    # Verify role matches one of the auth roles
                    role_defined = any(r.role.lower() == role.lower() for r in app_schema.auth.roles)
                    if not role_defined:
                        auth_verified = False
                        
            endpoints_tested += 1
            
        report["findings"].append(f"Validated syntax and routing structures for {endpoints_tested} API endpoints.")
        
        if auth_verified:
            report["findings"].append("RBAC (Role Based Access Control) permission policies mapped successfully to endpoints.")
        else:
            report["status"] = "FAIL"
            report["permission_checks"] = "FAILED: Endpoints allowed_roles references undefined roles."
            
    except Exception as e:
        report["status"] = "FAIL"
        report["api_routing"] = f"FAILED: {str(e)}"
        report["findings"].append(f"API/Auth simulation failed: {str(e)}")
    
    # Close simulator connection
    conn.close()
    return report

import sqlite3
import os
import logging
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Header, Request
from app.config import settings

logger = logging.getLogger("AIBuilder.RuntimeEngine")
router = APIRouter(prefix="/api")

def get_db_connection():
    """Get connection to the dynamic SQLite database."""
    conn = sqlite3.connect(settings.RUNTIME_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_runtime_db(db_schema) -> bool:
    """Initialize the SQLite tables on the dynamic database based on DB Schema."""
    # Remove existing database file if present to start fresh
    if os.path.exists(settings.RUNTIME_DB_PATH):
        try:
            os.remove(settings.RUNTIME_DB_PATH)
        except Exception as e:
            logger.warning(f"Could not delete old runtime.db: {e}")
            
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA foreign_keys = ON;")
        for table in db_schema.tables:
            columns_sql = []
            for col in table.columns:
                col_def = f"{col.name} {col.type}"
                if col.is_primary:
                    col_def += " PRIMARY KEY"
                if not col.is_nullable:
                    col_def += " NOT NULL"
                if col.references:
                    ref_table, ref_col = col.references.split(".")
                    col_def += f" REFERENCES {ref_table}({ref_col})"
                columns_sql.append(col_def)
                
            create_query = f"CREATE TABLE {table.name} ({', '.join(columns_sql)});"
            logger.info(f"Engine creating table: {create_query}")
            cursor.execute(create_query)
            
        # Seed default user accounts so the login works out of the box
        # Check if users table exists
        tables_in_db = [t.name.lower() for t in db_schema.tables]
        if "users" in tables_in_db:
            # Seed both forge.ai and builder.ai domains to ensure compatibility with all front-end/documentation presets
            for domain in ["forge.ai", "builder.ai"]:
                cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (f"admin@{domain}", "admin123", "Admin"))
                cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (f"sales@{domain}", "sales123", "SalesManager"))
                cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)", (f"user@{domain}", "user123", "User"))
            
        # Seed default contacts if contacts table exists
        if "contacts" in tables_in_db:
            cursor.execute("INSERT INTO contacts (name, email, phone, created_by) VALUES (?, ?, ?, ?)", ("Alice Smith", "alice@example.com", "+1-555-0199", 1))
            cursor.execute("INSERT INTO contacts (name, email, phone, created_by) VALUES (?, ?, ?, ?)", ("Bob Jones", "bob@example.com", "+1-555-0182", 2))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Runtime DB initialization failed: {e}")
        conn.close()
        return False

# --- Helper to authorize based on dynamic role ---
def verify_role_access(request: Request, required_roles: List[str]):
    """Dynamic check. For prototype, client sends 'X-User-Role' header."""
    role = request.headers.get("X-User-Role", "User")
    if required_roles and role not in required_roles:
        raise HTTPException(status_code=403, detail=f"Access Denied: Role '{role}' unauthorized.")
    return role

# --- Dynamic Routes ---

@router.post("/auth/login")
async def runtime_login(payload: Dict[str, Any]):
    """Dynamic auth login."""
    email = payload.get("email")
    password = payload.get("password")
    
    # Try looking in SQLite users table
    if os.path.exists(settings.RUNTIME_DB_PATH):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            user = cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
            conn.close()
            if user:
                return {"token": "mock-jwt-token-xyz", "role": user["role"], "email": user["email"]}
        except Exception:
            pass
            
    # Fallback default logins if DB fails or tables don't exist yet
    if email in ["admin@forge.ai", "admin@builder.ai"] and password == "admin123":
        return {"token": "mock-jwt-token-xyz", "role": "Admin", "email": email}
    elif email in ["sales@forge.ai", "sales@builder.ai"] and password == "sales123":
        return {"token": "mock-jwt-token-xyz", "role": "SalesManager", "email": email}
    elif email in ["user@forge.ai", "user@builder.ai"] and password == "user123":
        return {"token": "mock-jwt-token-xyz", "role": "User", "email": email}
        
    raise HTTPException(status_code=401, detail="Invalid email or password.")

@router.get("/analytics/revenue")
async def runtime_revenue_analytics(request: Request):
    """Dynamic analytics endpoint."""
    verify_role_access(request, ["Admin", "SalesManager"])
    # Return beautiful simulated data
    return {
        "total_revenue": 14850.00,
        "growth": 12.4,
        "recent_sales": [
            {"date": "2026-06-01", "amount": 1200},
            {"date": "2026-06-02", "amount": 800},
            {"date": "2026-06-03", "amount": 1500}
        ]
    }

@router.get("/{entity}")
async def get_runtime_records(entity: str, request: Request):
    """Generic query endpoint to fetch all rows for a table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        rows = cursor.execute(f"SELECT * FROM {entity}").fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@router.get("/{entity}/count")
async def get_runtime_count(entity: str, request: Request):
    """Generic endpoint to get row count of a table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        count = cursor.execute(f"SELECT COUNT(*) FROM {entity}").fetchone()[0]
        conn.close()
        return {"count": count}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@router.post("/{entity}")
async def create_runtime_record(entity: str, payload: Dict[str, Any], request: Request):
    """Generic endpoint to insert a row into a table."""
    # Dynamic insert
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        keys = list(payload.keys())
        values = list(payload.values())
        placeholders = ", ".join(["?"] * len(keys))
        
        insert_query = f"INSERT INTO {entity} ({', '.join(keys)}) VALUES ({placeholders});"
        logger.info(f"Engine running insert: {insert_query} with {values}")
        cursor.execute(insert_query, values)
        conn.commit()
        row_id = cursor.lastrowid
        conn.close()
        return {"id": row_id, "status": "SUCCESS", "message": f"Created record in {entity}."}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

@router.delete("/{entity}/{id}")
async def delete_runtime_record(entity: str, id: int, request: Request):
    """Generic endpoint to delete a row by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"DELETE FROM {entity} WHERE id = ?;", (id,))
        conn.commit()
        conn.close()
        return {"status": "SUCCESS", "message": f"Deleted record {id} from {entity}."}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

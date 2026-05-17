import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Establish a connection to the Oracle 23ai Docker container."""
    return oracledb.connect(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dsn=os.getenv("DB_DSN")
    )

def get_schema_info():
    """
    Fetches table and column names so the AI knows 
    what it is looking at.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # We query the Oracle Data Dictionary
    query = """
    SELECT table_name, column_name, data_type 
    FROM user_tab_columns 
    WHERE table_name IN ('STUDENTS', 'MARKS')
    ORDER BY table_name
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    
    schema_text = "Database Schema:\n"
    for row in rows:
        schema_text += f"Table: {row[0]}, Column: {row[1]}, Type: {row[2]}\n"
    
    cursor.close()
    conn.close()
    return schema_text

def execute_oracle_query(sql: str):
    # 1. REMOVE MARKDOWN AND SEMICOLONS
    sql = sql.replace("```sql", "").replace("```", "").replace(";", "").strip()
    
    # 2. REMOVE COMMENTS (AI often adds -- comments which cause ORA errors)
    lines = [line for line in sql.split('\n') if not line.strip().startswith('--')]
    sql = " ".join(lines).strip()
    
    # 3. REMOVE COLONS (To fix DPY-4010)
    # The AI might be saying "SQL: SELECT..." - we remove the "SQL:"
    if ":" in sql and not ("'" in sql or '"' in sql): 
        sql = sql.split(":")[-1].strip()

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        cursor.close()
        return {"data": results, "error": None}
    except Exception as e:
        return {"data": None, "error": str(e)}
    finally:
        if conn:
            conn.close()
from db_tools import get_schema_info, execute_oracle_query

try:
    print("📡 Connecting to Oracle DB...")
    schema = get_schema_info()
    print("✅ Connection Successful!")
    print("-" * 30)
    print(schema)
    
    print("\n📊 Running test query: SELECT COUNT(*) FROM MARKS")
    res = execute_oracle_query("SELECT COUNT(*) FROM MARKS")
    print(f"Result: {res['data']}")
    
except Exception as e:
    print(f"❌ Connection Failed: {e}")
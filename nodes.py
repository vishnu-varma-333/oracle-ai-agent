import os
import time
import warnings
import logging
import ssl
from langchain_google_genai import ChatGoogleGenerativeAI
from state import AgentState
from db_tools import get_schema_info, execute_oracle_query
from dotenv import load_dotenv

# --- MAC SSL PATCH ---
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")
logging.getLogger("google").setLevel(logging.ERROR)
load_dotenv()

# --- EXPLICIT MAC INITIALIZATION ---
# We force transport="rest" because your Mac needs it to avoid hanging.
llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
    transport="rest" 
)

def safe_invoke(prompt):
    """Vocal invoker to find the exact hang point."""
    print("   📡 Sending request to Gemini API...", flush=True)
    start_time = time.time()
    
    try:
        response = llm.invoke(prompt)
        end_time = time.time()
        print(f"   ✅ AI responded in {round(end_time - start_time, 2)}s", flush=True)
        
        content = response.content
        if isinstance(content, list):
            content = "\n".join([c['text'] if isinstance(c, dict) and 'text' in c else str(c) for c in content])
        return str(content)
    except Exception as e:
        print(f"   ❌ AI API Error: {e}", flush=True)
        raise e

def node_sql_planner(state: AgentState):
    print("🧠 Node: Planning SQL Query...", flush=True)
    schema = state.get("schema_info") or get_schema_info()
    
    error_context = ""
    if state.get("error_message"):
        error_context = f"\nYour last attempt failed with: {state['error_message']}. DO NOT REPEAT THAT MISTAKE."

    prompt = f"""
    You are a Senior Oracle DBA. Write a clean SELECT query for the user's question.
    
    Schema:
    {schema}
    
    Example Questions and Oracle SQL:
    - Q: List all tables
      A: SELECT table_name FROM user_tables
    - Q: Count students
      A: SELECT COUNT(*) FROM STUDENTS
    - Q: Students with score < 35
      A: SELECT NAME FROM STUDENTS WHERE ID IN (SELECT STUDENT_ID FROM MARKS WHERE SCORE < 35)
    
    Current Question: {state['question']}
    {error_context}
    
    CRITICAL RULES:
    1. Output ONLY the SQL string.
    2. No markdown, no comments, no colons (:), no semicolons (;).
    3. Use Oracle syntax (e.g., USER_TABLES for listing tables).
    """
    
    sql = safe_invoke(prompt)
    current_revs = state.get("revision_count", 0)
    return {"sql_query": sql.strip(), "schema_info": schema, "revision_count": current_revs + 1}

def node_db_executor(state: AgentState):
    # This node is the 'Hands'
    print(f"🚀 Node: Executing SQL on Oracle...", flush=True)
    result = execute_oracle_query(state['sql_query'])
    
    if result["error"]:
        return {"error_message": result["error"], "db_result": None}
    return {"db_result": result["data"], "error_message": None}

def node_synthesizer(state: AgentState):
    print("📝 Node: Synthesizing Final Answer...", flush=True)
    
    if state.get("error_message") and not state.get("db_result"):
        return {"final_answer": f"I hit a technical wall. Oracle Error: {state['error_message']}"}

    prompt = f"Question: {state['question']}\nResult: {state['db_result']}\nAnswer in a sentence:"
    answer = safe_invoke(prompt)
    return {"final_answer": answer}
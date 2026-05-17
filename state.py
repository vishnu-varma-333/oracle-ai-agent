from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # Input from user
    question: str
    
    # Context about the database
    schema_info: str
    
    # Agent's thought process
    sql_query: str
    db_result: Optional[List]
    error_message: Optional[str]
    
    # Final response
    final_answer: str
    
    # Loop control
    revision_count: int
from langgraph.graph import StateGraph, END
from state import AgentState
from nodes import node_sql_planner, node_db_executor, node_synthesizer

workflow = StateGraph(AgentState)

# 1. Add Nodes
workflow.add_node("planner", node_sql_planner)
workflow.add_node("executor", node_db_executor)
workflow.add_node("synthesizer", node_synthesizer)

# 2. Set Entry Point
workflow.set_entry_point("planner")

# 3. Simple Edge: Planner always goes to Executor
workflow.add_edge("planner", "executor")

# 4. Conditional Edge: From Executor, decide where to go
def should_continue(state: AgentState):
    if state.get("error_message"):
        if state.get("revision_count", 0) < 3:
            return "retry" # Maps to planner
    return "finalize" # Maps to synthesizer

workflow.add_conditional_edges(
    "executor",
    should_continue,
    {
        "retry": "planner",
        "finalize": "synthesizer"
    }
)

# 5. Synthesizer always goes to END
workflow.add_edge("synthesizer", END)

app = workflow.compile()
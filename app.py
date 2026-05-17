import streamlit as st
import time
from graph import app

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Oracle Intelligence Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM PREMIUM STYLING ---
# FIXED: Changed unsafe_allow_stdio to unsafe_allow_html
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #e6e9ef; }
    .st-emotion-cache-1c7n2ka { background-color: #ffffff; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    h1 { color: #1e293b; font-weight: 800; letter-spacing: -1px; }
    .status-text { font-size: 0.85rem; color: #64748b; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM STATUS ---
with st.sidebar:
    st.image("https://www.oracle.com/a/ocom/img/hp/oracle-23ai-logo.png", width=150)
    st.title("System Control")
    st.markdown("---")
    st.success("🟢 Oracle 23ai: Online")
    st.info("🤖 Agent Model: Gemini Flash")
    
    st.markdown("### Database Overview")
    st.caption("Tables managed by AI:")
    st.code("• STUDENTS\n• MARKS", language="text")
    
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- MAIN INTERFACE ---
st.title("Oracle Intelligence Pro")
st.markdown("#### *Conversational Enterprise Data Analytics*")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT & AGENT EXECUTION ---
if prompt := st.chat_input("Ask a question about your students or marks..."):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Agent Execution with Status Container
    with st.chat_message("assistant"):
        with st.status("💎 Architecting Data Response...", expanded=True) as status:
            
            try:
                # Node 1: Planning
                st.write("🧠 Interpreting natural language...")
                initial_state = {
                    "question": prompt,
                    "revision_count": 0,
                    "error_message": None,
                    "db_result": None,
                    "schema_info": None
                }
                
                final_state = app.invoke(initial_state)
                
                # Node 2: Execution
                st.write("🚀 Querying Oracle High-Performance Cluster...")
                sql_used = final_state.get("sql_query", "Unknown")
                
                # Node 3: Synthesis
                st.write("📝 Synthesizing business insights...")
                response = final_state.get("final_answer", "Analysis complete.")
                
                status.update(label="✅ Insight Generated", state="complete", expanded=False)

                # 3. Show Final Results
                st.markdown(response)
                
                # 4. Premium Technical Dropdown
                with st.expander("📊 Technical Analysis"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("Generated SQL")
                        st.code(sql_used, language="sql")
                    with col2:
                        st.caption("Execution Result")
                        st.json(final_state.get("db_result", []))

                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                status.update(label="❌ System Error", state="error")
                st.error(f"An unexpected error occurred: {e}")

# --- FOOTER ---
st.markdown("---")
st.caption("Oracle AI Agent v2.0 | Powered by LangGraph & Gemini 1.5")
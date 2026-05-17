from graph import app

def interactive_chat():
    print("\n🎓 Welcome to the Oracle AI Student Portal")
    print("Type 'exit' or 'quit' to stop.\n")
    
    while True:
        user_input = input("👤 Ask a question about the DB: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
            
        initial_state = {
            "question": user_input,
            "revision_count": 0,
            "error_message": None,
            "db_result": None,
            "schema_info": None
        }
        
        # Run the agent
        final_state = app.invoke(initial_state)
        
        print("\n" + "="*50)
        print(f"🤖 AGENT: {final_state.get('final_answer')}")
        print("="*50 + "\n")

if __name__ == "__main__":
    interactive_chat()
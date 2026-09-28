import os
from triage_agent.graph import app

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable is missing.")
        exit(1)
        
    initial_payload = {
        "incident_payload": "URGENT: CheckoutService is returning 500 Internal Server Error. Alert triggered at 10:45 AM UTC."
    }
    
    print("Triggering Modular Incident Triage Graph...\n")
    
    # thread_id is required by the Checkpointer to track this specific execution
    config = {"configurable": {"thread_id": "incident-9999"}}
    
    for output in app.stream(initial_payload, config=config):
        for node_name, state_update in output.items():
            print(f"--- Node [{node_name}] Completed ---")
            
    print("\n=== FINAL REPORT ===")
    
    # Because we are using MemorySaver, we can look up the final state directly!
    final_state = app.get_state(config).values
    print(final_state.get("final_report"))
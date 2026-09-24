from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

# 1. Define the State Schema
# This dictates the data structure passed between nodes. Because the parallel 
# nodes update distinct keys (log_summary and commit_summary), LangGraph 
# safely merges their outputs without conflicts.
class IncidentState(TypedDict):
    incident_payload: str
    log_summary: str
    commit_summary: str
    final_report: str

# Initialize the LLM (defaults to reading the OPENAI_API_KEY env variable)
llm = ChatOpenAI(temperature=0, model="gpt-4o")

# 2. Define the Agent Nodes
def log_analyst(state: IncidentState):
    sys_prompt = (
        "You are a Log Analyst SRE. Review the incident payload and extract "
        "any stack traces or error signatures. If none exist, output 'No anomalies'."
    )
    messages = [
        SystemMessage(content=sys_prompt), 
        HumanMessage(content=state["incident_payload"])
    ]
    response = llm.invoke(messages)
    # The dictionary returned here updates the 'log_summary' key in the global state
    return {"log_summary": response.content}

def code_analyst(state: IncidentState):
    sys_prompt = (
        "You are a Release Engineer. Identify recent code deployments or config "
        "changes related to this payload. If none exist, output 'No recent deployments'."
    )
    messages = [
        SystemMessage(content=sys_prompt), 
        HumanMessage(content=state["incident_payload"])
    ]
    response = llm.invoke(messages)
    return {"commit_summary": response.content}

def synthesizer(state: IncidentState):
    sys_prompt = (
        "You are an Incident Commander. Synthesize the provided log and commit "
        "summaries into a Root Cause Hypothesis and suggest two mitigation steps."
    )
    # Constructing the context payload for the final synthesis
    context = (
        f"Original Alert: {state['incident_payload']}\n"
        f"Log Analysis: {state.get('log_summary')}\n"
        f"Code Analysis: {state.get('commit_summary')}"
    )
    messages = [
        SystemMessage(content=sys_prompt), 
        HumanMessage(content=context)
    ]
    response = llm.invoke(messages)
    return {"final_report": response.content}

# 3. Construct the Graph Orchestration
workflow = StateGraph(IncidentState)

# Register the nodes
workflow.add_node("log_analyst", log_analyst)
workflow.add_node("code_analyst", code_analyst)
workflow.add_node("synthesizer", synthesizer)

# Fan-out: The start node triggers both analysts in parallel
workflow.add_edge(START, "log_analyst")
workflow.add_edge(START, "code_analyst")

# Fan-in: Both analysts must complete before routing to the synthesizer
workflow.add_edge("log_analyst", "synthesizer")
workflow.add_edge("code_analyst", "synthesizer")

# End execution
workflow.add_edge("synthesizer", END)

# Compile the graph into a runnable application
app = workflow.compile()

# 4. Execute the Graph
if __name__ == "__main__":
    initial_payload = {
        "incident_payload": "URGENT: CheckoutService is returning 500 Internal Server Error. CPU spiked to 99%."
    }
    
    print("Triggering Incident Triage Graph...\n")
    
    # app.stream yields the state updates from each node as they complete
    for output in app.stream(initial_payload):
        for node_name, state_update in output.items():
            print(f"--- Node [{node_name}] Completed ---")
            print(state_update, "\n")
            
    print("=== FINAL REPORT ===")
    # Fetching the final compiled state
    final_state = app.get_state(app.config).values
    print(final_state.get("final_report"))
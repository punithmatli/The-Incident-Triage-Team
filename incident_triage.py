import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", category=DeprecationWarning)

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

class IncidentState(TypedDict):
    incident_payload: str
    log_summary: str
    commit_summary: str
    final_report: str

@tool
def query_cloudwatch_logs(service_name: str, time_window_minutes: int) -> str:
    """Queries AWS CloudWatch for recent errors related to a service."""
    print(f"   --> 🔧 [Tool Executing] query_cloudwatch_logs for '{service_name}'")
    if "CheckoutService" in service_name:
        return "FATAL: Connection pool exhausted for Database 'OrdersDB' at 10:42 AM UTC."
    return "No anomalies found."

@tool
def query_recent_commits(repo_name: str, hours_back: int) -> str:
    """Queries GitHub for commits made to a repository within a timeframe."""
    print(f"   --> 🔧 [Tool Executing] query_recent_commits for '{repo_name}'")
    if "checkout" in repo_name.lower():
        return "Commit 8f92a1: 'Decrease DB connection pool max size to 5' by dev@company.com"
    return "No recent deployments."

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# FIX: Removed the modifier keyword argument entirely to support your older LangGraph version
log_agent_runnable = create_react_agent(llm, tools=[query_cloudwatch_logs])
code_agent_runnable = create_react_agent(llm, tools=[query_recent_commits])

def log_analyst(state: IncidentState):
    # FIX: Inject the system prompt dynamically as the first message
    sys_prompt = "You are a Log Analyst SRE. Use your tools to investigate the alert. Return a concise summary of the errors."
    inputs = {
        "messages": [
            ("system", sys_prompt),
            ("user", f"Investigate this alert: {state['incident_payload']}")
        ]
    }
    response = log_agent_runnable.invoke(inputs)
    final_message = response["messages"][-1].content
    return {"log_summary": final_message}

def code_analyst(state: IncidentState):
    sys_prompt = "You are a Release Engineer. Use your tools to check for recent code deployments related to the alert. Return a concise summary."
    inputs = {
        "messages": [
            ("system", sys_prompt),
            ("user", f"Investigate this alert: {state['incident_payload']}")
        ]
    }
    response = code_agent_runnable.invoke(inputs)
    final_message = response["messages"][-1].content
    return {"commit_summary": final_message}

def synthesizer(state: IncidentState):
    sys_prompt = "You are an Incident Commander. Synthesize the findings into a Root Cause Hypothesis and Mitigation."
    context = (
        f"Original Alert: {state['incident_payload']}\n"
        f"Log Analysis: {state.get('log_summary')}\n"
        f"Code Analysis: {state.get('commit_summary')}"
    )
    messages = [SystemMessage(content=sys_prompt), HumanMessage(content=context)]
    response = llm.invoke(messages)
    return {"final_report": response.content}

workflow = StateGraph(IncidentState)
workflow.add_node("log_analyst", log_analyst)
workflow.add_node("code_analyst", code_analyst)
workflow.add_node("synthesizer", synthesizer)

workflow.add_edge(START, "log_analyst")
workflow.add_edge(START, "code_analyst")
workflow.add_edge("log_analyst", "synthesizer")
workflow.add_edge("code_analyst", "synthesizer")
workflow.add_edge("synthesizer", END)

app = workflow.compile()

if __name__ == "__main__":
    import os
    if not os.environ.get("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable is missing.")
        exit(1)
        
    initial_payload = {
        "incident_payload": "URGENT: CheckoutService is returning 500 Internal Server Error. Alert triggered at 10:45 AM UTC."
    }
    
    print("Triggering Incident Triage Graph...\n")
    
    final_report = "Report generation failed."
    
    # We catch the final_report as it gets yielded by the synthesizer
    for output in app.stream(initial_payload):
        for node_name, state_update in output.items():
            print(f"--- Node [{node_name}] Completed ---")
            if "final_report" in state_update:
                final_report = state_update["final_report"]
            
    print("\n=== FINAL REPORT ===")
    print(final_report)
    
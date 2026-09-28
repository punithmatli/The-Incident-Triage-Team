from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from triage_agent.state import IncidentState

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

def synthesizer(state: IncidentState):
    sys_prompt = "You are an Incident Commander. Synthesize the findings into a Root Cause Hypothesis and Mitigation."
    
    # We pull the context from the blackboard state populated by the other nodes
    context = (
        f"Original Alert: {state['incident_payload']}\n"
        f"Log Analysis: {state.get('log_summary', 'Pending')}\n"
        f"Code Analysis: {state.get('commit_summary', 'Pending')}"
    )
    
    messages = [SystemMessage(content=sys_prompt), HumanMessage(content=context)]
    response = llm.invoke(messages)
    
    return {"final_report": response.content}
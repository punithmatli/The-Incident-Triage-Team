from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from triage_agent.state import IncidentState
from triage_agent.tools.cloudwatch import query_cloudwatch_logs

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

# The agent subgraph that handles the tool-calling loop
log_agent_runnable = create_react_agent(llm, tools=[query_cloudwatch_logs])

def log_analyst(state: IncidentState):
    sys_prompt = "You are a Log Analyst SRE. Use your tools to investigate the alert. Return a concise summary of the errors."
    inputs = {
        "messages": [
            ("system", sys_prompt),
            ("user", f"Investigate this alert: {state['incident_payload']}")
        ]
    }
    response = log_agent_runnable.invoke(inputs)
    return {"log_summary": response["messages"][-1].content}
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from triage_agent.state import IncidentState
from triage_agent.tools.github import query_recent_commits

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")

code_agent_runnable = create_react_agent(llm, tools=[query_recent_commits])

def code_analyst(state: IncidentState):
    sys_prompt = "You are a Release Engineer. Use your tools to check for recent code deployments related to the alert. Return a concise summary."
    inputs = {
        "messages": [
            ("system", sys_prompt),
            ("user", f"Investigate this alert: {state['incident_payload']}")
        ]
    }
    response = code_agent_runnable.invoke(inputs)
    return {"commit_summary": response["messages"][-1].content}
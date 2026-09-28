from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Import the state schema
from triage_agent.state import IncidentState

# We will create these node modules in the next step
from triage_agent.nodes.log_node import log_analyst
from triage_agent.nodes.code_node import code_analyst
from triage_agent.nodes.synth_node import synthesizer

# 1. Initialize the Graph Builder
workflow = StateGraph(IncidentState)

# 2. Add the specialized worker nodes
workflow.add_node("log_analyst", log_analyst)
workflow.add_node("code_analyst", code_analyst)
workflow.add_node("synthesizer", synthesizer)

# 3. Define the Fan-Out Routing (Parallel Execution)
workflow.add_edge(START, "log_analyst")
workflow.add_edge(START, "code_analyst")

# 4. Define the Fan-In Routing (Synchronization Barrier)
workflow.add_edge("log_analyst", "synthesizer")
workflow.add_edge("code_analyst", "synthesizer")

# 5. Define the Termination
workflow.add_edge("synthesizer", END)

# 6. Initialize Persistent Memory
# MemorySaver writes the state to memory after every node completes. 
# In a production environment, you swap this for AsyncPostgresSaver.
memory = MemorySaver()

# 7. Compile the Application
# We expose 'app' so main.py or a FastAPI server can import and run it.
app = workflow.compile(checkpointer=memory)
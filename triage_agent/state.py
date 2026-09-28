from typing import TypedDict

class IncidentState(TypedDict):
    """
    The shared memory structure passed between all nodes in the graph.
    LangGraph merges node outputs into this state automatically.
    """
    incident_payload: str
    log_summary: str
    commit_summary: str
    final_report: str
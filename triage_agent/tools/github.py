from langchain_core.tools import tool

@tool
def query_recent_commits(repo_name: str, hours_back: int) -> str:
    """Queries GitHub for commits made to a repository within a timeframe."""
    print(f"   --> 🔧 [Tool Executing] query_recent_commits for '{repo_name}'")
    if "checkout" in repo_name.lower():
        return "Commit 8f92a1: 'Decrease DB connection pool max size to 5' by dev@company.com"
    return "No recent deployments."
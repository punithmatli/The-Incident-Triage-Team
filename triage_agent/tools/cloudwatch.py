from langchain_core.tools import tool

@tool
def query_cloudwatch_logs(service_name: str, time_window_minutes: int) -> str:
    """Queries AWS CloudWatch for recent errors related to a service."""
    print(f"   --> 🔧 [Tool Executing] query_cloudwatch_logs for '{service_name}'")
    if "CheckoutService" in service_name:
        return "FATAL: Connection pool exhausted for Database 'OrdersDB' at 10:42 AM UTC."
    return "No anomalies found."
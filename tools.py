import datetime
import math
from langchain_core.tools import tool


@tool
def tool_time() -> str:
    """Return current local time string in format YYYY-MM-DD HH:MM:SS."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def tool_calc(expression: str) -> str:
    """A tiny safe-ish calculator. Handles + - * / ** () and math functions."""
    allowed_names = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    allowed_names.update({"__builtins__": {}})
    return str(eval(expression, allowed_names, {}))


# Export all tools as a list
ALL_TOOLS = [tool_time, tool_calc]

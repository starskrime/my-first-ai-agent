"""
Main MCP Server using FastMCP
Combines weather and news tools into a single server
"""

from dotenv import load_dotenv

# Load environment variables (critical for MCP server running as separate process)
load_dotenv()

from fastmcp import FastMCP

# Import tool functions
from weather import get_weather
from news import get_local_news

# Initialize FastMCP server
mcp = FastMCP("my-first-mcp-server")

# Register weather tool
mcp.tool()(get_weather)

# Register news tool
mcp.tool()(get_local_news)

# Run the server when called directly
if __name__ == "__main__":
    mcp.run()

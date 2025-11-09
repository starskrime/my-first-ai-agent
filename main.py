import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from tools import ALL_TOOLS
from mcp_client import FastMCPClient

# Custom system prompt
SYSTEM_PROMPT = """You are an intelligent travel planning assistant with access to real-time data tools.

Available capabilities:
- Current time and date information
- Mathematical calculations
- Flight search (real airline tickets via Google Flights)
- Weather forecasts (current conditions + 5-day outlook)
- Local news and events for any destination

Instructions:
- Proactively combine weather, news, and flight data for comprehensive travel recommendations
- Use tools to provide accurate, up-to-date information rather than relying on general knowledge
- Be concise and actionable in your responses
- When dates are mentioned, consider weather and local events for those specific times
- Present flight options with prices, duration, and airline details when available"""

# Initialize MCP client
# Use sys.executable to ensure subprocess uses same Python interpreter (with virtualenv)
mcp_client = FastMCPClient([sys.executable, 'mcp_server/main.py'])

# MCP Tools - Dynamically created from MCP server
MCP_TOOLS = []

def create_mcp_tool(tool_def):
    """Create a LangChain tool wrapper for an MCP tool"""
    from langchain_core.tools import StructuredTool
    from pydantic import BaseModel, create_model, Field
    from typing import Type

    tool_name = tool_def['name']
    tool_description = tool_def.get('description', 'MCP tool')
    input_schema = tool_def.get('inputSchema', {})

    # Extract properties from JSON Schema
    properties = input_schema.get('properties', {})
    required = input_schema.get('required', [])

    # Build Pydantic model fields dynamically
    fields = {}
    for prop_name, prop_def in properties.items():
        prop_type = str  # Default to string
        prop_description = prop_def.get('description', '')

        # Determine if field is required
        if prop_name in required:
            fields[prop_name] = (prop_type, Field(..., description=prop_description))
        else:
            fields[prop_name] = (prop_type, Field(None, description=prop_description))

    # Create Pydantic model dynamically
    ArgsSchema: Type[BaseModel] = create_model(f"{tool_name}Args", **fields)

    # Create wrapper function
    def mcp_tool_func(**kwargs) -> str:
        return mcp_client.call_tool(tool_name, kwargs)

    # Create StructuredTool with explicit schema
    wrapped_tool = StructuredTool.from_function(
        func=mcp_tool_func,
        name=tool_name,
        description=tool_description,
        args_schema=ArgsSchema
    )

    return wrapped_tool

# Initialize LLM
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.7)

# Conversation memory (initialize with system prompt)
conversation_history = [SystemMessage(content=SYSTEM_PROMPT)]

def chat(user_message: str) -> str:
    """Send a message and get a response while maintaining conversation history and handling tool calls."""
    # Add user message to history
    conversation_history.append(HumanMessage(content=user_message))

    # Get response from LLM
    response = llm_with_tools.invoke(conversation_history)

    # Check if the response contains tool calls
    while response.tool_calls:
        # Add the assistant's response to history
        conversation_history.append(response)

        # Process each tool call
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_input = tool_call["args"]

            print(f"\n[Using tool: {tool_name}]")

            # Execute the tool dynamically
            tool_result = TOOL_MAP[tool_name].invoke(tool_input)

            # Add tool result to history
            conversation_history.append(
                ToolMessage(
                    content=tool_result,
                    tool_call_id=tool_call["id"]
                )
            )

        # Get the next response from LLM (with tool results)
        response = llm_with_tools.invoke(conversation_history)

    # Add final AI response to history
    conversation_history.append(response)

    return response.content

# Run the agent
if __name__ == "__main__":
    print("🚀 Starting AI Travel Agent...")

    # Start MCP server
    if not mcp_client.start():
        print("❌ Failed to start MCP server. Exiting...")
        exit(1)

    # Create LangChain tool wrappers for MCP tools
    for tool_def in mcp_client.get_tools():
        MCP_TOOLS.append(create_mcp_tool(tool_def))

    # Combine all tools
    ALL_COMBINED_TOOLS = ALL_TOOLS + MCP_TOOLS

    # Create tool map for dynamic invocation
    TOOL_MAP = {tool.name: tool for tool in ALL_COMBINED_TOOLS}

    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(list(TOOL_MAP.values()))

    print(f"📡 Available tools: {len(ALL_COMBINED_TOOLS)} tools loaded")
    print(f"   - Traditional: {', '.join([t.name for t in ALL_TOOLS])}")
    print(f"   - MCP: {', '.join([t.name for t in MCP_TOOLS])}\n")

    print("Chat with AI Travel Agent (type 'quit' to exit):\n")

    try:
        while True:
            user_input = input("You: ").strip()

            if user_input.lower() == 'quit':
                break

            if not user_input:
                continue

            response = chat(user_input)

            # Create border around response
            import unicodedata

            def display_width(s):
                """Calculate display width accounting for wide characters (emojis, etc.)"""
                width = 0
                for char in s:
                    # East Asian Wide and Fullwidth characters take 2 spaces
                    if unicodedata.east_asian_width(char) in ('F', 'W'):
                        width += 2
                    # Emojis and other special characters typically take 2 spaces
                    elif ord(char) > 0x1F300:  # Emoji range starts here
                        width += 2
                    else:
                        width += 1
                return width

            response_lines = response.split('\n')
            max_display_width = max(display_width(line) for line in response_lines) if response_lines else 0
            border_width = max_display_width + 4  # Add padding

            print("\n" + "#" * border_width)
            for line in response_lines:
                # Calculate padding needed
                line_width = display_width(line)
                padding_needed = max_display_width - line_width
                print(f"# {line}{' ' * padding_needed} #")
            print("#" * border_width + "\n")

    finally:
        # Clean up MCP server
        mcp_client.stop()
        print("👋 Goodbye!")

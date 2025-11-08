from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from tools import ALL_TOOLS

load_dotenv()

# Custom system prompt
SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.

You can:
- Get the current time when needed
- Perform mathematical calculations
- Search for airline tickets between destinations with specific dates
- and much more using LLM capabilities

Always be concise and helpful. Use tools when appropriate to provide accurate information."""

# Initialize LLM
llm = ChatAnthropic(model="claude-sonnet-4-5-20250929", temperature=0.7)

# Create tool map for dynamic invocation
TOOL_MAP = {tool.name: tool for tool in ALL_TOOLS}

# Bind tools to LLM
llm_with_tools = llm.bind_tools(list(TOOL_MAP.values()))

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
    print("Chat with AI Agent (type 'quit' to exit):\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == 'quit':
            break
        
        if not user_input:
            continue
        
        response = chat(user_input)
        print(f"\nAI-Agent: {response}\n")

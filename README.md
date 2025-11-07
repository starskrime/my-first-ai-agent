# AI Agent with Tool Calling

A lightweight Python chatbot powered by Claude (Anthropic) with dynamic tool calling capabilities. This agent can maintain conversation context, execute tools on-demand, and provide intelligent responses.

## Features

- **Conversational AI**: Chat naturally with Claude Sonnet 4.5
- **Dynamic Tool Execution**: Automatically invokes tools when needed
- **Conversation Memory**: Maintains full conversation history
- **Custom System Prompt**: Easily configurable assistant behavior
- **Built-in Tools**:
  - `tool_time`: Get current date and time
  - `tool_calc`: Perform mathematical calculations with advanced math functions

## Prerequisites

- Python 3.12+
- Anthropic API key

## Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:starskrime/my-first-ai-agent.git
   cd my-first-ai-agent
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Run the agent:
```bash
python main.py
```

### Example Conversations

```
You: What time is it?
[Using tool: tool_time]
AI-Agent: It's currently 2025-11-06 14:30:45.

You: Calculate sqrt(144) + 5^2
[Using tool: tool_calc]
AI-Agent: The result is 37.0 (sqrt(144) = 12, plus 5^2 = 25).

You: quit
```

## Project Structure

```
research_agent/
├── main.py              # Main application file
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in repo)
└── README.md           # This file
```

## Configuration

### Custom System Prompt

Edit the `SYSTEM_PROMPT` variable in `main.py` to customize the assistant's behavior:

```python
SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.

You can:
- Get the current time when needed
- Perform mathematical calculations
- and much more using LLM capabilities

Always be concise and helpful. Use tools when appropriate to provide accurate information."""
```

### Adding New Tools

To add a new tool:

1. Define it using the `@tool` decorator:
   ```python
   @tool
   def my_new_tool(param: str) -> str:
       """Description of what this tool does."""
       # Your implementation
       return result
   ```

2. Add it to the tool map:
   ```python
   TOOL_MAP = {tool.name: tool for tool in [tool_time, tool_calc, my_new_tool]}
   ```

That's it! The agent will automatically discover and use your new tool.

## How It Works

1. **User Input**: You type a message
2. **LLM Processing**: Claude analyzes the message and decides if tools are needed
3. **Tool Execution**: If tools are required, they're executed automatically
4. **Response Generation**: Claude uses tool results to formulate a response
5. **History Tracking**: All messages (user, assistant, and tool calls) are stored for context

## Dependencies

- `langchain-anthropic`: Anthropic's Claude integration
- `langchain-core`: Core LangChain functionality for messages and tools
- `python-dotenv`: Environment variable management

## API Costs

This project uses Claude Sonnet 4.5. Monitor your usage at [Anthropic Console](https://console.anthropic.com/).

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

MIT License - feel free to use this project for learning and development.

## Troubleshooting

**Issue**: `ANTHROPIC_API_KEY not found`
- **Solution**: Ensure your `.env` file exists and contains a valid API key

**Issue**: Tool not being called
- **Solution**: Make sure your tool has a clear docstring describing when to use it

**Issue**: Import errors
- **Solution**: Run `pip install -r requirements.txt` to install all dependencies

## Learn More

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Tool Calling Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)

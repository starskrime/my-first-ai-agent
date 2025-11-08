# AI Agent with Tool Calling

A powerful Python chatbot powered by Claude (Anthropic) with dynamic tool calling capabilities. This agent can maintain conversation context, execute tools on-demand, search real-time flight data, and provide intelligent responses.

## Features

- **Conversational AI**: Chat naturally with Claude Sonnet 4.5
- **Dynamic Tool Execution**: Automatically invokes tools when needed
- **Conversation Memory**: Maintains full conversation history
- **Custom System Prompt**: Easily configurable assistant behavior
- **Modular Tool Architecture**: Tools organized in separate file for easy management
- **Built-in Tools**:
  - `tool_time`: Get current date and time
  - `tool_calc`: Perform mathematical calculations with advanced math functions
  - `search_flights`: Search real-time airline tickets using Google Flights data via SerpApi

## Prerequisites

- Python 3.8+
- Anthropic API key
- SerpApi API key (for flight search functionality)

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
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   SERPAPI_API_KEY=your_serpapi_key_here
   ```

   **Getting API Keys**:
   - **Anthropic API**: Sign up at [Anthropic Console](https://console.anthropic.com/)
   - **SerpApi**: Get a free key (100 searches/month) at [SerpApi](https://serpapi.com/)

## Usage

Run the agent:
```bash
python main.py
```

### Example Conversations

**Time and Calculations:**
```
You: What time is it?
[Using tool: tool_time]
AI-Agent: It's currently 2025-11-08 14:30:45.

You: Calculate sqrt(144) + 5^2
[Using tool: tool_calc]
AI-Agent: The result is 37.0 (sqrt(144) = 12, plus 5^2 = 25).
```

**Flight Search:**
```
You: Find flights from DFW to JFK departing 2025-11-18 returning 2025-11-21
[Using tool: search_flights]

AI-Agent: I found 5 round-trip flight options from DFW to JFK:

**Best Value:**
1. **Frontier - $224** (Cheapest)
   - Nonstop flight
   - Departs: 7:05 AM → Arrives: 11:59 AM
   - Duration: 3h 54m
   - Aircraft: Airbus A321

2. **Delta - $508**
   - Nonstop flight
   - Departs: 8:45 AM → Arrives: 1:12 PM
   - Duration: 3h 27m

[... more options ...]

You: quit
```

## Project Structure

```
my-first-ai-agent/
├── main.py              # Main application with chat loop
├── tools.py             # Tool definitions (time, calc, flight search)
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in repo)
└── README.md            # This file
```

## Configuration

### Custom System Prompt

Edit the `SYSTEM_PROMPT` variable in `main.py` to customize the assistant's behavior:

```python
SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools.

You can:
- Get the current time when needed
- Perform mathematical calculations
- Search for airline tickets between destinations with specific dates
- and much more using LLM capabilities

Always be concise and helpful. Use tools when appropriate to provide accurate information."""
```

### Adding New Tools

To add a new tool, edit `tools.py`:

1. Define it using the `@tool` decorator:
   ```python
   @tool
   def my_new_tool(param: str) -> str:
       """Description of what this tool does."""
       # Your implementation
       return result
   ```

2. Add it to the `ALL_TOOLS` list:
   ```python
   ALL_TOOLS = [tool_time, tool_calc, search_flights, my_new_tool]
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
- `requests`: HTTP library for API calls (flight search)

## API Costs

- **Claude Sonnet 4.5**: Monitor usage at [Anthropic Console](https://console.anthropic.com/)
- **SerpApi**: Free tier includes 100 searches/month. [View pricing](https://serpapi.com/pricing)

## Contributing

Feel free to open issues or submit pull requests for improvements.

## License

MIT License - feel free to use this project for learning and development.

## Troubleshooting

**Issue**: `ANTHROPIC_API_KEY not found`
- **Solution**: Ensure your `.env` file exists and contains a valid API key

**Issue**: `SERPAPI_API_KEY not found` or flight search returns error
- **Solution**: Add your SerpApi key to `.env`. Get a free key at [serpapi.com](https://serpapi.com)

**Issue**: `ModuleNotFoundError: No module named 'langchain_core'`
- **Solution**: Run `pip install -r requirements.txt` to install all dependencies

**Issue**: Tool not being called
- **Solution**: Make sure your tool has a clear docstring describing when to use it

**Issue**: Flight search returns no results
- **Solution**: Ensure dates are in YYYY-MM-DD format and use valid airport codes (e.g., JFK, LAX, DFW)

### Testing SerpApi Connection

Run the test script to verify your SerpApi setup:
```bash
python test_serpapi.py
```

This will test the API connection and show a sample flight search result.

## Learn More

- [Anthropic API Documentation](https://docs.anthropic.com/)
- [LangChain Documentation](https://python.langchain.com/)
- [Tool Calling Guide](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [SerpApi Documentation](https://serpapi.com/google-flights-api)

## What's New

### v2.0 - Flight Search Integration
- Added real-time flight search using Google Flights data via SerpApi
- Organized tools into separate `tools.py` module
- Enhanced error handling and debugging
- Added SerpApi connection test script
- Updated documentation with flight search examples

### v1.0 - Initial Release
- Basic conversational AI with Claude Sonnet 4.5
- Time and calculator tools
- Conversation memory and context tracking

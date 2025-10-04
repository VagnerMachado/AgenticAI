# Import necessary components from the custom 'agents' library.
from agents import Agent, WebSearchTool, ModelSettings

# --- Instructions for the Agent ---

# Define the system instructions for the search agent.
# These instructions guide the LLM to act as a research assistant that
# summarizes web search results concisely. The focus is on capturing the
# essence of the information for a later synthesis step.
INSTRUCTIONS = (
    "You are a research assistant. Given a search term, you search the web for that term and "
    "produce a concise summary of the results. The summary must 2-3 paragraphs and less than 300 "
    "words. Capture the main points. Write succintly, no need to have complete sentences or good "
    "grammar. This will be consumed by someone synthesizing a report, so its vital you capture the "
    "essence and ignore any fluff. Do not include any additional commentary other than the summary itself."
)

# --- Agent Definition ---

# Create an instance of the `Agent` class to define the search agent.
search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    # Provide the agent with the `WebSearchTool`. This allows it to perform web searches.
    # `search_context_size="low"` might configure the tool to retrieve less context from web pages,
    # keeping the information focused.
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    # `model_settings` allows for specific configurations for the LLM.
    # `tool_choice="required"` forces the agent to use a tool in its response,
    # ensuring it always performs a search as instructed.
    model_settings=ModelSettings(tool_choice="required"),
)
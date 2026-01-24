from pydantic import BaseModel, Field
from agents import Agent

# --- Constants and Instructions ---

# Define the number of web searches the planner should generate.
HOW_MANY_SEARCHES = 10

# Define the system instructions for the planner agent.
# This guides the LLM's behavior, telling it to act as a research assistant
# and generate a specific number of search queries.
INSTRUCTIONS = f"You are a helpful research assistant. Given a query, come up with a set of web searches \
to perform to best answer the query. Output {HOW_MANY_SEARCHES} terms to query for."

# --- Pydantic Output Schemas ---

# Pydantic models are used to define the expected structure of the LLM's output.
# This ensures the output is predictable and can be reliably used by other parts of the system.

class WebSearchItem(BaseModel):
    """
    Represents a single web search to be performed.
    """
    # The reasoning behind why this specific search is necessary.
    reason: str = Field(description="Your reasoning for why this search is important to the query.")
    # The actual query string to be used in the web search.
    query: str = Field(description="The search term to use for the web search.")


class WebSearchPlan(BaseModel):
    """
    Represents the complete plan of web searches to be executed.
    """
    # A list of individual search items.
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform to best answer the query.")
    
# --- Agent Definition ---

# Create an instance of the `Agent` class to define the planner agent.
# The `Agent` class is a core component from the custom 'agents' library.
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    # `output_type` is set to `WebSearchPlan`, which instructs the agent to
    # format its output according to this Pydantic model.
    output_type=WebSearchPlan,
)
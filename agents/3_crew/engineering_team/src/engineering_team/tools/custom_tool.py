from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

# --- Tool Input Schema ---
# Pydantic models are used to define the expected input structure for a tool.
# This ensures that the data passed to the tool is valid and well-defined.
class MyCustomToolInput(BaseModel):
    """
    Input schema for MyCustomTool.
    
    This class defines the arguments that the tool accepts. Each argument is
    defined as a field with a type and an optional description.
    """
    # The 'argument' field is a string and is required.
    # The `Field` function from Pydantic allows for additional metadata, such as a description.
    argument: str = Field(..., description="Description of the argument.")

# --- Custom Tool Definition ---
# All custom tools must inherit from the `BaseTool` class provided by crewai.
class MyCustomTool(BaseTool):
    """
    A template for creating a custom tool.

    This class demonstrates the basic structure of a tool that can be used by agents
    in a crew. It defines the tool's metadata and its core logic.
    """
    # The `name` of the tool is how agents will identify and refer to it.
    name: str = "Name of my tool"
    
    # The `description` is crucial for the agent to understand what the tool
    # does and when to use it. It should be clear and concise.
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    
    # The `args_schema` specifies the input schema for the tool.
    # It points to the Pydantic model defined above.
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        """
        The main execution method of the tool.

        This method contains the core logic of the tool. It receives the arguments
        defined in the input schema and should return a string as output.
        
        Args:
            argument (str): The value of the 'argument' field from the input schema.

        Returns:
            str: The result of the tool's execution.
        """
        # The implementation of the tool's functionality goes here.
        # This example returns a fixed string, but a real tool would
        # perform a meaningful action, such as calling an API, accessing a database,
        # or performing a calculation.
        return "this is an example of a tool output, ignore it and move along."

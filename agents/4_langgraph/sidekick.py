from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from typing import List, Any, Optional, Dict
from pydantic import BaseModel, Field
from sidekick_tools import playwright_tools, other_tools
import uuid
import asyncio
from datetime import datetime

# Load environment variables from a .env file, overriding existing ones.
load_dotenv(override=True)

# --- State and Schema Definitions ---

class State(TypedDict):
    """
    Defines the state of the graph. This TypedDict holds all the information
    that is passed between the nodes of the graph.
    """
    # `messages`: A list of messages in the conversation. `add_messages` is a
    # special function that appends new messages to this list.
    messages: Annotated[List[Any], add_messages]
    # `success_criteria`: The criteria for determining if the task is complete.
    success_criteria: str
    # `feedback_on_work`: Feedback provided by the evaluator on the worker's output.
    feedback_on_work: Optional[str]
    # `success_criteria_met`: A boolean flag indicating if the success criteria have been met.
    success_criteria_met: bool
    # `user_input_needed`: A boolean flag indicating if the agent needs more input from the user.
    user_input_needed: bool

class EvaluatorOutput(BaseModel):
    """
    Defines the output schema for the evaluator LLM.
    Using a Pydantic model ensures that the LLM's output is structured and can be reliably parsed.
    """
    feedback: str = Field(description="Feedback on the assistant's response")
    success_criteria_met: bool = Field(description="Whether the success criteria have been met")
    user_input_needed: bool = Field(description="True if more input is needed from the user, or clarifications, or the assistant is stuck")

# --- Sidekick Agent Class ---

class Sidekick:
    """
    The main class for the Sidekick agent. It encapsulates the agent's logic,
    state, and the LangGraph graph that defines its workflow.
    """
    def __init__(self):
        """Initializes the Sidekick agent."""
        self.worker_llm_with_tools = None
        self.evaluator_llm_with_output = None
        self.tools = None
        self.graph = None
        # Generate a unique ID for this session to manage conversational memory.
        self.sidekick_id = str(uuid.uuid4())
        # `MemorySaver` provides a simple in-memory checkpointing mechanism for the graph.
        self.memory = MemorySaver()
        # Placeholders for Playwright browser and context.
        self.browser = None
        self.playwright = None

    async def setup(self):
        """
        Asynchronously sets up the Sidekick agent's components.
        This includes initializing tools and LLMs, and building the graph.
        """
        # Load Playwright tools for web browsing and other tools.
        self.tools, self.browser, self.playwright = await playwright_tools()
        self.tools += await other_tools()
        
        # Configure the worker LLM with the available tools.
        worker_llm = ChatOpenAI(model="gpt-4o-mini")
        self.worker_llm_with_tools = worker_llm.bind_tools(self.tools)
        
        # Configure the evaluator LLM to produce structured output based on the EvaluatorOutput schema.
        evaluator_llm = ChatOpenAI(model="gpt-4o-mini")
        self.evaluator_llm_with_output = evaluator_llm.with_structured_output(EvaluatorOutput)
        
        # Build the LangGraph graph.
        await self.build_graph()

    def worker(self, state: State) -> Dict[str, Any]:
        """
        The 'worker' node of the graph. This is the main agent that performs the work.
        """
        # Construct the system message with instructions, success criteria, and any feedback.
        system_message = f"""You are a helpful assistant that can use tools to complete tasks.
    You keep working on a task until either you have a question or clarification for the user, or the success criteria is met.
    You have many tools to help you, including tools to browse the internet, navigating and retrieving web pages.
    You have a tool to run python code, but note that you would need to include a print() statement if you wanted to receive output.
    The current date and time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

    This is the success criteria:
    {state['success_criteria']}
    You should reply either with a question for the user about this assignment, or with your final response.
    If you have a question for the user, you need to reply by clearly stating your question. An example might be:

    Question: please clarify whether you want a summary or a detailed answer

    If you've finished, reply with the final answer, and don't ask a question; simply reply with the answer.
    """
        
        if state.get("feedback_on_work"):
            system_message += f"""
    Previously you thought you completed the assignment, but your reply was rejected because the success criteria was not met.
    Here is the feedback on why this was rejected:
    {state['feedback_on_work']}
    With this feedback, please continue the assignment, ensuring that you meet the success criteria or have a question for the user."""
        
        # Ensure there is a system message in the conversation history.
        messages = state["messages"]
        if not any(isinstance(m, SystemMessage) for m in messages):
            messages = [SystemMessage(content=system_message)] + messages
        else:
            for m in messages:
                if isinstance(m, SystemMessage):
                    m.content = system_message
                    break
        
        # Invoke the LLM with the tools and the conversation history.
        response = self.worker_llm_with_tools.invoke(messages)
        
        # Return the LLM's response to be added to the state.
        return {"messages": [response]}

    def worker_router(self, state: State) -> str:
        """
        A conditional edge that routes the graph based on the worker's output.
        """
        last_message = state["messages"][-1]
        # If the last message has tool calls, route to the 'tools' node.
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        # Otherwise, route to the 'evaluator' node.
        else:
            return "evaluator"
        
    def format_conversation(self, messages: List[Any]) -> str:
        """Helper function to format the conversation history for the evaluator."""
        conversation = "Conversation history:\n\n"
        for message in messages:
            if isinstance(message, HumanMessage):
                conversation += f"User: {message.content}\n"
            elif isinstance(message, AIMessage):
                text = message.content or "[Tool use]"
                conversation += f"Assistant: {text}\n"
        return conversation
        
    def evaluator(self, state: State) -> Dict[str, Any]:
        """
        The 'evaluator' node of the graph. It assesses the worker's performance.
        """
        last_response = state["messages"][-1].content

        system_message = """You are an evaluator that determines if a task has been completed successfully by an Assistant.
    Assess the Assistant's last response based on the given criteria. Respond with your feedback, and with your decision on whether the success criteria has been met,
    and whether more input is needed from the user."""
        
        user_message = f"""You are evaluating a conversation between the User and Assistant. You decide what action to take based on the last response from the Assistant.

    The entire conversation with the assistant, with the user's original request and all replies, is:
    {self.format_conversation(state['messages'])}

    The success criteria for this assignment is:
    {state['success_criteria']}

    And the final response from the Assistant that you are evaluating is:
    {last_response}

    Respond with your feedback, and decide if the success criteria is met by this response.
    Also, decide if more user input is required, either because the assistant has a question, needs clarification, or seems to be stuck and unable to answer without help.
    """
        if state.get("feedback_on_work"):
            user_message += f"\nAlso, note that in a prior attempt from the Assistant, you provided this feedback: {state['feedback_on_work']}"
            user_message += "\nIf you're seeing the Assistant repeating the same mistakes, then consider responding that user input is required."
        
        evaluator_messages = [SystemMessage(content=system_message), HumanMessage(content=user_message)]

        # Invoke the evaluator LLM to get structured feedback.
        eval_result = self.evaluator_llm_with_output.invoke(evaluator_messages)
        
        # Return the evaluation results to be updated in the state.
        return {
            "messages": [{"role": "assistant", "content": f"Evaluator Feedback on this answer: {eval_result.feedback}"}],
            "feedback_on_work": eval_result.feedback,
            "success_criteria_met": eval_result.success_criteria_met,
            "user_input_needed": eval_result.user_input_needed
        }

    def route_based_on_evaluation(self, state: State) -> str:
        """
        A conditional edge that routes the graph based on the evaluator's decision.
        """
        # If the task is done or needs user input, end the current run.
        if state["success_criteria_met"] or state["user_input_needed"]:
            return "END"
        # Otherwise, loop back to the 'worker' for another attempt.
        else:
            return "worker"

    async def build_graph(self):
        """
        Builds the LangGraph graph by defining nodes and edges.
        """
        graph_builder = StateGraph(State)

        # Add the nodes to the graph.
        graph_builder.add_node("worker", self.worker)
        # `ToolNode` is a pre-built node that executes tools.
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_node("evaluator", self.evaluator)

        # Define the edges and control flow.
        graph_builder.add_edge(START, "worker")
        graph_builder.add_conditional_edges("worker", self.worker_router, {"tools": "tools", "evaluator": "evaluator"})
        graph_builder.add_edge("tools", "worker")
        graph_builder.add_conditional_edges("evaluator", self.route_based_on_evaluation, {"worker": "worker", "END": END})

        # Compile the graph, enabling in-memory checkpointing.
        self.graph = graph_builder.compile(checkpointer=self.memory)

    async def run_superstep(self, message: str, success_criteria: str, history: list) -> list:
        """
        Runs a single "superstep" of the graph. This is the main entry point
        for processing a user request.
        """
        config = {"configurable": {"thread_id": self.sidekick_id}}

        # Initialize the state for this run.
        state = {
            "messages": [HumanMessage(content=message)],
            "success_criteria": success_criteria or "The answer should be clear and accurate",
            "feedback_on_work": None,
            "success_criteria_met": False,
            "user_input_needed": False
        }
        # Asynchronously invoke the graph with the initial state.
        result = await self.graph.ainvoke(state, config=config)
        
        # Format the output for the Gradio chat history.
        user_message = {"role": "user", "content": message}
        # The assistant's reply is the second to last message.
        assistant_reply = {"role": "assistant", "content": result["messages"][-2].content}
        # The evaluator's feedback is the last message.
        evaluator_feedback = {"role": "assistant", "content": result["messages"][-1].content}
        
        return (history or []) + [user_message, assistant_reply, evaluator_feedback]
    
    def cleanup(self):
        """
        Cleans up resources, such as closing the Playwright browser.
        """
        if self.browser:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.browser.close())
                if self.playwright:
                    loop.create_task(self.playwright.stop())
            except RuntimeError:
                # If no event loop is running, run the cleanup synchronously.
                asyncio.run(self.browser.close())
                if self.playwright:
                    asyncio.run(self.playwright.stop())

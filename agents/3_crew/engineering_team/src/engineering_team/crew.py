from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Use the @CrewBase decorator to define a crew configuration class.
# This class serves as a blueprint for creating and managing a group of agents and their tasks.
@CrewBase
class EngineeringTeam():
    """
    Defines the EngineeringTeam crew, which is responsible for designing,
    coding, and testing a software module based on provided requirements.
    """

    # --- Configuration ---
    # Load agent and task configurations from YAML files.
    # This approach separates the configuration from the code, making it easier to manage and modify.
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # --- Agent Definitions ---

    @agent
    def engineering_lead(self) -> Agent:
        """
        Defines the Engineering Lead agent.
        This agent is responsible for creating the initial design based on the requirements.
        """
        return Agent(
            config=self.agents_config['engineering_lead'],
            verbose=True,
        )

    @agent
    def backend_engineer(self) -> Agent:
        """
        Defines the Backend Engineer agent.
        This agent writes the Python code based on the design provided by the Engineering Lead.
        Code execution is enabled in a safe Docker environment.
        """
        return Agent(
            config=self.agents_config['backend_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Ensures code is run in a secure, isolated Docker container
            max_execution_time=500,      # Sets a timeout for code execution
            max_retry_limit=3            # Limits the number of retries on failure
        )
    
    @agent
    def frontend_engineer(self) -> Agent:
        """
        Defines the Frontend Engineer agent.
        This agent creates a simple Gradio UI to demonstrate the backend functionality.
        """
        return Agent(
            config=self.agents_config['frontend_engineer'],
            verbose=True,
        )
    
    @agent
    def test_engineer(self) -> Agent:
        """
        Defines the Test Engineer agent.
        This agent writes unit tests for the backend module to ensure its correctness.
        Code execution is enabled in a safe Docker environment.
        """
        return Agent(
            config=self.agents_config['test_engineer'],
            verbose=True,
            allow_code_execution=True,
            code_execution_mode="safe",  # Ensures code is run in a secure, isolated Docker container
            max_execution_time=500,      # Sets a timeout for code execution
            max_retry_limit=3            # Limits the number of retries on failure
        )

    # --- Task Definitions ---

    @task
    def design_task(self) -> Task:
        """
        Defines the design task.
        This task is assigned to the Engineering Lead to create the software design.
        """
        return Task(
            config=self.tasks_config['design_task']
        )

    @task
    def code_task(self) -> Task:
        """
        Defines the coding task.
        This task is assigned to the Backend Engineer to implement the design.
        """
        return Task(
            config=self.tasks_config['code_task'],
        )

    @task
    def frontend_task(self) -> Task:
        """
        Defines the frontend task.
        This task is assigned to the Frontend Engineer to create a UI.
        """
        return Task(
            config=self.tasks_config['frontend_task'],
        )

    @task
    def test_task(self) -> Task:
        """
        Defines the testing task.
        This task is assigned to the Test Engineer to write unit tests.
        """
        return Task(
            config=self.tasks_config['test_task'],
        )   

    # --- Crew Definition ---

    @crew
    def crew(self) -> Crew:
        """
        Assembles and configures the crew.
        This method brings together the defined agents and tasks and sets the execution process.
        """
        return Crew(
            agents=self.agents,  # The list of agents available to the crew
            tasks=self.tasks,    # The list of tasks to be executed
            process=Process.sequential,  # Tasks will be executed one after another in the defined order
            verbose=True,        # Enables detailed logging of the crew's execution
        )
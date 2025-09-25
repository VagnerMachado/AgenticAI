from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field
from typing import List
import os
from .tools.push_tool import PushNotificationTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

class TrendingCompany(BaseModel):
    """ A company that is in the news and attracting attention """
    name: str = Field(description="Company name")
    ticker: str = Field(description="Stock ticker symbol")
    reason: str = Field(description="Reason this company is trending in the news")

class TrendingCompanyList(BaseModel):
    """ List of multiple trending companies that are in the news """
    companies: List[TrendingCompany] = Field(description="List of companies trending in the news")

class TrendingCompanyResearch(BaseModel):
    """ Detailed research on a company """
    name: str = Field(description="Company name")
    market_position: str = Field(description="Current market position and competitive analysis")
    future_outlook: str = Field(description="Future outlook and growth prospects")
    investment_potential: str = Field(description="Investment potential and suitability for investment")

class TrendingCompanyResearchList(BaseModel):
    """ A list of detailed research on all the companies """
    research_list: List[TrendingCompanyResearch] = Field(description="Comprehensive research on all trending companies")


@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(config=self.agents_config['trending_company_finder'],
                     tools=[SerperDevTool()], memory=True)
    
    @agent
    def financial_researcher(self) -> Agent:
        return Agent(config=self.agents_config['financial_researcher'], 
                     tools=[SerperDevTool()])

    @agent
    def stock_picker(self) -> Agent:
        return Agent(config=self.agents_config['stock_picker'], 
                     tools=[PushNotificationTool()], memory=True)
    
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList,
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,
        )

    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
        )
    

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )

        # candidate embedder configs to try (covers different crewai/openai API shapes)
        candidate_embedder_configs = [            
            # include API key explicitly so chromadb/openai embedding sees it
            {"provider": "openai", "model": "text-embedding-3-small", "config": {"api_key": os.getenv("OPENAI_API_KEY")}},
            {"provider": "openai", "model_name": "text-embedding-3-small", "config": {"api_key": os.getenv("OPENAI_API_KEY")}},
            {"provider": "openai", "deployment": "text-embedding-3-small", "config": {"api_key": os.getenv("OPENAI_API_KEY")}},
            {"provider": "openai", "config": {"model": "text-embedding-3-small", "api_key": os.getenv("OPENAI_API_KEY")}},
            {"provider": "openai", "config": {"api_key": os.getenv("OPENAI_API_KEY")}},  # minimal
         ]

        # attempt to build RAGStorage with each candidate until one works
        short_term_storage = None
        entity_storage = None
        last_error = None
        for cfg in candidate_embedder_configs:
            try:
                short_term_storage = ShortTermMemory(
                    storage=RAGStorage(
                        embedder_config=cfg,
                        type="short_term",
                        path="./memory/"
                    )
                )
                entity_storage = EntityMemory(
                    storage=RAGStorage(
                        embedder_config=cfg,
                        type="short_term",
                        path="./memory/"
                    )
                )
                last_error = None
                break
            except TypeError as e:
                # record and try next config
                last_error = e

        if last_error is not None:
            # failed to create a compatible embedder config — fall back to no memory
            print("Warning: failed to construct RAGStorage with tried embedder configs:", last_error)
            # disable memory to allow the crew to run
            return Crew(
                agents=self.agents,
                tasks=self.tasks,
                process=Process.hierarchical,
                verbose=True,
                manager_agent=manager,
                memory=False,
                long_term_memory=LongTermMemory(
                    storage=LTMSQLiteStorage(
                        db_path="./memory/long_term_memory_storage.db"
                    )
                ),
            )

        # success: return crew with working short-term and entity memory
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            long_term_memory=LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            short_term_memory=short_term_storage,
            entity_memory=entity_storage,
        )
    
    # The original simpler version without the robust embedder config handling
    # @crew
    # def crew(self) -> Crew:
    #     """Creates the StockPicker crew"""

    #     manager = Agent(
    #         config=self.agents_config['manager'],
    #         allow_delegation=True
    #     )
            
    #     return Crew(
    #         agents=self.agents,
    #         tasks=self.tasks, 
    #         process=Process.hierarchical,
    #         verbose=True,
    #         manager_agent=manager,
    #         memory=True,
    #         # Long-term memory for persistent storage across sessions
    #         long_term_memory = LongTermMemory(
    #             storage=LTMSQLiteStorage(
    #                 db_path="./memory/long_term_memory_storage.db"
    #             )
    #         ),
    #         # Short-term memory for current context using RAG
    #         short_term_memory = ShortTermMemory(
    #             storage = RAGStorage(
    #                     embedder_config={
    #                         "provider": "openai",
    #                         "config": {
    #                             "model": 'text-embedding-3-small'
    #                         }
    #                     },
    #                     type="short_term",
    #                     path="./memory/"
    #                 )
    #             ),            # Entity memory for tracking key information about entities
    #         entity_memory = EntityMemory(
    #             storage=RAGStorage(
    #                 embedder_config={
    #                     "provider": "openai",
    #                     "config": {
    #                         "model": 'text-embedding-3-small'
    #                     }
    #                 },
    #                 type="short_term",
    #                 path="./memory/"
    #             )
    #         ),
    #     )

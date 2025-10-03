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
import inspect

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

        # Candidate configs with top-level keys only (no nested "config")
        candidate_configs = [
            {"provider": "openai", "model_name": "text-embedding-3-small", "api_key": os.getenv("OPENAI_API_KEY")},
            {"provider": "openai", "deployment": "text-embedding-3-small", "api_key": os.getenv("OPENAI_API_KEY")},  # Azure style
            {"provider": "openai", "model_name": "text-embedding-3-large", "api_key": os.getenv("OPENAI_API_KEY")},
            {"provider": "openai", "api_key": os.getenv("OPENAI_API_KEY")},  # minimal
        ]

        # Helper: prune kwargs to only those accepted by the provider constructor
        def prune_kwargs_for_provider(provider_name: str, cfg: dict) -> dict:
            if provider_name == "openai":
                try:
                    # import provider class directly and inspect its __init__
                    from chromadb.utils.embedding_functions.openai_embedding_function import OpenAIEmbeddingFunction
                    sig = inspect.signature(OpenAIEmbeddingFunction.__init__)
                    accepted = set(sig.parameters.keys()) - {"self", "args", "kwargs"}
                    # keep only accepted top-level keys
                    return {k: v for k, v in cfg.items() if k in accepted}
                except Exception:
                    # fallback: pass api_key and common names if inspection fails
                    allowed = {"model_name", "deployment", "api_key"}
                    return {k: v for k, v in cfg.items() if k in allowed}
            # other providers: no pruning here (extend as needed)
            return cfg

        # Attempt to build RAGStorage with each pruned candidate
        short_term_storage = None
        entity_storage = None
        last_error = None
        for cfg in candidate_configs:
            try:
                pruned = prune_kwargs_for_provider(cfg.get("provider"), cfg)
                # include provider separately so factory receives it too
                pruned_with_provider = dict(pruned)
                pruned_with_provider["provider"] = cfg["provider"]

                short_term_storage = ShortTermMemory(
                    storage=RAGStorage(
                        embedder_config=pruned_with_provider,
                        type="short_term",
                        path="./memory/"
                    )
                )
                entity_storage = EntityMemory(
                    storage=RAGStorage(
                        embedder_config=pruned_with_provider,
                        type="short_term",
                        path="./memory/"
                    )
                )
                last_error = None
                break
            except Exception as e:
                last_error = e
                print("RAGStorage try failed for config:", cfg, "error:", e)

        if last_error is not None:
            print("Warning: failed to construct RAGStorage with tried embedder configs:", last_error)
            # fallback: disable short/ entity memory to allow crew to run
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

        # success: return crew with working memory
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            long_term_memory = LongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path="./memory/long_term_memory_storage.db"
                )
            ),
            short_term_memory = short_term_storage,
            entity_memory = entity_storage,
        )
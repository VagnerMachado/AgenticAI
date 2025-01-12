# Import necessary components from other modules.
# Note: The 'agents' module is a custom library providing core agent functionalities.
from agents import Runner, trace, gen_trace_id
from search_agent import search_agent
from planner_agent import planner_agent, WebSearchItem, WebSearchPlan
from writer_agent import writer_agent, ReportData
from email_agent import email_agent
import asyncio

class ResearchManager:
    """
    Orchestrates the entire deep research process by coordinating a team of specialized agents.
    This class manages the flow from planning searches to sending a final report via email.
    """

    async def run(self, query: str):
        """
        Run the deep research process, yielding status updates and the final report.

        This is the main entry point for the research manager. It follows a sequential
        process of planning, searching, writing, and emailing.

        Args:
            query (str): The user's research query.
        
        Yields:
            str: Status updates throughout the process and the final markdown report.
        """
        # Generate a unique trace ID for observability.
        trace_id = gen_trace_id()
        with trace("Research trace", trace_id=trace_id):
            # Provide a link to the trace for debugging and monitoring.
            print(f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}")
            yield f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            
            yield "Starting research..."
            # 1. Plan the web searches required to answer the query.
            search_plan = await self.plan_searches(query)
            
            yield "Searches planned, starting to search..."
            # 2. Perform the web searches in parallel.
            search_results = await self.perform_searches(search_plan)
            
            yield "Searches complete, writing report..."
            # 3. Synthesize the search results into a detailed report.
            report = await self.write_report(query, search_results)
            
            yield "Report written, sending email..."
            # 4. Send the final report via email.
            await self.send_email(report)
            
            yield "Email sent, research complete."
            # 5. Yield the final report to be displayed in the UI.
            yield report.markdown_report

    async def plan_searches(self, query: str) -> WebSearchPlan:
        """
        Plan the web searches to be performed for the query using the planner_agent.
        """
        print("Planning searches...")
        # The `Runner.run` method executes a given agent with the provided input.
        result = await Runner.run(
            planner_agent,
            f"Query: {query}",
        )
        print(f"Will perform {len(result.final_output.searches)} searches")
        # The result's output is cast to the `WebSearchPlan` Pydantic model.
        return result.final_output_as(WebSearchPlan)

    async def perform_searches(self, search_plan: WebSearchPlan) -> list[str]:
        """
        Perform the web searches in parallel using asyncio.
        """
        print("Searching...")
        num_completed = 0
        # Create a list of asyncio tasks, one for each search item.
        tasks = [asyncio.create_task(self.search(item)) for item in search_plan.searches]
        results = []
        # Process tasks as they complete.
        for task in asyncio.as_completed(tasks):
            result = await task
            if result is not None:
                results.append(result)
            num_completed += 1
            print(f"Searching... {num_completed}/{len(tasks)} completed")
        print("Finished searching")
        return results

    async def search(self, item: WebSearchItem) -> str | None:
        """
        Perform a single web search using the search_agent.
        """
        input_str = f"Search term: {item.query}\nReason for searching: {item.reason}"
        try:
            result = await Runner.run(
                search_agent,
                input_str,
            )
            return str(result.final_output)
        except Exception as e:
            print(f"Search for '{item.query}' failed: {e}")
            return None

    async def write_report(self, query: str, search_results: list[str]) -> ReportData:
        """
        Write the final report using the writer_agent.
        """
        print("Writing report...")
        input_str = f"Original query: {query}\nSummarized search results: {search_results}"
        result = await Runner.run(
            writer_agent,
            input_str,
        )
        print("Finished writing report")
        return result.final_output_as(ReportData)
    
    async def send_email(self, report: ReportData) -> None:
        """
        Send the final report as an email using the email_agent.
        """
        print("Sending email...")
        await Runner.run(
            email_agent,
            report.markdown_report,
        )
        print("Email sent")
        return
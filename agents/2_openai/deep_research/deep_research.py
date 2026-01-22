import gradio as gr
from dotenv import load_dotenv
from research_manager import ResearchManager

# Load environment variables from a .env file.
load_dotenv(override=True)

# --- Core Application Logic ---

async def run(query: str):
    """
    Runs the deep research process for a given query and streams the results.

    This asynchronous generator function initializes a ResearchManager and calls its `run` method.
    It yields each chunk of output received from the manager, allowing for real-time
    updates in the Gradio interface.

    Args:
        query (str): The research topic provided by the user.
    """
    # Create a new ResearchManager instance for each request.
    # The `run` method orchestrates the entire research process, from planning to emailing the report.
    async for chunk in ResearchManager().run(query):
        # Yield each piece of output (status updates or the final report) as it becomes available.
        yield chunk

# --- Gradio User Interface Definition ---

# Create a Gradio Blocks interface for a custom layout.
with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("# Deep Research")
    
    # UI Components
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")
    
    # --- Event Handling ---
    
    # When the 'Run' button is clicked, call the `run` function with the query as input.
    # The output of the `run` function (streamed chunks) will be displayed in the `report` component.
    run_button.click(fn=run, inputs=query_textbox, outputs=report)
    
    # Allow submitting the query by pressing Enter in the textbox.
    query_textbox.submit(fn=run, inputs=query_textbox, outputs=report)

# Launch the Gradio application and open it in the default web browser.
ui.launch(inbrowser=True)

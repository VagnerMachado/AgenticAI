import gradio as gr
from sidekick import Sidekick

# --- Core Application Logic ---

async def setup():
    """
    Initializes the Sidekick agent.
    This function is called when the Gradio UI is first loaded.
    It creates a new instance of the Sidekick and runs its asynchronous setup process.
    """
    sidekick = Sidekick()
    await sidekick.setup()
    return sidekick

async def process_message(sidekick, message, success_criteria, history):
    """
    Processes a user's message by invoking the Sidekick agent.
    
    Args:
        sidekick: The current instance of the Sidekick agent.
        message (str): The user's request.
        success_criteria (str): The success criteria for the task.
        history (list): The chat history.

    Returns:
        A tuple containing the updated chat history and the Sidekick instance.
    """
    # Run a "superstep" of the Sidekick's graph with the user's input.
    results = await sidekick.run_superstep(message, success_criteria, history)
    # Return the new conversation history and the (potentially updated) sidekick state.
    return results, sidekick
    
async def reset():
    """
    Resets the application state.
    This function creates a new Sidekick instance and clears the UI components.
    """
    new_sidekick = Sidekick()
    await new_sidekick.setup()
    # Return empty strings and None to clear the message box, success criteria, and chatbot.
    return "", "", None, new_sidekick

def free_resources(sidekick):
    """
    Cleans up resources when the application is closed.
    This function is registered as a delete_callback for the Gradio State.
    """
    print("Cleaning up")
    try:
        if sidekick:
            # Call the cleanup method on the Sidekick instance to close browser, etc.
            sidekick.cleanup()
    except Exception as e:
        print(f"Exception during cleanup: {e}")

# --- Gradio User Interface Definition ---

# Create a Gradio Blocks interface for more control over the layout.
with gr.Blocks(title="Sidekick", theme=gr.themes.Default(primary_hue="emerald")) as ui:
    gr.Markdown("## Sidekick Personal Co-Worker")
    
    # Use gr.State to hold the Sidekick instance. This allows it to persist
    # across interactions without being part of the visible UI.
    # The `delete_callback` ensures cleanup is called when the user session ends.
    sidekick = gr.State(delete_callback=free_resources)
    
    with gr.Row():
        chatbot = gr.Chatbot(label="Sidekick", height=300, type="messages")
    
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to the Sidekick")
        with gr.Row():
            success_criteria = gr.Textbox(show_label=False, placeholder="What are your success critiera?")
    
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")
        
    # --- Event Handling ---

    # `ui.load` runs the `setup` function once when the UI is loaded in the browser.
    ui.load(setup, [], [sidekick])
    
    # Wire up the UI components to the processing functions.
    # The `process_message` function is called when the user submits the message,
    # success criteria, or clicks the "Go!" button.
    message.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    success_criteria.submit(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    go_button.click(process_message, [sidekick, message, success_criteria, chatbot], [chatbot, sidekick])
    
    # The `reset` function is called when the "Reset" button is clicked.
    reset_button.click(reset, [], [message, success_criteria, chatbot, sidekick])

# Launch the Gradio application. `inbrowser=True` opens it in a new tab.
ui.launch(inbrowser=True)
import os
from typing import Dict

import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content, To
# Import necessary components from the custom 'agents' library.
from agents import Agent, function_tool

# --- Tool Definition ---

# The `@function_tool` decorator wraps a Python function, making it available
# as a tool for an agent to use. The agent can intelligently decide when to call
# this function and what arguments to pass based on its instructions.
@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """
    Send an email with the given subject and HTML body using the SendGrid API.

    Args:
        subject (str): The subject line of the email.
        html_body (str): The HTML content of the email body.

    Returns:
        Dict[str, str]: A dictionary indicating the status of the operation.
    """
    # Initialize the SendGrid client with the API key from environment variables.
    # IMPORTANT: Ensure the 'SENDGRID_API_KEY' environment variable is set.
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    
    # --- Email Configuration ---
    # IMPORTANT: These email addresses should be configured for your specific use case.
    # The `from_email` must be a verified sender in your SendGrid account.
    from_email = Email("vagnermachado84@gmail.com") 
    to_email = To("vagnermachado84@hotmail.com") 
    
    # Create the email content and mail object.
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    
    # Send the email.
    response = sg.client.mail.send.post(request_body=mail)
    print("Email response status code:", response.status_code)
    
    return {"status": "success"}

# --- Instructions for the Agent ---

# Define the system instructions for the email agent.
# These instructions tell the agent its purpose: to take a report and use its tool
# to send it as a nicely formatted HTML email.
INSTRUCTIONS = """You are able to send a nicely formatted HTML email based on a detailed report.
You will be provided with a detailed report. You should use your tool to send one email, providing the 
report converted into clean, well presented HTML with an appropriate subject line."""

# --- Agent Definition ---

# Create an instance of the `Agent` class to define the email agent.
email_agent = Agent(
    name="Email agent",
    instructions=INSTRUCTIONS,
    # Provide the agent with the `send_email` tool.
    tools=[send_email],
    model="gpt-4o-mini",
)

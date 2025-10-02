#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime

from coder.crew import Coder

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

assignment = 'write a python script to create a REST API using FastAPI that returns the current date and time in JSON format.' \
'The API takes a country as parameter for the time. If the country has multiple time zones, return the time for the capital city.' \
'Countries and their capitals can be found at http://worldtimeapi.org/ sand example http://worldtimeapi.org/api/timezone/America/New_York' \
'The ouptput should be like {"current_datetime": "2023-10-05T14:48:00Z"}. based on the call to previous provider response' \
'The API should have a single endpoint /current_datetime that responds to GET requests.' \
'The code should be well-structured and include error handling.' \
'The code should be compatible with Python 3.8 or higher.' \
'The code should include instructions on how to run the API server.' \
'In addition to the code, and output sample, create a section listing all necessary dependencies.' \
'Ensure that the API is secure and can handle multiple requests efficiently.' \
'Finally, provide a brief explanation of how the code works and any assumptions made.' \
'All code, sample output, requirement and dependencies should be output to output/code_and_output.txt'\


def run():
    """
    Run the crew.
    """
    inputs = {
        'assignment': assignment,
    }
    
    result = Coder().crew().kickoff(inputs=inputs)
    print(result.raw)





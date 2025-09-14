#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from debate.crew import Debate

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

# NOTE: INSTEAD OF RUNNING WITH CREWAI, I HAD TO RUN WITH PYTHON VIA
#  python -c "from src.debate.crew import Debate; crew = Debate().crew(); result = crew.kickoff(); print(result)"
 
# WHEN RUNNING THE CREW THE SAME ISSUE HAD WITH CHROMA DB SHOWED UP AGAIN
#  Running the Crew
#   × Failed to build `chroma-hnswlib==0.7.6`
#   ├─▶ The build backend returned an error
#   ╰─▶ Call to `setuptools.build_meta.build_wheel` failed (exit code: 1)

#       [stdout]
#       running bdist_wheel
#       running build
#       running build_ext
#       building 'hnswlib' extension

#       [stderr]
#       error: Microsoft Visual C++ 14.0 or greater is
#       required. Get it with "Microsoft C++ Build Tools":
#       https://visualstudio.microsoft.com/visual-cpp-build-tools/

# PS D:\V\Documents\Workspace\7. AI Agent\agents\3_crew\debate> python -c "from src.debate.crew import Debate; crew = Debate().crew(); result = crew.kickoff(); print(result)"

def run():
    """
    Run the crew.
    """
    inputs = {
        'motion': 'There needs to be strict laws to regulate LLMs',
    }
    
    try:
        result = Debate().crew().kickoff(inputs=inputs)
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

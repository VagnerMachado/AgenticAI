# ...existing code...
#!/usr/bin/env python
import sys
import warnings
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# load .env before importing modules that may read env vars
# use parents[4] for repo root 'agents', or parents[2] if .env is inside stock_picker
env_path = Path(__file__).resolve().parents[4] / ".env"
print("Loading .env from:", env_path, "exists:", env_path.exists())
load_dotenv(env_path)
# debug: show whether OPENAI_API_KEY loaded and print a masked preview (safe)
import os
_openai_key = os.getenv("OPENAI_API_KEY")
print("OPENAI_API_KEY loaded:", _openai_key is not None)
if _openai_key:
    # mask middle of key, show first/last 4 chars
    if len(_openai_key) > 8:
        masked = f"{_openai_key[:4]}{'*'*(len(_openai_key)-8)}{_openai_key[-4:]}"
    else:
        masked = "*" * len(_openai_key)
    print("OPENAI_API_KEY (masked):", masked)

from stock_picker.crew import StockPicker


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the research crew.
    """
    # load .env from project root (adjust parents index if needed)
    inputs = {
        'sector': 'Health Care and Techonology stocks',
        "current_date": str(datetime.now())
    }

    # Create and run the crew
    result = StockPicker().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL DECISION ===\n\n")
    print(result.raw)


if __name__ == "__main__":
    run()


# Course Information

- General guide: 
	- https://edwarddonner.com/2025/04/21/the-complete-agentic-ai-engineering-course/
	
- Udemy:
	- https://cglearning.udemy.com/course/the-complete-agentic-ai-engineering-course/learn/lecture/49739779#overview
	- https://cglearning.udemy.com/course/llm-engineering-master-ai-and-large-language-models/
	
We install the Cursor IDE and UV package manager ( https://github.com/astral-sh/uv/releases)

- Add uv to path
- Run `uv sync` from root of repo in cursor terminal so `uv` can manage all dependencies.
- `uv run <script>`  will run python script in the virtual environment


We also installed Ollaman local. I went with qwen 0.6b as it is a light mode for exploration.
I need to review the Path Variables and add it to System Variables as well.

You might need to restart Cursor (and maybe reboot). Then open a Terminal (control+\`) and run `ollama serve`

Useful Ollama commands (run these in the terminal, or with an exclamation mark in notebook):

`ollama pull <model_name>` downloads a model locally  
`ollama ls` lists all the models you've downloaded  
`ollama rm <model_name>` deletes the specified model from your downloads

---

The error indicates that `uv` is not installed or not in your PATH. Here's how to install and use `uv`:

## Install uv

**Option 1: Using pip (recommended)**
```bash
pip install uv
```

**Option 2: Using PowerShell (Windows)**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Option 3: Using curl (if available)**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## After installation, restart your terminal/PowerShell

Close and reopen your terminal, then verify installation:
```bash
uv --version
```

## Using uv in your project

Once installed, you can use uv to manage your Python environment:

```bashuv
# Create a virtual environment
uv venv

# Activate it (Windows)
.venv\Scripts\activate

#If the above fails due to execution policy, then in the terminal you run
 Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

# Install packages
uv pip install openai-agents sendgrid python-dotenv pydantic

# Or install from requirements.txt
uv pip install -r requirements.txt
```

The `uv` tool is a fast Python package installer and resolver, similar to pip but much faster. It's particularly useful for managing dependencies in Python projects.
 
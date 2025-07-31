
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
 
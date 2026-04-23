from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.models.anthropic_llm import Claude
from google.adk.models import Gemini
from google.genai import Client
from fastmcp import FastMCP
import os

mcp = FastMCP("Vibe Swarm Tools")

# Initialize Vertex AI Client for Gemini models
gemini_client = Client(
    vertexai=True, 
    project=os.environ.get("GOOGLE_CLOUD_PROJECT", "firsttestproject-343414"), 
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-east5")
)

# 4. The High-Speed Memory Layer & Execution Tools
@mcp.tool()
def get_code_context(query: str):
    """Calls Vertex Matching Engine to get sub-ms code snippets."""
    print(f"Executing Vertex Vector Search for: {query}")
    return [f"Match 1 for {query}: def demo(): pass", f"Match 2 for {query}: class Demo: pass"]

@mcp.tool()
def write_project_file(filepath: str, content: str) -> str:
    """Writes a file to the project workspace. Use this to build both frontend and backend code."""
    import os
    # Ensure safe path within workspace
    safe_path = os.path.abspath(os.path.join("workspace", filepath))
    if not safe_path.startswith(os.path.abspath("workspace")):
        return "Error: Invalid path."
        
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    with open(safe_path, "w") as f:
        f.write(content)
    return f"Successfully wrote to {filepath}"

@mcp.tool()
def read_project_file(filepath: str) -> str:
    """Reads a file from the project workspace. Use this to read memory files like history_recap.md."""
    import os
    safe_path = os.path.abspath(os.path.join("workspace", filepath))
    if not safe_path.startswith(os.path.abspath("workspace")) or not os.path.exists(safe_path):
        return f"File {filepath} not found or does not exist yet."
    with open(safe_path, "r") as f:
        return f.read()

@mcp.tool()
def generate_asset(prompt: str, filename: str) -> str:
    """Uses the Nano Banana model to generate image assets based on the prompt."""
    import os
    print(f"Nano Banana Model generating asset for: {prompt}")
    
    # Simulate Nano Banana model generating an SVG image
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300">
        <rect width="100%" height="100%" fill="#ffeaa7"/>
        <text x="50%" y="50%" font-family="Arial" font-size="20" fill="#2d3436" text-anchor="middle" dy=".3em">
            Nano Banana Gen: {prompt}
        </text>
    </svg>'''
    
    safe_path = os.path.abspath(os.path.join("workspace", "public", "assets", filename))
    os.makedirs(os.path.dirname(safe_path), exist_ok=True)
    with open(safe_path, "w") as f:
        f.write(svg_content)
    return f"Asset {filename} generated successfully."

# 3B. Define the Heterogeneous Worker Pool (Developers)
gemini_worker_model = f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT', 'firsttestproject-343414')}/locations/global/publishers/google/models/gemini-3.1-pro-preview"
gemini_worker = LlmAgent(
    model=Gemini(model=gemini_worker_model, client=gemini_client),
    name="gemini_worker",
    tools=[get_code_context, read_project_file, write_project_file, generate_asset],
    instruction="""You are a Developer (Data & Scaffolding Worker).
Trigger: Task delegated by the Tech Lead (Architect).
Mandate: 
1. Use `write_project_file` to write large data files, base HTML structure, or massive configurations.
2. Use `generate_asset` to create large batches of SVG assets.
CRITICAL RULE: All web files (HTML, CSS, JS, assets) MUST be written inside the `public/` directory (e.g., `public/index.html`, `public/js/data.js`).
Always break large files into modular components if necessary. When your specific task is done, state "TASK_COMPLETE" to return control to the Architect."""
)

claude_worker = LlmAgent(
    model=Claude(model="claude-sonnet-4-6"), 
    name="claude_worker", 
    tools=[get_code_context, read_project_file, write_project_file], 
    instruction="""You are a Developer (Logic & Styling Worker). 
Trigger: Task delegated by the Tech Lead (Architect).
Mandate:
1. Use `write_project_file` to implement complex business logic (e.g., cart.js, routing).
2. Write intricate CSS animations, responsive breakpoints, and styling.
3. CRITICAL RULE: All web files (HTML, CSS, JS) MUST be written inside the `public/` directory (e.g., `public/css/style.css`).
4. CRITICAL CSS RULE: You must explicitly link the CSS in the HTML head using: <link rel="stylesheet" href="style.css" />
5. TOOL OPTIMIZATION RULE: LLM function calls can fail if the `content` string is thousands of lines long. To prevent errors, ALWAYS break large codebases (especially CSS) into modular, smaller files (e.g., base.css, nav.css, layout.css) and write them sequentially, then @import them in the main style.css file.
When your specific task is done, state "TASK_COMPLETE" to return control to the Architect."""
)      

# 3A. Define the Architect (Tech Lead & Validator)
architect_model_path = f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT', 'firsttestproject-343414')}/locations/global/publishers/anthropic/models/claude-opus-4-6"
architect = LlmAgent(
    model=Claude(model=architect_model_path), 
    name="architect", 
    tools=[read_project_file, write_project_file],
    instruction="""You are the Tech Lead (Architect).
You manage the Developer pool (`gemini_worker` and `claude_worker`). 

Workflow:
1. The Captain (Project Manager) gives you a task.
2. Create a blueprint and write it to 'DECISIONS.md' using `write_project_file`.
   - CRITICAL RULE: Your blueprint MUST specify that all web files are placed in the `public/` directory (e.g., `public/index.html`, `public/css/style.css`).
3. Use `transfer_to_agent` to delegate work to your developers. 
   - `gemini_worker` for heavy data/HTML/assets.
   - `claude_worker` for complex JS/CSS.
4. When the developers return "TASK_COMPLETE", you MUST validate their code using `read_project_file`.
5. If the code is buggy or incomplete, send it back to the developers for fixes.
6. Once you are satisfied the code matches the blueprint, state "ARCHITECTURE_IMPLEMENTED" to report back to the Captain.""",
    sub_agents=[gemini_worker, claude_worker]
) 

# Define the Janitor
janitor_model_path = f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT', 'firsttestproject-343414')}/locations/global/publishers/google/models/gemini-3.1-flash-lite-preview"
janitor_agent = LlmAgent(
    model=Gemini(model=janitor_model_path, client=gemini_client),
    name="janitor",
    tools=[read_project_file, write_project_file],
    instruction="""You are the Janitor (Context Hygiene).
Trigger: Invoked by the Project Manager (Captain).
Mandate: Compress the current conversation and completed tasks into a dense 500-token summary. 
Use `write_project_file` to update 'history_recap.md'. Include a brief recap of files modified.
CRITICAL: Once you have updated the memory files, you must output the exact phrase: "ALL_TASKS_COMPLETE" and stop calling tools."""
)

# 1. Define the Captain (Root Orchestrator / Project Manager)
captain_model_path = f"projects/{os.environ.get('GOOGLE_CLOUD_PROJECT', 'firsttestproject-343414')}/locations/global/publishers/google/models/gemini-3.1-pro-preview"
captain_agent = LlmAgent(
    model=Gemini(model=captain_model_path, client=gemini_client),
    name="captain",
    instruction="""You are the Project Manager (Captain).
Trigger: Turn Start / New Request.

Workflow:
1. Analyze the user's vibe and break it into macro-tasks. Check 'TODO.md' if it exists.
2. Use `transfer_to_agent` to delegate a macro-task to your Tech Lead (`architect`). 
3. The Tech Lead will command the developers and build the feature, then return "ARCHITECTURE_IMPLEMENTED".
4. Check if all macro-tasks for the initial plan are complete.
5. If more tasks remain, delegate the next one to the `architect`.
6. If the entire project is complete, you MUST use `transfer_to_agent` to route to the `janitor` to compress the memory and conclude the session.""",
    sub_agents=[architect, janitor_agent]
)

# 3C. Implement the Janitor logic (Context Compaction)
def trigger_janitor_compaction(current_tokens: int):
    """
    Triggered periodically or via ADK's SessionState.
    """
    if current_tokens > 150000:
        print("Token limit exceeded! Engaging janitor_agent to write summary...")
        return True
    return False

if __name__ == "__main__":
    print("Agent definitions loaded successfully.")

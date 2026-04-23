import os
import asyncio
import base64
import shutil
import json
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from agent import write_project_file, generate_asset, captain_agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import uvicorn

# Ensure the app can reach Vertex AI in the correct region
os.environ["GOOGLE_CLOUD_PROJECT"] = "firsttestproject-343414"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GEMINI_USE_VERTEX"] = "true"

app = FastAPI(title="Vibe Agentic Swarm Demo")

# Shared runner for iterative state across requests in the demo
global_runner = InMemoryRunner(agent=captain_agent, app_name='vibe_swarm')

def write_default_docs():
    os.makedirs(os.path.join("workspace", "public"), exist_ok=True)
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vibe Agentic Swarm - Docs</title>
    <style>
        body { font-family: system-ui, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 2rem; background: #f8f9fa; }
        h1 { color: #2c3e50; font-size: 2.5rem; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem;}
        h2 { color: #34495e; margin-top: 2rem; }
        .card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 1.5rem; }
        .role { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
        .role-icon { font-size: 2rem; }
        .btn { background: #3498db; color: white; border: none; padding: 10px 20px; font-size: 1.1rem; border-radius: 5px; cursor: pointer; transition: 0.2s; }
        .btn:hover { background: #2980b9; }
        code { background: #eee; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>⚡ Vibe Agentic Swarm Demo</h1>
    <p class="lead">Welcome to the 2026 Breakthrough in autonomous software generation. This environment leverages a multi-agent swarm to architect, build, and deploy full-stack applications from simple "vibe" prompts.</p>
    
    <div class="card">
        <h2>How It Works</h2>
        <div class="role">
            <div class="role-icon">🧑‍✈️</div>
            <div><strong>1. The Captain (Topic Manager)</strong><br>Powered by <em>Gemini 3.1 Pro</em>. Analyzes your prompt, determines the scope, and orchestrates the swarm.</div>
        </div>
        <div class="role">
            <div class="role-icon">📐</div>
            <div><strong>2. The Architect (Master Planner)</strong><br>Powered by <em>Claude Opus 4.6</em>. Reads project history, creates a high-IQ blueprint in <code>DECISIONS.md</code>, and dynamically routes tasks to the worker pool.</div>
        </div>
        <div class="role">
            <div class="role-icon">🏗️</div>
            <div><strong>3. Data & Scaffolding Worker</strong><br>Powered by <em>Gemini 3.1 Pro</em>. Executes heavy data generation, massive scaffolding, and SVG asset creation seamlessly.</div>
        </div>
        <div class="role">
            <div class="role-icon">👷</div>
            <div><strong>4. Logic & Styling Worker</strong><br>Powered by <em>Claude Sonnet 4.6</em>. Executes complex JavaScript business logic, dynamic components, and nuanced CSS styling.</div>
        </div>
        <div class="role">
            <div class="role-icon">🧹</div>
            <div><strong>5. The Janitor (Context Hygiene)</strong><br>Powered by <em>Gemini 3.1 Flash Lite</em>. Compresses the session context into <code>history_recap.md</code> for durable memory.</div>
        </div>
    </div>

    <div class="card">
        <h2>Ready to build?</h2>
        <p>Use the terminal on the right to enter your prompt. If you want to clear the memory and start a completely new project, click the button below.</p>
        <button class="btn" onclick="window.parent.resetWorkspace()">🔄 Start from Scratch</button>
    </div>
</body>
</html>"""
    with open(os.path.join("workspace", "public", "index.html"), "w") as f:
        f.write(html)

def reset_workspace():
    if os.path.exists("workspace"):
        shutil.rmtree("workspace")
    write_default_docs()

# Unconditionally reset the workspace on startup to clear any cached container files
reset_workspace()

# Basic Authentication Middleware
@app.middleware("http")
async def basic_auth(request: Request, call_next):
    # Allow health check to pass without auth for GCP Cloud Run
    if request.url.path == "/health":
        return await call_next(request)
        
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Basic "):
        return Response("Unauthorized. Please provide Basic Auth credentials.", status_code=401, headers={"WWW-Authenticate": "Basic"})
        
    try:
        encoded_credentials = auth_header.split(" ")[1]
        decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
        username, password = decoded_credentials.split(":", 1)
        
        if username != "admin" or password != "vibe2026":
            return Response("Unauthorized. Invalid credentials.", status_code=401, headers={"WWW-Authenticate": "Basic"})
    except Exception:
        return Response("Unauthorized. Invalid auth format.", status_code=401, headers={"WWW-Authenticate": "Basic"})
        
    return await call_next(request)

app.mount("/site", StaticFiles(directory=os.path.join("workspace", "public")), name="site")

@app.get("/")
def root():
    """Return an interactive web UI to prompt the swarm."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vibe Agentic Swarm Demo</title>
        <style>
            body { 
                font-family: monospace; 
                background: #1e1e1e; 
                color: #00ff00; 
                margin: 0; 
                padding: 0; 
                display: flex; 
                height: 100vh; 
                width: 100vw; 
                overflow: hidden; 
            }
            .left-pane { 
                flex: 1; 
                background: #ffffff; 
                border-right: 2px solid #333; 
                position: relative;
            }
            iframe { 
                width: 100%; 
                height: 100%; 
                border: none; 
            }
            .right-pane { 
                flex: 0 0 500px; 
                display: flex; 
                flex-direction: column; 
                padding: 1.5rem; 
                box-sizing: border-box; 
                background: #1e1e1e; 
            }
            h1 { 
                font-size: 1.5rem; 
                margin-top: 0; 
                margin-bottom: 0.5rem; 
                text-align: center; 
            }
            .subtitle {
                text-align: center;
                font-size: 0.9rem;
                color: #888;
                margin-bottom: 1rem;
            }
            #output { 
                flex: 1; 
                background: #000; 
                padding: 1rem; 
                border: 1px solid #333; 
                overflow-y: auto; 
                white-space: pre-wrap; 
                margin-bottom: 1rem; 
                border-radius: 5px;
            }
            .input-area { 
                display: flex; 
                flex-direction: column; 
                gap: 0.5rem; 
                flex-shrink: 0;
            }
            label {
                font-weight: bold;
            }
            textarea { 
                width: 100%; 
                height: 80px; 
                background: #000; 
                color: #00ff00; 
                border: 1px solid #333; 
                padding: 0.5rem; 
                font-family: monospace; 
                box-sizing: border-box; 
                resize: vertical;
                border-radius: 5px;
            }
            button { 
                background: #00ff00; 
                color: #000; 
                border: none; 
                padding: 0.8rem; 
                cursor: pointer; 
                font-weight: bold; 
                width: 100%; 
                border-radius: 5px;
                text-transform: uppercase;
            }
            button:hover { background: #00cc00; }
            .btn-danger { background: #ff4444; margin-top: 0.5rem; }
            .btn-danger:hover { background: #cc0000; }
            a { color: #00ff00; }
            .preview-placeholder { 
                position: absolute; 
                top: 50%; 
                left: 50%; 
                transform: translate(-50%, -50%); 
                color: #888; 
                font-family: sans-serif; 
                text-align: center; 
                pointer-events: none; 
            }
        </style>
    </head>
    <body>
        <div class="left-pane">
            <div id="placeholder" class="preview-placeholder" style="display:none;">
                <h2>Live Website Preview</h2>
                <p>The generated site will appear here.</p>
            </div>
            <iframe id="previewFrame" src="/site/index.html"></iframe>
        </div>
        <div class="right-pane">
            <h1>Vibe Agentic Swarm Demo</h1>
            <div class="subtitle">powered by Gemini & Claude</div>
            
            <div id="output">System ready... Waiting for instructions.</div>
            
            <div class="input-area">
                <label for="promptBox">Enter your prompt to build or modify the full-stack application:</label>
                <textarea id="promptBox" placeholder="e.g. build me an ecommerce website..."></textarea>
                <button onclick="submitPrompt()">Engage Swarm</button>
                <button class="btn-danger" onclick="resetWorkspace()">Reset Workspace</button>
            </div>
        </div>
        <script>
            let currentSessionId = null;
            
            async function resetWorkspace() {
                if(!confirm("Clear all files and start from scratch?")) return;
                const out = document.getElementById('output');
                out.innerHTML = "Resetting workspace...\\n";
                try {
                    await fetch('/reset', {method: 'POST'});
                    currentSessionId = null;
                    document.getElementById('previewFrame').src = "/site/index.html?t=" + new Date().getTime();
                    out.innerHTML = "System ready... Waiting for instructions.\\n";
                } catch(e) {
                    out.innerHTML = "Error: " + e.message;
                }
            }
            
            async function submitPrompt() {
                const promptBox = document.getElementById('promptBox');
                const prompt = promptBox.value;
                const out = document.getElementById('output');
                const frame = document.getElementById('previewFrame');
                
                if(!prompt) return;
                
                out.innerHTML += "\\n\\n> " + prompt + "\\nInitializing connection to Swarm...\\n";
                out.scrollTop = out.scrollHeight;
                promptBox.value = ""; // clear box
                
                try {
                    const res = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: prompt, session_id: currentSessionId })
                    });
                    
                    const reader = res.body.getReader();
                    const decoder = new TextDecoder("utf-8");
                    
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;
                        
                        const chunk = decoder.decode(value, {stream: true});
                        const lines = chunk.split("\\n");
                        for (let line of lines) {
                            if (line.startsWith("data: ")) {
                                try {
                                    const data = JSON.parse(line.substring(6));
                                    if (data.type === 'session') {
                                        currentSessionId = data.session_id;
                                    } else if (data.type === 'message' || data.type === 'status' || data.type === 'error') {
                                        out.innerHTML += data.content + "\\n";
                                        out.scrollTop = out.scrollHeight;
                                    } else if (data.type === 'complete') {
                                        out.innerHTML += "\\n[Task Complete. Refreshing preview...]\\n";
                                        out.scrollTop = out.scrollHeight;
                                        // Force cache break to refresh iframe
                                        frame.src = data.site_url + "?t=" + new Date().getTime();
                                    }
                                } catch(e) {
                                    console.error("Error parsing stream chunk:", e);
                                }
                            }
                        }
                    }
                } catch(e) {
                    out.innerHTML += "\\nError: " + e.message;
                    out.scrollTop = out.scrollHeight;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/reset")
def reset_endpoint():
    """Wipes the workspace and restores the default documentation."""
    reset_workspace()
    return {"status": "success"}

@app.post("/chat")
async def chat_endpoint(request: Request):
    """
    Endpoint for interacting with the Captain using SSE for long-running ADK tasks.
    Maintains iterative session context.
    """
    data = await request.json()
    prompt = data.get("prompt", "")
    session_id = data.get("session_id", None)
    
    async def event_generator():
        yield f"data: {json.dumps({'type': 'status', 'content': 'Swarm engaged. Analyzing vibe and generating assets...'})}\n\n"
        await asyncio.sleep(0.1) # Yield control to flush
        
        try:
            nonlocal session_id
            session = None
            if session_id:
                try:
                    session = await global_runner.session_service.get_session(app_name='vibe_swarm', user_id='user1', session_id=session_id)
                except Exception:
                    pass
            
            if not session:
                session = await global_runner.session_service.create_session(app_name='vibe_swarm', user_id='user1')
                session_id = session.id
                
            yield f"data: {json.dumps({'type': 'session', 'session_id': session_id})}\n\n"
            await asyncio.sleep(0.1)
            
            content = types.Content(role='user', parts=[types.Part.from_text(text=prompt)])
            
            # Custom Retry Logic for 429 Quota Exhaustion
            max_retries = 5
            cooldowns = [5, 10, 20, 30, 30]
            attempt = 0
            success = False
            
            while attempt < max_retries and not success:
                try:
                    while True:
                        async for event in global_runner.run_async(user_id='user1', session_id=session_id, new_message=content):
                            author = getattr(event, "author", "system")

                            if hasattr(event, "content") and event.content and hasattr(event.content, "parts"):
                                for part in event.content.parts:
                                    if hasattr(part, "text") and part.text:
                                        chunk = f"**[{author}]**: {part.text}\n"
                                        yield f"data: {json.dumps({'type': 'message', 'content': chunk})}\n\n"
                                        await asyncio.sleep(0.1)

                                        if "ALL_TASKS_COMPLETE" in part.text:
                                            yield f"data: {json.dumps({'type': 'complete', 'site_url': '/site/index.html'})}\n\n"
                                            return 

                                    elif hasattr(part, "function_call") and part.function_call:
                                        tool_name = part.function_call.name
                                        args_str = ""
                                        if hasattr(part.function_call, "args") and part.function_call.args:
                                            args = part.function_call.args
                                            if tool_name == "write_project_file" and "filepath" in args:
                                                args_str = f" (`{args['filepath']}`)"
                                            elif tool_name == "read_project_file" and "filepath" in args:
                                                args_str = f" (`{args['filepath']}`)"
                                            elif tool_name == "generate_asset" and "filename" in args:
                                                args_str = f" (`{args['filename']}`)"
                                            elif tool_name == "get_code_context" and "query" in args:
                                                query = args['query'] if len(args['query']) < 30 else args['query'][:27] + "..."
                                                args_str = f" (`\"{query}\"`)"

                                        chunk = f"**[{author}]** is using tool: `{tool_name}`{args_str}...\n"
                                        yield f"data: {json.dumps({'type': 'message', 'content': chunk})}\n\n"
                                        await asyncio.sleep(0.1)

                            elif isinstance(event, str):
                                yield f"data: {json.dumps({'type': 'message', 'content': event})}\n\n"
                                await asyncio.sleep(0.1)

                        # Check if the session is actually done, or if an agent just transferred control back
                        # and we need to prompt the captain to continue orchestration.
                        session = await global_runner.session_service.get_session(app_name='vibe_swarm', user_id='user1', session_id=session_id)
                        
                        # Tell the Captain to evaluate the current state.
                        # It will check if all macro-tasks are done, and either delegate the next task to the Tech Lead
                        # or call the Janitor to close out the session.
                        content = types.Content(role='user', parts=[types.Part.from_text(text="Please evaluate the current state against your macro-tasks. If tasks remain, route to the architect. If all tasks are completed and the architect returned 'ARCHITECTURE_IMPLEMENTED', route to the janitor to finish. DO NOT STOP until the janitor completes.")])                            
                    success = True # If the loop finishes without raising a 429, we succeeded
                    
                except Exception as loop_err:
                    error_text = str(loop_err)
                    if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                        if attempt < max_retries:
                            cooldown = cooldowns[attempt]
                            yield f"data: {json.dumps({'type': 'status', 'content': f'⚠️ Vertex AI Quota hit (429). Retrying in {cooldown} seconds...'})}\n\n"
                            await asyncio.sleep(cooldown)
                            attempt += 1
                            # Clear the content payload so we just resume the session without re-prompting the captain
                            content = types.Content(role='user', parts=[types.Part.from_text(text="Continue where you left off.")])
                        else:
                            raise loop_err # Re-raise if we exhausted all retries
                    else:
                        raise loop_err # Immediately throw non-429 errors
            
            if success:
                yield f"data: {json.dumps({'type': 'complete', 'site_url': '/site/index.html'})}\n\n"
                    
        except Exception as e:
            import traceback
            error_text = str(e)
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                error_msg = f"API Quota Exceeded (429): Google Cloud Vertex AI has temporarily blocked this request due to usage limits on the specific model. Please wait a moment and try again.\n\nDetails: {error_text}"
            else:
                error_msg = f"Error running ADK Agent: {error_text}\n{traceback.format_exc()}"
            yield f"data: {json.dumps({'type': 'error', 'content': error_msg})}\n\n"
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
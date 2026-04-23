# 🚀 Vibe Agentic Swarm Demo

Welcome to the **Vibe Agentic Swarm**, a 2026-era autonomous software generation platform. This environment leverages a heterogeneous swarm of the world's most advanced Large Language Models (LLMs) to automatically architect, code, validate, and deploy full-stack web applications based entirely on natural language "vibes."

## 🧠 The Architecture

The system utilizes Google's Agent Development Kit (ADK) to orchestrate models based on their explicit strengths:

1.  **🧑‍✈️ The Captain (Project Manager):** Powered by `Gemini 3.1 Pro`. Analyzes the prompt and commands the Tech Lead.
2.  **📐 The Architect (Tech Lead & Validator):** Powered by `Claude Opus 4.6`. Reads project history, drafts a high-IQ blueprint in `DECISIONS.md`, routes tasks to the developers, and strictly validates their code.
3.  **🏗️ Gemini Worker (Data Developer):** Powered by `Gemini 3.1 Pro`. Executes heavy data generation, massive scaffolding, and SVG asset creation.
4.  **👷 Claude Worker (UI/UX Developer):** Powered by `Claude Sonnet 4.6`. Executes complex JavaScript business logic, dynamic components, and nuanced CSS styling.
5.  **🧹 The Janitor (Context Hygiene):** Powered by `Gemini 3.1 Flash Lite`. Compresses the session context into `history_recap.md` for durable memory across iterative prompts.

---

## 🛠️ How to Reproduce & Run

This application is packaged as a FastAPI server that acts as an Agent-to-Agent (A2A) protocol wrapper over the ADK. It can be run locally or deployed to Google Cloud Run.

### Prerequisites

*   **Python 3.12+**
*   **Google Cloud Platform (GCP) Account** with Vertex AI API enabled.
*   **Application Default Credentials (ADC)** configured locally, or a Service Account attached if running in the cloud.

Because the models route explicitly through Vertex AI endpoints, **you do not need consumer API keys (e.g., Anthropic API Key or Google AI Studio Key)**. You only need valid GCP IAM permissions for Vertex AI.

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/gmilen-sketch/vibe-swarm-demo.git
    cd vibe-swarm-demo
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Authenticate with Google Cloud:**
    ```bash
    gcloud auth application-default login
    ```

4.  **Configure Environment Variables:**
    Open `main.py` and `agent.py` and ensure the `GOOGLE_CLOUD_PROJECT` string matches your actual GCP Project ID. Alternatively, export them to your terminal:
    ```bash
    export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
    export GOOGLE_CLOUD_LOCATION="global"
    export GEMINI_USE_VERTEX="true"
    ```

5.  **Run the Server:**
    ```bash
    python main.py
    ```
    The application will start on `http://0.0.0.0:8080`.

### Running via Docker

You can also build and run the application using the provided Dockerfile.

```bash
docker build -t vibe-swarm .
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT="your-gcp-project-id" \
  -e GOOGLE_CLOUD_LOCATION="global" \
  -e GEMINI_USE_VERTEX="true" \
  -v ~/.config/gcloud:/root/.config/gcloud \
  vibe-swarm
```
*(Note: If running Docker locally, you must mount your gcloud config volume so the container can access your Application Default Credentials).*

---

## 🔐 Authentication

The application is protected by Basic HTTP Authentication to secure the expensive LLM execution endpoints.

*   **Username:** `admin`
*   **Password:** `vibe2026`

When you navigate to `http://localhost:8080`, simply enter these credentials to access the interactive split-screen terminal and live preview.
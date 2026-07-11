# JIRA Ticket Writer

An AI-powered assistant that converts casual work descriptions into properly formatted JIRA tickets. It automatically detects whether your input is a bug, a feature request, or a task, and routes it to a specialized formatter agent. Built with Cognizant's [neuro-san](https://github.com/cognizant-ai-lab/neuro-san) multi-agent framework.

---

## Prerequisites

- Python 3.11+
- A [Mistral API key](https://console.mistral.ai/) (uses `mistral-medium-2505`)

---

## Setup

```sh
git clone <repo-url>
cd jira-ticket-writer
python -m venv .venv
.venv\\Scripts\\activate          # Windows
# source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
```

Set your API key (create a `.env` file in the project root):

```sh
echo MISTRAL_API_KEY=your-key-here > .env
```

Or export directly in your terminal:

```sh
# PowerShell
$env:MISTRAL_API_KEY="your-key-here"

# Linux / macOS
export MISTRAL_API_KEY=your-key-here
```

---

## Running

### Launch the Streamlit web interface

```sh
streamlit run frontend/run.py
```

Open the URL printed in the terminal (usually http://localhost:8501).

### Example inputs to try

- `spent 3 hours debugging login timeout on prod, redis TTL was 5s instead of 5min`
- `need to add pagination to users API, currently returns all 50k records and frontend crashes`
- `fixed broken CI pipeline, docker tag was hardcoded to latest instead of git sha`

The agent detects whether it is a bug, story, or task and formats it accordingly.

After the ticket is generated, a **Download** button appears to save it as a `.md` file.

To save server-side, type: `save this as my_ticket_name`

### Run headless (for testing)

```sh
python backend/run.py
```

---

## Project Structure

```
jira-ticket-writer/
+-- backend/
|   +-- run.py                      # Backend entry point (invoke_agent)
|   +-- registries/
|   |   +-- manifest.hocon          # Agent registry
|   |   +-- jira_ticket.hocon       # Multi-agent network definition (5 agents)
|   |   +-- llm_config.hocon        # Shared Mistral LLM configuration
|   +-- coded_tools/
|       +-- jira_ticket/
|           +-- save_ticket.py      # CodedTool: saves ticket as Markdown file
+-- frontend/
|   +-- run.py                      # Streamlit chat UI with progress & download
+-- requirements.txt                # Python dependencies
+-- architecture.md                 # System architecture
+-- summary.md                      # Project summary
+-- README.md                       # This file
```

---

## How It Works

| Agent | Type | Role |
|-------|------|------|
| TicketWriter | LLM (Orchestrator) | Detects ticket type from casual input, routes to specialist |
| BugTicketWriter | LLM (Specialist) | Formats bug/defect tickets with symptom, root cause, steps to reproduce |
| StoryTicketWriter | LLM (Specialist) | Formats user stories with As-a/I-want/So-that structure |
| TaskTicketWriter | LLM (Specialist) | Formats task/work-log tickets |
| SaveTicket | CodedTool (Python) | Saves formatted ticket to a Markdown file on disk |

The orchestrator uses LLM-driven routing (no hard-coded if/else logic) to select the right specialist based on natural language understanding.

See [architecture.md](architecture.md) and [summary.md](summary.md) for detailed documentation.

---

## Troubleshooting

- **MISTRAL_API_KEY not found**: Ensure `.env` file is in the project root or the variable is exported.
- **Port already in use**: `streamlit run frontend/run.py --server.port 8502`
- **Slow response**: The agent makes 2 LLM calls (router + specialist). Typical response time is 10-30 seconds on Mistral free tier.

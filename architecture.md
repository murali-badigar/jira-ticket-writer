# Architecture

## Overview

This project is an **AI-powered JIRA Ticket Writer** built on Cognizant's **neuro-san** multi-agent framework. It accepts a casual, natural-language work description and produces a properly formatted JIRA ticket by routing the request to a specialized formatting agent based on the detected ticket type (Bug, Story, or Task).

The system is composed of a **Streamlit web frontend**, a **Python backend**, and a **multi-agent network** orchestrated by neuro-san.

---

## System Architecture Diagram

```
+------------------------------------------------------------------+
|                      User (Browser)                               |
+---------------------------------+--------------------------------+
                                  | HTTP (Streamlit)
+---------------------------------v--------------------------------+
|                  Frontend (frontend/run.py)                       |
|                 Streamlit Chat Interface                          |
|  - Chat UI with message history                                  |
|  - Animated progress indicator (st.status)                       |
|  - Download button for generated tickets                         |
|  - Multi-turn context persistence via session state              |
+---------------------------------+--------------------------------+
                                  | invoke_agent()
+---------------------------------v--------------------------------+
|                   Backend (backend/run.py)                        |
|           DirectAgentSessionFactory (neuro-san)                   |
|  - In-process agent execution (no separate server needed)        |
|  - Sets AGENT_MANIFEST_FILE and AGENT_TOOL_PATH env vars         |
|  - Calls session.streaming_chat() and returns final message      |
+---------------------------------+--------------------------------+
                                  | neuro-san Agent Engine
+---------------------------------v--------------------------------+
|                neuro-san Multi-Agent Network                      |
|       (backend/registries/jira_ticket.hocon)                     |
|                                                                  |
|  +------------------------------------------------------------+  |
|  |        TicketWriter (Orchestrator / Front Man)              |  |
|  |  LLM: Mistral Medium 2505                                  |  |
|  |  - Detects ticket type from casual input                   |  |
|  |  - Routes to BugTicketWriter / StoryTicketWriter /          |  |
|  |    TaskTicketWriter based on intent                         |  |
|  |  - Presents formatted ticket to user                       |  |
|  |  - Calls SaveTicket when user requests save                |  |
|  +------------------------------------------------------------+  |
|       |              |              |              |              |
|       v              v              v              v              |
|  +-----------+ +-----------+ +-----------+ +---------------+     |
|  |BugTicket  | |StoryTicket| |TaskTicket | | SaveTicket    |     |
|  |Writer     | |Writer     | |Writer     | | (CodedTool)   |     |
|  |LLM agent  | |LLM agent  | |LLM agent  | | Python class  |     |
|  |Bug format | |Story fmt  | |Task fmt   | | Writes .md    |     |
|  +-----------+ +-----------+ +-----------+ +---------------+     |
+------------------------------------------------------------------+
                                  | API calls
+---------------------------------v--------------------------------+
|              Mistral API (mistral-medium-2505)                    |
+------------------------------------------------------------------+
```

---

## Component Breakdown

### 1. Frontend (frontend/run.py)

A Streamlit chat interface that:
- Renders a scrolling conversation history.
- Shows an animated `st.status()` progress panel during ticket generation ("Classifying ticket type..." -> "Ticket ready!").
- Provides a Download button after each generated ticket for saving as `.md`.
- Persists `chat_context` in session state for multi-turn conversations.

### 2. Backend (backend/run.py)

A Python module that:
- Bootstraps environment variables for neuro-san (manifest path, tool path, PYTHONPATH).
- Uses `DirectAgentSessionFactory` for in-process agent execution (no separate server process needed).
- Exposes `invoke_agent()` which creates a session and returns the final response.

### 3. Agent Registry (backend/registries/)

| File | Purpose |
|------|---------|
| manifest.hocon | Lists active agent HOCON files |
| jira_ticket.hocon | Defines the 5-agent network |
| llm_config.hocon | Shared Mistral Medium 2505 configuration |

### 4. Multi-Agent Network (jira_ticket.hocon)

Five cooperating agents defined declaratively in HOCON:

| Agent | Type | Role |
|-------|------|------|
| TicketWriter | LLM (Orchestrator) | Routes input to the correct specialist based on intent |
| BugTicketWriter | LLM (Specialist) | Formats bug tickets: symptom, root cause, steps to reproduce, fix verification |
| StoryTicketWriter | LLM (Specialist) | Formats stories: As-a/I-want/So-that, technical approach, acceptance criteria |
| TaskTicketWriter | LLM (Specialist) | Formats tasks: what was done, why, outcome, completion criteria |
| SaveTicket | CodedTool | Writes ticket to Markdown file on disk |

### 5. CodedTool (backend/coded_tools/jira_ticket/save_ticket.py)

A Python class implementing neuro-san's `CodedTool` interface:
- Receives `content` and optional `filename` parameters from the LLM.
- Sanitizes the filename and writes to `backend/output/<filename>.md`.
- Returns the file path so the orchestrator can report it to the user.

---

## Agentic System Highlights

- **LLM-driven routing**: The TicketWriter orchestrator reads the user's casual input and autonomously selects the correct specialist (Bug/Story/Task). No hard-coded routing logic exists anywhere in the code.
- **Specialist separation**: Each ticket type has its own agent with formatting rules optimized for that category, producing higher-quality output than a single generic formatter.
- **CodedTool integration**: File I/O (SaveTicket) is a first-class tool the LLM can invoke autonomously when the user requests it, demonstrating neuro-san's Python extensibility.
- **Multi-turn conversation**: `chat_context` threads state between turns. Users can generate a ticket, request edits ("make priority Critical"), then save.
- **Declarative configuration**: The entire 5-agent topology is declared in a single HOCON file with no orchestration boilerplate in application code.
- **Two-hop efficiency**: Frontman -> Specialist -> Response. Only 2 LLM calls, keeping response time to ~10-30 seconds.

---

## Data Flow

```
User: "redis TTL was wrong, caused login timeouts, fixed it"
  |
  v
Streamlit frontend calls invoke_agent('jira_ticket', text)
  |
  v
Backend creates DirectAgentSession (in-process, no server)
  |
  v
TicketWriter (Mistral LLM) determines: this is a bug fix
  |
  v
TicketWriter calls BugTicketWriter(description=user_text)
  |
  v
BugTicketWriter (Mistral LLM) returns formatted bug ticket
  |
  v
TicketWriter presents the formatted ticket to the user
  |
  v
Response returned to Streamlit -> rendered as markdown
  + Download button appears

(If user then says "save this as login-fix"):
  TicketWriter calls SaveTicket(content, filename="login-fix")
  -> SaveTicket writes backend/output/login-fix.md
  -> Returns confirmation to user
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | neuro-san 0.6.42 (Cognizant open-source) |
| LLM | Mistral Medium 2505 (mistral-medium-2505) |
| Frontend | Streamlit (with st.status progress indicator) |
| Agent Config | HOCON (declarative, no code routing) |
| Custom Tools | Python 3 (CodedTool interface) |
| Output | Markdown (.md) with browser download |

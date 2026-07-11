# Project Summary

## What We Built

Every developer, tester, and project manager writes JIRA tickets daily. The task is simple in concept but tedious in practice: you know what happened or what needs doing, but formatting it into a proper ticket with the right title, type, priority, structured description, acceptance criteria, labels, and estimate takes disproportionate effort. Under time pressure, people write vague tickets ("fix bug") that cause confusion downstream, or spend 5-10 minutes carefully formatting each one.

We built an **AI-powered JIRA Ticket Writer** that eliminates this friction entirely. Type a single casual sentence about your work, and the system automatically detects whether it is a bug, a feature request, or a completed task, routes it to a specialized formatter, and produces a complete, properly structured JIRA ticket in ~10 seconds. A download button lets you save it instantly.

---

## The Problem

Three friction points in daily ticket creation:

1. **Format overhead**: JIRA expects structured fields (title, type, priority, description, acceptance criteria, labels, estimate). Converting a mental note into this format takes disproportionate effort.
2. **Type confusion**: Is this a bug, a story, or a task? People miscategorize, causing workflow and reporting issues.
3. **Quality inconsistency**: Under time pressure, people skip acceptance criteria, write vague descriptions, or omit labels, causing confusion for teammates and stakeholders.

---

## How It Works

The application is a conversational Streamlit web app. The user types naturally and the backend, powered by a multi-agent system on Cognizant's open-source neuro-san framework, produces a formatted ticket.

### The Agentic System (5 Agents)

The core is a network of five cooperating AI agents, all configured declaratively in a HOCON file and orchestrated by neuro-san at runtime:

**TicketWriter (Orchestrator)** - The front man agent. It receives the user's casual input, determines the ticket type (bug, story, or task) from natural language context, and routes to the appropriate specialist. It also handles the "save" command by invoking the SaveTicket tool. No hard-coded routing logic exists - the LLM decides autonomously.

**BugTicketWriter (Specialist)** - Formats bug/defect tickets with structured sections: symptom, root cause, impact, fix applied, steps to reproduce, and fix-verification acceptance criteria.

**StoryTicketWriter (Specialist)** - Formats user stories with the standard As-a/I-want/So-that structure, technical approach notes, and testable acceptance criteria.

**TaskTicketWriter (Specialist)** - Formats task and work-log tickets with what was done, why, the outcome, and completion criteria.

**SaveTicket (CodedTool)** - A custom Python component that writes the formatted ticket as a Markdown file to disk. It demonstrates neuro-san's CodedTool extensibility, allowing the LLM to invoke real Python logic (file I/O) as part of the agent workflow.

### Key Design Decisions

- **LLM-as-router**: The orchestrator decides the ticket type from natural language. Adding a new type (Spike, Epic) requires only a new HOCON block, no code change.
- **Two-hop efficiency**: Only 2 LLM calls per request (router + specialist), keeping response time to ~10-30 seconds.
- **No clarifying questions**: The agent infers everything from context for maximum speed. Ticket creation should feel instant, not like a form to fill.
- **Progress feedback**: The frontend uses Streamlit's `st.status()` widget to show an animated progress panel during generation, so users see activity rather than a frozen screen.
- **Browser download**: A download button appears after each ticket, letting users save as `.md` without needing server-side file access.

---

## Technology Choices

| Concern | Choice | Reason |
|---------|--------|--------|
| Agent orchestration | neuro-san 0.6.42 | Declarative HOCON config; CodedTool interface; multi-turn context; no boilerplate |
| LLM | Mistral Medium 2505 | Strong instruction-following; function-calling support for agent routing; free tier available |
| Frontend | Streamlit | Rapid chat UI; session state for context; built-in download buttons and status widgets |
| Output | Markdown | Universal; renders in JIRA description fields; easily pasteable |
| Execution model | DirectAgentSessionFactory | In-process execution; no separate server; no port management |

---

## Project Structure

```
jira-ticket-writer/
+-- backend/
|   +-- run.py                      # Backend entry point & invoke_agent()
|   +-- registries/
|   |   +-- manifest.hocon          # Active agent registry
|   |   +-- jira_ticket.hocon       # 5-agent network definition
|   |   +-- llm_config.hocon        # Shared Mistral LLM config
|   +-- coded_tools/
|       +-- jira_ticket/
|           +-- save_ticket.py      # SaveTicket CodedTool (Markdown export)
+-- frontend/
|   +-- run.py                      # Streamlit chat interface
+-- requirements.txt                # Python dependencies
+-- architecture.md                 # System architecture documentation
+-- summary.md                      # This file
+-- README.md                       # Setup and run instructions
```

---

## What Makes This Interesting for the Hackathon

- **Solves a universal daily pain point**: Every team member writes tickets. This saves 5 minutes per ticket, every day.
- **Fast, interactive response**: 2 LLM hops = ~10-30 seconds. Users see animated progress, not a frozen screen.
- **LLM-driven routing demonstrated**: The orchestrator pattern showcases neuro-san's AAOSA (Adaptive Agent-Oriented Software Architecture) capability with no hard-coded routing.
- **Specialist quality**: Each ticket type gets optimized formatting from a dedicated agent, producing better output than a single generic prompt.
- **CodedTool integration**: SaveTicket demonstrates real Python extensibility, with the LLM autonomously invoking file I/O.
- **Extensible by design**: Adding new ticket types (Spike, Epic, Sub-task) or project-specific templates requires only a new agent block in HOCON, no code change.
- **Real output artifact**: Download button provides a tangible `.md` file, not just text in a chat window.
- **Full-stack in ~100 lines of Python**: Frontend, backend, orchestration, and file export, with the rest expressed declaratively in HOCON.

---

## Example Interaction

```
User:  spent 3 hours debugging login timeout on prod, redis session
       TTL was set to 5 seconds instead of 5 minutes, fixed it

Agent: **Title**: Fix Redis session TTL causing login timeouts

       **Type**: Bug
       **Priority**: High
       **Status**: Done

       **Description**:
       - **Symptom**: Users experienced login timeouts in production
       - **Root Cause**: Redis session TTL misconfigured (5s instead of 300s)
       - **Impact**: Production users affected by premature session expiry
       - **Fix Applied**: Corrected TTL from 5 seconds to 5 minutes

       **Acceptance Criteria**:
       - [ ] Redis session TTL is 300 seconds in production
       - [ ] No timeout-related errors in application logs post-fix

       **Labels**: backend, auth, production, redis
       **Time Spent**: 3 hours

User:  save this as PROJ-login-fix

Agent: Ticket saved to backend/output/PROJ-login-fix.md
```

---

## Future Work

- Direct JIRA API integration via MCP to create tickets without copy-paste.
- Project-specific templates (custom fields, labels, components per team).
- Bulk mode: paste a standup update and generate multiple tickets at once.
- Learning from accepted tickets to refine formatting over time.
- Additional ticket types: Spike, Epic, Sub-task.

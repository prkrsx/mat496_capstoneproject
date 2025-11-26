## Title: React/TypeScript Learning Coach Agent (Python + LangGraph)

## Overview

My project is a Python + LangGraph based **React/TypeScript Learning Coach** agent that helps a user learn how to build a React application step by step, instead of generating the full project code for them.

The typical workflow is:

1. The user describes the React app they want to build (features, goals, constraints).
2. The agent uses prompting + structured JSON output to:
   - extract a **learner profile** (assumed level, goals),
   - extract a **project specification** (summary, feature list).
3. The agent then creates a **multi‑stage project plan** using structured output:
   - Each stage has a name, goal, tasks, fundamentals (React/TS concepts), and relevant docs/links.
4. For each stage, the agent acts as a **coach**:
   - explains what to do,
   - suggests what files/folders to create,
   - highlights the core concepts,
   - and asks the user to implement the code locally.
5. The user reports back with progress, questions, and optional code snippets:
   - the agent uses **tool calling** to:
     - run a small **semantic search** (`fetch_docs`) over a curated React/TS docs store,
     - run a **code analysis tool** (`analyze_code_snippet`) to detect likely issues and missing fundamentals.
   - The retrieved docs are then passed into the LLM prompt as context, so the answers become **Retrieval‑Augmented Generation (RAG)**.
6. The agent enforces a **“coach mode”**:
   - it avoids giving full solutions by default,
   - focuses on hints, explanations, and partial examples,
   - only produces fuller code if the user explicitly asks for it.
7. At any point, if the user wants to **change or add a feature**, the agent:
   - updates the project specification,
   - calls the planning logic again to **re‑plan** stages,
   - and then continues coaching with the updated roadmap.

The whole system runs locally as a **CLI application**: the user interacts in the terminal, while LangGraph manages the stateful agent logic underneath.

## Reason for picking up this project

This project is directly aligned with the core topics of the course:

- **Prompting**  
  Each LangGraph node (onboarding, planning, coaching) has its own carefully designed system + human prompts. The prompts enforce “coach mode” (no full solutions by default) and ask the model to output **structured JSON** so that later nodes can consume consistent data.

- **Structured Output**  
  The onboarding node prompts the LLM to return JSON with fields like `project_summary`, `features`, `assumed_level`.  
  The planning node prompts for `stages` as a JSON list, where each stage has `name`, `goal`, `tasks`, `fundamentals`, and `docs`.  
  These JSON responses are parsed in Python and stored in the LangGraph `GraphState` so that later nodes can use them programmatically.

- **Semantic Search**  
  I create a small, curated **React/TypeScript docs store** (JSX, props vs state, hooks, routing, etc.) in code.  
  A `fetch_docs(query)` tool performs lightweight semantic search (keyword/similarity based) over this store to retrieve the most relevant snippets for a given topic or user question.

- **Retrieval Augmented Generation (RAG)**  
  The coaching node calls `fetch_docs(...)` and then **injects the retrieved docs into the LLM prompt** as additional context.  
  This means the agent’s explanations about React/TS are grounded in specific documentation snippets rather than being purely free‑form, satisfying the core RAG pattern (query → retrieve → generate).

- **Tool calling LLMs & MCP‑style tools**  
  I define explicit Python “tools”:
  - `fetch_docs(query)` for doc retrieval,
  - `analyze_code_snippet(code, stage_info)` for structured code feedback.  
  The LangGraph nodes decide when to call these tools based on the current state and the user’s latest message, and then feed the tool outputs back into the LLM prompts. This demonstrates a tool‑calling pattern where the LLM is not doing everything in one monolithic call.

- **LangGraph: State, Nodes, Graph**  
  The project is built around a LangGraph `StateGraph` with:
  - a typed `GraphState` that stores `messages`, `learner_profile`, `project_spec`, `stages`, `current_stage_index`, and `status`,
  - nodes for `onboarding`, `planning`, and `coaching`,
  - a routing function and conditional edges to manage transitions between planning, coaching, re‑planning, and finishing.

Overall, this project uses LangGraph not just as a thin wrapper, but as the main way to encode a **stateful teaching workflow**: plan → coach → adapt → re‑plan, while revising all the major course topics in a single coherent application.

## Plan

I plan to excecute these steps to complete my project.

- [TODO] Step 1: Set up the local project structure
  - Fork the `capstone-template` repository and create a `react-learning-coach-agent` folder.
  - Initialize a Python virtual environment and install `langgraph`, `langchain-openai`, `langchain`, and `python-dotenv`.
  - Create initial empty files: `state.py`, `nodes.py`, `tools.py`, `docs_store.py`, `graph.py`, `main.py`, and `README.md`.

- [TODO] Step 2: Define LangGraph state and build a minimal graph
  - Implement `GraphState` in `state.py` with fields: `messages`, `learner_profile`, `project_spec`, `stages`, `current_stage_index`, and `status`.
  - Create a minimal `StateGraph` in `graph.py` with one test node (e.g. echo) and a simple CLI loop in `main.py` to verify the LangGraph setup works locally.

- [TODO] Step 3: Implement onboarding node with prompting + structured output
  - In `nodes.py`, add an `onboarding_node` that:
    - takes the user’s natural language description of the desired React app,
    - uses an LLM prompt to output **only JSON** with `project_summary`, `features`, and `assumed_level`,
    - parses this JSON and stores it in `project_spec` and `learner_profile`,
    - sets `status = "planning"` and adds a short assistant summary message.

- [TODO] Step 4: Implement planning node with structured multi‑stage plan
  - In `nodes.py`, add a `planning_node` that:
    - reads `project_spec`,
    - prompts the LLM to return JSON `{ "stages": [...] }` where each stage has `name`, `goal`, `tasks[]`, `fundamentals[]`, and `docs[]`,
    - parses and stores the list in `stages`, resets `current_stage_index = 0`, and sets `status = "coaching"`,
    - sends a brief assistant message listing the stage names as the roadmap.

- [TODO] Step 5: Add React/TypeScript docs store and semantic search tool
  - In `docs_store.py`, create a small in‑memory list of React/TS topics with `topic`, `content`, and `link` fields.
  - In `tools.py`, implement `fetch_docs(query, k=3)` that performs simple semantic/keyword search over the docs store and returns the top‑k relevant entries.
  - This will demonstrate **Semantic Search** inside the project.

- [TODO] Step 6: Add code analysis tool for structured feedback
  - In `tools.py`, implement `analyze_code_snippet(code, stage_info)` that:
    - uses a constrained LLM prompt to output JSON with `issues`, `suggested_fundamentals`, and `high_level_hint`,
    - is called when the user includes code snippets in their message (detected by simple markers).
  - This will demonstrate a second example of **tool‑calling**.

- [TODO] Step 7: Implement coaching node using tools + RAG
  - In `nodes.py`, implement `coaching_node` that:
    - reads the current stage from `stages[current_stage_index]`,
    - interprets special messages like “done with this stage” (advance stage) and “add/change feature” (set `status = "replan"`),
    - calls `fetch_docs(...)` with a query based on the current stage fundamentals and the user’s question, and injects these docs into the LLM prompt (RAG),
    - calls `analyze_code_snippet(...)` when the user sends code and includes that feedback in the context,
    - uses a “coach mode” system prompt to avoid giving full code unless explicitly asked.
  - This node becomes the main teaching/tutoring loop for each stage.

- [TODO] Step 8: Implement re‑planning flow for feature changes
  - Extend `planning_node` so that when `status == "replan"`:
    - it updates `project_spec` with the new/changed feature from the latest user message,
    - regenerates the `stages` list (or augments it) and resets/coherently updates `current_stage_index`,
    - sends a message summarizing the updated plan.
  - This shows how LangGraph’s state and nodes can adapt to mid‑project scope changes.

- [TODO] Step 9: Wire up routing and refine the CLI experience
  - Implement a `route_next_node` function that:
    - routes from `coaching` back to `coaching`, to `planning` (when `status = "replan"`), or to `END` (when `status = "finished"`).
  - Update `graph.py` with LangGraph conditional edges from `coaching_node` using `route_next_node`.
  - Refine `main.py` so the CLI:
    - prints helpful prompts (e.g. “type ‘done with this stage’ when finished”),
    - shows current stage name after each coaching reply.

- [TODO] Step 10: Test multiple scenarios and finalize documentation
  - Test the agent locally with:
    - a beginner todo app,
    - a slightly more complex app with routing or auth,
    - at least one mid‑project feature change.
  - Collect a few transcripts demonstrating:
    - structured onboarding and planning,
    - coach‑mode answers with RAG‑based doc snippets,
    - code analysis hints, and re‑planning.
  - Update the README and this report (changing `[TODO]` to `[DONE]`), and write the **Conclusion** section based on actual results.

## Conclusion:

I had planned to achieve a **React/TypeScript Learning Coach** that (1) uses LangGraph state, nodes, and graph structure, (2) demonstrates prompting, structured output, semantic search, RAG, and tool‑calling, and (3) guides a learner through building a React app without directly writing all the code for them.

By the end of the project, I will evaluate whether:

- the agent reliably produces a useful multi‑stage learning plan for different React app ideas,
- the coaching loop actually helps debug and explain concepts instead of just dumping code,
- the semantic search + RAG over the small React/TS docs store meaningfully improves explanations,
- and the LangGraph design (state + nodes + conditional edges) stays understandable and maintainable.

In the final version of this section, I will clearly state whether I believe I have achieved these goals satisfactorily, and explain the reasons for my satisfaction or dissatisfaction (for example: which features worked well, what limitations remained due to time, and what improvements I would like to make in a future iteration).

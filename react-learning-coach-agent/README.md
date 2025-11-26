# Title: React/TypeScript Learning Coach Agent (Python + LangGraph, RAG)

## Overview

My project is a Python + LangGraph based learning coach agent that helps a user design and build React/TypeScript applications step by step, without writing the whole project for them.
The workflow is:
1.	The user describes the React app they want (features, goals, constraints).
2.	The agent converts this into a structured project specification and then a multi‑stage plan (e.g. setup, folder structure, core features, routing, styling, etc.), using prompting + structured JSON output.
3.	For each stage, the agent:
o	explains the goals and tasks,
o	lists key React/TS fundamentals to learn,
o	retrieves relevant documentation/tutorial snippets using semantic search over a small local React/TS docs store, and
o	uses Retrieval‑Augmented Generation (RAG) to ground explanations in those snippets.
4.	The user writes code locally and reports back with progress, errors, or snippets. The agent:
o	calls a code‑analysis tool to inspect the snippet and identify likely issues and missing concepts,
o	gives hints, explanations, and partial examples, but does not provide full solutions unless the user explicitly asks.
5.	The agent maintains explicit state (learner profile, project spec, stages, current stage, status). If the user requests a new/changed feature mid‑project or after finishing, the agent updates the project spec and re‑plans the stages.
6.	When all stages are complete, the agent summarizes what was built and what React/TS concepts were learned.
Everything runs locally as a CLI application that repeatedly calls a compiled LangGraph with stateful nodes and tools.

## Reason for picking up this project

This project is tightly aligned with the main topics of the course:
•	Prompting:
Each node (onboarding, planning, coaching, code‑review) uses carefully designed system + human prompts. I explicitly instruct the LLM to behave as a coach, to avoid full code unless requested, and to output strict JSON when I need structured data (project spec, stages, feedback).
•	Structured Output:
o	The onboarding node prompts the model to output JSON with fields like project_summary, features, assumed_level.
o	The planning node prompts for { "stages": [...] }, where each stage has name, goal, tasks, fundamentals, docs.
o	The code‑analysis tool returns JSON with issues, suggested_fundamentals, and high_level_hint.
These outputs are parsed and stored in a typed GraphState, so later nodes can reliably consume them.
•	Semantic Search:
I implement a small local React/TypeScript docs store (a Python list of topic–content–link entries). A fetch_docs(query) tool performs simple semantic/keyword search over this store, returning the most relevant snippets for the current topic or user question.
•	Retrieval Augmented Generation (RAG):
The coaching node calls fetch_docs(...) and injects the retrieved snippets into the LLM prompt as context. The model’s explanations and hints are therefore grounded in specific React/TS documentation rather than being purely free‑form. This is a minimal but clear RAG loop: query → retrieve docs → use docs in generation.
•	Tool calling LLMs & MCP‑style tools:
I define explicit tools in Python:
o	fetch_docs(query) for retrieval/semantic search.
o	analyze_code_snippet(code, stage_info) which uses an LLM with a constrained prompt to analyze user code and return structured feedback.
The coaching node decides when to call these tools and then incorporates their outputs into the final LLM call, following the tool‑calling pattern discussed in class.
•	LangGraph: State, Nodes, Graph:
The whole agent is implemented as a LangGraph:
o	A GraphState TypedDict with:
	messages
	learner_profile
	project_spec
	stages
	current_stage_index
	status ("onboarding" | "planning" | "coaching" | "replan" | "finished")
o	Nodes:
	onboarding_node – parse user request into learner profile + project spec (JSON).
	planning_node – convert project spec into a multi‑stage learning plan (JSON).
	coaching_node – per‑stage tutor that uses tools (fetch_docs, analyze_code_snippet) and RAG, and enforces coach mode.
	route_next_node – conditional router that decides whether to stay in coaching, re‑plan, or finish.
o	Graph:
	START → onboarding → planning → coaching,
	then conditional edges from coaching based on status.
I chose this project because it is both technically rich (covers all syllabus topics) and personally meaningful: I have been learning React/TypeScript myself, and I find the idea of an AI that helps you learn (instead of doing the work for you) very compelling.

## Plan

I plan to execute these steps to complete my project.
•	[TODO] Step 1: Set up the local Python project
o	Fork the capstone template, create the react-learning-coach-agent folder.
o	Create state.py, nodes.py, tools.py, docs_store.py, graph.py, main.py, and README.md.
o	Initialize a virtual environment and install langgraph, langchain-openai, langchain, and python-dotenv.
o	Add a minimal GraphState and a trivial echo node to verify the LangGraph wiring via a local CLI.
•	[TODO] Step 2: Implement onboarding with prompting + structured output
o	Write onboarding_node that takes the user’s natural‑language project request and uses a system prompt to extract a JSON object with project_summary, features, and assumed_level.
o	Parse the JSON and populate project_spec and learner_profile in GraphState.
o	Update the graph so START → onboarding.
•	[TODO] Step 3: Implement planning with structured JSON stages
o	Write planning_node that reads project_spec and prompts the LLM to return { "stages": [...] }, where each stage has name, goal, tasks[], fundamentals[], docs[].
o	Parse and store stages and initialize current_stage_index = 0, set status = "coaching".
o	Wire the graph as onboarding → planning → coaching (with a temporary stub for coaching_node).
•	[TODO] Step 4: Build a small React/TS docs store and semantic search tool
o	Create docs_store.py with a small curated list of React/TypeScript topics (JSX, props vs state, hooks, routing, etc.), each containing a short explanation and an official docs link.
o	Implement fetch_docs(query, k) in tools.py to do simple semantic/keyword search over the docs list and return the top‑k relevant snippets.
o	This will be used by the coaching node to ground explanations.
•	[TODO] Step 5: Implement a code‑analysis tool using an LLM (tool calling)
o	Implement analyze_code_snippet(code, stage_info) in tools.py that uses a constrained LLM prompt to return JSON feedback with issues, suggested_fundamentals, and a high_level_hint.
o	Ensure it does not output full solutions but points out likely mistakes and missing concepts.
o	This will be called when the user pastes code during a stage.
•	[TODO] Step 6: Implement the coaching node with RAG and tools
o	Implement coaching_node that:
	reads the current stage from stages[current_stage_index],
	checks the latest user message for:
	stage completion (e.g. “done with this stage”),
	feature change requests (e.g. “add feature …”),
	presence of code snippets,
	calls fetch_docs(...) with a query based on stage fundamentals and the user message,
	optionally calls analyze_code_snippet(...) when code is detected,
	builds a RAG prompt including stage info, retrieved docs, and optional code‑analysis output, and then calls the LLM with a coach‑mode system prompt (no full code unless explicitly asked),
	appends the assistant’s reply to messages and updates status appropriately.
•	[TODO] Step 7: Implement re‑planning for mid‑project feature changes
o	Extend route_next_node to look at status and route:
	"coaching" → continue in coaching,
	"replan" → go back to planning_node,
	"finished" → end the graph.
o	Modify planning_node so that if called with status = "replan", it:
	updates project_spec["features"] using the latest user message (new feature description),
	regenerates the stages list,
	resets current_stage_index as needed, and returns an updated plan to the user.
•	[TODO] Step 8: Build and refine the CLI interaction loop
o	In main.py, implement a loop that:
	initializes a GraphState,
	reads user input from the terminal,
	appends it to messages,
	invokes the compiled LangGraph,
	prints the latest assistant response.
o	Add small UX hints like:
	how to mark a stage as done,
	how to request feature changes,
	how to exit.
o	Test locally with a few sample projects.
•	[TODO] Step 9: Testing, prompt tuning, and documentation
o	Run multiple end‑to‑end test sessions:
	a beginner‑level app (simple todo list),
	an intermediate app (todo + auth + dark mode),
	a session where the user changes features mid‑way.
o	Adjust prompts and node logic so:
	the agent reliably outputs valid JSON where required,
	explanations are clear and grounded in the retrieved docs,
	coach mode is respected (no full code unless explicitly requested).
o	Update the README with any changes and capture 1–2 example transcripts for the report.
•	[TODO] Step 10: Conclusion and final report
o	Fill in the conclusion section below after implementation.
o	Mark completed steps as [DONE] before each corresponding commit.
o	Ensure commit history shows work spread over at least two dates before the deadline.

## Conclusion:

I had planned to build a LangGraph‑based React/TypeScript learning coach that:
•	turns a natural‑language project idea into a structured, multi‑stage learning plan,
•	uses prompting and structured output to maintain state,
•	uses semantic search and RAG over a small React/TS docs store to ground explanations,
•	calls tools for documentation retrieval and code analysis, and
•	acts as a coach who helps the user build the project themselves instead of generating the entire codebase.
In the end, I will evaluate whether I have achieved these goals satisfactorily. I will reflect on:
•	how well the agent followed the coach‑mode behavior (especially avoiding full solutions by default),
•	how effective the stage‑wise planning and re‑planning were for feature changes,
•	how useful the RAG‑based explanations and code‑analysis feedback were in practice, and
•	which parts of the LangGraph design (state, nodes, conditional edges) worked well and which I would improve in a future iteration.

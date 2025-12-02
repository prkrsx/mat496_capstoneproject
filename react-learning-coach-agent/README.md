# Title: React/TypeScript Learning Coach Agent

## Overview

This project is a **React/TypeScript Learning Coach Agent** built with Python and LangGraph that helps users learn React development through hands-on guided projects rather than generating code for them.

**What it does:**
- Takes your project idea as input (e.g., "I want to build a todo app with authentication")
- Creates a personalized multi-stage learning plan based on your skill level
- Guides you through each stage with explanations, exercises, and concept breakdowns
- Uses RAG (Retrieval-Augmented Generation) to provide accurate React/TypeScript documentation
- Analyzes your code and provides constructive feedback
- Adapts the learning path when you want to add new features

**Key Features:**
-  Personalized learning paths (beginner/intermediate/advanced)
-  Structured multi-stage project planning
-  Coach-mode teaching (hints over solutions)
-  Semantic search over React/TypeScript documentation
-  Code analysis and feedback tools
-  Dynamic re-planning for scope changes
-  Three interaction modes: CLI, LangGraph Studio, and Web UI

## Reason for picking up this project

This project is built on the philosphy of "learning from mistakes", the agent helps you learn how to write your code so you can learn while doing which helps in learning the foundations, and helps/points you towards where you went wrong and what could be the correct approach. 

This project also comprehensively demonstrates all major topics from MAT496:

**1. Prompting**  
Each LangGraph node uses carefully designed system prompts. The coaching node enforces "coach mode" to provide hints rather than full solutions, while onboarding and planning nodes guide structured information extraction.

**2. Structured Output**  
- Onboarding node extracts JSON: `{project_summary, features, assumed_level}`
- Planning node generates: `{stages: [{name, goal, tasks, fundamentals, docs}]}`
- Code analysis returns: `{issues, suggested_fundamentals, hints}`

**3. Semantic Search**  
The `fetch_docs(query)` tool performs keyword/similarity search over a curated React/TypeScript documentation store to retrieve relevant snippets.

**4. Retrieval Augmented Generation (RAG)**  
The coaching node retrieves documentation via `fetch_docs()` and injects it into LLM prompts, ensuring answers are grounded in official React/TypeScript documentation rather than hallucinations.

**5. Tool calling LLMs & MCP**  
Two custom tools:
- `fetch_docs(query)`: Retrieves documentation snippets
- `analyze_code_snippet(code, stage_info)`: Provides structured code feedback

**6. LangGraph: State, Nodes, Graph**  
Complete LangGraph implementation with:
- Typed `GraphState` (messages, learner_profile, project_spec, stages, status)
- Nodes: onboarding → planning → coaching (with loops)
- Conditional routing for re-planning and stage advancement

## Video Summary Link

[Video demonstration will be added here]

## Installation & Setup

### Prerequisites
- Python 3.13+ (3.14 tested)
- OpenAI API key

### Step 1: Clone and Setup Environment

```bash
# Navigate to the project directory
cd react-learning-coach-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install langgraph langchain-openai langchain-core python-dotenv yaspin streamlit
```

### Step 2: Configure Environment

Create a `.env` file in the `react-learning-coach-agent` directory:

```bash
OPENAI_API_KEY=your_api_key_here
```

## Usage Instructions

This project offers three ways to interact with the learning coach:

### Option 1: Command-Line Interface (CLI)

The simplest way to use the agent - pure text-based interaction.

```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Run the CLI
python main.py
```

**Example interaction:**
```
Welcome to the React Learning Coach!

Describe the React app you want to build:
> I want to build a todo app with TypeScript and local storage

[Agent creates learning plan with 5 stages...]

Stage 1: Project Setup & Environment
What would you like to do? (type 'continue', 'done', 'give me exercises', etc.)
> continue

[Agent provides guidance on setting up React with TypeScript...]

> I'm stuck on TypeScript interfaces

[Agent retrieves relevant docs and explains...]

> done with this stage

[Agent advances to Stage 2...]
```

**Commands you can use:**
- `continue` - Get next instructions for current stage
- `done` - Mark current stage complete and move to next
- `give me exercises` - Get practice exercises
- `add feature: [description]` - Add new feature and re-plan
- `I'm actually [beginner/intermediate/advanced]` - Change skill level
- Ask any question naturally

### Option 2: LangGraph Studio (Visual Development)

Use LangGraph Studio for visual debugging and development.

```bash
# Install LangGraph CLI if not already installed
pip install langgraph-cli

# Start LangGraph Studio
langgraph dev
```

Then open your browser to the provided URL (typically `http://localhost:8123`).

**LangGraph Studio Features:**
-  Visual graph representation of agent flow
-  Step-by-step state inspection
-  Debug node transitions and routing
-  View message history and state changes
-  Test specific nodes in isolation

**How to use:**
1. The studio will automatically detect `langgraph.json`
2. Use the interface to send messages and see the graph execute
3. Inspect state at each node
4. View tool calls and their outputs

### Option 3: Streamlit Web UI

Modern, user-friendly web interface with chat-based interaction.

```bash
# Make sure streamlit is installed
pip install streamlit

# Run the web UI
streamlit run streamlit_app.py --server.port 8501
```

Then open your browser to `http://localhost:8501`

**Web UI Features:**
-  Modern dark mode interface
-  Chat-based interaction
-  Visual progress tracking
-  Quick action buttons (Continue, Practice, Mark Done)
-  Collapsible sections for stages and features
-  Quick start templates (Todo App, E-commerce, Chat App)
-  Responsive design

**How to use:**
1. Choose a quick start template or type your project idea
2. Chat naturally with the agent
3. Use sidebar buttons for quick actions
4. Track your progress in the sidebar
5. Expand sections to see all stages and features

## Project Structure

```
react-learning-coach-agent/
├── state.py              # LangGraph state definition
├── nodes.py              # Agent nodes (onboarding, planning, coaching)
├── tools.py              # Tool functions (fetch_docs, analyze_code)
├── docs_store.py         # React/TypeScript documentation store
├── graph.py              # LangGraph graph construction
├── main.py               # CLI entry point
├── streamlit_app.py      # Web UI entry point
├── langgraph.json        # LangGraph Studio configuration
├── .env                  # Environment variables (create this)
└── README.md             # This file
```

## Architecture Overview

```
User Input
    ↓
Onboarding Node (Structured Output)
    ↓
Planning Node (Multi-stage Plan) ←─────┐
    ↓                                  │
Coaching Node                          │
    ↓                                  │
Tools Called:                          │
- fetch_docs()                         │ (Loop until done)
- analyze_code()                       │
    ↓                                  │
Response + RAG ────────────────────────┘
    ↓
Re-planning (if feature added)
    ↓
Completion
```

## Examples

### Example 1: Beginner Todo App
```
User: I want to build a simple todo app
Agent: [Creates 4-stage plan covering: Setup, Components, State, Styling]
User: continue
Agent: [Explains JSX and basic React components with examples]
User: give me exercises
Agent: [Provides 3 practice exercises on components]
```

### Example 2: Intermediate with Feature Addition
```
User: I want to build an e-commerce product catalog
Agent: [Creates 5-stage plan]
User: continue through Stage 2
Agent: [Guides through product listing components]
User: add feature: user authentication
Agent: [Re-plans and adds 2 new stages for auth]
```

## Troubleshooting

**"Port 8501 already in use"**
```bash
# Kill existing Streamlit process
lsof -ti:8501 | xargs kill -9
```

**"Module not found" errors**
```bash
# Ensure virtual environment is activated and reinstall
pip install langgraph langchain-openai langchain-core python-dotenv yaspin streamlit
```

**LangGraph Studio not detecting graph**
```bash
# Ensure langgraph.json exists and points to correct graph file
cat langgraph.json
```

## Plan

Implementation steps executed to complete this project:

- [DONE] Step 1: Set up the local project structure
  - Forked the `capstone-template` repository and created `react-learning-coach-agent` folder
  - Initialized Python virtual environment and installed all dependencies
  - Created initial files: `state.py`, `nodes.py`, `tools.py`, `docs_store.py`, `graph.py`, `main.py`, `README.md`

- [DONE] Step 2: Define LangGraph state and build a minimal graph
  - Implemented `GraphState` in `state.py` with all required fields
  - Created basic `StateGraph` in `graph.py`
  - Built CLI loop in `main.py` to verify setup

- [DONE] Step 3: Implement onboarding node with prompting + structured output
  - Added `onboarding_node` with LLM prompt for JSON extraction
  - Parses `project_summary`, `features`, and `assumed_level`
  - Stores data in state and transitions to planning

- [DONE] Step 4: Implement planning node with structured multi-stage plan
  - Added `planning_node` that generates structured stage list
  - Each stage contains: name, goal, tasks, fundamentals, docs
  - Initializes coaching loop

- [DONE] Step 5: Add React/TypeScript docs store and semantic search tool
  - Created `docs_store.py` with curated React/TS documentation
  - Implemented `fetch_docs(query, k=3)` with semantic search
  - Demonstrates Semantic Search pattern

- [DONE] Step 6: Add code analysis tool for structured feedback
  - Implemented `analyze_code_snippet()` in `tools.py`
  - Returns structured JSON with issues and hints
  - Demonstrates tool-calling pattern

- [DONE] Step 7: Implement coaching node using tools + RAG
  - Built `coaching_node` with full teaching loop
  - Integrates `fetch_docs()` for RAG-based answers
  - Uses `analyze_code_snippet()` for code feedback
  - Enforces "coach mode" prompting

- [DONE] Step 8: Implement re-planning flow for feature changes
  - Extended `planning_node` to handle `status == "replan"`
  - Updates project spec and regenerates stages
  - Maintains coherent learning progression

- [DONE] Step 9: Wire up routing and refine the CLI experience
  - Implemented routing logic with conditional edges
  - Added user-friendly CLI prompts and commands
  - Displays current stage and progress

- [DONE] Step 10: Test multiple scenarios and finalize documentation
  - Tested with beginner, intermediate, and advanced scenarios
  - Validated feature additions and re-planning
  - Verified RAG, semantic search, and tool calling

- [DONE] Step 11: Build Streamlit web UI
  - Created modern dark-mode web interface
  - Added chat-based interaction with session state
  - Implemented visual progress tracking and quick actions
  - Tested deployment and user experience

- [DONE] Step 12: Add LangGraph Studio support
  - Created `langgraph.json` configuration
  - Tested visual debugging and state inspection
  - Documented Studio usage

## Conclusion

I had planned to achieve a **React/TypeScript Learning Coach** that:
1. Uses LangGraph state, nodes, and graph structure comprehensively
2. Demonstrates all major course topics (prompting, structured output, semantic search, RAG, tool-calling)
3. Guides learners through building React apps without directly writing code for them
4. Provides multiple interaction modes (CLI, LangGraph Studio, Web UI)

**Achievement Status: Accomplished** 

**What worked well:**
-  **LangGraph implementation**: Clean state management with typed GraphState, well-defined nodes, and robust conditional routing
-  **Course topic coverage**: All MAT496 topics integrated naturally - prompting in every node, structured output for onboarding/planning, semantic search via `fetch_docs()`, RAG in coaching responses, and tool-calling for both docs and code analysis
-  **Coach mode effectiveness**: The agent successfully provides hints and guidance rather than complete solutions, encouraging active learning
-  **RAG quality**: Retrieving React/TS docs and injecting them into prompts significantly improved answer accuracy and reduced hallucinations
-  **Adaptability**: Re-planning feature works smoothly when users add/change features mid-project
-  **User experience**: Three interaction modes (CLI, Studio, Web UI) provide flexibility for different use cases
-  **Code quality**: Comprehensive error handling, proper state management, and clean separation of concerns

**What could be improved:**
- The docs store is currently small and curated - could be expanded with more comprehensive React/TypeScript documentation
- Code analysis tool uses simple methods to examine code and return - could integrate actual linters or TypeScript compiler checks for indepth examination enhancing learner's knowledge
- User Experience on Web UI can be improved to include commands at every step of an interaction to either add features or jump to another stage for seamless interaction
- Web UI could add more features like saving conversation history or exporting learning plans
- The project is an opinionated workflow of an agent helping build the project from ground up. So if one asks the agent to review a code snippet without starting a project, it will hallucinate.

**Overall**: This project successfully demonstrates mastery of LangGraph and all course concepts while creating a genuinely useful learning tool. The agent maintains coherent state across complex interactions, leverages RAG effectively, and provides meaningful educational guidance. I am satisfied with the comprehensive implementation and the practical utility of the final product.

import json
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import GraphState
from tools import fetch_docs

# LLM for all nodes
llm = ChatOpenAI(model="gpt-4o-mini")  # or another OpenAI chat model


def onboarding_node(state: GraphState) -> GraphState:
    print("DEBUG: onboarding")
    """
    Extracts a structured project specification and learner profile
    from the user's initial request.
    """
    last_msg = state["messages"][-1]
    user_text = last_msg.content

    system = SystemMessage(
        content=(
            "You are a React/TypeScript project coach. "
            "Extract a structured project specification and learner profile "
            "from the user's request. Respond with ONLY valid JSON."
        )
    )
    human = HumanMessage(
        content=(
            "User request:\n"
            f"{user_text}\n\n"
            "Return JSON with fields:\n"
            "{\n"
            '  \"project_summary\": string,\n'
            '  \"features\": string[],\n'
            '  \"assumed_level\": \"beginner\" | \"intermediate\" | \"advanced\"\n'
            "}\n"
        )
    )

    resp = llm.invoke([system, human])
    data = json.loads(resp.content)

    state["project_spec"] = {
        "summary": data["project_summary"],
        "features": data["features"],
    }
    state["learner_profile"] = {
        "assumed_level": data["assumed_level"],
    }
    state["status"] = "planning"

    summary_msg = (
        f"Got it. You want to build: {data['project_summary']} "
        f"with features: {', '.join(data['features'])}. "
        f"I'll assume you're {data['assumed_level']} with React/TS."
    )
    state["messages"].append(AIMessage(content=summary_msg))
    return state


def planning_node(state: GraphState) -> GraphState:
    print("DEBUG: planning")
    """
    Uses project_spec to create (or recreate) a multi-stage learning plan.
    """
    spec = state["project_spec"]

    # If we just came from 'replan', reset status
    if state.get("status") == "replan":
        state["status"] = "planning"

    system = SystemMessage(
        content=(
            "You are a React/TypeScript learning planner. "
            "Break the project into 4-6 stages a learner can follow. "
            "Each stage must have: name, goal, tasks (string[]), "
            "fundamentals (string[]), docs (string[]). "
            "Return JSON: { \"stages\": [ ... ] } and nothing else."
        )
    )
    human = HumanMessage(
        content=(
            f"Project summary: {spec['summary']}\n"
            f"Features: {spec['features']}\n"
            "Design the stages so they teach React/TS concepts incrementally."
        )
    )

    resp = llm.invoke([system, human])
    data = json.loads(resp.content)

    state["stages"] = data["stages"]
    state["current_stage_index"] = 0
    state["status"] = "coaching"

    titles = [s["name"] for s in data["stages"]]
    msg = "Here's your learning plan with stages:\n" + " → ".join(titles)
    state["messages"].append(AIMessage(content=msg))
    return state


def coaching_node(state: GraphState) -> GraphState:
    """
    Stage-aware coach:
    - Explains current stage.
    - Lists tasks + fundamentals.
    - Uses fetch_docs for extra docs.
    - Handles 'done with this stage' and 'add feature'.
    """
    stages = state.get("stages", [])
    i = state.get("current_stage_index", 0)

    # If no stages, just finish.
    if not stages or i >= len(stages):
        state["messages"].append(AIMessage(content="No more stages. You're done!"))
        state["status"] = "finished"
        return state

    stage = stages[i]
    last_msg = state["messages"][-1].content
    last_lower = last_msg.lower()

    # 1) Handle "done with this stage"
    if "done with this stage" in last_lower or "stage finished" in last_lower:
        i += 1
        state["current_stage_index"] = i
        if i >= len(stages):
            state["status"] = "finished"
            state["messages"].append(
                AIMessage(content="Amazing work. All stages are complete – your project is done!")
            )
        else:
            next_stage = stages[i]
            state["status"] = "coaching"
            state["messages"].append(
                AIMessage(
                    content=(
                        f"Nice! Moving to the next stage.\n\n"
                        f"Next stage: {next_stage['name']}\n"
                        f"Goal: {next_stage['goal']}"
                    )
                )
            )
        return state

    # 2) Handle "add/change feature"
    if "add feature" in last_lower or "change feature" in last_lower or "new feature" in last_lower:
        features = state["project_spec"].get("features", [])
        features.append(last_msg)
        state["project_spec"]["features"] = features

        state["status"] = "replan"
        state["messages"].append(
            AIMessage(
                content=(
                    "Got it, you want to change the feature set. "
                    "I'll update the plan in the next step."
                )
            )
        )
        return state

    # 3) Build stage info
    stage_info = (
        f"Stage name: {stage['name']}\n"
        f"Stage goal: {stage['goal']}\n"
        f"Tasks: {stage['tasks']}\n"
        f"Fundamentals: {stage['fundamentals']}\n"
    )

    # 4) RAG: fetch docs
    query = " ".join(stage.get("fundamentals", [])) + " " + last_msg
    docs = fetch_docs(query)
    docs_text = "\n".join(
        [f"- {d['topic']}: {d['content']} (link: {d['link']})" for d in docs]
    ) or "None found"

    system = SystemMessage(
        content=(
            "You are a React/TypeScript coach. "
            "Explain the current stage, the concrete tasks to do now, and the key fundamentals. "
            "Use the provided docs as reference. "
            "Do NOT write the full app; give hints and partial examples. "
            "End by asking the learner to try a specific coding step and report back."
        )
    )

    human = HumanMessage(
        content=(
            f"User message:\n{last_msg}\n\n"
            f"Current stage info:\n{stage_info}\n\n"
            f"Relevant docs:\n{docs_text}\n\n"
            "Respond as a coach:\n"
            "- Restate the stage name and goal.\n"
            "- List 2–4 concrete tasks to do now.\n"
            "- Point out which fundamentals to focus on.\n"
            "- Finish by asking them to try a specific change or step and come back with errors or questions.\n"
        )
    )

    resp = llm.invoke([system, human])
    state["messages"].append(AIMessage(content=resp.content))
    state["status"] = "coaching"
    return state


def route_next_node(state: GraphState) -> str:
    """
    For now, always finish after one coaching step.
    This prevents recursion while we debug.
    """
    return "finished"


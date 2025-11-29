import json
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from state import GraphState

llm = ChatOpenAI(model="gpt-4o-mini")  # or another OpenAI chat model


def onboarding_node(state: GraphState) -> GraphState:
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
    """
    Uses project_spec to create a multi-stage learning plan.
    """
    spec = state["project_spec"]

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
    Temporary coaching stub.
    """
    state["messages"].append(
        AIMessage(content="Coaching stub – real coaching logic coming soon.")
    )
    state["status"] = "finished"
    return state


def route_next_node(state: GraphState) -> str:
    """
    Temporary routing: always finish after one coaching call.
    """
    return "finished"

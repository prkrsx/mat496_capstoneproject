# state.py
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    messages: Annotated[List[Any], add_messages]

    learner_profile: Dict[str, Any]
    project_spec: Dict[str, Any]

    stages: List[Dict[str, Any]]
    current_stage_index: int

    status: str  # "onboarding" | "planning" | "coaching" | "replan" | "finished"

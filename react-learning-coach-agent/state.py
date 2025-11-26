from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    # Conversation history as LangChain Message objects
    messages: Annotated[List[Any], add_messages]

    # Learner/project info (will be used later)
    learner_profile: Dict[str, Any]
    project_spec: Dict[str, Any]

    # Plan info (will be used later)
    stages: List[Dict[str, Any]]
    current_stage_index: int

    # Control/status
    status: str  # "onboarding" | "planning" | "coaching" | "replan" | "finished"

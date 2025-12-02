from langgraph.graph import StateGraph, START, END
from state import GraphState
from nodes import onboarding_node, planning_node, coaching_node

def route_after_onboarding(state: GraphState) -> str:
    """After onboarding, check if we should plan or coach."""
    status = state.get("status", "")
    if status == "onboarding_complete":
        return "planning"
    return "coaching"

def route_after_planning(state: GraphState) -> str:
    """After planning, end execution and wait for next user message."""
    return "end"

def route_coaching(state: GraphState) -> str:
    """Route from coaching based on status."""
    status = state.get("status", "coaching")
    if status in ["replan"]:
        return "planning"
    if status == "finished":
        return "finished"
    # When status is coaching, end the graph and wait for next user input
    return "end"

def build_graph():
    workflow = StateGraph(GraphState)
    
    # Add nodes
    workflow.add_node("onboarding", onboarding_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("coaching", coaching_node)
    
    # Define flow
    workflow.add_edge(START, "onboarding")
    workflow.add_conditional_edges(
        "onboarding",
        route_after_onboarding,
        {"planning": "planning", "coaching": "coaching"}
    )
    workflow.add_conditional_edges(
        "planning",
        route_after_planning,
        {"end": END}
    )
    workflow.add_conditional_edges(
        "coaching",
        route_coaching,
        {
            "planning": "planning",
            "end": END,
            "finished": END
        }
    )
    
    return workflow.compile()

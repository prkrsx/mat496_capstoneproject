from langgraph.graph import StateGraph, START, END

from state import GraphState
from nodes import onboarding_node, planning_node, coaching_node, route_next_node


def build_graph():
    g = StateGraph(GraphState)

    # Add nodes
    g.add_node("onboarding", onboarding_node)
    g.add_node("planning", planning_node)
    g.add_node("coaching", coaching_node)

    # Linear flow: START -> onboarding -> planning -> coaching
    g.add_edge(START, "onboarding")
    g.add_edge("onboarding", "planning")
    g.add_edge("planning", "coaching")

    # After coaching, decide what to do next
    g.add_conditional_edges(
        "coaching",
        route_next_node,
        {
            "stay_in_coaching": "coaching",
            "replan": "planning",
            "finished": END,
        },
    )

    return g.compile()

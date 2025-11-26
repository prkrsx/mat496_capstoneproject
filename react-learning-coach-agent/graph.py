from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

from state import GraphState


def echo_node(state: GraphState) -> GraphState:
    """
    Simple test node for Phase 1:
    - Reads the last message (a HumanMessage)
    - Appends an AIMessage that echoes it
    """
    last_msg = state["messages"][-1]  # HumanMessage
    last_text = last_msg.content

    # Append AIMessage (not a plain dict)
    state["messages"].append(
        AIMessage(content=f"Echo: {last_text}")
    )
    return state


def build_graph():
    """
    Build a minimal StateGraph with a single echo node.
    """
    g = StateGraph(GraphState)
    g.add_node("echo", echo_node)
    g.add_edge(START, "echo")
    g.add_edge("echo", END)
    return g.compile()

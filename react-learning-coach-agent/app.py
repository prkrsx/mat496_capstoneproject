"""
LangGraph Studio entrypoint.
"""
from graph import build_graph

def agent():
    """Compiled graph for LangGraph CLI/Studio."""
    return build_graph()

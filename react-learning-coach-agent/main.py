#!/usr/bin/env python3
"""
React Learning Coach: Interactive CLI for React/TypeScript project learning.
"""

from dotenv import load_dotenv
from typing import Dict, Any
from pathlib import Path

load_dotenv()

from langchain_core.messages import HumanMessage
from yaspin import yaspin
from yaspin.spinners import Spinners
from graph import build_graph

def print_header() -> None:
    """Application header."""
    print("\n" + "=" * 70)
    print(" 🎓 REACT LEARNING COACH")
    print("=" * 70)
    print("I'll guide you through building React/TypeScript projects step-by-step.\n")
    print("💡 Tip: I adapt to your level (beginner/intermediate/advanced)")
    print("💡 Type 'help' anytime to see available commands\n")

def print_help() -> None:
    """Formatted command help."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                               AVAILABLE COMMANDS                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ NAVIGATION                                                                   ║
║   • continue / start       → Begin or show current stage                     ║
║   • done / next stage      → Complete stage and move forward                 ║
║   • go to stage X          → Jump to any stage (e.g., 'go to stage 3')       ║
║                                                                              ║
║ LEARNING                                                                     ║
║   • give me exercises      → Get 3 practice problems                         ║
║   • give me exercises for X→ Practice specific topic                         ║
║   • [ask any question]     → Get explanations                                ║
║                                                                              ║
║ PLANNING                                                                     ║
║   • add feature: [desc]    → Add new feature to project                      ║
║   • I'm actually [level]   → Change difficulty level                         ║
║                                                                              ║
║ OTHER                                                                        ║
║   • help                   → Show this menu                                  ║
║   • quit / exit            → End session                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

def create_initial_state() -> Dict[str, Any]:
    """Clean initial state."""
    return {
        "messages": [],
        "learner_profile": {},
        "project_spec": {"features": []},
        "stages": [],
        "current_stage_index": 0,
        "status": "onboarding",
    }

def print_new_ai_messages(state: Dict[str, Any], last_count: int) -> int:
    """Print new AI messages only."""
    new_msgs = state["messages"][last_count:]
    for msg in new_msgs:
        if msg.type == "ai":
            print(f"\n{msg.content}\n")
            print("-" * 70 + "\n")
    return len(state["messages"])

def main() -> None:
    """Main CLI loop."""
    state = create_initial_state()
    
    print_header()
    print("What would you like to build? (e.g., 'a todo app with TypeScript')\n")

    last_count = 0
    first_run = True

    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("\n✅ Happy coding! Keep learning and building! 🚀\n")
            break

        if user_input.lower() == "help":
            print_help()
            continue

        state["messages"].append(HumanMessage(content=user_input))

        # FIXED: Always use FULL GRAPH - no manual routing
        with yaspin(Spinners.dots12, text="🤔 Coach is thinking...") as spinner:
            graph = build_graph()
            state = graph.invoke(state)
            spinner.ok("✓ ")

        last_count = print_new_ai_messages(state, last_count)
        first_run = False

if __name__ == "__main__":
    main()

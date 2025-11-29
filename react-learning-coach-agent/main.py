from dotenv import load_dotenv
load_dotenv()  # load OPENAI_API_KEY etc. if needed later

from langchain_core.messages import HumanMessage, AIMessage

from graph import build_graph


def main():
    graph = build_graph()

    # Initialize state with required keys
    state = {
        "messages": [],
        "learner_profile": {},
        "project_spec": {},
        "stages": [],
        "current_stage_index": 0,
        "status": "onboarding",
    }

    while True:
        user = input("You: ")
        if user.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # Append user input as a HumanMessage
        state["messages"].append(HumanMessage(content=user))

        # Run the graph once
        state = graph.invoke(state)

        # The last message should now be an AIMessage; print its content
        last_msg = state["messages"][-1]
        print("Agent:", last_msg.content)



if __name__ == "__main__":
    main()

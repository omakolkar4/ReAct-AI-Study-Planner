from agent import ReActAgent


def main():
    print("=" * 60)
    print("                 AI STUDY PLANNER")
    print("                 ReAct Reasoning Agent")
    print("=" * 60)

    goal = input("\nEnter your goal: ").strip()
    if not goal:
        print("Please enter a valid goal.")
        return

    print("\nRunning the local ReAct agent...\n")
    result = ReActAgent().run(goal)

    print("=" * 60)
    print("                    STUDY PLAN RESULT")
    print("=" * 60)
    print("Subject:", result.get("subject"))
    print("Days:", result.get("exam_days"))
    print("Topics:", len(result.get("topics", [])))
    print("Study-plan days:", len(result.get("study_plan", {}).get("days", [])))
    print("Questions:", len(result.get("questions", [])))
    print("Replanned:", result.get("replanned"))
    print("Completed:", result.get("completed"))

    print("\n" + "=" * 60)
    print("             THOUGHT / ACTION / OBSERVATION")
    print("=" * 60)
    for index, step in enumerate(result.get("trace", []), start=1):
        print(f"\nSTEP {index} — {step.get('status', '').upper()}")
        print("Thought:", step.get("thought", ""))
        print("Action:", step.get("action", ""))
        print("Observation:", step.get("observation", ""))
    print("\nExecution finished.")


if __name__ == "__main__":
    main()

import json
import streamlit as st
from agent import ReActAgent

st.set_page_config(
    page_title="ReAct AI Study Planner",
    page_icon="📚",
    layout="wide",
)

st.title("📚 ReAct AI Study Planner")
st.caption("Local Qwen 2.5 3B model through Ollama | Thought → Action → Observation")

with st.sidebar:
    st.header("About the Agent")
    st.write("**LLM:** Qwen 2.5 3B")
    st.write("**Framework:** ReAct (Reason + Act)")
    st.write("**Runtime:** Local Ollama")
    st.write("**Tools:** Topic identification, notes checking, replanning, timetable and questions")
    st.divider()
    st.caption("The trace shows short, user-facing action rationales and tool observations.")

goal = st.text_area(
    "🎯 Enter your examination goal",
    value="Prepare me for my NLP examination in 3 days.",
    height=100,
)

if st.button("🚀 Generate My Study Plan", type="primary", use_container_width=True):
    if not goal.strip():
        st.warning("Please enter an examination goal.")
    else:
        try:
            with st.spinner("The local agent is executing its tools..."):
                result = ReActAgent().run(goal.strip())
            st.session_state["study_result"] = result
        except Exception as error:
            st.error("Unable to execute the AI agent. Check that Ollama is running and the model is installed.")
            st.exception(error)

result = st.session_state.get("study_result")

if result:
    st.divider()
    if result.get("error"):
        st.error(result["error"])
    elif result.get("completed"):
        st.success("The agent completed the study-planning workflow.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Subject", result.get("subject") or "Not identified")
    c2.metric("Days Remaining", result.get("exam_days", 0))
    c3.metric("Practice Questions", len(result.get("questions", [])))

    if result.get("replanned"):
        st.warning(
            "Dynamic replanning occurred: local notes were unavailable, "
            "so the agent switched to alternative study resources."
        )

    st.subheader("🧩 Agent Sub-tasks")
    subtasks = [
        "Identify the subject and important examination topics",
        "Check the local study_materials folder",
        "If notes are missing, find alternative study resources",
        "Create a day-wise examination timetable",
        "Generate ten practice questions",
    ]
    for number, task in enumerate(subtasks, start=1):
        st.write(f"{number}. {task}")

    st.divider()
    st.subheader("📖 Important Topics")
    for topic in result.get("topics", []):
        with st.container(border=True):
            st.markdown(
                f"**{topic.get('name', 'Topic')}** — "
                f"{topic.get('priority', 'Normal')} Priority"
            )
            if topic.get("reason"):
                st.write(topic["reason"])

    st.divider()
    st.subheader("🗓️ Personalised Study Timetable")
    plan = result.get("study_plan", {})
    days = plan.get("days", [])
    if len(days) != result.get("exam_days", 0):
        st.warning(
            f"Expected {result.get('exam_days')} days, but received {len(days)}."
        )
    for day in days:
        with st.expander(
            f"Day {day.get('day', '')}: {day.get('title', 'Study Plan')}",
            expanded=True,
        ):
            for session in day.get("sessions", []):
                st.markdown(f"**{session.get('time', '')} — {session.get('topic', '')}**")
                st.write(session.get("task", ""))
            st.markdown("**Daily Revision**")
            st.write(day.get("revision", ""))
            st.success(f"Daily Goal: {day.get('daily_goal', '')}")

    if plan.get("plan_source"):
        st.caption(plan["plan_source"])
    if plan.get("final_tips"):
        st.subheader("💡 Final Preparation Tips")
        for tip in plan["final_tips"]:
            st.write(f"• {tip}")

    st.divider()
    st.subheader("📚 Study Resources")
    resources = result.get("resources", {}).get("resources", [])
    if resources:
        for resource in resources:
            with st.container(border=True):
                st.markdown(f"**{resource.get('title', 'Study Resource')}**")
                st.caption(resource.get("type", "Resource"))
                st.write(resource.get("purpose", ""))
        if result.get("resources", {}).get("source"):
            st.caption(f"Resource source: {result['resources']['source']}")
    else:
        st.info("No study resources were returned.")

    st.divider()
    st.subheader("✍️ Practice Questions")
    for index, question in enumerate(result.get("questions", []), start=1):
        with st.container(border=True):
            st.markdown(f"**Q{index}. {question.get('question', '')}**")
            st.caption(
                f"Topic: {question.get('topic', '')} | "
                f"Difficulty: {question.get('difficulty', '')}"
            )

    st.divider()
    with st.expander("🤖 Agent Activity — ReAct Trace", expanded=True):
        st.caption("Short rationale (Thought), tool call (Action), and result (Observation).")
        for index, step in enumerate(result.get("trace", []), start=1):
            st.markdown(f"### Step {index}")
            st.markdown("**💭 Thought**")
            st.write(step.get("thought", "Not recorded"))
            st.markdown("**⚙️ Action**")
            st.code(step.get("action", "Not recorded"))
            st.markdown("**👁️ Observation**")
            observation = step.get("observation", "")
            if isinstance(observation, (dict, list)):
                st.json(observation)
            else:
                st.write(observation)
            status = step.get("status", "success")
            if status == "failed":
                st.error("Tool execution failed.")
            elif status == "replanned":
                st.warning("The agent changed its plan after the earlier failure.")
            else:
                st.success("Action executed successfully.")
            st.divider()

    st.download_button(
        "⬇️ Download Study Plan",
        data=json.dumps(plan, indent=4, ensure_ascii=False),
        file_name="AI_Study_Plan.json",
        mime="application/json",
    )

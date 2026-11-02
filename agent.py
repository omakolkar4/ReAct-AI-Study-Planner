from tools import (
    generate_thought,
    identify_topics,
    check_local_notes,
    find_alternative_material,
    create_study_plan,
    generate_questions,
)


class ReActAgent:
    """A controlled ReAct workflow: reason, execute a tool, observe, and replan."""

    def __init__(self):
        self.trace = []

    def record_step(self, thought, action, observation, status="success"):
        self.trace.append({
            "thought": thought,
            "action": action,
            "observation": observation,
            "status": status,
        })

    def run(self, goal):
        self.trace = []
        state = {
            "goal": goal,
            "subject": "",
            "exam_days": 3,
            "topics": [],
            "notes": [],
            "resources": {"resources": []},
            "study_plan": {},
            "questions": [],
            "replanned": False,
            "completed": False,
            "error": None,
        }

        # 1. Understand the goal and break it into topics.
        action = "identify_topics"
        thought = generate_thought(action, {"goal": goal})
        try:
            result = identify_topics(goal)
            state.update({
                "subject": result["subject"],
                "exam_days": result["exam_days"],
                "topics": result["topics"],
            })
            self.record_step(thought, action, result, "success")
        except Exception as error:
            self.record_step(thought, action, str(error), "failed")
            state["error"] = str(error)
            return self.finish_result(state)

        # 2. Check whether local notes are available.
        action = "check_local_notes"
        thought = generate_thought(action, {
            "subject": state["subject"],
            "topics": [t["name"] for t in state["topics"]],
        })
        try:
            result = check_local_notes()
            state["notes"] = result["notes"]
            state["resources"] = {
                "resources": [
                    {
                        "title": note["filename"],
                        "type": "Local Study Notes",
                        "purpose": "Use this local file for examination preparation.",
                    }
                    for note in state["notes"]
                ],
                "source": "Local study_materials folder",
            }
            self.record_step(thought, action, {
                "message": result["message"],
                "notes_found": [n["filename"] for n in state["notes"]],
            }, "success")
        except FileNotFoundError as error:
            self.record_step(
                thought, action, f"FileNotFoundError: {error}", "failed"
            )
            state["replanned"] = True

            # 3. Replan because the expected local notes were unavailable.
            action = "find_alternative_material"
            thought = generate_thought(action, {
                "subject": state["subject"],
                "topics": [t["name"] for t in state["topics"]],
                "previous_failure": str(error),
                "reason": "Local study notes were unavailable.",
            })
            try:
                state["resources"] = find_alternative_material(
                    state["subject"], state["topics"]
                )
                self.record_step(
                    thought,
                    action,
                    {
                        "reason_for_replanning": "Local notes were unavailable.",
                        "alternative_resources": state["resources"],
                    },
                    "replanned",
                )
            except Exception as alternative_error:
                self.record_step(
                    thought, action, str(alternative_error), "failed"
                )
                state["error"] = str(alternative_error)
                return self.finish_result(state)
        except Exception as error:
            self.record_step(thought, action, str(error), "failed")
            state["error"] = str(error)
            return self.finish_result(state)

        # 4. Create one study plan. The tool validates the requested day count.
        action = "create_study_plan"
        thought = generate_thought(action, {
            "subject": state["subject"],
            "exam_days": state["exam_days"],
            "topic_count": len(state["topics"]),
            "resource_count": len(state["resources"].get("resources", [])),
        })
        try:
            state["study_plan"] = create_study_plan(
                state["subject"],
                state["exam_days"],
                state["topics"],
                state["resources"],
            )
            actual_days = len(state["study_plan"].get("days", []))
            self.record_step(thought, action, {
                "requested_days": state["exam_days"],
                "generated_days": actual_days,
                "plan_source": state["study_plan"].get("plan_source", "Qwen response"),
            }, "success")
        except Exception as error:
            self.record_step(thought, action, str(error), "failed")
            state["error"] = str(error)
            return self.finish_result(state)

        # 5. Generate one set of practice questions.
        action = "generate_questions"
        thought = generate_thought(action, {
            "subject": state["subject"],
            "topic_count": len(state["topics"]),
        })
        try:
            result = generate_questions(state["subject"], state["topics"])
            state["questions"] = result["questions"]
            self.record_step(thought, action, {
                "questions_generated": len(state["questions"]),
            }, "success")
        except Exception as error:
            self.record_step(thought, action, str(error), "failed")
            state["error"] = str(error)
            return self.finish_result(state)

        # 6. Finish and report completion.
        action = "finish"
        thought = generate_thought(action, {
            "study_plan_created": bool(state["study_plan"]),
            "questions_generated": len(state["questions"]),
        })
        state["completed"] = bool(
            state["topics"]
            and len(state["study_plan"].get("days", [])) == state["exam_days"]
            and len(state["questions"]) == 10
        )
        self.record_step(thought, action, {
            "completed": state["completed"],
            "subject": state["subject"],
            "study_days": len(state["study_plan"].get("days", [])),
            "questions_generated": len(state["questions"]),
            "replanned": state["replanned"],
        }, "success" if state["completed"] else "failed")

        if not state["completed"]:
            state["error"] = state["error"] or "The final output did not pass validation."
        return self.finish_result(state)

    def finish_result(self, state):
        state["trace"] = self.trace
        return state

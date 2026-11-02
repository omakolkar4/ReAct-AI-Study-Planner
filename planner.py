
# planner.py

class TaskPlanner:

    def create_plan(self, goal):

        print("\n[PLANNER] Breaking the goal into subtasks...")

        tasks = [
            "Identify important NLP topics",
            "Check local study notes",
            "Find alternative study material if notes are unavailable",
            "Create a study timetable",
            "Generate practice questions"
        ]

        return tasks

    def replan(self, failed_task, error):

        print("\n[REPLANNING] Original plan needs modification.")
        print("Failed Task:", failed_task)
        print("Reason:", error)

        new_plan = [
            "Find alternative NLP study material",
            "Create a study timetable",
            "Generate practice questions"
        ]

        print("[REPLANNING] New plan created successfully.")

        return new_plan

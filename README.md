<<<<<<< HEAD

# AI Study Planner – ReAct Reasoning Agent

## 1. Introduction

The AI Study Planner is a reasoning agent that uses the ReAct (Reason + Act) approach to complete multi-step goals.

It breaks a large goal into smaller tasks, executes actions, observes the results and changes its plan when an error occurs.

## 2. Objective

To implement a reasoning agent that can perform task decomposition, execute multiple actions and handle failures through dynamic replanning.

## 3. Technologies Used

- Python
- Object-Oriented Programming
- ReAct Reasoning Framework
- Exception Handling

## 4. Features

- Goal input from the user
- Automatic task decomposition
- Sequential task execution
- Thought, Action and Observation trace
- Failure detection
- Dynamic replanning
- Final result generation

## 5. Working

The agent accepts a study-related goal and divides it into smaller subtasks.

It first identifies NLP topics and attempts to access local notes.

When the notes are unavailable, the agent detects the failure and creates a new plan.

It then uses alternative study material, creates a timetable and generates practice questions.

## 6. Execution

Run the following command:

```bash
python main.py
```

## 7. Conclusion

The project demonstrates how a ReAct reasoning agent can complete a multi-step goal.

It also demonstrates dynamic replanning by detecting a failed action and selecting an alternative approach.
=======
# ReAct-AI-Study-Planner
AI Study Planner using ReAct Reasoning Agent, Python, Streamlit, Ollama and Qwen 2.5 3B.
>>>>>>> 93e97a78552e47a1e72679a26216c70721291184

import json
from pathlib import Path
import ollama

MODEL = "qwen2.5:3b"
STUDY_MATERIALS_DIR = Path(__file__).parent / "study_materials"


def ask_ai(prompt, system_prompt="You are a helpful AI study assistant."):
    """Call the locally running Ollama model and parse its JSON response."""
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        format="json",
        options={"temperature": 0.3},
    )
    content = response.message.content
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start, end = content.find("{"), content.rfind("}")
        if start >= 0 and end > start:
            return json.loads(content[start:end + 1])
        raise ValueError("Qwen did not return valid JSON.")


def generate_thought(action, context):
    """Create a short, user-facing rationale for the execution trace."""
    prompt = f"""
Action: {action}
Context: {json.dumps(context, ensure_ascii=False)}
Write one concise sentence explaining why this action is the next useful step.
Return JSON: {{"thought": "one sentence"}}
"""
    try:
        result = ask_ai(prompt)
        return result.get(
            "thought",
            f"I will run {action} using the information currently available.",
        )
    except Exception:
        return f"I will run {action} using the information currently available."


def identify_topics(goal):
    prompt = f"""
A student has this examination goal: {goal}
Identify the subject, number of days remaining, and 8 to 10 important topics.
Use the number of days explicitly stated in the goal; if not stated, use 3.
Return JSON:
{{
  "subject": "Subject name",
  "exam_days": 3,
  "topics": [
    {{"name": "Topic", "priority": "High", "reason": "Why it matters"}}
  ]
}}
"""
    result = ask_ai(prompt)
    subject = str(result.get("subject", "")).strip()
    topics = result.get("topics")
    if not subject or not isinstance(topics, list) or not topics:
        raise ValueError("Qwen did not identify a subject and study topics.")

    try:
        days = int(result.get("exam_days", 3))
    except (TypeError, ValueError):
        days = 3

    clean_topics = []
    for item in topics:
        if isinstance(item, str):
            item = {"name": item, "priority": "Normal", "reason": ""}
        if isinstance(item, dict) and item.get("name"):
            clean_topics.append({
                "name": str(item["name"]),
                "priority": str(item.get("priority", "Normal")),
                "reason": str(item.get("reason", "")),
            })
    if not clean_topics:
        raise ValueError("No usable study topics were returned.")

    return {
        "subject": subject,
        "exam_days": max(1, min(days, 14)),
        "topics": clean_topics[:12],
    }


def check_local_notes():
    """Read .txt and .md files from study_materials; fail if none are usable."""
    if not STUDY_MATERIALS_DIR.exists():
        raise FileNotFoundError(
            f"Study materials folder not found: {STUDY_MATERIALS_DIR}"
        )

    paths = list(STUDY_MATERIALS_DIR.glob("*.txt"))
    paths += list(STUDY_MATERIALS_DIR.glob("*.md"))
    notes = []
    for path in paths:
        content = path.read_text(encoding="utf-8", errors="ignore").strip()
        if content:
            notes.append({"filename": path.name, "content": content[:10000]})

    if not notes:
        raise FileNotFoundError(
            "No non-empty .txt or .md study notes were found in study_materials."
        )

    return {
        "status": "success",
        "message": f"Found {len(notes)} local study file(s).",
        "notes": notes,
    }


def find_alternative_material(subject, topics):
    """Suggest alternatives when local notes cannot be accessed."""
    names = [t.get("name", "") for t in topics]
    prompt = f"""
Suggest five useful study resources for an examination.
Subject: {subject}
Topics: {json.dumps(names, ensure_ascii=False)}
Return JSON:
{{
 "resources": [
  {{"title": "Resource suggestion", "type": "Book/Video/Practice/Reference",
    "purpose": "What the student should use it for"}}
 ]
}}
Do not invent URLs or claim that a link has been verified.
"""
    try:
        result = ask_ai(prompt)
        resources = result.get("resources", [])
        cleaned = [
            {
                "title": str(r.get("title", "")).strip(),
                "type": str(r.get("type", "Study reference")),
                "purpose": str(r.get("purpose", "")),
            }
            for r in resources
            if isinstance(r, dict) and str(r.get("title", "")).strip()
        ]
        if cleaned:
            return {"resources": cleaned[:5], "source": "Qwen-generated suggestions"}
    except Exception:
        pass

    # A transparent fallback: suggestions, not claimed as verified links.
    return {
        "resources": [
            {
                "title": f"University syllabus and classroom material for {subject}",
                "type": "Course reference",
                "purpose": "Use the prescribed syllabus to confirm topic coverage.",
            },
            {
                "title": f"Textbook chapters covering {subject}",
                "type": "Textbook",
                "purpose": "Revise definitions, concepts and worked examples.",
            },
            {
                "title": "Instructor-recommended lecture videos",
                "type": "Video",
                "purpose": "Use videos to revisit difficult concepts.",
            },
            {
                "title": "Previous university question papers",
                "type": "Practice",
                "purpose": "Practise the question patterns used in examinations.",
            },
            {
                "title": "Self-made topic-wise revision notes",
                "type": "Revision",
                "purpose": "Summarise key terms, diagrams and differences.",
            },
        ],
        "source": "Built-in fallback suggestions; not externally verified",
    }


def _fallback_study_plan(subject, exam_days, topics):
    """Deterministic backup so the result always has the requested number of days."""
    names = [t.get("name", "Revision") for t in topics] or [subject]
    days = []
    for day_number in range(1, exam_days + 1):
        first = names[(day_number - 1) % len(names)]
        second = names[day_number % len(names)] if len(names) > 1 else first
        third = names[(day_number + 1) % len(names)] if len(names) > 2 else second
        sessions = [
            {
                "time": "9:00 AM - 10:30 AM",
                "topic": first,
                "task": f"Study the core concepts of {first} and write concise notes.",
            },
            {
                "time": "11:00 AM - 12:00 PM",
                "topic": second,
                "task": f"Practise examples and short-answer questions on {second}.",
            },
        ]
        if len(names) > 2:
            sessions.append({
                "time": "4:00 PM - 5:00 PM",
                "topic": third,
                "task": f"Revise {third} and test your understanding.",
            })
        days.append({
            "day": day_number,
            "title": f"Day {day_number}: {subject} preparation",
            "sessions": sessions,
            "revision": "Spend 20–30 minutes recalling the day's topics without looking at notes.",
            "daily_goal": f"Complete the scheduled sessions and revise the topics covered on Day {day_number}.",
        })
    return {
        "days": days,
        "final_tips": [
            "Prioritise topics listed in your official syllabus.",
            "Take short breaks between study sessions.",
            "Attempt a timed revision test before the examination.",
        ],
        "plan_source": "Python fallback timetable because the AI response failed validation",
    }


def create_study_plan(subject, exam_days, topics, resources):
    prompt = f"""
Create a personalised {exam_days}-day examination timetable.
Subject: {subject}
Days remaining: {exam_days}
Topics: {json.dumps(topics, ensure_ascii=False)}
Resources: {json.dumps(resources, ensure_ascii=False)[:6000]}
Requirements:
- Return exactly {exam_days} days numbered 1 through {exam_days}.
- Include 2 or 3 sessions per day, each with time, topic and task.
- Include daily revision and a daily goal for every day.
- Include final preparation tips.
Return JSON:
{{
 "days": [
  {{
   "day": 1, "title": "Day 1 title",
   "sessions": [
    {{"time": "9 AM - 10 AM", "topic": "Topic", "task": "Study task"}}
   ],
   "revision": "Revision instruction",
   "daily_goal": "Daily goal"
  }}
 ],
 "final_tips": ["Tip"]
}}
"""
    try:
        result = ask_ai(prompt)
        days = result.get("days")
        valid = isinstance(days, list) and len(days) == exam_days
        if valid:
            for index, day in enumerate(days, start=1):
                if not isinstance(day, dict):
                    valid = False
                    break
                if not isinstance(day.get("sessions"), list) or not day["sessions"]:
                    valid = False
                    break
                day["day"] = index
                day.setdefault("title", f"Day {index}")
                day.setdefault("revision", "Review the topics studied today.")
                day.setdefault("daily_goal", "Complete today's study sessions.")
                for session in day["sessions"]:
                    if isinstance(session, dict):
                        session.setdefault("time", "Study session")
                        session.setdefault("topic", subject)
                        session.setdefault("task", "Study and practise this topic.")
        if valid:
            result["days"] = days
            result.setdefault("final_tips", [])
            return result
    except Exception:
        pass

    return _fallback_study_plan(subject, exam_days, topics)


def generate_questions(subject, topics):
    prompt = f"""
Generate exactly 10 examination practice questions.
Subject: {subject}
Topics: {json.dumps(topics, ensure_ascii=False)}
Return JSON:
{{
 "questions": [
  {{"question": "Question text", "topic": "Topic", "difficulty": "Easy"}}
 ]
}}
Use a mixture of Easy, Medium and Hard questions.
"""
    try:
        result = ask_ai(prompt)
        questions = result.get("questions", [])
        cleaned = [
            {
                "question": str(q.get("question", "")).strip(),
                "topic": str(q.get("topic", "General")),
                "difficulty": str(q.get("difficulty", "Medium")),
            }
            for q in questions
            if isinstance(q, dict) and str(q.get("question", "")).strip()
        ]
        if len(cleaned) >= 10:
            return {"questions": cleaned[:10]}
    except Exception:
        pass

    topic_names = [t.get("name", subject) for t in topics] or [subject]
    fallback = []
    templates = [
        ("Define {topic} and explain its importance.", "Easy"),
        ("Describe the main steps or components of {topic}.", "Medium"),
        ("Explain {topic} with a suitable example.", "Easy"),
        ("Discuss the advantages and limitations of {topic}.", "Hard"),
        ("Differentiate {topic} from a related concept.", "Medium"),
        ("How can {topic} be applied to a practical problem?", "Hard"),
        ("Write short notes on the key concepts in {topic}.", "Easy"),
        ("Explain the challenges associated with {topic}.", "Medium"),
        ("Give an example-based explanation of {topic}.", "Medium"),
        ("Evaluate the role of {topic} in {subject}.", "Hard"),
    ]
    for index, (template, difficulty) in enumerate(templates):
        topic = topic_names[index % len(topic_names)]
        fallback.append({
            "question": template.format(topic=topic, subject=subject),
            "topic": topic,
            "difficulty": difficulty,
        })
    return {"questions": fallback}

REACT AI STUDY PLANNER — RUN INSTRUCTIONS

1. Open this folder in VS Code.
2. Open PowerShell in the project folder.
3. Create/activate a virtual environment if you do not already have one:
   python -m venv venv
   .\venv\Scripts\Activate.ps1
4. Install packages:
   pip install -r requirements.txt
5. Make sure Ollama is installed and running.
6. Download the model once if needed:
   ollama pull qwen2.5:3b
7. Run the web application:
   streamlit run app.py

To run the terminal version instead:
   python main.py

DYNAMIC REPLANNING TEST:
- For the missing-notes scenario, ensure the project folder does not contain
  a study_materials folder with non-empty .txt or .md notes.
- The check_local_notes tool should then report FileNotFoundError.
- The agent should execute find_alternative_material and continue.
- Do not delete any personal notes just to perform this test; use a separate
  empty test folder or temporarily move sample notes if appropriate.

If valid local .txt or .md notes exist in study_materials, the agent uses
them and does not replan. This is the normal successful-notes scenario.

The fallback timetable and question set are used only if the model returns
an invalid response. They are clearly labelled in the application where
applicable. Alternative resource suggestions are not verified external links.

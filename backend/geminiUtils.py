import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

def get_summary_and_action_items(transcript_text: str) -> str:
    if not transcript_text:
        return {"error": "No transcript text provided for summarization."}
    
    response_schema = {
        "type": "OBJECT",
        "properties": {
            "summary": {"type": "STRING", "description": "Concise summary of the meeting."},
            "action_items": {
                "type": "ARRAY",
                "description": "List of actionable tasks from the meeting.",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "task": {"type": "STRING", "description": "Clear description of the task."},
                        "assignee": {"type": "STRING", "nullable": True, "description": "Person or team responsible, or 'Unassigned'."},
                        "deadline": {"type": "STRING", "nullable": True, "description": "Stated or inferred deadline (e.g., YYYY-MM-DD, 'ASAP', 'Next Week')."},
                        "status": {"type": "STRING", "enum": ["new", "in-progress", "completed"], "default": "new", "description": "Current status of the action item."}
                    },
                    "required": ["task", "status"] 
                }
            },
            "key_decisions": {
                "type": "ARRAY",
                "description": "List of key decisions made during the meeting.",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "description": {"type": "STRING", "description": "Description of the key decision."},
                        "participants_involved": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "List of participants involved in the decision."},
                        "date_made": {"type": "STRING", "description": "Date the decision was made (YYYY-MM-DD)."}
                    },
                    "required": ["description", "date_made"]
                }
            }
        },
        "required": ["summary", "action_items", "key_decisions"]
    }

    prompt = f"""
    You are an expert meeting assistant tasked with summarizing discussions, identifying actionable tasks, and extracting key decisions.
    Given the following meeting transcript, please perform the following tasks and output the result as a JSON object strictly following the provided schema:

    1.  Generate a concise and human-readable summary of the key discussions, decisions, and outcomes from the meeting. The summary should capture the essence of the conversation without unnecessary details.

    2.  Extract all action items mentioned or implied in the transcript. For each action item, provide the 'task', 'assignee' (infer if not explicit, or 'Unassigned'), 'deadline' (infer if not explicit, or 'No Deadline'), and 'status' (default to 'new').

    3.  Extract all key decisions made during the meeting. For each decision, provide a 'description', 'participants_involved' (list of names), and the 'date_made' (infer if not explicit, or use the current date if no specific date is mentioned in the transcript).

    ---
    ## Meeting Transcript:
    {transcript_text}
    ---
    """
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": response_schema
            }
        )

        if not response or not response.text:
            return {"error": "The model did not return a valid response."}

        parsed_json = json.loads(response.text)
        return parsed_json

    except json.JSONDecodeError as e:
        print(f"JSON parsing error from model response: {e}")
        print(f"Raw model response text: {response.text}")
        return {"error": f"Failed to parse JSON response from model: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred during content generation: {e}")
        return {"error": f"Could not generate summary and action items: {e}. Please try again later."}
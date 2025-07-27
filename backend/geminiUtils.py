import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")  # or gemini-pro

def get_summary_and_action_items(transcript_text: str):
    if not transcript_text:
        return {"error": "No transcript text provided for summarization."}

    response_schema = {
        "type": "OBJECT",
        "properties": {
            "summary": {"type": "STRING"},
            "action_items": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "task": {"type": "STRING"},
                        "assignee": {"type": "STRING"},
                        "deadline": {"type": "STRING"},
                        "status": {"type": "STRING", "enum": ["new", "in-progress", "completed"]}
                    },
                    "required": ["task", "status"]
                }
            },
            "key_decisions": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "description": {"type": "STRING"},
                        "participants_involved": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "date_made": {"type": "STRING"}
                    },
                    "required": ["description", "date_made"]
                }
            },
            "speakers_detected": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Names or identifiers of speakers who contributed"
            },
            "tone_overview": {
                "type": "STRING",
                "description": "Overall tone or sentiment of the meeting"
            },
            "important_topics": {
                "type": "ARRAY",
                "items": {"type": "STRING"},
                "description": "Major themes or topics discussed"
            }
        },
        "required": ["summary", "action_items", "key_decisions"]
    }


    prompt = f"""
    You are an advanced meeting assistant with smart context awareness.

    TRANSCRIPT:
    ---
    {transcript_text}
    ---

    Instructions:
    1. Provide a concise summary.
    2. Extract all action items (task, assignee, deadline, status).
    3. Extract key decisions (description, participants involved, date).
    4. Detect and list all speakers.
    5. Provide a high-level tone overview (e.g., optimistic, tense, goal-oriented).
    6. Identify 3-5 important topics discussed.

    Make sure to return valid JSON following this schema exactly.
    Avoid hallucinations and use only transcript data.
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
            print("❌ No response text from Gemini.")
            return {"error": "Empty response from Gemini"}

        print("✅ Raw response from Gemini:\n", response.text)
        parsed_json = json.loads(response.text)
        return parsed_json

    except json.JSONDecodeError as e:
        print("❌ JSON Decode Error:", e)
        print("🔍 Response text that failed:\n", response.text)
        return {"error": f"Invalid JSON format from Gemini: {e}"}

    except Exception as e:
        print("🔥 General Gemini Error:", e)
        return {"error": f"Could not generate summary and action items: {e}"}

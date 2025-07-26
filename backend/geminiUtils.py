import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def get_summary_and_action_items(transcript_text):
    prompt = f"""
    You are a meeting assistant. Given the meeting transcript below:
    
    {transcript_text}
    
    1. Summarize the meeting in human-readable format.
    2. Extract action items with:
        - Task
        - Assignee (if mentioned)
        - Deadline (infer if possible)
    Return in a structured format (like JSON or Markdown).
    """
    response = model.generate_content(prompt)
    return response.text

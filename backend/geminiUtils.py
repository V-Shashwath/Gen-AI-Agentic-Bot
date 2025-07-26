import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

def generate_summary(transcript):
    try:
        model = genai.GenerativeModel("gemini-pro")  # ✅ No `models/` or v1beta

        prompt = f"""
        You are an AI meeting assistant.
        Given the following meeting transcript:

        ====
        {transcript}
        ====

        1. Provide a concise summary.
        2. Extract clear action items.
        3. Format output clearly for sharing.

        """

        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        print("🔥 Gemini API failed:", repr(e))
        return "Gemini error"

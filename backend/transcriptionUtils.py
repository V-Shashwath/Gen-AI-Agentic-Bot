import assemblyai as aai
import os
from dotenv import load_dotenv

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

async def transcribe_audio(file_path: str) -> str:
  if not aai.settings.api_key:
    raise ValueError("ASSEMBLYAI_API_KEY is not set in environment variables.")

  try:
    transcriber = aai.Transcriber()
    
    print(f"Starting transcription for: {file_path}")
    transcript = await transcriber.transcribe_local_file(file_path)
    print(f"Transcription status: {transcript.status}")

    if transcript.status == aai.TranscriptStatus.error:
      raise Exception(f"AssemblyAI transcription failed: {transcript.error}")

    return transcript.text

  except Exception as e:
    print(f"Error during AssemblyAI transcription: {e}")
    raise
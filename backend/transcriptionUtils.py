import assemblyai as aai
import os
from dotenv import load_dotenv
import json

load_dotenv()
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

async def transcribe_audio(file_path: str) -> str:
    if not aai.settings.api_key:
        raise ValueError("ASSEMBLYAI_API_KEY is not set in environment variables.")

    try:
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            sentiment_analysis=True,
            entity_detection=True,
            summarization=False
        )

        transcriber = aai.Transcriber(config=config)

        print(f"Starting transcription for: {file_path}")
        transcript = transcriber.transcribe(file_path)
        print(f"Transcription status: {transcript.status}")

        if transcript.status == aai.TranscriptStatus.error:
            raise Exception(f"AssemblyAI transcription failed: {transcript.error}")

        # Save full transcript with speaker/sentiment/entity info
        detailed_path = file_path.replace(".mp3", "_detailed.json").replace(".wav", "_detailed.json")
        with open(detailed_path, "w", encoding="utf-8") as f:
            json.dump(transcript.json_response, f, indent=2)

        return transcript.text

    except Exception as e:
        print(f"Error during AssemblyAI transcription: {e}")
        raise

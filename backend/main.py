from fastapi import FastAPI, UploadFile, File
from geminiUtils import get_summary_and_action_items

app = FastAPI()

@app.post("/analyze/")
async def analyze_transcript(file: UploadFile = File(...)):
    content = await file.read()
    transcript = content.decode("utf-8")

    result = get_summary_and_action_items(transcript)
    return {"result": result}

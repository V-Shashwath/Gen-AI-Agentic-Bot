from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from geminiUtils import generate_summary
import traceback

app = FastAPI()

@app.post("/analyze/")
async def analyze(file: UploadFile = File(...)):
    try:
        # Read file content as text
        contents = await file.read()
        transcript = contents.decode("utf-8")

        # Pass to Gemini function
        response = generate_summary(transcript)

        return {"result": response}
    
    except Exception as e:
        print("⚠️ Error in /analyze endpoint:")
        traceback.print_exc()  # This will print full error stacktrace
        return JSONResponse(status_code=500, content="Internal Server Error")

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import aiofiles
import os
import uuid

from geminiUtils import get_summary_and_action_items
from transcriptionUtils import transcribe_audio

from slack_integration import send_slack_message, format_meeting_analysis_for_slack

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Meeting Analysis API",
    description="API for transcribing audio/video meetings and analyzing them to extract summaries, action items, and key decisions.",
    version="1.0.0"
)

class ActionItem(BaseModel):
    task: str
    assignee: Optional[str] = None
    deadline: Optional[str] = None
    status: str = "new"

class KeyDecision(BaseModel):
    description: str
    participants_involved: List[str] = []
    date_made: str # YYYY-MM-DD

class MeetingAnalysisResult(BaseModel):
    meeting_id: str
    timestamp: str
    summary: str
    action_items: List[ActionItem]
    key_decisions: List[KeyDecision]
    raw_transcript_preview: Optional[str] = None
    full_transcript_path: Optional[str] = None

client: AsyncIOMotorClient = None
database = None
meetings_collection = None

class SlackExportRequest(BaseModel):
    meeting_analysis: MeetingAnalysisResult = Field(..., description="The MeetingAnalysisResult object to be exported.")
    slack_channel_id: str = Field(..., description="The ID of the Slack channel or user to send the message to.")
    export_format: str = Field("summary_and_tasks", description="Specifies what content to export.", enum=["summary_only", "tasks_only", "summary_and_tasks"])

# --- Application Lifecycle Events ---

@app.on_event("startup")
async def startup_db_client():
    """
    Connects to the MongoDB database when the FastAPI application starts.
    """
    global client, database, meetings_collection
    mongo_db_url = os.getenv("MONGO_DB_URL")
    db_name = os.getenv("DB_NAME")

    if not mongo_db_url or not db_name:
        raise ValueError("MONGO_DB_URL and DB_NAME must be set in environment variables.")

    try:
        client = AsyncIOMotorClient(mongo_db_url)
        database = client[db_name]
        meetings_collection = database["meetings"] 
        print(f"Connected to MongoDB: {db_name}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_db_client():
    """
    Closes the MongoDB connection when the FastAPI application shuts down.
    """
    global client
    if client:
        client.close()
        print("Disconnected from MongoDB.")


# --- API Endpoints ---

@app.post("/analyze/", summary="Analyze a pre-existing transcript")
async def analyze_transcript(file: UploadFile = File(..., description="Text file containing the meeting transcript.")):
    """
    Accepts a plain text file containing a meeting transcript and processes it
    to generate a summary, action items, and key decisions.
    """
    content = await file.read()
    try:
        transcript = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Could not decode transcript file. Please ensure it's a valid UTF-8 text file."
        )

    analysis_result = get_summary_and_action_items(transcript)

    if "error" in analysis_result:
        raise HTTPException(status_code=500, detail=analysis_result["error"])

    meeting_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    return MeetingAnalysisResult(
        meeting_id=meeting_id,
        timestamp=timestamp,
        summary=analysis_result.get("summary", "No summary could be generated."),
        action_items=[ActionItem(**item) for item in analysis_result.get("action_items", [])],
        key_decisions=[KeyDecision(**item) for item in analysis_result.get("key_decisions", [])],
        raw_transcript_preview=transcript[:500] + "..." if len(transcript) > 500 else transcript
    )


@app.post("/transcribe-and-analyze/", response_model=MeetingAnalysisResult, summary="Transcribe Audio/Video and Analyze Meeting")
async def transcribe_and_analyze(
    file: UploadFile = File(..., description="Audio or video file of the meeting."),
    meeting_title: Optional[str] = None 
):
    """
    Accepts an audio or video file, transcribes it using AssemblyAI,
    then processes the transcript using Gemini to generate a summary,
    action items, and key decisions. The results are stored persistently.
    """
    # Validate file type 
    allowed_content_types = ["audio/", "video/"]
    if not any(file.content_type.startswith(t) for t in allowed_content_types):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. Please upload an audio or video file."
        )

    # Save the uploaded file temporarily
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    temp_file_path = f"/tmp/{unique_filename}"

    try:
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            while content := await file.read(1024 * 1024): # Read in chunks of 1MB
                await out_file.write(content)

        print(f"File saved temporarily at: {temp_file_path}")

        # Transcribe the audio/video file using AssemblyAI
        raw_transcript_text = await transcribe_audio(temp_file_path)
        if not raw_transcript_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcription failed or returned empty text. No speech detected or an error occurred."
            )

        # Process the raw transcript using Gemini for summary, action items, and key decisions
        analysis_result_data = get_summary_and_action_items(raw_transcript_text)

        if "error" in analysis_result_data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=analysis_result_data["error"])

        # Construct the MeetingAnalysisResult Pydantic model instance
        meeting_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        summary = analysis_result_data.get("summary", "No summary could be generated.")
        action_items_list = [ActionItem(**item) for item in analysis_result_data.get("action_items", [])]
        key_decisions_list = [KeyDecision(**item) for item in analysis_result_data.get("key_decisions", [])]

        meeting_analysis_object = MeetingAnalysisResult(
            meeting_id=meeting_id,
            timestamp=timestamp,
            summary=summary,
            action_items=action_items_list,
            key_decisions=key_decisions_list,
            raw_transcript_preview=raw_transcript_text[:500] + "..." if len(raw_transcript_text) > 500 else raw_transcript_text,
            full_transcript_path=temp_file_path 
        )

        # Store the analysis result in MongoDB
        await meetings_collection.insert_one(meeting_analysis_object.model_dump(by_alias=True))
        print(f"Meeting analysis result for ID {meeting_id} stored in MongoDB.")

        return meeting_analysis_object

    except HTTPException:
        raise
    except Exception as e:
        print(f"An unexpected error occurred during transcription and analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}"
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            print(f"Cleaned up temporary file: {temp_file_path}")
            

@app.get("/meetings/", response_model=List[MeetingAnalysisResult], summary="Get all meeting analysis results")
async def get_all_meetings():
    """
    Retrieves all stored meeting analysis results from the database.
    """
    meetings = []
    cursor = meetings_collection.find({})
    for doc in await cursor.to_list(length=100): # Limiting to 100 
        doc.pop("_id", None) # MongoDB's _id field is not part of the Pydantic model
        meetings.append(MeetingAnalysisResult(**doc))
    return meetings


@app.get("/meetings/{meeting_id}", response_model=MeetingAnalysisResult, summary="Get a specific meeting analysis result by ID")
async def get_meeting_by_id(meeting_id: str):
    """
    Retrieves a single meeting analysis result by its unique meeting ID.
    """
    meeting_doc = await meetings_collection.find_one({"meeting_id": meeting_id})
    if meeting_doc:
        meeting_doc.pop("_id", None) 
        return MeetingAnalysisResult(**meeting_doc)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found")
    
    
# --- Integration Endpoints ---

@app.post("/export/slack", summary="Export meeting analysis to Slack")
async def export_to_slack(request: SlackExportRequest):
    """
    Exports the meeting summary and action items to a specified Slack channel.
    """
    message_text = format_meeting_analysis_for_slack(
        request.meeting_analysis.model_dump(),
        request.export_format
    )

    slack_response = await send_slack_message(
        channel_id=request.slack_channel_id,
        message_text=message_text
    )

    if "error" in slack_response:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=slack_response["error"])

    return {"message": "Content successfully exported to Slack.", "slack_response": slack_response}
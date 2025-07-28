# Agentic-AI-Meeting-Bot

The *AI Meeting Agent* is a cutting-edge bot designed to transform chaotic meeting transcripts into clear, actionable outcomes. Leveraging advanced generative AI, it automatically summarizes discussions, extracts crucial action items with inferred deadlines and assignees, and formats everything for seamless export to common collaboration tools like Slack. This agent empowers teams to cut through noise, gain instant clarity, and ensure accountability in fast-paced, remote, or hybrid work environments.

*Tech Stack:*

* *Frontend:* React.js + Vite
* *Backend:* Python (FastAPI)
* *LLMs:* Gemini
* *APIs:* AssemblyAI (Transcription); Slack (Task/Export)
* *Future Enhancement:* Retrieval Augmented Generation (RAG) for enhanced context from existing documents (infrastructure for vector database and embeddings is present).

## 🎬 Demo

Check out a quick overview of the AI Meeting Agent in action!

*Video Demo:*

[![Watch the demo video](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

---

## 🚀 How to Run the App

### Prerequisites

* Python 3.9+
* A running MongoDB instance
* API keys for AssemblyAI and Google Gemini.

### Setup Steps

1.  *Clone the Repository:*

    bash
    git clone https://github.com/V-Shashwath/Gen-AI-Agentic-Bot.git
    cd Gen-AI-Agentic-Bot
    

2.  *Create a Virtual Environment:*

    bash
    python -m venv venv
    

3.  *Activate the Virtual Environment:*

    * *On macOS/Linux:*
        bash
        source venv/bin/activate
        
    * *On Windows:*
        bash
        .\venv\Scripts\activate
        

4.  *Install Dependencies:*
    Install all the necessary Python packages using the requirements.txt file.

    bash
    pip install -r requirements.txt
    

5.  *Navigate to the Backend Directory:*

    bash
    cd backend
    

6.  **Configure Environment Variables (.env file):**
    Create a file named .env directly inside your backend directory. Fill it with your API keys and MongoDB connection details:

    dotenv
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ASSEMBLYAI_API_KEY="YOUR_ASSEMBLYAI_API_KEY"
    MONGO_DB_URL="mongodb://localhost:27017/"
    DB_NAME="meeting_analysis_db"
    SLACK_BOT_TOKEN="xoxb-YOUR_SLACK_BOT_TOKEN"
    EMAIL_USERNAME="your_email@gmail.com" 
    EMAIL_PASSWORD="your_email_app_password" 
    

7.  *Run the FastAPI Application:*

    bash
    uvicorn app:app --reload
    

8.  *Access the API Documentation:*
    Once the server is running, open your web browser and navigate to:
    http://127.0.0.1:8000/docs

    This will open the interactive Swagger UI, where you can explore the available endpoints, view their specifications, and test them directly.

---

## 🖥 Usage

### 1. Analyze a Meeting

* Open the React frontend (http://localhost:3000).
* Choose your input type:
    * *Audio/Video File:* Upload an audio (e.g., .mp3, .wav) or video (e.g., .mp4) file. The backend will transcribe it using AssemblyAI and then analyze the transcript.
    * *Text Transcript:* Upload a plain .txt file containing a pre-existing meeting transcript.
    * *Record Audio:* Use your microphone to record audio directly from the browser.
* Click "Start Analysis".
* The application will display the generated summary, action items, key decisions, and other insights. This data is also stored in MongoDB, and its content is prepared for future RAG capabilities.

### 2. Export Meeting Analysis

After a meeting has been analyzed, you can export the results:

* *Export to Slack:*
    * Enter a Slack Channel ID (e.g., C1234567890 for a public channel, or a direct message ID).
    * Select the export format (Summary & Tasks, Summary Only, Tasks Only).
    * Click "Send to Slack".
* *Export via Email:*
    * Enter the recipient's email address.
    * Click "Send Email".

### 3. Future RAG Capabilities (Backend Infrastructure Ready)

While the RAG querying feature is not yet fully implemented in the frontend, the backend has the necessary infrastructure (vector database setup and embedding generation) to support it. This means you can:

* *Index Meeting Data:* Every time a meeting is analyzed, its content is automatically processed and indexed in a vector database (ChromaDB, by default).
* *Index External Documents (Backend Only):* You can manually index other relevant documents (like past notes, policy documents, etc.) via a backend endpoint to enrich the knowledge base for future RAG queries.
    * Use a tool like Postman or curl to send a POST request to http://localhost:8000/index-documents/.
    * Attach the files you want to index as multipart/form-data.

---

## ⚙ API Endpoints

The backend is built with FastAPI and exposes the following key endpoints:

* **POST /transcribe-and-analyze/**
    * *Description:* Transcribes an uploaded audio/video file using AssemblyAI, then analyzes the transcript with Gemini to extract summaries, action items, and key decisions. The analysis result is stored in MongoDB and indexed for future RAG capabilities.
    * *Request:* multipart/form-data with a file (audio/video).
    * *Response:* MeetingAnalysisResult object.

* **POST /analyze/**
    * *Description:* Analyzes an uploaded plain text transcript file with Gemini to extract summaries, action items, and key decisions. The analysis result is stored in MongoDB and indexed for future RAG capabilities.
    * *Request:* multipart/form-data with a file (text/plain).
    * *Response:* MeetingAnalysisResult object.

* **GET /meetings/**
    * *Description:* Retrieves a list of all previously analyzed and stored meeting results from the MongoDB database.
    * *Request:* None.
    * *Response:* A list of MeetingAnalysisResult objects.

* **GET /meetings/{meeting_id}**
    * *Description:* Retrieves a specific meeting analysis result by its unique meeting_id from the MongoDB database.
    * *Request:* Path parameter meeting_id (string).
    * *Response:* MeetingAnalysisResult object.

* **POST /export/slack**
    * *Description:* Formats a MeetingAnalysisResult and sends it as a message to a specified Slack channel.
    * *Request:* application/json with meeting_analysis (the result object), slack_channel_id (string), and export_format (string: summary_only, tasks_only, summary_and_tasks).
    * *Response:* Confirmation message.

* **POST /export/email**
    * *Description:* Formats a MeetingAnalysisResult and sends it as an email to a specified recipient.
    * *Request:* application/json with meeting_analysis (the result object) and a recipient query parameter (string).
    * *Response:* Confirmation message.

* **POST /index-documents/**
    * *Description:* Indexes external documents into the vector database, making them available for future RAG queries.
    * *Request:* multipart/form-data with files (list of document files like .txt, .pdf).
    * *Response:* Confirmation message.

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. (If you have a LICENSE file, otherwise you can remove this section or specify the license you intend to use).

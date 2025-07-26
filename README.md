# Gen-AI-Agentic-Bot

The **AI Meeting Agent** is a cutting-edge bot designed to transform chaotic meeting transcripts into clear, actionable outcomes. Leveraging advanced generative AI, it automatically summarizes discussions, extracts crucial action items with inferred deadlines and assignees, and formats everything for seamless export to common collaboration tools like Slack, Notion, or Trello. This agent empowers teams to cut through noise, gain instant clarity, and ensure accountability in fast-paced, remote, or hybrid work environments.

**Tech Stack:**

* **Frontend:** React.js or Next.js
* **Backend:** Node.js / Python (FastAPI)
* **LLMs:** OpenAI GPT-4 / Claude / Gemini / open-source models (LLama2, Mistral)
* **APIs:** AssemblyAI, Whisper, Deepgram (Transcription); Notion, Trello, Slack (Task/Export)
* **Optional:** RAG for enhanced context from existing documents.

## API Specifications and Data Models

## 1\. Data Models

These models represent the structured data used and returned by the API.

### ActionItem

Represents a single actionable task identified from the meeting.

```json
{
  "type": "object",
  "properties": {
    "task": {
      "type": "string",
      "description": "A clear description of the action item."
    },
    "assignee": {
      "type": "string",
      "nullable": true,
      "description": "The person or team assigned to the task. Can be null if unassigned or inferred as 'Team'."
    },
    "deadline": {
      "type": "string",
      "nullable": true,
      "description": "The inferred or explicit deadline for the task (e.g., '2025-07-30', 'next Friday', 'before next call')."
    },
    "status": {
      "type": "string",
      "enum": ["new", "in progress", "completed", "on hold"],
      "default": "new",
      "description": "The current status of the action item."
    }
  },
  "required": ["task"]
}
```

### KeyDecision

Represents a significant decision made during the meeting.

```json
{
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "A summary of the key decision."
    },
    "participants_involved": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of participants involved in making or affected by the decision."
    },
    "date_made": {
      "type": "string",
      "format": "date",
      "description": "The date the decision was made (YYYY-MM-DD)."
    }
  },
  "required": ["description", "date_made"]
}
```

### MeetingAnalysisResult

The comprehensive output after processing a meeting transcript.

```json
{
  "type": "object",
  "properties": {
    "meeting_id": {
      "type": "string",
      "description": "Unique identifier for this meeting analysis result. (e.g., UUID)"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "Timestamp when the analysis was generated."
    },
    "summary": {
      "type": "string",
      "description": "A human-readable summary of the entire meeting."
    },
    "action_items": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/ActionItem"
      },
      "description": "A list of extracted action items."
    },
    "key_decisions": {
      "type": "array",
      "items": {
        "$ref": "#/components/schemas/KeyDecision"
      },
      "description": "A list of identified key decisions."
    },
    "raw_transcript_preview": {
      "type": "string",
      "nullable": true,
      "description": "A short preview of the raw transcript for context."
    }
  },
  "required": ["meeting_id", "timestamp", "summary", "action_items", "key_decisions"]
}
```

-----

## 2\. API Endpoints

### A. Transcript Ingestion

**POST /transcripts**

Uploads a raw meeting transcript for processing.

  * **Description**: This endpoint accepts a meeting transcript, either as plain text or an audio/video file (future enhancement for integrated transcription).

  * **Request Body**:

      * `Content-Type: text/plain` (for raw text) or `multipart/form-data` (for file upload)

      * **For `text/plain`:**

        ```
        John: Let's finalize the Q3 roadmap by Friday.
        Sarah: I’ll lead the marketing update section.
        Alex: Please share the competitor insights before next week’s call.
        ```

      * **For `multipart/form-data`:**

          * `file`: (type: binary) The transcript file (e.g., `.txt`, `.mp3`, `.wav`).
          * `file_type`: (type: string, enum: `text`, `audio`, `video`) Specifies the type of content in the file.
          * `meeting_title`: (type: string, optional) An optional title for the meeting.

  * **Responses**:

      * **202 OK**: Accepted for processing.

        ```json
        {
          "message": "Transcript received and queued for analysis.",
          "transcript_id": "uuid-of-transcript-job"
        }
        ```

      * **400 Bad Request**: Invalid input.

-----

### B. Summarization and Task Extraction

**POST /analyze**

Analyzes a provided transcript to generate a summary, action items, and key decisions.

  * **Description**: This endpoint takes a raw transcript and uses the LLM to extract structured information.

  * **Request Body**:

      * `Content-Type: application/json`

        ```json
        {
          "transcript_text": "John: Let's finalize the Q3 roadmap by Friday. Sarah: I’ll lead the marketing update section. Alex: Please share the competitor insights before next week’s call.",
          "meeting_title": "Q3 Planning Meeting",
          "context_data": {
            "previous_meeting_notes": "...",
            "project_name": "...",
            "participants": ["John", "Sarah", "Alex"]
          }
        }
        ```

      * **Properties**:

          * `transcript_text`: (type: string, required) The full text of the meeting transcript.
          * `meeting_title`: (type: string, optional) A title for the meeting.
          * `context_data`: (type: object, optional) Additional context for the LLM (e.g., previous notes for RAG, known participants).

  * **Responses**:

      * **200 OK**: Analysis successful.

        ```json
        {
          "meeting_id": "meeting-analysis-12345",
          "timestamp": "2025-07-26T13:00:00Z",
          "summary": "The meeting focused on Q3 roadmap finalization. Sarah will lead the marketing update, and Alex needs to share competitor insights.",
          "action_items": [
            {
              "task": "Finalize Q3 roadmap",
              "assignee": "John",
              "deadline": "2025-07-26",
              "status": "new"
            },
            {
              "task": "Lead marketing update section",
              "assignee": "Sarah",
              "deadline": null,
              "status": "new"
            },
            {
              "task": "Share competitor insights",
              "assignee": "Alex",
              "deadline": "before next week's call",
              "status": "new"
            }
          ],
          "key_decisions": [
            {
              "description": "Q3 roadmap to be finalized by Friday.",
              "participants_involved": ["John"],
              "date_made": "2025-07-26"
            }
          ],
          "raw_transcript_preview": "John: Let's finalize the Q3 roadmap by Friday..."
        }
        ```

      * **400 Bad Request**: Missing `transcript_text`.

      * **500 Internal Server Error**: Error during LLM processing.

-----

### C. Integration Endpoints (Export)

These endpoints facilitate sending the `MeetingAnalysisResult` to various external tools. Each endpoint would require specific authentication and payload structures for the respective third-party API.

**POST /export/slack**

Exports the meeting summary and action items to Slack.

  * **Description**: Sends a formatted message to a specified Slack channel or user.

  * **Request Body**:

      * `Content-Type: application/json`

        ```json
        {
          "meeting_analysis": { /* MeetingAnalysisResult object */ },
          "slack_channel_id": "C12345ABC",
          "export_format": "summary_and_tasks"
        }
        ```

      * **Properties**:

          * `meeting_analysis`: (type: object, required) The `MeetingAnalysisResult` object to be exported.
          * `slack_channel_id`: (type: string, required) The ID of the Slack channel or user to send the message to.
          * `export_format`: (type: string, enum: [`summary_only`, `tasks_only`, `summary_and_tasks`], default: `summary_and_tasks`) Specifies what content to export.

  * **Responses**:

      * **200 OK**: Message sent to Slack.

      * **400 Bad Request**: Missing data or invalid Slack channel.

      * **500 Internal Server Error**: Error communicating with Slack API.

-----

**POST /export/notion**

Exports the meeting summary and action items to Notion.

  * **Description**: Creates a new page or updates an existing database entry in Notion with the meeting details.

  * **Request Body**:

      * `Content-Type: application/json`

        ```json
        {
          "meeting_analysis": { /* MeetingAnalysisResult object */ },
          "notion_database_id": "your-notion-database-id",
          "notion_page_title": "Q3 Planning Meeting Summary",
          "parent_page_id": "optional-parent-page-id"
        }
        ```

      * **Properties**:

          * `meeting_analysis`: (type: object, required) The `MeetingAnalysisResult` object.
          * `notion_database_id`: (type: string, required) The ID of the Notion database to add the entry to.
          * `notion_page_title`: (type: string, required) The title for the new Notion page.
          * `parent_page_id`: (type: string, optional) If the new page should be a sub-page of an existing one.

  * **Responses**:

      * **200 OK**: Content exported to Notion.

      * **400 Bad Request**: Missing data or invalid Notion ID.

      * **500 Internal Server Error**: Error communicating with Notion API.

-----

**POST /export/trello**

Exports action items as cards to a Trello board.

  * **Description**: Creates new cards on a specified Trello list for each action item.

  * **Request Body**:

      * `Content-Type: application/json`

        ```json
        {
          "meeting_analysis": { /* MeetingAnalysisResult object */ },
          "trello_board_id": "your-trello-board-id",
          "trello_list_id": "your-trello-list-id"
        }
        ```

      * **Properties**:

          * `meeting_analysis`: (type: object, required) The `MeetingAnalysisResult` object.
          * `trello_board_id`: (type: string, required) The ID of the Trello board.
          * `trello_list_id`: (type: string, required) The ID of the list within the board to add cards to.

  * **Responses**:

      * **200 OK**: Cards created in Trello.

      * **400 Bad Request**: Missing data or invalid Trello IDs.

      * **500 Internal Server Error**: Error communicating with Trello API.
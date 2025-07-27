import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
notion = Client(auth=os.getenv("NOTION_API_KEY"))

def create_meeting_page(database_id, meeting):
    properties = {
        "Title": {
            "title": [
                {
                    "text": {
                        "content": f"Meeting {meeting['meeting_id']}"
                    }
                }
            ]
        },
        "Summary": {
            "rich_text": [
                {
                    "text": {
                        "content": meeting["summary"]
                    }
                }
            ]
        },
        "Timestamp": {
            "date": {
                "start": meeting["timestamp"]
            }
        },
        "Action Items": {
            "multi_select": [
                {"name": item["task"]} for item in meeting.get("action_items", [])
            ]
        },
        "Assignees": {
            "multi_select": [
                {"name": item["assignee"]} for item in meeting.get("action_items", [])
            ]
        },
        "Deadline": {
            "date": {
                "start": meeting["action_items"][0]["deadline"]
            } if meeting.get("action_items") else None
        },
        "Key Decisions": {
            "rich_text": [
                {
                    "text": {
                        "content": "\n".join([
                            f"{d['description']} (Participants: {', '.join(d['participants_involved'])}, Date: {d['date_made']})"
                            for d in meeting.get("key_decisions", [])
                        ])
                    }
                }
            ]
        }
    }

    # Filter out empty/None fields
    properties = {k: v for k, v in properties.items() if v is not None}

    notion.pages.create(
        parent={"database_id": database_id},
        properties=properties
    )

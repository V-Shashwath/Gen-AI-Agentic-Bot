import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Any, List

from dotenv import load_dotenv
load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_BOT_TOKEN)

async def send_slack_message(channel_id: str, message_text: str) -> Dict[str, Any]:
    """
    Sends a message to a specified Slack channel.
    """
    if not SLACK_BOT_TOKEN:
        print("Error: SLACK_BOT_TOKEN is not set in environment variables.")
        return {"error": "Slack bot token is not configured."}

    try:
        response = await slack_client.chat_postMessage(
            channel=channel_id,
            text=message_text,
            mrkdwn=True
        )
        print(f"Slack message sent to {channel_id}: {response['ts']}")
        return {"success": True, "ts": response["ts"], "channel": response["channel"]}
    except SlackApiError as e:
        print(f"Error sending Slack message: {e.response['error']}")
        return {"error": f"Slack API error: {e.response['error']}"}
    except Exception as e:
        print(f"An unexpected error occurred while sending Slack message: {e}")
        return {"error": f"Failed to send Slack message: {e}"}

def format_meeting_analysis_for_slack(meeting_analysis: Dict[str, Any], export_format: str) -> str:
    """
    Formats the meeting analysis result into a Slack-friendly Markdown string.
    """
    formatted_message = []

    if export_format in ["summary_only", "summary_and_tasks"]:
        formatted_message.append(f"*Meeting Summary for {meeting_analysis.get('meeting_id', 'Unknown Meeting')}*")
        formatted_message.append(f"_{meeting_analysis.get('timestamp', 'N/A')}_")
        formatted_message.append(f"\n>{meeting_analysis.get('summary', 'No summary available.')}\n")

    if export_format in ["tasks_only", "summary_and_tasks"]:
        action_items = meeting_analysis.get('action_items', [])
        if action_items:
            formatted_message.append("*Action Items:*")
            for item in action_items:
                task = item.get('task', 'N/A')
                assignee = item.get('assignee', 'Unassigned')
                deadline = item.get('deadline', 'No Deadline')
                status = item.get('status', 'new')
                formatted_message.append(f"• *Task:* {task}\n  • *Assignee:* {assignee}\n  • *Deadline:* {deadline}\n  • *Status:* {status}")
        else:
            if export_format == "tasks_only":
                formatted_message.append("No action items identified.")

    key_decisions = meeting_analysis.get('key_decisions', [])
    if key_decisions and export_format == "summary_and_tasks": 
        formatted_message.append("\n*Key Decisions:*")
        for decision in key_decisions:
            desc = decision.get('description', 'N/A')
            parts = ", ".join(decision.get('participants_involved', [])) or "N/A"
            date = decision.get('date_made', 'N/A')
            formatted_message.append(f"• {desc} (Participants: {parts}, Date: {date})")

    return "\n".join(formatted_message)
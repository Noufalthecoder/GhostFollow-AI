import os
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

try:
    from .conversation_detector import log_activity
    from .database import Conversation, FollowUp
except ImportError:
    from conversation_detector import log_activity
    from database import Conversation, FollowUp

# Ensure the automation package can be imported when backend runs directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from automation.gmail_agent import send_gmail_followup  # noqa: E402


class FollowupDeliveryAgent:
    def __init__(self, db: Session):
        self.db = db

    def send(self, conversation: Conversation, message: str, dry_run: bool = False) -> dict:
        log_activity(
            self.db,
            step="Preparing Gmail automation",
            details=f"Preparing follow-up for {conversation.customer_name}",
            status="info",
            conversation_id=conversation.id,
        )

        result = {
            "status": "queued",
            "detail": "Message queued",
            "provider": "playwright-gmail-agent",
        }

        if dry_run or os.getenv("DEMO_MODE", "true").lower() == "true":
            result = {
                "status": "demo-sent",
                "detail": "Demo mode enabled; skipped live Gmail send.",
                "provider": "demo-agent",
            }
        else:
            result = send_gmail_followup(
                recipient_email=conversation.customer_email,
                subject_hint=conversation.subject or "",
                followup_message=message,
                thread_query=conversation.customer_name,
            )

        followup = FollowUp(
            conversation_id=conversation.id,
            generated_message=message,
            sent_time=datetime.utcnow(),
            status=result.get("status", "unknown"),
        )
        conversation.followup_sent = result.get("status") in {"sent", "demo-sent"}
        self.db.add(followup)
        self.db.add(conversation)
        self.db.commit()

        log_activity(
            self.db,
            step="Sending message via Gmail",
            details=f"Delivery result: {result.get('detail', 'No details')}",
            status="success" if conversation.followup_sent else "warning",
            conversation_id=conversation.id,
        )
        return result

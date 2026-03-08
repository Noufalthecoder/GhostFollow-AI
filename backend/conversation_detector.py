from datetime import datetime, timedelta

from sqlalchemy.orm import Session

try:
    from .database import ActivityLog, Conversation
except ImportError:
    from database import ActivityLog, Conversation


def log_activity(db: Session, step: str, details: str, status: str = "info", conversation_id: int | None = None) -> None:
    db.add(
        ActivityLog(
            conversation_id=conversation_id,
            step=step,
            status=status,
            details=details,
        )
    )
    db.commit()


def detect_ghosted(last_message_time: datetime, threshold_hours: int = 48) -> tuple[bool, str]:
    now = datetime.utcnow()
    silence_window = now - last_message_time
    is_ghosted = silence_window >= timedelta(hours=threshold_hours)
    reason = (
        f"No customer reply for {int(silence_window.total_seconds() // 3600)} hours."
        if is_ghosted
        else f"Latest message is within the last {threshold_hours} hours."
    )
    return is_ghosted, reason


def demo_conversations() -> list[dict]:
    now = datetime.utcnow()
    return [
        {
            "platform": "gmail",
            "customer_name": "Ava Thompson",
            "customer_email": "ava.thompson@example.com",
            "subject": "Pricing details for team plan",
            "last_message": "Ok let me think.",
            "conversation_context": (
                "Customer: Can you share pricing?\n"
                "Business: Our pricing starts at $49/month\n"
                "Customer: Ok let me think."
            ),
            "last_message_time": now - timedelta(days=3, hours=2),
        },
        {
            "platform": "gmail",
            "customer_name": "Noah Rivera",
            "customer_email": "noah.rivera@example.com",
            "subject": "Question about onboarding",
            "last_message": "Can your team help with migration?",
            "conversation_context": (
                "Customer: Can your team help with migration?\n"
                "Business: Yes, we offer white-glove onboarding."
            ),
            "last_message_time": now - timedelta(days=5),
        },
        {
            "platform": "gmail",
            "customer_name": "Mia Chen",
            "customer_email": "mia.chen@example.com",
            "subject": "Feature request",
            "last_message": "Thanks! I will circle back tomorrow.",
            "conversation_context": (
                "Customer: Do you support SSO?\n"
                "Business: Yes, on our growth and enterprise tiers.\n"
                "Customer: Thanks! I will circle back tomorrow."
            ),
            "last_message_time": now - timedelta(hours=14),
        },
    ]


def scan_and_mark_ghosted(db: Session, threshold_hours: int = 48) -> list[Conversation]:
    conversations = db.query(Conversation).all()

    for convo in conversations:
        is_ghosted, reason = detect_ghosted(convo.last_message_time, threshold_hours)
        convo.ghosted_status = is_ghosted
        convo.ai_reasoning = reason
        db.add(convo)

        log_activity(
            db,
            step="Checking conversation inactivity",
            details=f"Conversation #{convo.id}: {reason}",
            status="success" if is_ghosted else "info",
            conversation_id=convo.id,
        )

    db.commit()
    return conversations

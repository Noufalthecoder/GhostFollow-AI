import os
from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from .agent import FollowupDeliveryAgent
    from .conversation_detector import demo_conversations, log_activity, scan_and_mark_ghosted
    from .database import ActivityLog, Conversation, FollowUp, get_db, init_db
    from .followup_generator import generate_followup
except ImportError:
    from agent import FollowupDeliveryAgent
    from conversation_detector import demo_conversations, log_activity, scan_and_mark_ghosted
    from database import ActivityLog, Conversation, FollowUp, get_db, init_db
    from followup_generator import generate_followup

app = FastAPI(title="GhostFollow AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScanRequest(BaseModel):
    threshold_hours: int = 48


class GenerateRequest(BaseModel):
    conversation_id: int | None = None
    conversation_context: str | None = None


class SendRequest(BaseModel):
    conversation_id: int
    message: str | None = None
    dry_run: bool = False


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "time": datetime.utcnow().isoformat()}


@app.post("/scan-conversations")
def scan_conversations(payload: ScanRequest, db: Session = Depends(get_db)) -> dict:
    if os.getenv("DEMO_MODE", "true").lower() == "true" and db.query(Conversation).count() == 0:
        for convo_data in demo_conversations():
            db.add(Conversation(**convo_data))
        db.commit()

    log_activity(db, "Starting scan", "Analyzing conversation inactivity windows", "info")
    records = scan_and_mark_ghosted(db, payload.threshold_hours)
    ghosted_count = len([c for c in records if c.ghosted_status])

    return {
        "total": len(records),
        "ghosted": ghosted_count,
        "threshold_hours": payload.threshold_hours,
    }


@app.post("/generate-followup")
def create_followup(payload: GenerateRequest, db: Session = Depends(get_db)) -> dict:
    context = payload.conversation_context
    conversation = None

    if payload.conversation_id is not None:
        conversation = db.get(Conversation, payload.conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        context = conversation.conversation_context

    if not context:
        raise HTTPException(status_code=400, detail="Provide conversation_id or conversation_context")

    log_activity(
        db,
        "Generating follow-up",
        "Invoking LLM provider to generate contextual follow-up",
        "info",
        payload.conversation_id,
    )
    generated = generate_followup(context)

    if conversation:
        conversation.ai_reasoning = "\n".join(generated.get("reasoning", []))
        db.add(conversation)
        db.commit()

    return generated


@app.post("/send-followup")
def send_followup(payload: SendRequest, db: Session = Depends(get_db)) -> dict:
    conversation = db.get(Conversation, payload.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    message = payload.message
    if not message:
        generated = generate_followup(conversation.conversation_context)
        message = generated.get("message")

    if not message:
        raise HTTPException(status_code=400, detail="Unable to generate follow-up message")

    agent = FollowupDeliveryAgent(db)
    result = agent.send(conversation, message, payload.dry_run)

    return {
        "conversation_id": conversation.id,
        "message": message,
        "result": result,
    }


@app.get("/conversations")
def get_conversations(db: Session = Depends(get_db)) -> dict:
    conversations = db.query(Conversation).order_by(Conversation.last_message_time.desc()).all()

    data = [
        {
            "id": c.id,
            "platform": c.platform,
            "customer_name": c.customer_name,
            "customer_email": c.customer_email,
            "subject": c.subject,
            "last_message": c.last_message,
            "conversation_context": c.conversation_context,
            "last_message_time": c.last_message_time.isoformat(),
            "ghosted_status": c.ghosted_status,
            "followup_sent": c.followup_sent,
            "ai_reasoning": c.ai_reasoning,
        }
        for c in conversations
    ]
    return {"items": data, "count": len(data)}


@app.get("/followups")
def get_followups(db: Session = Depends(get_db)) -> dict:
    rows = db.query(FollowUp).order_by(FollowUp.id.desc()).all()
    items = [
        {
            "id": row.id,
            "conversation_id": row.conversation_id,
            "generated_message": row.generated_message,
            "sent_time": row.sent_time.isoformat() if row.sent_time else None,
            "status": row.status,
        }
        for row in rows
    ]
    return {"items": items, "count": len(items)}


@app.get("/activity")
def get_activity(db: Session = Depends(get_db)) -> dict:
    rows = db.query(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(200).all()
    items = [
        {
            "id": row.id,
            "conversation_id": row.conversation_id,
            "step": row.step,
            "status": row.status,
            "details": row.details,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
    return {"items": items, "count": len(items)}

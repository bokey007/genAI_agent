from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import shutil
from datetime import datetime, timedelta

from src.database import get_db
from src import models
from src.graph.builder import graph, checkpointer
from src.graph.state import GraphState
from src.rag import add_documents_from_file

app = FastAPI()

# Placeholder for admin user check
def is_admin(user_id: str):
    return True

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), user_id: str = "admin", db: Session = Depends(get_db)):
    if not is_admin(user_id):
        raise HTTPException(status_code=403, detail="Only admin users can upload files.")

    upload_dir = "uploads"
    file_path = f"{upload_dir}/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    add_documents_from_file(file_path, file.content_type)
    
    return {"filename": file.filename, "content_type": file.content_type}

class ChatRequest(BaseModel):
    session_id: str | None = None
    user_id: str | None = None
    message: str
    satisfied: bool | None = None
    comment: str | None = None

@app.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if request.session_id:
        session = db.query(models.Session).filter(models.Session.session_id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = models.Session(session_id=str(uuid.uuid4()), user_id=request.user_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    initial_state: GraphState = {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "messages": [("user", request.message)],
        "turn_count": session.turn_count,
        "unsatisfied_count": session.unsatisfied_count,
        "ticket_created": bool(session.tickets),
        "critique": "",
        "reflection_count": 0,
        "satisfied": request.satisfied,
        "comment": request.comment,
    }

    final_state = graph.invoke(initial_state, {"configurable": {"user_id": session.user_id, "thread_id": session.session_id, "checkpointer": checkpointer}})

    session.turn_count = final_state["turn_count"]
    session.unsatisfied_count = final_state["unsatisfied_count"]
    db.commit()

    return {"response": final_state["messages"][-1].content, "session_id": session.session_id}

@app.get("/history/{user_id}")
def get_history(user_id: str, db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)

    today_sessions = db.query(models.Session).filter(models.Session.user_id == user_id, models.Session.creation_time >= today).all()
    last_7_days_sessions = db.query(models.Session).filter(models.Session.user_id == user_id, models.Session.creation_time >= seven_days_ago, models.Session.creation_time < today).all()
    last_30_days_sessions = db.query(models.Session).filter(
        models.Session.user_id == user_id, 
        models.Session.creation_time >= thirty_days_ago, 
        models.Session.creation_time < seven_days_ago
    ).all()

    return {
        "today": [s.session_id for s in today_sessions],
        "last_7_days": [s.session_id for s in last_7_days_sessions],
        "last_30_days": [s.session_id for s in last_30_days_sessions],
    }
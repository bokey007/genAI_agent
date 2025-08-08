from pydantic import BaseModel

class Message(BaseModel):
    session_id: str
    message: str

class Ticket(BaseModel):
    session_id: str
    external_id: str = None
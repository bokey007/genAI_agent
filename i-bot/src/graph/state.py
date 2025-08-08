from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    session_id: str
    user_id: str
    messages: Annotated[list, add_messages]
    turn_count: int
    unsatisfied_count: int
    ticket_created: bool
    critique: str
    reflection_count: int
    satisfied: Optional[bool]
    comment: Optional[str]
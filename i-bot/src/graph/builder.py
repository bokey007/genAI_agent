from functools import partial

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from src.graph.state import GraphState
from src.graph.nodes import generate_node, reflection_node, feedback_node, ticket_node, should_continue
from src.config import settings

checkpointer = MemorySaver()

def should_reflect(state: GraphState):
    if state.get("reflection_count", 0) > 0 and state.get("reflection_count", 0) < 3 and state["critique"] == "bad":
        return "generate"
    return "feedback"

builder = StateGraph(GraphState)

builder.add_node("generate", lambda state, config: generate_node(state, config))
builder.add_node("reflect", reflection_node)
builder.add_node("feedback", feedback_node)
builder.add_node("ticket", ticket_node)

builder.set_entry_point("generate")

builder.add_edge("generate", "reflect")
builder.add_conditional_edges(
    "reflect",
    should_reflect,
    {
        "generate": "generate",
        "feedback": "feedback",
    }
)

builder.add_conditional_edges(
    "feedback",
    should_continue,
    {
        "ticket": "ticket",
        "generate": "generate",
        END: END
    }
)
builder.add_edge("ticket", END)

graph = builder.compile(checkpointer=checkpointer)
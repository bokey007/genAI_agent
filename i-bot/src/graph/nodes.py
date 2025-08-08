from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage

from src.graph.state import GraphState
from src.rag import similarity_search, manage_memory
from src.database import get_db
from src import models
from src.tools import create_ticket
from src.config import llm

def generate_node(state: GraphState, config: dict):
    print("Generating response...")
    user_message = state["messages"][-1].content
    context = similarity_search(user_message, state["user_id"], config)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the following context to answer the user's question:\n\n{context}\n\nIf you need to remember something, use the manage_memory tool."),
        ("user", "{question}"),
    ])

    chain = prompt | llm.bind_tools([manage_memory])

    response = chain.invoke({"context": context, "question": user_message}, config)

    return {"messages": [AIMessage(content=response.content)]}

def reflection_node(state: GraphState):
    print("Reflecting on response...")
    critique_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a critic. Your job is to evaluate the quality of a response to a user's question. The response should be helpful and accurate. Respond with 'good' or 'bad'."),
        ("user", "The user's question was: {question}\n The response was: {response}"),
    ])

    chain = critique_prompt | llm

    critique = chain.invoke({"question": state["messages"][-2].content, "response": state["messages"][-1].content})

    return {"critique": critique.content, "reflection_count": state.get("reflection_count", 0) + 1}

def feedback_node(state: GraphState):
    print("Processing feedback...")
    turn_count = state["turn_count"] + 1
    unsatisfied_count = state["unsatisfied_count"]

    if state.get("satisfied") is not None:
        if not state["satisfied"]:
            unsatisfied_count += 1
        
        db = next(get_db())
        session = db.query(models.Session).filter(models.Session.session_id == state["session_id"]).first()
        
        feedback = models.Feedback(
            session_id=session.id,
            turn_number=turn_count,
            satisfied_flag=state["satisfied"],
            comment=state.get("comment"),
            response_text=state["messages"][-1].content,
        )
        db.add(feedback)
        db.commit()

    return {"turn_count": turn_count, "unsatisfied_count": unsatisfied_count}

def ticket_node(state: GraphState):
    print("Creating ticket...")
    
    # Create ticket in ServiceNow
    title = f"Unresolved issue for user {state['user_id']}"
    description = f"The user was not satisfied after {state['turn_count']} turns. The last message was: {state['messages'][-1].content}"
    servicenow_ticket = create_ticket(title, description)
    
    # Create ticket in local DB
    db = next(get_db())
    session = db.query(models.Session).filter(models.Session.session_id == state["session_id"]).first()

    ticket = models.Ticket(
        session_id=session.id,
        external_id=servicenow_ticket["result"]["sys_id"] if servicenow_ticket else None
    )
    db.add(ticket)
    db.commit()

    return {"ticket_created": True, "messages": [AIMessage(content="I'm sorry I couldn't help you. A ticket has been created and a human agent will get back to you shortly.")]}

def should_continue(state: GraphState):
    if state.get("satisfied") is not None and not state["satisfied"]:
        if state["unsatisfied_count"] >= 2 and not state["ticket_created"]:
            return "ticket"
        else:
            return "generate"
    return END
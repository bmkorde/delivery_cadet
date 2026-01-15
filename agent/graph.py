from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState, AnyMessage, add_messages
from typing_extensions import Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from agent.tools import get_schema, run_sql
from agent.prompts import PROMPT


# ---- Agent State ----
class AgentState(MessagesState):
    question: str
    sql: str
    result: any

# ---- Initialize LLM ----
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# ---- Node 1: Generate SQL ----
def generate_sql(state: AgentState):
    schema = get_schema()
    prompt = f"""
You are a SQL expert.

Database schema:
{schema}

Convert the following question into SQL.
Return ONLY the SQL query.

Question:
{state["question"]}
"""

    sql = llm.invoke(prompt).content.strip()

    return {
        "sql": sql,
        "messages": state["messages"] + [AIMessage(content=f"SQL Generated:\n{sql}")]
    }


# ---- Node 2: Execute SQL ----
def execute_sql(state):
    query = state["sql"]
    raw = run_sql(query)

    # 🔴 HANDLE run_sql RETURN FORMAT
    if isinstance(raw, dict):
        if raw.get("success") is True:
            rows = raw.get("data", [])
        else:
            rows = []
            error = raw.get("error", "Unknown SQL error")
            return {
                "result": [],
                "messages": state["messages"] + [
                    AIMessage(content=f"SQL Error: {error}")
                ]
            }
    else:
        rows = raw if isinstance(raw, list) else []

    return {
        "result": rows,
        "messages": state["messages"]
    }

# ---- Node 3: Format Result ----


def format_result(state):
    rows = state.get("result", [])

    if not rows:
        answer = "No data found."
    else:
        headers = rows[0].keys()

        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        for row in rows:
            table += "| " + " | ".join(str(row[h]) for h in headers) + " |\n"

        answer = table

    return {
        "messages": state["messages"] + [AIMessage(content=answer)]
    }
# ---- Build LangGraph ----
builder = StateGraph(AgentState)

builder.add_node("generate_sql", generate_sql)
builder.add_node("execute_sql", execute_sql)
builder.add_node("format_result", format_result)

builder.set_entry_point("generate_sql")

builder.add_edge("generate_sql", "execute_sql")
builder.add_edge("execute_sql", "format_result")

builder.set_finish_point("format_result")

graph = builder.compile()


# ---- Public function for UI ----
def ask_question(question: str) -> str:
    result = graph.invoke(
        {
            "question": question,
            "messages": []
        }
    )

    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            return msg.content

    return "No response generated."

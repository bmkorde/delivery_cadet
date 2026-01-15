from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState, AnyMessage, add_messages
from typing_extensions import Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage
from agent.tools import get_schema, run_sql
from agent.prompts import PROMPT


# ------------------ Agent State ------------------
class AgentState(MessagesState):
    question: str
    sql: str
    result: list


# ------------------ LLM ------------------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)


# ------------------ SYSTEM PROMPT ------------------
PROMPT = """
You are a senior MySQL 8+ database expert.

STRICT RULES:
- Use ONLY MySQL 8+ syntax
- NEVER use QUALIFY or FILTER
- NEVER invent tables, columns, or aliases
- Use ONLY columns that exist in the schema
- Use MINIMUM joins
- Prefer direct relationships
- Revenue by country should use sales_franchises.country unless stated otherwise

OUTPUT RULES:
- Return ONLY raw SQL
- No explanations
- No markdown
- No ```sql fences
"""


# ------------------ Node 1: Generate SQL ------------------
def generate_sql(state: AgentState):
    schema = get_schema()

    prompt = f"""
{PROMPT}

DATABASE SCHEMA:
{schema}

QUESTION:
{state["question"]}
"""

    print("\n===== PROMPT SENT TO LLM =====\n")
    print(prompt)
    print("\n=============================\n")

    sql = llm.invoke(prompt).content.strip()

    return {
        "sql": sql,
        "messages": state["messages"] + [
            AIMessage(content=f"Generated SQL:\n{sql}")
        ]
    }


# ------------------ Node 2: Execute SQL ------------------
def execute_sql(state: AgentState):
    sql = state["sql"]
    raw = run_sql(sql)

    # run_sql ALWAYS returns a dict
    if not isinstance(raw, dict):
        return {
            "messages": state["messages"] + [
                AIMessage(content="❌ Internal error: Invalid SQL execution response.")
            ]
        }

    # SQL execution failed
    if raw.get("success") is not True:
        return {
            "messages": state["messages"] + [
                AIMessage(
                    content=(
                        "❌ SQL EXECUTION ERROR\n\n"
                        f"Error:\n{raw.get('error')}\n\n"
                        f"SQL:\n{raw.get('sql')}"
                    )
                )
            ]
        }

    # SQL execution succeeded
    return {
        "result": raw.get("data", []),
        "messages": state["messages"]
    }


# ------------------ Node 3: Format Result ------------------
def format_result(state: AgentState):
    # If execute_sql already returned an error message, stop here
    if "result" not in state:
        return state

    rows = state["result"]

    if not rows:
        answer = "Query executed successfully but returned *0 rows*."
    else:
        headers = list(rows[0].keys())

        table = "| " + " | ".join(headers) + " |\n"
        table += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        for row in rows:
            table += "| " + " | ".join(str(row[h]) for h in headers) + " |\n"

        answer = table

    return {
        "messages": state["messages"] + [AIMessage(content=answer)]
    }


# ------------------ Build LangGraph ------------------
builder = StateGraph(AgentState)

builder.add_node("generate_sql", generate_sql)
builder.add_node("execute_sql", execute_sql)
builder.add_node("format_result", format_result)

builder.set_entry_point("generate_sql")
builder.add_edge("generate_sql", "execute_sql")
builder.add_edge("execute_sql", "format_result")
builder.set_finish_point("format_result")

graph = builder.compile()


# ------------------ Public API ------------------
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

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
load_dotenv()
from agent.graph import ask_question
import markdown

app = FastAPI()

# 🔐 Session for chat memory
app.add_middleware(
    SessionMiddleware,
    secret_key="delivery-cadet-secret"
)

# Static + Templates
app.mount("/static", StaticFiles(directory="ui/static"), name="static")
templates = Jinja2Templates(directory="ui/templates")


@app.get("/", response_class=HTMLResponse)
def chat_page(request: Request):

    # Load chat history from session
    history = request.session.get("history", [])

    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "history": history
        }
    )


@app.post("/ask", response_class=HTMLResponse)
def ask(request: Request, question: str = Form(...)):

    # Load existing history
    history = request.session.get("history", [])

    # Ask agent
    response = ask_question(question)

    # Convert markdown → HTML (tables supported)
    html_response = markdown.markdown(
        response,
        extensions=["tables"]
    )

    # Append messages
    history.append({
        "role": "user",
        "content": question
    })

    history.append({
        "role": "agent",
        "content": html_response
    })

    # Save back to session
    request.session["history"] = history

    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "history": history
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

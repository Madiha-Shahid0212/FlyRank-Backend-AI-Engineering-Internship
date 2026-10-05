import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from schema import TriageInput, TriageOutput

load_dotenv()
app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_handler(request, exc):
    fields = [".".join(str(x) for x in e["loc"] if x != "body") for e in exc.errors()]
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid input", "fields": fields},
    )


@app.post("/triage")
def triage(body: TriageInput):
    if os.getenv("LLM_STUB") == "1":
        return TriageOutput(
            category="bug",
            urgency="normal",
            confidence=0.9,
            reason="stub response",
        )
    return JSONResponse(status_code=501, content={"error": "model not wired yet"})
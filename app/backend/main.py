from fastapi import FastAPI, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
#from opentelemetry.instrumentation.openai import OpenAIInstrumentor

import logger

import os
from dotenv import load_dotenv
load_dotenv()

APPLICATIONINSIGHTS_CONNECTION_STRING = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

from routers import yourwebcopilot

app = FastAPI()
if APPLICATIONINSIGHTS_CONNECTION_STRING:
    configure_azure_monitor(
        connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING,
    )
    tracer = trace.get_tracer(__name__)
    FastAPIInstrumentor.instrument_app(app)
    #OpenAIInstrumentor().instrument()

@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    logger.error(str(exc))
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

# /yourwebcopilot
app.include_router(yourwebcopilot.router)

import os

# staticディレクトリがあればマウントする
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
from fastapi import FastAPI, status, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routers import yourwebcopilot

app = FastAPI()
@app.exception_handler(RequestValidationError)
async def handler(request:Request, exc:RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

# /yourwebcopilot
app.include_router(yourwebcopilot.router)

import os

# staticディレクトリがあればマウントする
if os.path.exists("static"):
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
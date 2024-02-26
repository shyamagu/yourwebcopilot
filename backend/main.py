from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/api")
async def root():
    return {"message": "Hello World"}

@app.get("/hello")
def yourcopilot():
    with open("static/hello.html", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

# staticディレクトリにindex.htmlを置く
app.mount("/", StaticFiles(directory="static", html=True), name="static")
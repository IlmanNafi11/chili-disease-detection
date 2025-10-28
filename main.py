from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    data = {
        "status_bibit": "Sehat",
        "kelembapan": "60%",
        "tanggal": "27 Oktober 2025"
    }
    return templates.TemplateResponse("index.html", {"request": request, "data": data})

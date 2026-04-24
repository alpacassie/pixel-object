import base64
import traceback
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from openai import OpenAI

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI()
client = OpenAI()

STYLE_PROMPT = (
    "Transform this photo into pixel art in the style of a small decorative sprite: "
    "chunky readable pixels around 64-96 pixels across the subject, "
    "soft muted color palette, clean simplified silhouette of the main object "
    "centered in frame, subtle shading with limited color ramps, "
    "transparent background, no text, no borders. "
    "Preserve the recognizable form and pose of the subject."
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.post("/generate")
async def generate(photo: UploadFile = File(...)):
    contents = await photo.read()
    try:
        result = client.images.edit(
            model="gpt-image-2",
            image=(photo.filename or "upload.png", contents, photo.content_type or "image/png"),
            prompt=STYLE_PROMPT,
            size="1024x1024",
            quality="medium",
            background="transparent",
            output_format="png",
            n=1,
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=502, detail=f"{type(e).__name__}: {e}")

    png_bytes = base64.b64decode(result.data[0].b64_json)
    return Response(content=png_bytes, media_type="image/png")

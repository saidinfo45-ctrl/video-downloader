from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import yt_dlp
import tempfile
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoRequest(BaseModel):
    url: str


@app.get("/")
def home():
    return {"status": "VideoSave API is running"}


@app.post("/download")
def download_video(request: VideoRequest):
    url = request.url.strip()

    if not url:
        raise HTTPException(status_code=400, detail="الرابط فارغ")

    temp_dir = tempfile.mkdtemp()

    output_template = os.path.join(temp_dir, "video.%(ext)s")

    options = {
        "outtmpl": output_template,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        files = os.listdir(temp_dir)

        if not files:
            raise Exception("لم يتم العثور على الفيديو")

        file_path = os.path.join(temp_dir, files[0])

        return FileResponse(
            file_path,
            media_type="video/mp4",
            filename="VideoSave.mp4",
            background=None,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"تعذر تحميل الفيديو: {str(e)}"
        )

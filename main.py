from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

app = FastAPI()

@app.post("/convert")
async def convert(link: str = Form(...)):
    uid = str(uuid.uuid4())
    input_file = f"{uid}.m4a"
    thumbnail_file = f"{uid}.jpg"
    output_file = f"{uid}.mp3"

    # Download audio and thumbnail
    subprocess.run(["yt-dlp", "-f", "bestaudio", "--write-thumbnail", "--skip-download",
                    "--output", uid, link], check=True)
    subprocess.run(["yt-dlp", "-f", "bestaudio", "-o", input_file, link], check=True)

    # Find the thumbnail (jpg or webp)
    thumb = thumbnail_file
    if os.path.exists(f"{uid}.webp"):
        thumb = f"{uid}.webp"
    elif os.path.exists(f"{uid}.jpg"):
        thumb = f"{uid}.jpg"

    # Convert to MP3 with thumbnail
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file,
        "-i", thumb,
        "-map", "0:a", "-map", "1:v",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-id3v2_version", "3",
        "-metadata:s:v", "title=Album cover",
        "-metadata:s:v", "comment=Cover (front)",
        output_file
    ], check=True)

    # Clean up input and thumbnail
    os.remove(input_file)
    os.remove(thumb)

    return FileResponse(output_file, filename=output_file, media_type="audio/mpeg")
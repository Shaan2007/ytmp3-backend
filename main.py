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
    output_file = f"{uid}.mp3"
    thumbnail_file_jpg = f"{uid}.jpg"
    thumbnail_file_webp = f"{uid}.webp"

    # Download thumbnail only
    subprocess.run([
        "yt-dlp",
        "--write-thumbnail",
        "--skip-download",
        "--no-check-certificate",
        "--add-header", "User-Agent: Mozilla/5.0",
        "--add-header", "Accept-Language: en-US,en;q=0.9",
        "--add-header", "Accept: text/html",
        "-o", uid,
        link
    ], check=True)

    # Download audio only
    subprocess.run([
        "yt-dlp",
        "-f", "bestaudio",
        "--no-check-certificate",
        "--add-header", "User-Agent: Mozilla/5.0",
        "--add-header", "Accept-Language: en-US,en;q=0.9",
        "--add-header", "Accept: text/html",
        "-o", input_file,
        link
    ], check=True)

    # Choose existing thumbnail (jpg or webp)
    thumbnail = None
    if os.path.exists(thumbnail_file_jpg):
        thumbnail = thumbnail_file_jpg
    elif os.path.exists(thumbnail_file_webp):
        thumbnail = thumbnail_file_webp

    # Convert to mp3 with thumbnail
    if thumbnail:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file, "-i", thumbnail,
            "-map", "0:a", "-map", "1:v",
            "-c:a", "libmp3lame", "-b:a", "192k",
            "-id3v2_version", "3",
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
            output_file
        ], check=True)
    else:
        # Fallback if no thumbnail
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file,
            "-c:a", "libmp3lame", "-b:a", "192k",
            output_file
        ], check=True)

    # Clean up
    os.remove(input_file)
    if thumbnail:
        os.remove(thumbnail)

    return FileResponse(output_file, filename=output_file, media_type="audio/mpeg")

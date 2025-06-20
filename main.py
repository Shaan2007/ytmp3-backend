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

    # Step 1: Download thumbnail
    subprocess.run([
        "yt-dlp",
        "--write-thumbnail",
        "--skip-download",
        "--add-header", "User-Agent: Mozilla/5.0",
        "-o", uid,
        link
    ], check=True)

    # Step 2: Download audio
    subprocess.run([
        "yt-dlp",
        "-f", "bestaudio",
        "--add-header", "User-Agent: Mozilla/5.0",
        "-o", input_file,
        link
    ], check=True)

    # Step 3: Use JPG or WEBP thumbnail
    thumbnail = thumbnail_file_jpg if os.path.exists(thumbnail_file_jpg) else thumbnail_file_webp

    # Step 4: Convert to MP3 with thumbnail
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file, "-i", thumbnail,
        "-map", "0:a", "-map", "1:v",
        "-c:a", "libmp3lame", "-b:a", "192k",
        "-id3v2_version", "3",
        "-metadata:s:v", "title=Album cover",
        "-metadata:s:v", "comment=Cover (front)",
        output_file
    ], check=True)

    # Step 5: Clean up
    os.remove(input_file)
    os.remove(thumbnail)

    # Step 6: Return MP3 file
    return FileResponse(output_file, filename=output_file, media_type="audio/mpeg")

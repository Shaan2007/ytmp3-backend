FROM python:3.11

RUN apt update && apt install -y ffmpeg

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

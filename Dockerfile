FROM python:3.11

# Install ffmpeg and other needed system packages
RUN apt update && apt install -y ffmpeg

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install -r requirements.txt

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

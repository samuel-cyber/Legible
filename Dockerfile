FROM python:3.12-slim

WORKDIR /app

# fontconfig lets matplotlib (Channel C's render-back) build its font cache
# without warning on first run; pymupdf ships its own MuPDF binary and needs
# nothing extra.
RUN apt-get update && apt-get install -y --no-install-recommends fontconfig \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render sets $PORT at runtime; Hugging Face Spaces (Docker SDK) defaults to
# 7860. Either way the container must listen on 0.0.0.0:$PORT.
ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

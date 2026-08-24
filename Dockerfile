FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system bot && adduser --system --ingroup bot bot
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=bot:bot bot.py .
RUN mkdir /data /models && chown bot:bot /data /models
USER bot
CMD ["python", "bot.py"]

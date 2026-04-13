FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir \
    "python-telegram-bot==21.6" \
    "requests==2.31.0"
COPY bot.py .
CMD ["python", "bot.py"]

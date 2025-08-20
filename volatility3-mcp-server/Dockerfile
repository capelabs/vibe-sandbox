FROM sk4la/volatility3:2.11.0

WORKDIR /app
COPY . /app

RUN pip install --break-system-packages --no-cache-dir -r /app/requirements.txt

EXPOSE 8000
ENTRYPOINT ["python", "-m", "uvicorn", "main:app"]

FROM sk4la/volatility3:2.11.0

COPY requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY . /app

EXPOSE 8000
ENTRYPOINT ["python", "main.py"]

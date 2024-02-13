FROM python:3.10-slim-buster
RUN apt update && apt install build-essential libffi-dev  -y
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
ENTRYPOINT ["python3", "cli.py"]

FROM python:3.10-slim-buster
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
ENTRYPOINT ['python3', 'filepass.py']
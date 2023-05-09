FROM python:3.10

WORKDIR /src

COPY requirements.txt .
 
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "main:app"]
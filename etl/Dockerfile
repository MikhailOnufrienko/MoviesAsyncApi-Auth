FROM python:3.10

WORKDIR /etl

COPY requirements.txt .
 
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .

CMD ["python", "services/main.py"]
FROM python:latest

COPY requirements.txt ./
RUN pip install --no-deps -r requirements.txt
RUN pip install psycopg2 gunicorn

COPY api api 
COPY migrations migrations 
COPY config.py run.py boot.sh ./

EXPOSE 5000

CMD ./boot.sh
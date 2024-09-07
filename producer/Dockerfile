FROM python:3-bookworm

WORKDIR /app

COPY . .

RUN ["pip","install","-r","requirements.txt"]

CMD ["python","RedditProducer.py"]
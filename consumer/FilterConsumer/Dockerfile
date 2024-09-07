FROM docker.io/bitnami/spark:3.5

WORKDIR /app

COPY . .

RUN ["pip","install","-r","requirements.txt"]

CMD ["spark-submit","--master","spark://spark-master:7077","--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", "main.py"]
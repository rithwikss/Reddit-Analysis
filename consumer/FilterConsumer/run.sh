docker cp -L main.py dbt-project-spark-master-1:/opt/bitnami/spark/main.py
docker cp -L .env dbt-project-spark-master-1:/opt/bitnami/spark/.env
docker-compose exec spark-master spark-submit --master spark://172.14.0.8:7077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0 main.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, ArrayType
from pyspark.sql.functions import from_json
import os
import dotenv

dotenv.load_dotenv()


KAFKA_BROKER = os.getenv("KAFKA_BROKER")
SPARK_BROKER = os.getenv("SPARK_BROKER").strip()
KAFKA_PROCESSED_TOPIC = os.getenv("KAFKA_PROCESSED_TOPIC")
CHECKPOINT_LOCATION = os.getenv("CHECKPOINT_LOCATION")
CONSUMER_GROUP=os.getenv("KAFKA_CONSUMER_GROUP")
KEYWORDS=os.getenv("KEYWORDS").split(",")
KAFKA_TOPIC = os.getenv("KAFKA_TOPICS")

print(KAFKA_TOPIC)
print(KAFKA_BROKER)


# Define the schema for comments
comment_schema = StructType([
    StructField("body", StringType(), nullable=True),
    StructField("score", IntegerType(), nullable=True),
    StructField("created_utc", TimestampType(), nullable=True),
    StructField("id", StringType(), nullable=True),
    StructField("permalink", StringType(), nullable=True),
    StructField("ups", IntegerType(), nullable=True),
    StructField("downs", IntegerType(), nullable=True),
    StructField("author", StringType(), nullable=True)
])

# Define the schema for posts
post_schema = StructType([
    StructField("title", StringType(), nullable=True),
    StructField("selftext", StringType(), nullable=True),
    StructField("url", StringType(), nullable=True),
    StructField("score", IntegerType(), nullable=True),
    StructField("authorName", StringType(), nullable=True),
    StructField("id", StringType(), nullable=True),
    StructField("created_utc", TimestampType(), nullable=True),
    StructField("permalink", StringType(), nullable=True),
    StructField("ups", IntegerType(), nullable=True),
    StructField("downs", IntegerType(), nullable=True),
    StructField("num_comments", IntegerType(), nullable=True),
])

# Create a SparkSession
spark = SparkSession.builder.master(SPARK_BROKER).appName("RedditDataAnalysis").getOrCreate()

# Read streaming data from Kafka
streaming_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "earliest") \
    .option("groupId", CONSUMER_GROUP) \
    .load()

# Convert value column to JSON and expand it using the defined schema
json_df = streaming_df.selectExpr("cast(value as string) as value")
json_expanded_df = json_df.withColumn("value", from_json(json_df["value"], post_schema)).select("value.*") 
df = json_expanded_df.where(
    json_expanded_df['title'].rlike("|".join(["(" + pat + ")" for pat in KEYWORDS]))
)

df.selectExpr("to_json(struct(*)) as value").writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKER) \
        .option("topic", KAFKA_PROCESSED_TOPIC) \
        .option("checkpointLocation", CHECKPOINT_LOCATION) \
        .start() \
        .awaitTermination()
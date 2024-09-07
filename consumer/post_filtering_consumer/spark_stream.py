from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructField, StructType, StringType, IntegerType
from consumer import analyzer_function
from sys import argv
import json

spark = SparkSession.builder.appName("DataConsumer").config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2").getOrCreate()

topic = "Filtered_Results"



# Define the schema for the DataFrame
schema = StructType([
    StructField("local_id", IntegerType(), True),
    StructField("reddit_id", StringType(), True),
	StructField("title", StringType(), True),
	StructField("selftext", StringType(), True),
	StructField("subreddit", StringType(), True),
	StructField("created", StringType(), True),
	StructField("num_comments", IntegerType(), True),
	StructField("ups", IntegerType(), True),
	StructField("downs", IntegerType(), True)	
])

def give_me_title(post):
	try:
		x = json.loads(post)['title']
		return str(x)
	except:
		return " "
	
udf_json = udf(lambda x: give_me_title(x), StringType())
udf_analyzer_function = udf(analyzer_function, StringType())


# Create streaming DataFrame
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", topic) \
    .option("startingOffsets", "earliest") \
    .load()

# Cast the value column to a string
df = df.withColumn("value", df["value"].cast(StringType()))

# Decode the value column
df = df.withColumn("ACTUAL_VALUE", from_json(df.value, schema))

# Extract the fields from the json object
df = df.withColumn("reddit_id", df.ACTUAL_VALUE.reddit_id)
df = df.withColumn("title", df.ACTUAL_VALUE.title)
df = df.withColumn("selftext", df.ACTUAL_VALUE.selftext)
df = df.withColumn("subreddit", df.ACTUAL_VALUE.subreddit)
df = df.withColumn("created", df.ACTUAL_VALUE.created)
df = df.withColumn("num_comments", df.ACTUAL_VALUE.num_comments)
df = df.withColumn("ups", df.ACTUAL_VALUE.ups)
df = df.withColumn("downs", df.ACTUAL_VALUE.downs)

# Sentiment analysis
df = df.withColumn("sentiment", udf_analyzer_function(df.title))



# Define the window and group by clauses
windowedCounts = df \
    .groupBy(
        window(df.timestamp, "1 minute", "1 minute"),
    ) \
    .count()

# display the sentiment for each title, by displaying only timestamp, title, sentiment, ups, downs and num_comments
sentiment_query = df \
    .select("timestamp", substring("title", 1, 50).alias("title"), "sentiment", "ups", "downs", "num_comments") \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", "false") \
    .start()

# diplay the count of each sentiment after grouping by sentiment and also display the count of ups, downs and num_comments
sentiment_query = df \
    .groupBy("sentiment") \
    .agg(count("sentiment"), sum("ups"), sum("downs"), sum("num_comments")) \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

# Write the output to the console
console_query = windowedCounts \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()


# Wait for the query to terminate
console_query.awaitTermination()
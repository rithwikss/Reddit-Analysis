import sqlite3
from json import loads
from time import time, sleep
from consumer import consumer
from sys import argv
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import pandas as pd
from pyspark.sql.functions import col

DB_CON = None


def init_db():
    global DB_CON
    DB_CON = sqlite3.connect("app.db")
    print("[LOG] Connected to database")


def cleanup():
    global DB_CON
    print("[LOG] Cleaning up...")
    DB_CON.close()
    print("[LOG] Goodbye!")


def get_all_data():
    global DB_CON
    cur = DB_CON.cursor()
    q = """ SELECT * FROM reddit_post; """
    cur.execute(q)
    try:
        records = cur.fetchall()
    except Exception as e:
        print("[ERROR] Error fetching batch data from db:", e)
        records = None
    cur.close()
    return records


def process_batch(delay):
    while True:
        start_time = time()  # Record start time

        # Create a SparkSession
        spark = SparkSession.builder.appName(
            "RedditSentimentAnalysis").getOrCreate()

        # Get the data from the SQLite database
        records = get_all_data()
        if not records:
            print("[LOG] No more records to process. Exiting.")
            break

        for i in records:
            print("[LOG] Sentiment =>", i[0], ":",
                  consumer.analyzer_function(i[2]))

        end_time = time()  # Record end time
        elapsed_time = end_time - start_time
        print(
            f"[LOG] Time elapsed for this batch to compute sentiment: {elapsed_time:.2f} seconds")

        # Define the schema for the DataFrame
        schema = StructType([
            StructField("local_id", IntegerType(), True),
            StructField("reddit_id", StringType(), True),
            StructField("title", StringType(), nullable=True),
            StructField("selftext", StringType(), nullable=True),
            StructField("subreddit", StringType(), True),
            StructField("num_comments", IntegerType(), True),
            StructField("ups", IntegerType(), True),
            StructField("downs", IntegerType(), True)
        ])

        start_time = time()  # Record start time
        records = get_all_data()

        # Create a DataFrame from the Python data
        df = spark.createDataFrame(records, schema)

        # Perform sentiment analysis using a UDF
        analyzer_function_udf = spark.udf.register(
            "analyzer_function", consumer.analyzer_function)
        sentiment_df = df.select("ups", "downs", "num_comments", analyzer_function_udf(
            col("title")).alias("sentiment"))

        # Print table after grouping based on sentiment
        result = sentiment_df.groupBy("sentiment").agg(
            {"ups": "sum", "downs": "sum", "num_comments": "sum", "sentiment": "count"}
        )
        result = result.withColumnRenamed("sum(ups)", "total_ups")
        result = result.withColumnRenamed("sum(downs)", "total_downs")
        result = result.withColumnRenamed(
            "sum(num_comments)", "total_num_comments")
        result = result.withColumnRenamed(
            "count(sentiment)", "sentiment_count")
        

        # Print the results
        result.show()

        # Stop the SparkSession
        spark.stop()

        end_time = time()  # Record end time
        elapsed_time = end_time - start_time
        print(
            f"[LOG] Time elapsed for this batch to compute aggregate queries: {elapsed_time:.2f} seconds")

        # Truncate the table
        truncate_table()

        # Delay before processing the next batch
        sleep(delay)


def truncate_table():
    global DB_CON
    cur = DB_CON.cursor()
    q = """ DELETE FROM reddit_post; """
    cur.execute(q)
    DB_CON.commit()
    print("[LOG] Table truncated.\n")


def main():
    init_db()
    try:
        delay = int(argv[1])
        process_batch(delay)
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
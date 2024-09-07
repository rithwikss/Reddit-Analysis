# Reddit-Analysis

This project is designed to perform real-time analysis on Reddit data using Apache Kafka, Apache Spark Streaming, and sentiment analysis. The pipeline involves several stages, including data ingestion, filtering, sentiment analysis, and batch processing.

# Overview

This project fetches data from Reddit, processes it through a Kafka producer, and sends it to a Kafka consumer. The data is then filtered using Spark Streaming, and two separate consumers handle further processing: one for sentiment analysis and another for storing the data in a database. Additionally, batch processing is performed at regular intervals to analyze the entire dataset.

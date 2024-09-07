import os
from dotenv import load_dotenv
import json


def start_producers(options:dict):
    load_dotenv()

    for subreddit in options["subreddit"]:
        print("running",subreddit)
        os.system("docker run -d --network=scrape-net -e SUBREDDIT={} -e USER_CONFIG='{}' -e KAFKA_SERVER={} -e CLIENT_ID={} -e USER_AGENT={} -e CLIENT_SECRET={} reddit-producer ".format(subreddit,json.dumps(options),os.getenv('KAFKA_CLUSTER_BOOTSTRAP_SERVERS'),os.getenv('REDDIT_CLIENT_ID'),os.getenv('REDDIT_USER_AGENT'),os.getenv('REDDIT_CLIENT_SECRET')))
    os.environ["KEYWORDS"]=",".join(options["sentimentKeyWord"])
    os.environ["KAFKA_TOPICS"]=",".join(options["subreddit"])
    print(os.environ.get("KAFKA_TOPICS"))
    os.system("docker-compose -f ../consumer/docker-compose.yaml up -d --build")

if __name__=="__main__":
    load_dotenv()
    start_producers()
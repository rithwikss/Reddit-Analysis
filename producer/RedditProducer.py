# from confluent_kafka import Producer
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import praw
import os
from dotenv import load_dotenv
import time
import json
import tqdm

load_dotenv()



KAFAKA_SERVER = os.getenv('KAFKA_CLUSTER_BOOTSTRAP_SERVERS')
CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
USER_AGENT = os.getenv('REDDIT_USER_AGENT')
USER_CONFIG=json.loads(os.getenv('USER_CONFIG'))
SUBREDDIT=os.getenv("SUBREDDIT")
POST_DATA = []


def get_comments(comments):
    _comments = []
    for comment in comments:
        if isinstance(comment, praw.models.MoreComments):
            continue  # Skip MoreComments objects
        comment_data = {
            "body": comment.body if comment.body else "Deleted",
            "score": comment.score,
            "created_utc": comment.created_utc,
            "id": comment.id,
            "permalink": comment.permalink,
            "ups": comment.ups,
            "downs": comment.downs,
            "author": comment.author.name if comment.author else "Deleted",
        }
        _comments.append(comment_data)
    return _comments

def get_data(SUBREDDIT,SORT_BY="hot", LIMIT=10):
    global POST_DATA
    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)

    POSTS = None

    if SORT_BY == "hot":
        POSTS = reddit.subreddit(SUBREDDIT).hot(limit=None if LIMIT <= 0 else LIMIT)
    elif SORT_BY == "top":
        POSTS = reddit.subreddit(SUBREDDIT).top(limit=None if LIMIT <= 0 else LIMIT)
    elif SORT_BY == "new":
        POSTS = reddit.subreddit(SUBREDDIT).new(limit=None if LIMIT <= 0 else LIMIT)
    elif SORT_BY == "controversial":
        POSTS = reddit.subreddit(SUBREDDIT).controversial(limit=None if LIMIT <= 0 else LIMIT)
    elif SORT_BY == "rising":
        POSTS = reddit.subreddit(SUBREDDIT).rising(limit=None if LIMIT <= 0 else LIMIT)

    print(POSTS)
    for post in tqdm.tqdm(POSTS, desc="Getting Data"):
        post_data = {
            "title": post.title,
            "selftext": post.selftext,
            "url": post.url,
            "score": post.score,
            "authorName": post.author.name if post.author else "Deleted",
            "id": post.id,
            "created_utc": post.created_utc,
            "permalink": post.permalink,
            "ups": post.ups,
            "downs": post.downs,
            "num_comments": post.num_comments,
        }
        POST_DATA.append(post_data)
        print("UTC ",)
    
def start_streaming(INTERVAL=10):
    global POST_DATA
    print(INTERVAL)
    producer = KafkaProducer(bootstrap_servers=KAFAKA_SERVER.split(","),value_serializer=lambda v: json.dumps(v).encode('utf-8'))
    print("Starting Streaming")
    for i in range(len(POST_DATA)):
        
        print("Posting data to Kafka")
        producer.send(SUBREDDIT,POST_DATA[i])
        print("Data Posted")
        time.sleep(INTERVAL)



if __name__ == "__main__":
    admin_client = KafkaAdminClient(
    bootstrap_servers=KAFAKA_SERVER
)
    try:
        admin_client.create_topics(new_topics=[NewTopic(name=SUBREDDIT, num_partitions=3, replication_factor=3)], validate_only=False)
    except:
        pass
    if(USER_CONFIG['subreddit'] == ""):
        print("Please provide a subreddit")
        exit(1)
    if USER_CONFIG['timeFrame'] == "":
        print("Please provide a time frame")
        exit(1)

    print(SUBREDDIT)
    print("Started producer")
    get_data(SUBREDDIT,USER_CONFIG['sort'],USER_CONFIG['limit'])
    print("Done Getting Data")

    start_streaming(int(USER_CONFIG['timeFrame']))
    pass


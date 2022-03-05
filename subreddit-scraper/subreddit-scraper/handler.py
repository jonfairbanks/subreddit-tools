import praw
import random
import redis
import requests
import string

SUBMISSION_LIMIT = 1000
PROBABILITY = .05 # 5%
YES = "y"
NO = "n"
REDDIT_URL = "https://reddit.com/r/"

def generate_user_agent(size = 16, chars = string.ascii_uppercase + string.digits):
    return 'Subreddit-Mapper-'.join(random.choice(chars) for _ in range(size))

def get_secret(name):
    filename = str("/var/openfaas/secrets/" + name)
    file = open(filename, 'r')
    data = file.read()
    file.close()
    return data

def reddit_login():
  try:
    reddit = praw.Reddit(
      user_agent=generate_user_agent(),
      client_id=get_secret("reddit_client_id"),
      client_secret=get_secret("reddit_client_secret"),
      username=get_secret("reddit_username"),
      password=get_secret("reddit_password")
    )
    return reddit
  except Exception as e:
    print("Reddit Login Failed:", e)
    exit(1)

def redis_connect():
  try:
    r = redis.Redis(
      host=get_secret("redis_host"),
      port=int(get_secret("redis_port")),
      password=get_secret("redis_password")
    )
    return r
  except Exception as e:
    print("Connection to Redis Failed:", e)
    exit(1)

def write_to_redis(r, data):
  r.setnx(str(data), "")
  return

def get_recent_subreddits(reddit):
  data = [] 
  for submission in reddit.subreddit('all').new(limit=SUBMISSION_LIMIT, params={'include_over_18': 'on'}):
    data.append(submission.subreddit)
  return data

def maybe(p):
    return YES if random.random() < p else NO

def handle(req):
  """handle a request to the function
  Args:
      req (str): request body
  """
  print('--- Subreddit Scraper ---\n')

  reddit = reddit_login()
  redisclient = redis_connect()

  recent_subreddits = get_recent_subreddits(reddit)
  print("Scraped", len(recent_subreddits), "subreddits\n")
  for sub in recent_subreddits:
    print("r/", sub, sep="")
    write_to_redis(redisclient, sub)
    # Randomly try to map found subreddits
    if(maybe(PROBABILITY) == "y"):
      # Map the subreddit
      endpoint = "https://fn.fairbanks.dev/async-function/subreddit-mapper/" + str(sub)
      requests.get(endpoint)
  
  print("\n✅ Subreddit data stored in Redis")
  del reddit
  del redisclient
  exit(0)
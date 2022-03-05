import praw
import random
import string
import sys

RED = str('\033[1;31;40m')
GREEN = str('\033[1;32;40m')
YELLOW = str('\033[1;33;40m')
BLUE = str('\033[1;34;40m')
GREY = str('\033[1;30;40m')
RESET = str('\033[1;37;40m')

def generate_user_agent(size = 16, chars = string.ascii_uppercase + string.digits):
    return 'Subreddit-Mapper-'.join(random.choice(chars) for _ in range(size))

def get_secret(name):
    filename = str("/var/openfaas/secrets/" + name)
    file = open(filename, 'r')
    data = file.read()
    file.close()
    return data

def login():
  try:
    reddit = praw.Reddit(
      user_agent=generate_user_agent(),
      client_id=get_secret("reddit_client_id"),
      client_secret=get_secret("reddit_client_secret"),
      username=get_secret("reddit_username"),
      password=get_secret("reddit_password")
    )
    print(GREEN + "Login Successful\n" + RESET)
    return reddit
  except Exception as e:
    print(RED + "Login Failed\n" + RESET)
    sys.exit(0)
import re
import redis
import string
import time

def get_secret(name):
  filename = str("/var/openfaas/secrets/" + name)
  file = open(filename, 'r')
  data = file.read()
  file.close()
  return data

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

def dedupe_list(x):
  return list(dict.fromkeys(x))

def strip_punctuation(x):
  return x.translate(str.maketrans('', '', string.punctuation))

def sub_exists(reddit, redis, x):
  exists = True

  try:
    # We'll check Redis cache first... it's faster!
    try:
      inCache = redis.exists(x)
      if(inCache == 0):
        err = x + " was not found"
        raise Exception(err)
      elif(inCache == 1):
        print("✅", x, "exists in cache!")
    except Exception as e:
      raise Exception(e)
  except:
    # Otherwise we'll fall back and see if it exists on Reddit.com
    try:
      reddit.subreddits.search_by_name(x, exact=True)
      exists = True
      # Looks like it exists on Reddit so we'll save it in Redis cache for next time
      redis.setnx(str(x), "")
      print("💾", x, "was found on Reddit! Caching for later...")
    except:
      exists = False
  
  return exists
  
def parse_subreddit(reddit, sub):
  redisclient = redis_connect()
  valid_subs = []
  print("\n", "[[[ 🔎 Mapping r/", sub, " ]]]", "\n", sep="")
  try:
    # Gather subreddit info
    subreddit = reddit.subreddit(sub)
    related_subs = []
    related_subs = re.findall(r"/r/([^\s/]+)", subreddit.description)

    # Strip punctuation from collected subreddits
    for i in range(len(related_subs)):
      related_subs[i] = strip_punctuation(related_subs[i])

    # Remove any duplicate subreddits
    related_subs = dedupe_list(related_subs)

    # Remove any mentions of the searched subreddit
    try:
      related_subs.remove(sub)
    except:
      pass # Do nothing

    try:
      related_subs.remove(sub.capitalize())
    except:
      pass # Do nothing

    try:
      related_subs.remove(sub.upper())
    except:
      pass # Do nothing
    
    try:
      related_subs.remove(sub.lower())
    except:
      pass # Do nothing
    
    # Check if the subreddits found actually exist
    for i in range(len(related_subs)):
      if(sub_exists(reddit, redisclient, related_subs[i])):
        valid_subs.append(related_subs[i])

  except Exception as e:
    print("⛔ Error finding data for r/", sub, ": ", e, sep="")
    pass

  return valid_subs
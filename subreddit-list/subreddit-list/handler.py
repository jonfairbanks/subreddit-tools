import redis
import string
import sys

from flask import jsonify

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
    sys.exit(0)

def dedupe_list(x):
  return list(dict.fromkeys(x))

def handle(req):
  redisclient = redis_connect()
  keys = []

  for key in redisclient.scan_iter():
    try:
      keys.append(key.decode("utf-8"))
    except Exception as e:
      print("Issue with a key:", key, e)

  keys = dedupe_list(keys)
  #keys.sort()
  keys = sorted(keys, key=str.lower)

  data = {
    "count": len(keys),
    "subreddits": keys
  }

  return jsonify(data)
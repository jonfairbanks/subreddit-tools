import json
import os
import sys
import time

from flask import Flask, request
from markupsafe import escape
from waitress import serve

from mapper import parse_subreddit
from reddit import login

DEPTH = 2

try:
  print('--- Subreddit Mapper ---\n')
  reddit = login()
except Exception as e:
  print("There was an error logging into Reddit:", e)

app = Flask(__name__)

@app.before_request
def fix_transfer_encoding():
    """
    Sets the "wsgi.input_terminated" environment flag, thus enabling
    Werkzeug to pass chunked requests as streams.  The gunicorn server
    should set this, but it's not yet been implemented.
    """

    transfer_encoding = request.headers.get("Transfer-Encoding", None)
    if transfer_encoding == u"chunked":
        request.environ["wsgi.input_terminated"] = True

@app.route("/", defaults={"path": ""}, methods=["POST", "GET"])
def health_check(path):
    return "OK"

@app.route('/<sub>')
def parse(sub):
    print("\nReceived request to map r/", sub, sep="")
    startTime = time.time()
    data = {}
    for i in range(DEPTH + 1):
      # If this is the first run, gather initial data
      if(i == 0):
        temp_data = {
            "layerId": i,
            "parent": None,
            "subreddit": escape(sub), 
            "related": parse_subreddit(reddit, escape(sub))
        }
        data[i] = temp_data

      # Otherwise use subreddits found from the first run for subsequent runs
      else:
        try:
          search = data[i-1]["related"]
          for s in range(len(search)):
            temp_data = {
              "layerId": i,
              "parent": data[i-1]["subreddit"],
              "subreddit": search[s], 
              "related": parse_subreddit(reddit, search[s])
            }
            data[len(data)] = temp_data
        except Exception as e:
          data[1] = {}

    executionTime = (time.time() - startTime)
    print('Execution time: ' + str(round(executionTime, 2)) + "s")
    
    return data

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000, threads=8)


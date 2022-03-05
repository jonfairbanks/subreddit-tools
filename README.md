# subreddit-tools

![subreddit-tools-architecture](https://raw.githubusercontent.com/jonfairbanks/subreddit-tools/main/resources/subreddit-tools.png)

#### A collection of serverless functions related to Subreddit mapping

- [Subreddit-Scraper](#): scrape Reddit.com/r/all for recent subreddits and cache to Redis
- [Subreddit-Mapper](#): given a Subreddit, map N layers deep for related subreddits
- [Subreddit-List](#): list all previously found subreddits
# douban-crawler
crawl user, movie data from douban.com

## Requirements

Scrapy
Python2

## Start Up
```
Spider for User Info
scrapy crawl douban_spider

Spider for User's Movies、Books history
scrapy crawl collect_spider -o result.json -t json
```

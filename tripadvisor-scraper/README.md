# CRAWL TRIPADVISOR DATA #
 cd tripadvisor-scraper/
 run command :
 scrapy crawl tripadvisor-restaurant -o output/result.json -t json

scrapy crawl tripadvisor-restaurant -t csv -o output/result.csv --loglevel=INFO
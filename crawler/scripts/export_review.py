import pymongo
import json

conn = pymongo.MongoClient()
mongodb = conn['hotel_crawler']

import argparse
parser = argparse.ArgumentParser(
    description="extracts json file from a crawling source")
parser.add_argument(
    "--source",
    help="source to extract data from")
parser.add_argument(
    "--file",
    help="output file path")
args = parser.parse_args()
if not args.file and args.source:
    parser.print_help()
    exit()

# open json file
with open(args.file, "w") as fp:
    # get cursor
    review_list = []
    all_reviews = mongodb.review.find({"source": args.source})
    for review in all_reviews:
        if not review.get("review_text"):
            continue
        review_dict = {"rating": 0, "review_text": review.get('review_text').strip(), "id": review.get("site_id")}
        review_list.append(review_dict)

    fp.write(json.dumps(review_list, indent=4, separators=(",", ": ")))

# at exit
conn.disconnect()

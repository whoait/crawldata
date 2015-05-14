import pymongo
import json

conn = pymongo.MongoClient()
mongodb = conn['hotel_crawler']

# set of review ids that are done
done_set = set([])

# first check for existing reviews
# populate done_set
with open("review_done.json", "r") as fp_done:
    existing_review_list = json.load(fp_done)
    for entry in existing_review_list:
        done_set.add(entry['id'])

# open json file
with open("review_out.json", "w") as fp:
    # get cursor
    review_list = []
    all_reviews = mongodb.review.find({})
    for review in all_reviews:
        if not review.get("review_text"):
            continue
        if review.get("site_id") in done_set:
            continue
        review_dict = {"rating": 0, "review_text": review.get('review_text').strip(), "id": review.get("site_id")}
        review_list.append(review_dict)

    fp.write(json.dumps(review_list, indent=4, separators=(",", ": ")))

# at exit
conn.disconnect()

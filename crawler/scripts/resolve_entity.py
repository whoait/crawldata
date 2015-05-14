__author__ = 'ongzl'
''' add entity id to review '''
import json
import pymongo
import optparse


parser = optparse.OptionParser()
parser.add_option("-d", "--data", dest="data_file", help="data file", metavar="DATA FILE")
parser.add_option("-i", "--input", dest="input_file", help="input file", metavar="INPUT FILE")
parser.add_option("-o", "--output", dest="output_file", help="output file", metavar="OUTPUT FILE")
options, args = parser.parse_args()

''' build dict of entities and reviews '''


review_entity_dict = {}


if options.data_file:
    with open(options.data_file, 'r') as fp_data:
        for line in fp_data:
            line_parts = line.split(',')
            line_key = int(line_parts[0])
            line_value = int(line_parts[1])
            review_entity_dict[line_key] = line_value
else:
    conn = pymongo.MongoClient()
    db = conn['hotel_crawler']
    for review in db.review.find({},
        {'_id': 0, 'site_id': 1, 'entity_source_id': 1}):
        review_entity_dict[review['site_id']] = review['entity_source_id']
    conn.close()


for i in range(0, 64):
    infilename = "review_out_%02d.json" % i
    outfilename = "output/review_out_%02d.json" % i

    output_list = []

    with open(infilename, 'r') as fp_in:
        with open(outfilename, 'w+') as fp_out:
            review_list = json.load(fp_in)
            for review in review_list:
                review_id = int(review.get('review_id')) or 0
                review['entity_id'] = review_entity_dict[review_id] if review_entity_dict.get(review_id) else 0
                if not (review_id):
                    print "No review id in review"
                if not (review_entity_dict.get(review_id)):
                    print "No review id in dict"
                output_list.append(review)
            json.dump(output_list, fp_out, indent=True, separators=(',', ':'))


def generate_dict_file():
    with open("data_out.csv", "w+") as fp:
        for review in db.review.find({}, {'_id':0, 'site_id': 1, 'entity_source_id': 1}):
            if review.get('site_id') and review.get('entity_source_id'):
                fp.write('{0},{1}\n'.format(review['site_id'], review['entity_source_id']))
            else:
                print "NO REVIEW FOR {0}".format(review)

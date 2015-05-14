__author__ = 'ongzl'

import sys
import json

if len(sys.argv) < 3:
    print "Please enter python label_csv_json.py <filepath of csv file> <filepath of existing json file>"

filepath_csv = sys.argv[1]
filepath_json = sys.argv[2]

review_dict_array = []
line_flag = False
duplicate_flag = False
seen_id_set = set([])

label_dict = {
    "va": "VALUE",
    "lo": "LOCATION",
    "sl": "SLEEP QUALITY",
    "ro": "ROOM",
    "cl": "CLEANLINESS",
    "se": "SERVICE",
    "fo": "FOOD",
    "fa": "FACILITY",
    "ns": "NS"
}

with open(filepath_json, "r") as fp:
    try:
        review_dict_array = json.load(fp)
        for item in review_dict_array:
            seen_id_set.add(item['review_id'])
    except:
        # no file here - just ignore
        pass

with open(filepath_csv, "r") as fp:
    line_dict = {}
    line_count = 0

    for line in fp:
        if line_flag:
            if duplicate_flag:
                duplicate_flag = False
            else:
                # process flags
                label_list = line.split("aspect here:")[1].split(",")
                clean_label_list = []
                for label in label_list:
                    if label in label_dict:
                        full_label = label_dict[label]
                        clean_label_list.append(full_label)
                line_dict['aspect'] = clean_label_list

                review_dict_array.append(line_dict)
                line_dict = {}
        else:
            # enter line
            line_parts = line.split(',')
            print line_parts
            line_dict['review_id'] = int(line_parts[0])
            line_dict['serial_id'] = int(line_parts[1])
            if line_dict['review_id'] in seen_id_set:
                duplicate_flag = True
                print "seen before!"
            else:
                seen_id_set.add(line_dict['serial_id'])
                # because file is in a fixed format,
                # we can split substring after 2nd ','
                index_0 = line.index(',')
                index_1 = line.index(',', index_0+1)
                line_dict['sentence'] = line[index_1+1:].strip()
                if line_dict['sentence'].endswith(',,,,,,,,'):
                    line_dict['sentence'] = line_dict['sentence'].replace(',,,,,,,,', '')

        line_flag = not line_flag
        line_count += 1
        if line_count % 10 == 0:
            print "{0}\n".format(line_count)

with open(filepath_json, "w") as fp_out:
    json.dump(review_dict_array, fp_out, indent=4, separators=(",", ": "))

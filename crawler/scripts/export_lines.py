import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


with open("review_line.json", "r") as fp:
    json_string = fp.read()
    line_list = json.loads(json_string)
    with open("output.csv","w") as wt:
        for line in line_list:
            if len(line['sentence']) < 5:
                continue
            string1 = "{0}\t{1}\t{2}\n".format(line['review_id'], line['serial_id'], line['sentence'])
            string2 = "\taspect here:\t\n"
            wt.write(string1)
            wt.write(string2)



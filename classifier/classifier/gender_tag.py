import json
import re
import codecs
import pickle
from demographer import process_tweet
import csv
import ast


# Use demographer to tag the author gender
def gender_tag(root_path):
    p = root_path + "cleaned1.json"
    count = 0
    csvfile = file('names.csv', 'wb')
    writer = csv.writer(csvfile)

    with codecs.open(p, 'r', encoding='utf8') as reader:
        for line in reader:
            count += 1
            if len(line.strip()) == 0:
                continue

            json_data = line
            python_obj = json.loads(json_data)
            author_name = python_obj["authors"]
            # Wrap the author's name using required form
            author_json = {'user':{'name':author_name[0]}}
            # Tag the author gender
            result0 = process_tweet(author_json)[0]["gender"][0]["value"]
            writer.writerow([count, author_name, result0])

        reader.close()
    csvfile.close()



def main():
    data_path = "./"
    data_name = "cleaned1.json"
    data_full_path = data_path + data_name

    gender_tag("./")


if __name__ == "__main__":
    main()

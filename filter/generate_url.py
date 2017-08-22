import json
import re
import codecs
from random_output import *

def extract_urls(filename):

    with codecs.open(filename, 'r', encoding='utf8') as reader:
        
        # Create ouput file
        url_file = "urls.json"
        output = codecs.open(url_file, 'w', encoding = "utf8")
              
        for line in reader:
            if len(line.strip()) == 0:
                continue

            # Convert JSON object to Python dictionary
            json_data = line
            python_obj = json.loads(json_data)

            if python_obj["authors"] == []:
                print python_obj["authors"]
                url = python_obj["url"]
                output.write(url)
                output.write('\n')


        output.close()

def main():
    extract_urls("filtered.json")


if __name__ == "__main__":
    main()
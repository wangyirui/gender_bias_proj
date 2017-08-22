#!/usr/bin/python

import json
import re
import codecs

def filter(filename, ratio):

    with codecs.open(filename, 'r', encoding='utf8') as reader:
        
        # Create ouput file
        filtered_name = "filtered" + str(ratio) + ".json"
        output = codecs.open(filtered_name, 'w', encoding = "utf8")
            
        #noise_name_list = ["Bill Clinton", "Donald Trump", "Bernie Sanders"]
        #target_name_list = ["Hillary Rodham Clinton", "Hillary Clinton", "Secretary Clinton", "Sec. Clinton", "Secretary of State Hillary Clinton", "Mrs. Clinton"]
        
        pattern1 = r'\b(Bill Clinton)|(Mr. Clinton)|(Donald Trump)|(Donald)|(Trump)|(Bernie Sanders)|(Bernie)|(Sanders)\b'
        pattern2 = r'\b(Hillary Rodham Clinton)|(Hillary Clinton)|(Secretary Clinton)|(Sec. Clinton)|(Secretary of State Hillary Clinton)|(Mrs. Clinton)|(Mrs. Bill Clinton)\b'
            
        count = 0
        
        for line in reader:
            if len(line.strip()) == 0:
                continue

            target_score = 0.0
            noise_score = 0.0

            # Number each record
            count += 1
            # Convert JSON object to Python dictionary
            json_data = line
            python_obj = json.loads(json_data)

            if "title" in python_obj and "text" in python_obj:
                noise_match = re.findall(pattern1, python_obj["text"])
                noise_score += len(noise_match)
                target_match = re.findall(pattern2, python_obj["text"])
                target_score += len(target_match)
                                              
            if target_score > 0.0 and (target_score / (target_score + noise_score) > ratio):
                # Add the field "num" to the JSon object
                python_obj["num"] = count
                write_json = json.dumps(python_obj)
                output.write(write_json)
                output.write('\n')


        output.close()

def main():
    # The ratio of Clinton's name to other related people's name
    ratio = 0.55
    file_path = "../"
    data_name = "ccb.news_dump.extraced.json"
    data_path = file_path + data_name
    filter(data_path, ratio)


if __name__ == "__main__":
    main()
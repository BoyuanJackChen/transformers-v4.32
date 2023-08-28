import numpy as np
import json

answer_dir = "100_test_tokens/"
answer_file_1 = "full_cascade_0.2.json"
answer_file_2 = "full_cascade_0.7.json"

with open(answer_dir+answer_file_1, 'r') as f:
    answer_data_1 = json.load(f)
with open(answer_dir+answer_file_2, 'r') as f:
    answer_data_2 = json.load(f)

for answer_data in [answer_data_1, answer_data_2]:
    count_16B = 0
    count_6B = 0
    count_2B = 0
    count_350M = 0
    for answer_dict in answer_data:
        checkpoint = answer_dict["checkpoint"]
        if checkpoint == "16B":
            count_16B += 1
        elif checkpoint == "6B":
            count_6B += 1
        elif checkpoint == "2B":
            count_2B += 1
        elif checkpoint == "350M":
            count_350M += 1
    count_350M -= count_2B
    count_2B -= count_6B
    count_6B -= count_16B
    print(f"16B: {count_16B}, 6B: {count_6B}, 2B: {count_2B}, 350M: {count_350M}")
    
from transformers import AutoTokenizer, AutoModelForCausalLM
import json

tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-16B-mono", device_map="auto")
answer_file = "100_test_tokens/full_cascade_0.7.json"
with open(answer_file, 'r') as f:
    answer_data = json.load(f)

all_line_nums = []

# [number, prompt, checkpoint, passed, answer, generated_testcode, test]
for i in range(len(answer_data)):
    answer_dict = answer_data[i]
    checkpoint = answer_dict["checkpoint"]
    number_str = answer_dict["number"]
    number = int(number_str.split('/')[-1])
    answer = answer_dict["answer"]
    prompt = answer_dict["prompt"]
    test = answer_dict["test"]
    test = test[test.find("def"):]
    testcode = answer_dict["generated_testcode"]
    # Count how many '\n' there are in testcode
    line_num = testcode.count('\n')
    all_line_nums.append(line_num)
    
# print max and min of num_lines
print(f"Max num_lines: {max(all_line_nums)}")
print(f"Min num_lines: {min(all_line_nums)}")

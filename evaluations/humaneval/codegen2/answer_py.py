from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import json
import os
import torch

def main():
    number_key = "task_id"
    prompt_key = "prompt"

    output_file_name = 'cg2_16B_py.json'
    existing_data = []
    existing_numbers = []
    if os.path.exists(output_file_name):
        with open(output_file_name, 'r') as f:
            existing_data = json.load(f)
        for data_dict in existing_data:
            existing_numbers.append(data_dict["number"])
        

    # Initialize model and tokenizer
    checkpoint = "Salesforce/codegen2-16B"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, device_map="auto")
    start_load_model = time.time()
    model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto")
    model.eval()
    print(f"Time to load model is {time.time() - start_load_model}")

    # Load Leetcode Dataset
    all_questions_dict = json.load(open("../data/HumanEval_py.json", "r"))

    # Generate answers
    answer_dict_list = []
    counter = 0

    start = time.time()
    for question in all_questions_dict:
        number = question[number_key]
        number_int = int(number.split('/')[1])
        if number in existing_numbers:
            print(f"Skipping question {number}")
            continue
        prompt = question[prompt_key]
        # prompt = prompt.replace("\t", "    ")
        print(f"On question {number}")

        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to('cuda')
        # print(f"input ids is {input_ids} has length {len(input_ids)}")
        generated_ids = model.generate(
            input_ids,
            max_new_tokens=500,
            num_beams=4,
            num_beam_groups=4,
            diversity_penalty=0.3,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
        )
        generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=False)
        prompt = tokenizer.batch_decode(input_ids, skip_special_tokens=False)[0]
        answer_dict = {
            "number": number, 
            "prompt": prompt,
            "answer": generated_text[0][len(prompt):],
            "test": question["test"],
            "canonical_solution": question["canonical_solution"],
            "declaration": question["declaration"],
            "example_test": question["example_test"],
        }
        answer_dict_list.append(answer_dict)
        counter += 1

        # Update to json file
        if not os.path.exists(output_file_name):
            output_data = [answer_dict]
            with open(output_file_name, 'w') as f:
                json.dump(output_data, f, indent=4)
        elif counter >= 1:
            with open(output_file_name, 'r') as f:
                output_data = json.load(f)
            output_data += answer_dict_list
            with open(output_file_name, 'w') as f:
                json.dump(output_data, f, indent=4)
            answer_dict_list = []
            counter = 0

    end = time.time()
    print(f"- Timing 32float - Time to generate HumanEval-python for starcoder with full capacity is {end - start} seconds")

if __name__== "__main__":
    main()

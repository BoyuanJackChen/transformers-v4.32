from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=int, default=3, help="Model name")
parser.add_argument("--pass_at", type=int, default=10, help="pass @ how many")
FLAGS = parser.parse_args()


stop_words = ["\n\n\n", "\n\n"]
imports = "\nimport math\nfrom typing import List\n"

def trim_with_stopwords(outputs, stopwords, original_prompt) -> str:
    result = []
    len_prompt = len(original_prompt)
    for output in outputs:
        answer = output[len_prompt:]
        min_i = len(answer)
        for w in sorted(stopwords, reverse=True):
            for i in range(len(answer)):
                if answer[i:].startswith(w) and min_i > i:
                    min_i = i
        answer = answer[:min_i]
        result.append(answer)
    return result

def main(args):
    loading_start = time.time()
    number_key = "number"
    prompt_key = "question"
    title_key = "title"
    difficulty_key = "difficulty"

    # Load HumanEval Dataset
    all_questions_dict = json.load(open("../../evaluations/leetcode_free/leetcode_free.json", "r"))

    # Generate answers
    answer_dict_list = []
    counter = 0
    
    checkpoint = ""
    if args.model == 0:
        model_size = "350M"
    elif args.model == 1:
        model_size = "2B"
    elif args.model == 2:
        model_size = "6B"
    elif args.model == 3:
        model_size = "16B"
    checkpoint = f"Salesforce/codegen-{model_size}-mono"
    
    output_file_name = f'{model_size}_pass{args.pass_at}.json'
    existing_data = []
    existing_numbers = []
    if os.path.exists(output_file_name):
        with open(output_file_name, 'r') as f:
            existing_data = json.load(f)
        for data_dict in existing_data:
            existing_numbers.append(data_dict["number"])
    existing_numbers = list(set(existing_numbers))
    
    model = AutoModelForCausalLM.from_pretrained(checkpoint, device_map="auto")
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, device_map="auto")
    loading_end = time.time()
    print(f"Time to load model is {loading_end - loading_start}")

    # Generate answers
    total_start = time.time()
    for question in all_questions_dict:
        number = question[number_key]
        if number in existing_numbers:
            print(f"Skipping question {number}")
            continue
        print(f"On question {number}")
        
        # Prepare prompt
        prompt = question[prompt_key]
        
        # prepare temperature
        if args.pass_at < 5:
            temperature = 0.2
        else:
            temperature = 0.8
                        
        # Generate solutions
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to('cuda')
        answer_ids = model.generate(
            input_ids,
            use_cache=True,
            pad_token_id=tokenizer.eos_token_id,
            max_new_tokens=300,
            top_k = 0,
            top_p = 0.95,
            temperature = temperature,
            num_return_sequences=args.pass_at,  # generate multiple answers to get pass @ ? accuracy
            num_beams=1,  # This ensures we're using sampling, not beam search
            do_sample=True  # This is important when using temperature, top_p, and top_k
        )
        answer_text = tokenizer.batch_decode(answer_ids, skip_special_tokens=False)
        prompt = tokenizer.batch_decode(input_ids, skip_special_tokens=False)[0]
        answer_trimmed = trim_with_stopwords(answer_text, stop_words, prompt)
        
        pass_idx = 1
        for answer_str in answer_trimmed:
            answer_dict = {
                "number": number,
                "title": question[title_key],
                "difficulty": question[difficulty_key],
                "prompt": prompt,
                "checkpoint": model_size,
                "pass": pass_idx,
                "answer": answer_str,
            }
            answer_dict_list.append(answer_dict)
            counter += 1
            pass_idx += 1

            # Update to json file
            if not os.path.exists(output_file_name):
                output_data = [answer_dict]
                with open(output_file_name, 'w') as f:
                    json.dump(output_data, f, indent=4)
                answer_dict_list = []
            elif counter >= 1:
                with open(output_file_name, 'r') as f:
                    output_data = json.load(f)
                output_data += answer_dict_list
                with open(output_file_name, 'w') as f:
                    json.dump(output_data, f, indent=4)
                answer_dict_list = []
        
    total_end = time.time()
    print(f"\nTotal time taken: {total_end - total_start} seconds")
        

if __name__== "__main__":
    main(FLAGS)

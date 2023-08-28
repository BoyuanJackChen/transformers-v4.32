from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import json
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--model", type=int, default=3, help="Model name")
parser.add_argument("--pass_at", type=int, default=10, help="pass @ how many")
FLAGS = parser.parse_args()

checking_end = "pass\n\n# Assume the above function is completed. Write 3 lines of testing code for the function.\n\nassert"
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
    number_key = "task_id"
    prompt_key = "prompt"
    temperature = 0.8

    # Load HumanEval Dataset
    all_questions_dict = json.load(open("../../evaluations/humaneval/data/HumanEval_py.json", "r"))

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
    
    output_file_name = f'{model_size}_pick_pass{args.pass_at}.json'
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
        number_int = int(number.split('/')[1])
        max_new_tokens = 200
        if number_int == 81:
            max_new_tokens = 300
        if number in existing_numbers:
            print(f"Skipping question {number}")
            continue
        print(f"On question {number}")
        prompt = question[prompt_key]
        input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to('cuda')
            
        # Generate solutions
        answer_ids = model.generate(
            input_ids,
            use_cache = True,
            pad_token_id = tokenizer.eos_token_id,
            max_new_tokens = max_new_tokens,
            top_k = 0,
            top_p = 0.95,
            temperature = temperature,
            num_return_sequences = args.pass_at,
            num_beams = 1,  # This ensures we're using sampling, not beam search
            do_sample = True  # This is important when using temperature, top_p, and top_k
        )
        answer_text = tokenizer.batch_decode(answer_ids, skip_special_tokens=False)
        prompt = tokenizer.batch_decode(input_ids, skip_special_tokens=False)[0]
        answer_trimmed = trim_with_stopwords(answer_text, stop_words, prompt)
        
        correct = False
        pass_idx = 0
        if args.pass_at == 1:
            pass_idx += 1
            this_answer = answer_trimmed[0]
        else:
            # Generate test code. Here we just generate one line, and we pick the one answer that passes it;
            # otherwise we just use the last one.
            prompt_testcode = prompt + checking_end
            input_ids = tokenizer(prompt_testcode, return_tensors="pt").input_ids.to('cuda')
            testcode_ids = model.generate(
                input_ids,
                use_cache = True,
                pad_token_id = tokenizer.eos_token_id,
                max_new_tokens = 32,
                top_k = 0,
                top_p = 0.95,
                temperature = temperature,
            )
            testcode_text = tokenizer.batch_decode(testcode_ids, skip_special_tokens=False)[0]
            testcode_trimmed = "\nassert" + testcode_text.split("\nassert", 1)[1]
            if "\n\n" in testcode_trimmed:
                testcode_trimmed = testcode_trimmed.split("\n\n", 1)[0]
            else:
                testcode_trimmed_list = testcode_trimmed.split("\n")[:2]
                testcode_trimmed = "\n".join(testcode_trimmed_list)
            
            for this_answer in answer_trimmed:
                pass_idx += 1
                answer_textcode = imports + prompt + this_answer + "\n" + testcode_trimmed
                try:
                    exec(answer_textcode, globals())
                    print("No error occurred!\n")
                    break
                except AssertionError as ae:
                    print("AssertionError occurred: ", ae, "\n")
                except SyntaxError as se:
                    print("SyntaxError occurred: ", se, "\n")
                except ValueError as ve:
                    print("ValueError occurred: ", ve, "\n")
                except ZeroDivisionError as ze:
                    print(f"ZeroDivisionError occurred: {ze}\n")
                except IndexError as ie:
                    print(f"IndexError occurred: {ie}\n")
                except TypeError as te:
                    print(f"TypeError occurred: {te}\n")
                except ImportError as im:
                    print(f"ImportError occurred: {im}\n")
                except AttributeError as at:
                    print(f"AttributeError occurred: {at}\n")
                except KeyError as ke:
                    print(f"KeyError occurred: {ke}\n")
                except MemoryError as me:
                    print(f"MemoryError occurred: {me}\n")
                except OverflowError as oe:
                    print(f"OverflowError occurred: {oe}\n")
                except RuntimeError as re:
                    print(f"RuntimeError occurred: {re}\n")
                except NameError as ne:
                    print(f"NameError occurred: {ne}\n")
                except FileNotFoundError as fe:
                    print(f"FileNotFoundError occurred: {fe}\n")
                except PermissionError as pe:
                    print(f"PermissionError occurred: {pe}\n")
                except Exception as e:
                    print(f"An unknown error occurred: {e}\n")
            
        answer_dict = {
            "number": number,
            "prompt": prompt,
            "checkpoint": model_size,
            "pass": args.pass_at,
            "correct": correct,
            "answer": this_answer,
            "generated_testcode": testcode_trimmed,
            "test": question["test"],
            "canonical_solution": question["canonical_solution"],
            "declaration": question["declaration"]
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

from transformers import AutoTokenizer, AutoModelForCausalLM
import time
import json
import os
import argparse

# Create some argparsers
parser = argparse.ArgumentParser(description='Generate answers for HumanEval')
parser.add_argument('--cascade', type=bool, default=True, help='Should we do cascade')
parser.add_argument('--use_350M', type=int, default=1, help='Should we include 350M model or not')
parser.add_argument('--answer_max', type=int, default=300, help='The max number of tokens for answers')
parser.add_argument('--test_lines', type=int, default=4, help='The max number of tokens for tests')
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
    prompt_key = "text"
    test_key = "test_list"
    canonical_key = "code"
    
    if args.use_350M:
        output_file_name = f'full_cascade_{args.test_lines}tests.json'
    else:
        output_file_name = f'no_350M_{args.test_lines}tests.json'
    existing_data = []
    existing_numbers = []
    if os.path.exists(output_file_name):
        with open(output_file_name, 'r') as f:
            existing_data = json.load(f)
        for data_dict in existing_data:
            existing_numbers.append(data_dict["number"])

    # Load MBPP Dataset
    all_questions_dict = json.load(open("../../evaluations/mbpp/mbpp.json", "r"))

    # Generate answers
    answer_dict_list = []
    counter = 0
    
    # Load all the models
    model_1 = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono", device_map="auto")
    model_1.eval()
    model_2 = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-2B-mono", device_map="auto")
    model_2.eval()
    model_3 = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-6B-mono", device_map="auto")
    model_3.eval()
    model_4 = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-16B-mono", device_map="auto")
    model_4.eval()
    tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-16B-mono", device_map="auto")
    print(f"Loading all the models took {time.time() - loading_start} seconds")

    # Generate answers
    total_start = time.time()
    for question in all_questions_dict:
        all_checkpoints = ["16B", "6B", "2B"]
        if args.use_350M:
            all_checkpoints.append("350M")
        number = question[number_key]
        if number in existing_numbers:
            print(f"Skipping question {number}")
            continue
        print(f"On question {number}")
        undone = True
        
        while undone:
            # Prepare prompt, specific for MBPP
            prompt = question[prompt_key]
            canonical_answer = question[canonical_key]
            canonical_answer_list = canonical_answer.split("\n")
            for line in canonical_answer_list:
                if line.startswith("def"):
                    def_line = line
                    break
            prompt += '\n' + def_line + '\n'
            prompt = prompt.replace(" \r", "")
            prompt = prompt.replace("\r", "")
            
            # Prepare test
            test_list = question[test_key]
            canonical_test = "\n".join(test_list)
            if len(question["challenge_test_list"]) > 0:
                canonical_test += "\n" + "\n".join(question["challenge_test_list"])
            
            # Initialize model and tokenizer
            model_size = all_checkpoints.pop()
            if model_size == "350M":
                model = model_1
            elif model_size == "2B":
                model = model_2
            elif model_size == "6B":
                model = model_3
            elif model_size == "16B":
                model = model_4
            
            # Generate solutions
            input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to('cuda')
            answer_ids = model.generate(
                input_ids,
                use_cache=True,
                pad_token_id=tokenizer.eos_token_id,
                max_new_tokens=args.answer_max,
                top_k = 0,
                top_p = 0.95,
                temperature = 0.2,
            )
            answer_text = tokenizer.batch_decode(answer_ids, skip_special_tokens=False)
            prompt = tokenizer.batch_decode(input_ids, skip_special_tokens=False)[0]
            answer_trimmed = trim_with_stopwords(answer_text, stop_words, prompt)[0]
            
            # Generate test code
            prompt_testcode = prompt + checking_end
            input_ids = tokenizer(prompt_testcode, return_tensors="pt").input_ids.to('cuda')
            testcode_ids = model.generate(
                input_ids,
                use_cache=True,
                pad_token_id=tokenizer.eos_token_id,
                max_new_tokens=args.test_lines * 50,
                top_k = 0,
                top_p = 0.95,
                temperature = 0.2,
            )
            testcode_text = tokenizer.batch_decode(testcode_ids, skip_special_tokens=False)[0]
            testcode_trimmed = "\nassert" + testcode_text.split("\nassert", 1)[1]
            if "\n\n" in testcode_trimmed:
                testcode_trimmed = testcode_trimmed.split("\n\n", 1)[0]
            else:
                testcode_trimmed_list = testcode_trimmed.split("\n")[:args.test_lines+1]
                testcode_trimmed = "\n".join(testcode_trimmed_list)
            print(f"HumanEval question {number}, Codegen {model_size}:")
            answer_textcode = imports + prompt + answer_trimmed + "\n" + testcode_trimmed
            print(answer_textcode)
            
            try:
                exec(answer_textcode, globals())
                print("No error occurred!\n")
                undone = False
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

            # Generate the result dictionary 
            answer_dict = {
                "number": number,
                "prompt": prompt,
                "checkpoint": model_size,
                "passed": (not undone),
                "answer": answer_trimmed,
                "generated_testcode": testcode_trimmed,
                "test": canonical_test,
                "canonical_solution": canonical_answer
            }
            answer_dict_list.append(answer_dict)
            counter += 1

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
            
            # Check if all models are used
            if len(all_checkpoints) == 0:
                undone = False
                
    total_end = time.time()
    print(f"\nTotal time taken: {total_end - total_start} seconds")
    print(f"Max answer tokens: {args.answer_max}")
    print(f"Max test lines: {args.test_lines}")
    print(f"Max test tokens: {args.test_lines * 50}")
        

if __name__== "__main__":
    main(FLAGS)

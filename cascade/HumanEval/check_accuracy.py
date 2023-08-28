import json
import pandas as pd
import multiprocessing

class TimeoutException(Exception):
    pass


answer_file = "16B_pass1.json"
bad_questions = [39]
with open(answer_file, 'r') as f:
    answer_data = json.load(f)

# Create a pandas dataframe with two columns: number and accuracy
df = pd.DataFrame(columns=["number", "accuracy"])

cascade_mode = False
multiple_pass = False
all_keys = answer_data[0].keys()
if "passed" in all_keys:
    cascade_mode = True
if "pass" in all_keys:
    multiple_pass = True

# Find the biggest pass
if multiple_pass:
    max_pass = 0
    for i in range(len(answer_data)):
        answer_dict = answer_data[i]
        current_pass = answer_dict["pass"]
        if current_pass==1 and max_pass>=1:
            break
        if current_pass > max_pass:
            max_pass = answer_dict["pass"]
    # max_pass = 1
    print(f"Max pass: {max_pass}")

# [number, prompt, checkpoint, passed, answer, generated_testcode, test]
for i in range(len(answer_data)):
    answer_dict = answer_data[i]
    checkpoint = answer_dict["checkpoint"]
    correct = False
    if cascade_mode and not answer_dict["passed"] and checkpoint != "16B":
        continue
    number_str = answer_dict["number"]
    number = int(number_str.split('/')[-1])
    if number in df["number"].values:
        continue
    if number in bad_questions:
        print(f"Number {number} is correct: {correct}")
        df.loc[len(df)] = [number, int(correct)]
        continue
    answer = answer_dict["answer"]
    prompt = answer_dict["prompt"]
    test = answer_dict["test"]
    test = test[test.find("def"):]
    full_code = prompt + answer + "\n\n" + test

    # # Create queues for inter-process communication
    # def worker(code_queue, result_queue):
    #     try:
    #         exec(code_queue.get())
    #         result_queue.put(True)
    #     except Exception as e:
    #         result_queue.put(False)
    # code_queue = multiprocessing.Queue()
    # result_queue = multiprocessing.Queue()
    # code_queue.put(full_code)
    # p = multiprocessing.Process(target=worker, args=(code_queue, result_queue))
    # p.start()
    # p.join(10)
    # if p.is_alive():
    #     p.terminate()
    #     p.join()
    # else:
    #     correct = result_queue.get()
    
    try:
        exec(full_code)
        correct = True
    except Exception as e:
        correct = False
    
    if multiple_pass and answer_dict['pass'] < max_pass:
        continue
    else:
        print(f"Number {number} is correct: {correct}")
        df.loc[len(df)] = [number, int(correct)]
    
accuracy = df["accuracy"].mean()
print(f"Accuracy: {accuracy}")

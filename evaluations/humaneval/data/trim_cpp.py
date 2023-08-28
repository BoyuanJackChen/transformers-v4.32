import json

language = "cpp"

with open(f'HumanEval_{language}.json', 'r') as f:
    data = json.load(f)

substring = "using namespace std;\n"
output_array = []
output_file = f"HumanEval_{language}_trimmed.json"
for i in data:
    prompt = i["prompt"]
    modified_prompt = prompt.replace(substring, "")
    task_id = i["task_id"]
    caconical_solution = i["canonical_solution"]
    test = i["test"]
    declaration = i["declaration"]
    declaration = declaration.replace(substring, "")
    example_test = i["example_test"]
    new_dict = {"prompt": modified_prompt, "task_id": task_id, "canonical_solution": caconical_solution, "test": test, "declaration": declaration, "example_test": example_test}
    output_array.append(new_dict)

with open(output_file, 'w') as f:
    json.dump(output_array, f, indent=4)
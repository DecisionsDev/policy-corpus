import os
import re
import sys
import inspect
import time
from enum import Enum
from pathlib import Path
from typing import Tuple, Dict
import json

from insurance.insurance_compliance.insurance_request import CarInsuranceRequest, Vehicle, Applicant, DrivingLicense

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_PROMPTS_PATH = os.path.join(ROOT_DIR, "../benchmark_your_policy_automation_docs")
SYSTEM_PROMPT_FILE = os.path.join(LLM_PROMPTS_PATH, "system_prompt.md")
USER_PROMPT_FILE_WITH_DATASTRUCTURES = os.path.join(LLM_PROMPTS_PATH, "user_prompt_with_datastructures_template.md")
USER_PROMPT_FILE_NO_DATASTRUCTURES = os.path.join(LLM_PROMPTS_PATH, "user_prompt_no_datastructures_template.md")

CONFIG_DIR = os.path.join(ROOT_DIR, "config")


class LLM_API(Enum):
    OLLAMA = 1
    WATSONXAI = 2


def load_config(filename):
    with open(filename, "r") as file:
        return json.load(file)


def file_to_string(filename):
    with open(filename, 'r') as file:
        return file.read()


def extract_code_from_response(response):
    patterns = [r'```python(.*?)```', r'```Python(.*?)```', r'```(.*?)```', r'"""(.*?)"""', r'""(.*?)""', r'"(.*?)"']
    for pattern in patterns:
        code_string = re.search(pattern, response, re.DOTALL)
        if code_string is not None:
            code_string = code_string.group(1).strip()
            break
    return response if not code_string else code_string

def call_ollama(model_config: Dict, system_prompt, user_prompt) -> Tuple[str, str, int]:
    try:
        import ollama
    except Exception as e:
        raise e

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
    generated_code = None
    generated_response = None
    total_completion_token = 0

    options = model_config["options"]
    options["additional_num_ctx"] += len(system_prompt) + len(user_prompt)

    for attempt in range(1000):
        try:
            response_cur = ollama.chat(
                model=model_config["model_name"], messages=messages, stream=False,
                options=options
            )
            if not response_cur["done"]:
                raise Exception("Non-200 response: " + str(response_cur))
            generated_response = response_cur["message"]["content"]
            generated_code = extract_code_from_response(generated_response)

            if generated_code:
                total_completion_token += response_cur["eval_count"]
                break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(1)

    return generated_response, generated_code, total_completion_token


def call_watsonxai(model_config, system_prompt, user_prompt) -> Tuple[str, str, int]:
    pass


def call_api(llm_api, model_config, system_prompt, user_prompt) -> Tuple[str, str, int]:
    if llm_api == LLM_API.OLLAMA:
        return call_ollama(model_config, system_prompt, user_prompt)
    elif llm_api == LLM_API.WATSONXAI:
        return call_watsonxai(model_config, system_prompt, user_prompt)

    return ("No supported LLM API type provided", "", 0)


def call_llm(policy_description_file_path, llm_api: LLM_API, config_file_path, output_file, *args):
    policy_document = file_to_string(policy_description_file_path)

    system_prompt = file_to_string(SYSTEM_PROMPT_FILE)
    model_config = load_config(config_file_path)

    if args:
        user_prompt = file_to_string(USER_PROMPT_FILE_WITH_DATASTRUCTURES)

        predefined_data_structures = ""
        for cls in args:
            predefined_data_structures += inspect.getsource(cls) + "\n"
        user_prompt = user_prompt.format(predefined_data_structures=predefined_data_structures, policy_document=policy_document)
    else:
        user_prompt = file_to_string(USER_PROMPT_FILE_NO_DATASTRUCTURES)
        user_prompt = user_prompt.format(policy_document=policy_document)

    generated_response, generated_code, number_tokens = call_api(llm_api, model_config, system_prompt, user_prompt)

    output_file = Path(output_file)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    output_file.write_text(generated_code)
    print(f"Number of tokens generated: {number_tokens}")
    print(generated_response)
    return generated_code, number_tokens


if __name__ == "__main__":
    call_llm(
        "../insurance/basic_eligibility_car_insurance.txt",
        LLM_API.OLLAMA,
        "./config/ollama_config_example.json",
        "generation_result.py",
        DrivingLicense, Applicant, Vehicle, CarInsuranceRequest
    )

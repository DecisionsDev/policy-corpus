import os
import re
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Tuple, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from common.generic_data_generator import DataGenerator
from common.watson_utils import DEFAULT_PARAMETERS, DEFAULT_URL
from luggage_data_generator import LuggageDataGenerator


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_PROMPTS_PATH = os.path.join(ROOT_DIR, "../benchmark_your_policy_automation_docs")
SYSTEM_PROMPT_FILE = os.path.join(LLM_PROMPTS_PATH, "system_prompt.md")
USER_PROMPT = os.path.join(LLM_PROMPTS_PATH, "user_prompt_template.md")

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


def extract_json_from_response(response):
    patterns = [r'```json(.*?)```', r'```Json(.*?)```', r'```JSON(.*?)```', r'```(.*?)```'] # r'"""(.*?)"""', r'""(.*?)""', r'"(.*?)"'
    for pattern in patterns:
        code_string = re.search(pattern, response, re.DOTALL)
        if code_string is not None:
            code_string = code_string.group(1).strip()
            break
    return None if not code_string else code_string


def call_ollama(model_config: Dict, system_prompt, user_prompt) -> Tuple[str, str, int]:
    try:
        import ollama
    except ImportError as e:
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
            generated_code = extract_json_from_response(generated_response)

            if generated_code:
                total_completion_token += response_cur["eval_count"]
                break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(1)

    return generated_response, generated_code, total_completion_token


def call_watsonxai(model_config: Dict, system_prompt, user_prompt) -> Tuple[str, str, int]:
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        from langchain_ibm import ChatWatsonx
    except ImportError as e:
        raise e

    os.environ["WATSONX_APIKEY"] = os.getenv("IBM_API_KEY")

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    chat = ChatWatsonx(
        model_id=model_config["model_id"],
        url=model_config["url"] if model_config["url"] else DEFAULT_URL,
        project_id=model_config["project_id"],
        params=model_config["options"] if model_config["options"] else DEFAULT_PARAMETERS,
    )

    generated_code = None
    generated_response = None
    total_completion_token = 0

    for attempt in range(1000):
        try:
            response_cur = chat.invoke(messages)

            generated_response = response_cur.content
            generated_code = extract_json_from_response(generated_response)

            if generated_code:
                total_completion_token += response_cur.response_metadata['token_usage']['generated_token_count'] + \
                        response_cur.response_metadata['token_usage']['input_token_count']
                break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            time.sleep(1)

    return generated_response, generated_code, total_completion_token


def call_api(llm_api, model_config, system_prompt, user_prompt) -> Tuple[str, str, int]:
    if llm_api == LLM_API.OLLAMA:
        return call_ollama(model_config, system_prompt, user_prompt)
    elif llm_api == LLM_API.WATSONXAI:
        return call_watsonxai(model_config, system_prompt, user_prompt)

    return "No supported LLM API type provided", "", 0


def call_api(llm_api, model_config, system_prompt, user_prompt) -> Tuple[str, str, int]:
    if llm_api == LLM_API.OLLAMA:
        return call_ollama(model_config, system_prompt, user_prompt)
    elif llm_api == LLM_API.WATSONXAI:
        return call_watsonxai(model_config, system_prompt, user_prompt)

    return "No supported LLM API type provided", "", 0


def call_llm(policy_description_file_path, csv_file, data_generator_class: DataGenerator, llm_api: LLM_API, config_file_path, result_output_path):
    policy_document = file_to_string(policy_description_file_path)

    system_prompt = file_to_string(SYSTEM_PROMPT_FILE)
    system_prompt = system_prompt.format(policy_document=policy_document)

    model_config = load_config(config_file_path)

    user_prompt_default = file_to_string(USER_PROMPT)

    dataFull = pd.read_csv(csv_file, na_filter=True).fillna("")
    dataFull = dataFull.sample(frac=1).reset_index(drop=True)

    data = dataFull.drop(columns=data_generator_class.EVAL_COLUMN_NAMES)
    # data = data.head(10)

    results = {}
    for idx, case in data.iterrows():
        user_prompt = user_prompt_default.format(test_case=case.to_json())
        generated_response, generated_answer, number_tokens = call_api(llm_api, model_config, system_prompt, user_prompt)
        results[idx] = {
            "test_case": dataFull.illoc[[idx]].to_dict(),
            "generated_response": generated_response,
            "generated_answer": json.loads(generated_answer) if generated_answer else None,
            "number_tokens": number_tokens
        }

    results_output_path = Path(result_output_path)
    results_output_path.parent.mkdir(exist_ok=True, parents=True)
    with open(result_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return results


if __name__ == "__main__":
    call_llm(
        "../luggage/luggage_policy.txt",
        "../luggage/luggage_compliance/luggage_policy_test_dataset_100.csv",
        LuggageDataGenerator(),
        LLM_API.OLLAMA,
        "./config/ollama_config_example.json",
        "generation_result.json",
    )

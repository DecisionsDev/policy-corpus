import os
import re
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Tuple, Dict, List
import json

import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

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


def call_ollama(model_config: Dict, system_prompt, user_prompts) -> Tuple[List[str | None], List[str | None], List[int]]:
    try:
        import ollama
    except ImportError as e:
        raise e

    messages = [{"role": "system", "content": system_prompt}]
    generated_codes = []
    generated_responses = []
    completion_tokens = []

    options = model_config["options"]
    options["additional_num_ctx"] += len(system_prompt) + len(max(user_prompts, key=len))
    for user_prompt in user_prompts:
        if len(messages) == 1:
            messages.append({"role": "user", "content": user_prompt})
        else:
            messages[1] = {"role": "user", "content": user_prompt}

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
                    completion_tokens.append(response_cur["eval_count"])
                    generated_codes.append(generated_code)
                    generated_responses.append(generated_response)
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(1)

    return generated_responses, generated_codes, completion_tokens


def call_watsonxai(model_config: Dict, system_prompt, user_prompts: []) -> Tuple[List[str | None], List[str | None], List[int]]:
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        from langchain_ibm import ChatWatsonx
    except ImportError as e:
        raise e

    os.environ["WATSONX_APIKEY"] = os.getenv("IBM_API_KEY")

    messages = [SystemMessage(content=system_prompt)]

    chat = ChatWatsonx(
        model_id=model_config["model_id"],
        url=model_config["url"] if model_config["url"] else DEFAULT_URL,
        project_id=model_config["project_id"],
        params=model_config["options"] if model_config["options"] else DEFAULT_PARAMETERS,
    )

    generated_codes = []
    generated_responses = []
    number_tokens = []

    for user_prompt in user_prompts:
        if len(messages) == 1:
            messages.append(user_prompt)
        else:
            messages[1] = user_prompt

        for attempt in range(1000):
            try:
                response_cur = chat.invoke(messages)

                generated_response = response_cur.content
                generated_code = extract_json_from_response(generated_response)

                if generated_code:
                    number_tokens.append(response_cur.response_metadata['token_usage']['completion_tokens'])
                    generated_codes.append(generated_code)
                    generated_responses.append(generated_response)
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(1)

    return generated_responses, generated_codes, number_tokens


def call_api(llm_api, model_config, system_prompt, user_prompts) -> Tuple[List[str], List[str], List[int]]:
    if llm_api == LLM_API.OLLAMA:
        return call_ollama(model_config, system_prompt, user_prompts)
    elif llm_api == LLM_API.WATSONXAI:
        return call_watsonxai(model_config, system_prompt, user_prompts)

    return ["No supported LLM API type provided"], [""], [0]


def call_llm(policy_description_file_path, csv_file, data_generator_class: DataGenerator, llm_api: LLM_API, config_file_path, result_output_path):
    policy_document = file_to_string(policy_description_file_path)

    system_prompt = file_to_string(SYSTEM_PROMPT_FILE)
    system_prompt = system_prompt.format(policy_document=policy_document)

    model_config = load_config(config_file_path)

    user_prompt_default = file_to_string(USER_PROMPT)

    dataFull = pd.read_csv(csv_file, na_filter=True).fillna("")
    dataFull = dataFull.sample(frac=1).reset_index(drop=True)

    data = dataFull.drop(columns=data_generator_class.EVAL_COLUMN_NAMES)
    data = data.head(5)

    results = {}
    user_prompts = []
    for idx, case in data.iterrows():
        user_prompts.append(user_prompt_default.format(test_case=case.to_json()))

    generated_responses, generated_answers, numbers_tokens = call_api(llm_api, model_config, system_prompt, user_prompts)
    for idx in range(len(generated_answers)):
        results[idx] = {
            "test_case": dataFull.iloc[idx].to_dict(),
            "generated_response": generated_responses[idx],
            "generated_answer": json.loads(generated_answers[idx]) if generated_answers[idx] else None,
            "number_tokens": numbers_tokens[idx]
        }

    results_output_path = Path(result_output_path)
    results_output_path.parent.mkdir(exist_ok=True, parents=True)
    with open(result_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return results


def benchmark_results(resulting_file, column_mapping: Dict[str, str]) -> List[Dict[str, float | int]]:
    # Load JSON file
    with open(resulting_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Extract test case and generated answer values
    test_case_values = []
    generated_values = []

    for key, item in data.items():
        test_case_entry = item["test_case"]
        generated_entry = item["generated_answer"]

        row_test_case = []
        row_generated = []

        for test_case_col, generated_col in column_mapping.items():
            row_test_case.append(test_case_entry.get(test_case_col))
            row_generated.append(generated_entry.get(generated_col))

        test_case_values.append(row_test_case)
        generated_values.append(row_generated)

    # Convert to DataFrame
    df_test_case = pd.DataFrame(test_case_values, columns=column_mapping.keys())
    df_generated = pd.DataFrame(generated_values, columns=column_mapping.keys())

    # Calculate metrics for each column
    metrics = {}
    for col in column_mapping.keys():
        y_true = df_test_case[col]
        y_pred = df_generated[col]

        # Convert categorical values to strings for comparison
        if not pd.api.types.is_numeric_dtype(y_true) or not pd.api.types.is_numeric_dtype(y_pred):
            y_true = y_true.astype(str)
            y_pred = y_pred.astype(str)

        # Compute metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        metrics[col] = {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1
        }

    return metrics


if __name__ == "__main__":
    # call_llm(
    #     "../luggage/luggage_policy.txt",
    #     "../luggage/luggage_compliance/luggage_policy_test_dataset_100.csv",
    #     LuggageDataGenerator(),
    #     LLM_API.WATSONXAI,
    #     "./config/watsonx_config_example.json",
    #     "generation_result_watson.json",
    # )
    call_llm(
        "../luggage/luggage_policy.txt",
        "../luggage/luggage_compliance/luggage_policy_test_dataset_100.csv",
        LuggageDataGenerator(),
        LLM_API.OLLAMA,
        "./config/ollama_config_example.json",
        "generation_result_ollama.json",
    )

    res = benchmark_results("generation_result_ollama.json", {"eligibility": "eligibility"})
    print(res)

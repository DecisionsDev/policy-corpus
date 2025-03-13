import argparse
import importlib
import inspect
import os
import re
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Tuple, Dict, List
import json
import pandas as pd

from common.benchmarking_results import benchmark_results, parse_column_mapping

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from common.generic_data_generator import DataGenerator
from common.watson_utils import DEFAULT_PARAMETERS, DEFAULT_URL


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
LLM_PROMPTS_PATH = os.path.join(ROOT_DIR, "../benchmark_your_policy_automation_docs")
SYSTEM_PROMPT_FILE = os.path.join(LLM_PROMPTS_PATH, "system_prompt_template.md")
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


def call_ollama(model_config: Dict, system_prompt, user_prompts) -> Tuple[List[str | None], List[str | None], List[int], List[float]]:
    try:
        import ollama
    except ImportError as e:
        raise e

    messages = [{"role": "system", "content": system_prompt}]
    generated_codes = []
    generated_responses = []
    completion_tokens = []
    exec_times = []

    options = model_config["options"]
    options["additional_num_ctx"] += len(system_prompt) + len(max(user_prompts, key=len))
    for user_prompt in user_prompts:
        if len(messages) == 1:
            messages.append({"role": "user", "content": user_prompt})
        else:
            messages[1] = {"role": "user", "content": user_prompt}
        start_time_round = time.time()
        for attempt in range(1000):
            try:
                response_cur = ollama.chat(
                    model=model_config["model_name"], messages=messages, stream=False,
                    options=options
                )
                end_time = time.time()
                if not response_cur["done"]:
                    raise Exception("Non-200 response: " + str(response_cur))
                generated_response = response_cur["message"]["content"]
                generated_code = extract_json_from_response(generated_response)

                if generated_code:
                    exec_times.append(round(end_time - start_time_round))
                    completion_tokens.append(response_cur["eval_count"])
                    generated_codes.append(generated_code)
                    generated_responses.append(generated_response)
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(1)

    return generated_responses, generated_codes, completion_tokens, exec_times


def call_watsonxai(model_config: Dict, system_prompt, user_prompts: []) -> Tuple[List[str | None], List[str | None], List[int], List[float]]:
    try:
        from langchain_core.messages import SystemMessage, HumanMessage
        from langchain_ibm import ChatWatsonx
    except ImportError as e:
        raise e

    if not os.getenv("WATSONX_APIKEY"):
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
    exec_times = []

    for user_prompt in user_prompts:
        if len(messages) == 1:
            messages.append(user_prompt)
        else:
            messages[1] = user_prompt

        start_time_round = time.time()

        for attempt in range(1000):
            try:
                response_cur = chat.invoke(messages)
                end_time = time.time()
                generated_response = response_cur.content
                generated_code = extract_json_from_response(generated_response)

                if generated_code:
                    exec_times.append(round(end_time - start_time_round))
                    number_tokens.append(response_cur.response_metadata['token_usage']['completion_tokens'])
                    generated_codes.append(generated_code)
                    generated_responses.append(generated_response)
                    break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed with error: {e}")
                time.sleep(1)

    return generated_responses, generated_codes, number_tokens, exec_times


def call_api(llm_api, model_config, system_prompt, user_prompts) -> Tuple[List[str], List[str], List[int], List[float]]:
    if llm_api == LLM_API.OLLAMA:
        return call_ollama(model_config, system_prompt, user_prompts)
    elif llm_api == LLM_API.WATSONXAI:
        return call_watsonxai(model_config, system_prompt, user_prompts)

    return ["No supported LLM API type provided"], [""], [0], [0]


def call_llm(policy_description_file_path, csv_file, data_generator_or_columns: DataGenerator | List[str], llm_api: LLM_API, config_file_path, result_output_path):
    policy_document = file_to_string(policy_description_file_path)

    system_prompt = file_to_string(SYSTEM_PROMPT_FILE)
    system_prompt = system_prompt.format(policy_document=policy_document)

    model_config = load_config(config_file_path)

    user_prompt_default = file_to_string(USER_PROMPT)

    dataFull = pd.read_csv(csv_file, na_filter=True).fillna("")
    dataFull = dataFull.sample(frac=1).reset_index(drop=True)

    # Handle both DataGenerator and direct list input
    if isinstance(data_generator_or_columns, list):
        eval_column_names = data_generator_or_columns  # Direct list of column names
    elif isinstance(data_generator_or_columns, DataGenerator):
        eval_column_names = data_generator_or_columns.EVAL_COLUMN_NAMES  # Extract from class
    else:
        raise TypeError("data_generator_or_columns must be either a list of strings or a DataGenerator instance.")

    data = dataFull.drop(columns=eval_column_names)
    # data = data.head(5)

    results = {}
    user_prompts = []
    print("Formulating user prompts...")
    for idx, case in data.iterrows():
        user_prompts.append(user_prompt_default.format(test_case=case.to_json()))

    print("Calling LLM with the created user prompts...")
    generated_responses, generated_answers, numbers_tokens, exec_times = call_api(llm_api, model_config, system_prompt, user_prompts)
    for idx in range(len(generated_answers)):
        results[idx] = {
            "test_case": dataFull.iloc[idx].to_dict(),
            "generated_response": generated_responses[idx],
            "generated_answer": json.loads(generated_answers[idx]) if generated_answers[idx] else None,
            "number_tokens": numbers_tokens[idx],
            "execution_time": exec_times[idx]
        }

    print("Saving the generation results...")

    results_output_path = Path(result_output_path)
    results_output_path.parent.mkdir(exist_ok=True, parents=True)
    with open(result_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    return results


def load_data_generator_or_columns(value):
    """
    Tries to load a DataGenerator subclass or interpret the input as a list of column names.
    - If `value` is a module.class string (e.g., 'my_module.MyGenerator'), loads the class dynamically.
    - If `value` is a comma-separated string (e.g., 'col1,col2,col3'), returns it as a list.
    """
    if "," in value:  # Check if input is a comma-separated list
        return value.split(",")  # Return list of strings

    try:
        module_name, class_name = value.rsplit(".", 1)  # Split "module.Class"
        module = importlib.import_module(module_name)  # Import module dynamically
        cls = getattr(module, class_name, None)  # Get the class

        if cls and inspect.isclass(cls) and issubclass(cls, DataGenerator):
            return cls()  # Instantiate the class
        else:
            raise ValueError(f"{class_name} is not a valid DataGenerator subclass.")

    except Exception as e:
        raise ImportError(f"Could not load data generator class '{value}': {e}")


if __name__ == "__main__":
    # from luggage_data_generator import LuggageDataGenerator
    # call_llm(
    #     "../luggage/luggage_policy.txt",
    #     "../luggage/luggage_compliance/luggage_policy_test_dataset_100.csv",
    #     LuggageDataGenerator(),
    #     LLM_API.WATSONXAI,
    #     "./config/watsonx_config_example.json",
    #     "generation_result_watson.json",
    # )

    # from luggage_data_generator import LuggageDataGenerator
    # call_llm(
    #     "../luggage/luggage_policy.txt",
    #     "../luggage/luggage_compliance/luggage_policy_test_dataset_100.csv",
    #     LuggageDataGenerator(),
    #     LLM_API.OLLAMA,
    #     "./config/ollama_config_example.json",
    #     "generation_result_deepseek_8b.json",
    # )

    parser = argparse.ArgumentParser(description="Benchmark the selected model against the reference dataset")
    parser.add_argument("--policy_desc", type=str, required=True, help="Path to the policy text description file.")
    parser.add_argument("--csv_file", type=str, required=True, help="Path to the reference testing dataset csv file.")
    parser.add_argument("--data_generator", type=str, required=True,
                        help="Either the full module path of a DataGenerator subclass, with which the reference csv dataset is generated (e.g., 'my_module.MyGenerator') "
                             "or a comma-separated list of evaluation columns (e.g., 'col1,col2,col3').")
    parser.add_argument("--api", type=str, required=False, choices=["ollama", "watsonx"],
                        help="The API to be used for the LLM call (ollama/watsonx).")
    parser.add_argument("--config_file", type=str, required=True, help="The model & api configuration file path.")
    parser.add_argument("--output_file", type=str, required=True, help="The path for the benchmarking results output")
    parser.add_argument("--output_file", type=str, required=True, help="The path for the benchmarking results output")
    parser.add_argument("--column_mapping", type=str, required=False,
                        help="Optional JSON string for column name mapping for benchmark metrics calculation. "
                             "The way they are saved in reference csv dataset vs the way they are saved in the resulting output_file (generated by LLM) "
                             "(e.g., '{\"eligibility\": \"elig\"}').")

    args = parser.parse_args()

    data_generator = load_data_generator_or_columns(args.data_generator)

    call_llm(args.policy_desc, args.csv_file, data_generator,
             LLM_API[args.api.upper()] if args.api else None, args.config_file, args.output_file)

    column_mapping = parse_column_mapping(args.column_mapping)
    if column_mapping:
        res = benchmark_results(args.output_file, column_mapping)
        print(res)

# python ./llm_calls.py --policy_desc "../luggage/luggage_policy.txt" --csv_file "../luggage/luggage_compliance/luggage_policy_test_dataset_100.csv" --data_generator "luggage_data_generator.LuggageDataGenerator" --api ollama --config_file "./config/ollama_config_example.json" --output_file "generation_result_test.json" --column_mapping '{"eligibility": "eligible"}'

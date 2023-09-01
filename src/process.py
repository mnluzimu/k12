import json
import os
from tqdm import tqdm
import re
import random

def is_number(s):
    pattern = r'^-?\d+(?:\.\d+)?$'
    return bool(re.match(pattern, s))

def save_jsonl(datas, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

def process(in_path, out_path, prefix):
    files = [f for f in os.listdir(in_path) if f.startswith(prefix) and os.path.isfile(os.path.join(in_path, f))]

    error_num = 0
    total_num = 0
    with open(os.path.join(out_path, "error.jsonl"), "w", encoding="utf-8") as f_error:
        for file_name in files:
            new_datas = []
            with open(os.path.join(in_path, file_name), "r", encoding="utf-8") as f:
                datas = [json.loads(line) for line in f]
                for idx, data in tqdm(enumerate(datas)):
                    try:
                        splits_question = question, answer_solution = data["text"].split("本题的答案为：")
                        question = splits_question[0]
                        answer_solution = "".join(splits_question[1:])
                        if len(answer_solution.split("本题的解析为：")) >= 2:
                            splits = answer_solution.split("本题的解析为：")
                        elif len(answer_solution.split("解：")) >= 2:
                            splits = answer_solution.split("解：")
                        elif len(answer_solution.split("解；")) >= 2:
                            splits = answer_solution.split("解；")
                        elif len(answer_solution.split("试题分析：")) >= 2:
                            splits = answer_solution.split("试题分析：")
                        else:
                            splits = []
                        answer = splits[0]
                        solution = "".join(splits[1:])
                        new_data = {
                            "id": f"{file_name}/{idx}",
                            "question": question.strip(" \n\t"),
                            "answer": answer.strip(" \n\t"),
                            "solution": solution.strip(" \n\t"),
                            "subject": data["subject"],
                            "qtype": data["qtpye"],
                            "gradeId": data["gradeId"],
                            "knowledges": data["knowledges"]
                        }
                        new_datas.append(new_data)
                        total_num += 1
                    except:
                        print(data)
                        data["file_name"] = file_name
                        f_error.write(json.dumps(data, ensure_ascii=False) + "\n")
                        error_num += 1
                        total_num += 1
            with open(os.path.join(out_path, f"out_{file_name}"), "w", encoding="utf-8") as f:
                for data in new_datas:
                    f.write(json.dumps(data, ensure_ascii=False) + "\n")
        

    print(f"error_num: {error_num}")
    print(f"total_num: {total_num}")


def process_test(in_path, out_path, prefix):
    files = [f for f in os.listdir(in_path) if f.startswith(prefix) and os.path.isfile(os.path.join(in_path, f))]

    with open(os.path.join(out_path, "k12_train_10000.jsonl"), "w", encoding="utf-8") as f_out:
        for file_name in files:
            with open(os.path.join(in_path, file_name), "r", encoding="utf-8") as f:
                datas = [json.loads(line) for line in f]
                for idx, data in tqdm(enumerate(datas)):
                    if is_number(data["answer"]):
                        system = ""
                        user = data["question"]
                        assistant = data["solution"] + f"\n所以本题的答案为{data['answer']}. ### {data['answer']}"
                        new_data = {"messages": [{"role": "system", "content": [{"type": "text", "content": system}]},
                                                {"role": "user", "content": [{"type": "text", "content": user}]},
                                                {"role": "assistant", "content": [{"type": "text", "content": assistant}]}]}
                        f_out.write(json.dumps(new_data, ensure_ascii=False) + "\n")
        
def process_train(in_path, out_path, prefix):
    files = [f for f in os.listdir(in_path) if f.startswith(prefix) and os.path.isfile(os.path.join(in_path, f))]

    with open(os.path.join(out_path, "k12_train_10000.jsonl"), "w", encoding="utf-8") as f_out:
        for file_name in files:
            with open(os.path.join(in_path, file_name), "r", encoding="utf-8") as f:
                datas = [json.loads(line) for line in f]
                for idx, data in tqdm(enumerate(datas)):
                    system = ""
                    user = data["question"]
                    assistant = data["gpt_solution"]
                    new_data = {"messages": [{"role": "system", "content": [{"type": "text", "content": system}]},
                                            {"role": "user", "content": [{"type": "text", "content": user}]},
                                            {"role": "assistant", "content": [{"type": "text", "content": assistant}]}]}
                    f_out.write(json.dumps(new_data, ensure_ascii=False) + "\n")

def split(data, out_path):
    # Shuffle the data
    random.shuffle(data)

    # Split the data into 90% train and 10% test
    split_idx = int(0.9 * len(data))
    train_data = data[:split_idx]
    test_data = data[split_idx:]
    save_jsonl(train_data, os.path.join(out_path, "train.jsonl"))
    save_jsonl(test_data, os.path.join(out_path, "test.jsonl"))

if __name__ == "__main__":
    # process("/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801", "/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/outs", "pretrain_Math")
    # process_test("/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/outs", "/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/test", "out_pretrain_Math")
    # with open("/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/test/k12_test.jsonl", "r") as f:
    #     datas = [json.loads(line) for line in f]
    # print(len(datas))
    # split(datas, "/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/test")
    process_train("/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/gpt_outs/processed", "/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/train", "processed_out_10000_k12_GPT3.jsonl")

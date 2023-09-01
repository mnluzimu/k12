import json
import os
from tqdm import tqdm
import re
from sklearn.model_selection import train_test_split
import random

def is_number(s):
    pattern = r'^-?\d+(?:\.\d+)?$'
    return bool(re.match(pattern, s))

def save_jsonl(datas, file_name):
    print("saving....")
    with open(file_name, "w", encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

def find_only_capital_letter(s):
    capital_letters = [c for c in s if c.isupper()]
    if len(capital_letters) == 1:
        return capital_letters[0]
    else:
        return None

def process(in_path, out_path, prefix):
    os.makedirs(out_path, exist_ok=True)
    files = [f for f in os.listdir(in_path) if f.startswith(prefix) and os.path.isfile(os.path.join(in_path, f))]

    error_data = []
    total_num = 0
    success_num = 0
    error_num = {"no answer": 0, "no solution": 0, "no picture": 0}
    for file_name in tqdm(files):
        new_data = []
        with open(os.path.join(in_path, file_name), "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]
            for idx, line in enumerate(data):
                total_num += 1
                error_line = {}
                if line['text'].find("本题的答案为：") == -1:
                    error_line['id'] = f"{file_name}/{idx}"
                    error_line['error_type'] = "no answer"
                    error_line.update(line)
                    error_data.append(error_line)
                    error_num["no answer"] += 1
                    continue
                elif line['text'].find("本题的解析为：") == -1:
                    error_line['id'] = f"{file_name}/{idx}"
                    error_line['error_type'] = "no solution"
                    error_line.update(line)
                    error_data.append(error_line)
                    error_num["no solution"] += 1
                    continue
                elif line['text'].find('画图，详见答案') != -1:
                    error_line['id'] = f"{file_name}/{idx}"
                    error_line['error_type'] = "no picture"
                    error_line.update(line)
                    error_data.append(error_line)
                    error_num["no picture"] += 1
                    continue
                splits_question = line["text"].split("本题的答案为：")
                question = splits_question[0][len(" 请回答以下问题："):]
                answer_solution = "".join(splits_question[1:])
                splits = answer_solution.split("本题的解析为：")
                
                # elif -len(answer_s错误olution.split("解：")) >= 2:
                #     splits = answer_solution.split("解：")
                # elif len(answer_solution.split("解；")) >= 2:
                #     splits = answer_solution.split("解；")
                
                answer = splits[0]
                answer_tmp = None
                if file_name == "pretrain_Math选择题.jsonl":
                    answer_tmp = find_only_capital_letter(answer)

                if answer_tmp:
                    answer = answer_tmp

                solution = "".join(splits[1:])
                new_line = {
                    "id": f"{file_name}/{idx}",
                    "question": question.strip(" \n\t"),
                    "answer": answer.strip(" \n\t"),
                    "solution": solution.strip(" \n\t"),
                    "subject": line["subject"],
                    "qtype": line["qtpye"],
                    "gradeId": line["gradeId"],
                    "knowledges": line["knowledges"]
                }
                new_data.append(new_line)
                success_num += 1
                    
        with open(os.path.join(out_path, f"process_{file_name}"), "w", encoding="utf-8") as f:
            for line in new_data:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
                
    with open(os.path.join(out_path, f"error.jsonl"), "w", encoding="utf-8") as f:
        for line in error_data:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
        

    print(f"total_num: {total_num}")
    print(f"success_num: {success_num}")
    print(f"error_num: {error_num}")


def process_for_GPT(in_path, out_path, prefix):
    os.makedirs(out_path, exist_ok=True)
    files = [f for f in os.listdir(in_path) if f.startswith(prefix) and os.path.isfile(os.path.join(in_path, f))]

    new_data = []
    for file_name in tqdm(files):
        with open(os.path.join(in_path, file_name), "r", encoding="utf-8") as f:
            data = [json.loads(line) for line in f]
            for idx, line in enumerate(data):
                new_line = {}
                extra = {}
                extra['id'] = line['id']
                extra['answer'] = line['answer']
                extra['solution'] = line['solution']
                new_line['text'] = [{'content': "Refer to the given solution and give your own solution using Chinese step by step.\nYou can't reveal that you know the standard answer in the process of solving the problem. Remember to put your answer in one and only one \\boxed{}.\n\nPROBLEM: " + line["question"] + "\n\nGROUND SOLUTION: "+ line["solution"] +"最终答案是\\boxed{" + line["answer"] + "}.\n\nYOUR SOLUTION:\n"}]
                new_line['first_text_length'] = len(new_line['text'][0]['content'])
                new_line['extra'] = extra
                new_data.append(new_line)
          
    def split_data(data, num_splits=12):
        """
        将数据分成几个部分。
        :param data: 要分割的数据。
        :param num_splits: 要创建的文件数。
        :param split_size: 前几个文件的每个文件的数据量。
        :return: 一个分割后的数据列表。
        """
        splits = []
        split_size = len(data) // num_splits
        for i in range(num_splits - 1):
            splits.append(data[i * split_size: (i + 1) * split_size])
        splits.append(data[(num_splits - 1) * split_size:])
        return splits             
    
    # 获取数据分割
    # data_splits = split_data(new_data)
    
    # for idx, split in enumerate(data_splits):
    #     with open(os.path.join(out_path, f"k12_GPT3_{idx+1}.jsonl"), "w", encoding="utf-8") as f_out:
    #         for line in split:
    #             f_out.write(json.dumps(line, ensure_ascii=False) + "\n")

    random.shuffle(new_data)
    save_jsonl(new_data[:100], os.path.join(out_path, "first_100.jsonl"))



if __name__ == "__main__":
    all_seed = 42
    # process("/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/my_orig", "/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/processed_data/my_half", "pretrain_Math")
    process_for_GPT("/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/processed_data/my_half", "/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/processed_data/gpt_my_half", "process_pretrain_Math")
    


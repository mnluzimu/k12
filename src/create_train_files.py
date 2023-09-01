import json
import os


def save_jsonl(datas, file_name):
    with open(file_name, "w", encoding="utf-8") as f:
        for data in datas:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_json(in_file):
    print(in_file)
    with open(in_file, "r", encoding="utf-8") as f:
        datas = [json.loads(line) for line in f]
    return datas

def generate_Llama_train(in_file, out_file):
    new_datas = []

    datas = load_json(in_file)

    for data in datas:
        system = {"role":"system", "content":[{"type":"text", "content":""}]}
        user = {"role":"user", "content":[{"type":"text", "content":"请回答以下问题并把答案放在\\boxed{}里：" + f"{data['question']}"}]}
        assistant = {"role":"assistant", "content":[{"type":"text", "content":data["gpt_solution"]}]}
        answer = data["answer"]
        question = data["question"]
        extra = {"id":data["id"], "answer":answer, "question":question}

        new_data = {"messages":[system, user, assistant], "extra":extra}
        new_datas.append(new_data)

    save_jsonl(new_datas, out_file)


if __name__ == "__main__":
    generate_Llama_train("/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/gpt_outs/processed/processed_out_10000_k12_GPT3.jsonl", "/mnt/cache/luzimu/qb_math_2023082801/qb_math_2023082801/train/k12_train_10000.jsonl")
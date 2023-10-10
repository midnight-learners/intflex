import openai
import os
import yaml
import json


def generate_question():
    """
    Generate similar question based on input question.
    """
    messages = []
    prompt_path = "./prompt/question_generation.json"
    with open(prompt_path, encoding="utf-8") as f:
        json_data = json.load(f)
        system_info = json_data["system"]
        message_info = json_data["message"]
    messages.append({"role": "system", "content": system_info})
    for item in message_info:
        if "user" in item:
            messages.append({"role": "user", "content": item["user"]})
        if "assistant" in item:
            messages.append({"role": "assistant", "content": item["assistant"]})

    messages.append({
        "role": "user",
        "content": "Please help me with generating a similar question including your detailed analysis, 4 choices and the correct choice with answer."
    })
    for item in messages:
        print(item)

    response_gpt = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
    )
    # token_used = response_gpt.usage.prompt_tokens
    # print(f'{token_used} prompt tokens used.')
    result = response_gpt.choices[0].message["content"]

    print(result)
    return result

    # formated_result = parse_result(result)
    # print(formated_result)
    # return formated_result, result
from typing import Generator
import openai
import os
from schema import ChatMessage
import yaml
import json

openai_config = yaml.safe_load(open("./config.yaml", "r"))['openai']
CHAT_MODEL_NAME = openai_config['chat_model']
EMBEDDING_MODEL_NAME = openai_config['embedding_model']


def openai_chat(
        messages: list[ChatMessage],
        *,
        model_name: str,
        temperature: float = 0.0,
        stream: bool = False,
        **kwargs
) -> str | Generator:
    # set API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # get response from GPT
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=list(map(
            lambda message: message.to_dict(),
            messages
        )),
        temperature=temperature,
        stream=stream,
        **kwargs
    )

    # Return a generator that
    # streams the output
    if stream:
        return response

    # Return the response content
    else:
        return response.choices[0].message.content


def get_text_embedding(text: str) -> list[float]:
    # set API key
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Embedding.create(
        model=EMBEDDING_MODEL_NAME,
        input=text
    )
    embedding = response["data"][0]["embedding"]

    return embedding


def get_openai_response(context_text: str, user_question: str) -> str:
    """
    Generate response based on input question and content text(from vector database).
    :param context_text: context text from vector database
    :param user_question: input question
    :return: LLM response
    """
    try:
        messages = []
        prompt_path = "./prompt/qa.json"
        with open(prompt_path, encoding="utf-8") as f:
            json_data = json.load(f)
            system = json_data["system"]
        messages.append({"role": "system", "content": system.format(
            context=context_text,
            question=user_question
        )})
    except Exception as e:
        print(f"Error: failed to load prompt file. {e}")
        return "Error: failed to load prompt file."

    try:
        response_gpt = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            max_tokens=512,
            top_p=1,
        )
        result = response_gpt.choices[0].message["content"]
    except Exception as e:
        print(f"Error: failed to generate response. {e}")
        return "Error: failed to generate response."

    return result


def generate_similar_question():
    """
    Generate similar question based on input question.
    """
    messages = []
    prompt_path = "./prompt/generate_similar_question.json"
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

    # selected_msg = random.sample(json_message, 3)  # randomly select 3 QA message
    # print(selected_msg)
    # for item in selected_msg:
    #     messages.append({"role": "user", "content": item["user"]})
    #     messages.append({"role": "assistant", "content": item["assistant"]})

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
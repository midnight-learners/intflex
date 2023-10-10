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
        prompt_path = "prompt/question_answering.json"
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


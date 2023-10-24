from typing import Generator

import openai
from prompt import qa_prompt


def get_text_embedding(text: str, embedding_model_name: str) -> list[float]:
    response = openai.Embedding.create(
        model=embedding_model_name,
        input=text
    )
    embedding = response["data"][0]["embedding"]

    return embedding


def get_openai_response(
        context_text: str,
        user_question: str,
        llm_model_name: str,
        is_stream: bool = False,
        chat_history: list = None
) -> str | Generator:
    """
    Generate response based on input question and content text(from vector database).

    :param context_text: context text from vector database
    :param user_question: input question
    :param llm_model_name: LLM model name
    :param is_stream: whether to use stream response
    :param chat_history: chat history

    :return: LLM response
    """
    if chat_history is None:
        messages = [
            {"role": "system", "content": qa_prompt["system"]},
            {"role": "user", "content": qa_prompt["user"].format(CONTENT=context_text, QUESTION=user_question)}
        ]
    else:
        messages = [
            {"role": "system", "content": qa_prompt["system"]},
            *chat_history,
            {"role": "user", "content": qa_prompt["user"].format(CONTENT=context_text, QUESTION=user_question)}
        ]

    response_gpt = openai.ChatCompletion.create(
        model=llm_model_name,
        messages=messages,
        temperature=0.9,
        max_tokens=512,
        top_p=1,
        stream=is_stream,
    )

    if not is_stream:
        total_tokens = response_gpt['usage']['total_tokens']  # 获取消耗的token数量
        print(f"\ttoken数量: {total_tokens}")
        return response_gpt.choices[0].message["content"]
    else:
        return response_gpt


def formatted_response(success: bool, msg: str, data=None) -> dict:
    if success:
        return {
            "code": 200,
            "msg": msg,
            "data": data
        }
    else:
        return {
            "code": 404,
            "msg": msg,
            "data": None
        }

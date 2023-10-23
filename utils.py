from typing import Any

import openai
import json
from prompt import qa_prompt


def get_text_embedding(text: str, embedding_model_name: str) -> list[float]:
    response = openai.Embedding.create(
        model=embedding_model_name,
        input=text
    )
    embedding = response["data"][0]["embedding"]

    return embedding


def get_openai_response(context_text: str, user_question: str, llm_model_name: str) -> str | None:
    """
    Generate response based on input question and content text(from vector database).

    :param context_text: context text from vector database
    :param user_question: input question
    :param llm_model_name: LLM model name
    :return: LLM response
    """
    messages = []
    for item in qa_prompt:
        if item["role"] == "system":
            messages.append(item)
        elif item["role"] == "user":
            messages.append({"role": "user", "content": item["content"].format(
                CONTENT=context_text,
                question=user_question
            )})

    try:
        response_gpt = openai.ChatCompletion.create(
            model=llm_model_name,
            messages=messages,
            temperature=0.9,
            max_tokens=512,
            top_p=1,
        )
        total_tokens = response_gpt['usage']['total_tokens']  # 获取消耗的token数量
        result = response_gpt.choices[0].message["content"]
    except Exception as e:
        print(f"Error: failed to generate response. {e}")
        return

    print(f"\ttoken数量: {total_tokens}")

    return result


def get_openai_stream_response(
        context_text: str,
        user_question: str,
        llm_model_name: str,
        chunk_size: int = 50
) -> str | None:
    """
    Generate response based on input question and content text(from vector database).

    :param context_text: context text from vector database
    :param user_question: input question
    :param llm_model_name: LLM model name
    :return: LLM response
    """
    messages = []
    for item in qa_prompt:
        if item["role"] == "system":
            messages.append(item)
        elif item["role"] == "user":
            messages.append({"role": "user", "content": item["content"].format(
                CONTENT=context_text,
                question=user_question
            )})

    response_gpt = openai.ChatCompletion.create(
        model=llm_model_name,
        messages=messages,
        temperature=0.9,
        max_tokens=512,
        top_p=1,
        stream=True
    )

    buffer = ""
    for streaming in response_gpt:
        chunk = streaming['choices'][0].get('delta', {}).get('content', '')
        buffer += chunk
        print(f"Buffer:{buffer}")
        if len(buffer) >= chunk_size:
            buffer = buffer.replace('\n', r'\n')
            yield 'data: %s\n\n' % buffer
            buffer = ""

    if buffer:
        buffer = buffer.replace('\n', r'\n')
        yield 'data: %s\n\n' % buffer


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

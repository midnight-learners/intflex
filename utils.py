import openai
import json


def get_text_embedding(text: str, embedding_model_name: str) -> list[float]:
    response = openai.Embedding.create(
        model=embedding_model_name,
        input=text
    )
    embedding = response["data"][0]["embedding"]

    return embedding


def get_openai_response(context_text: str, user_question: str, llm_model_name: str) -> str:
    """
    Generate response based on input question and content text(from vector database).

    :param context_text: context text from vector database
    :param user_question: input question
    :param llm_model_name: LLM model name
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
            model=llm_model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=512,
            top_p=1,
        )
        result = response_gpt.choices[0].message["content"]
    except Exception as e:
        print(f"Error: failed to generate response. {e}")
        return "Error: failed to generate response."

    return result


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


if __name__ == "__main__":
    messages = []
    prompt_path = "prompt/question_answering.json"
    with open(prompt_path, encoding="utf-8") as f:
        json_data = json.load(f)
        system = json_data["system"]
    messages.append({"role": "system", "content": system.format(
        context="context_text",
        question="user_question"
    )})
    print(messages)

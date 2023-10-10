from flask import Flask, request, jsonify
import json
from db import VecDBClient
from openai_utils import get_text_embedding, get_openai_response
from dotenv import load_dotenv
import openai
import os


app = Flask(__name__)
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = VecDBClient(
    url="http://localhost:6333",
    collection_name="inflex_document",
    embedding_dim=1536
)


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


@app.route('/qa', methods=['GET', 'POST'])
def qa_chat():
    """
    QA chat API.
    :return: Answer
    """

    """Get request parameters"""
    try:
        request_data = request.get_json()  # 获取 JSON 数据
        # 从 JSON 数据中提取参数
        user_id = int(request_data.get('userId'))  # 用户id
        user_type = str(request_data.get('userType'))  # 用户所属部门
        user_question = str(request_data.get('userQuestion'))  # 用户消息
        message_id = int(request_data.get('messageId'))  # 消息id
        print(f"/qa 接受参数：{user_id} {user_type} {user_question} {message_id}")
    except Exception as e:
        print(e)
        return formatted_response(success=False, msg="参数解析失败")

    """Retrieve similar vectors from database"""
    try:
        embedded_query = get_text_embedding(user_question)
        points = client.retrieve_similar_vectors(embedded_query, top_k=2)
        context_text = " ".join([point['page_content'] for point in points])
        # for point in points:
        #     print(f"point: {point['page_content']}")
        #     context_text += point['page_content']
    except Exception as e:
        print(f"Error: failed to retrieve similar vectors from database. {e}")
        return formatted_response(success=False, msg="向量数据库检索失败")

    """Generate response from LLM"""
    try:
        openai_response = get_openai_response(context_text, user_question)
    except Exception as e:
        print(f"Error: failed to generate response from LLM. {e}")
        return formatted_response(success=False, msg="语言模型生成回复失败")

    data = {"answer": openai_response}
    print(f"openai_response: {openai_response}")
    return formatted_response(success=True, msg="回复成功", data=data)


@app.route('/mark', methods=['GET', 'POST'])
def mark_answer():
    try:
        # 获取 JSON 数据
        request_data = request.get_json()
        # 从 JSON 数据中提取参数
        user_id = int(request_data.get('userId'))  # 用户id
        user_type = str(request_data.get('userType'))  # 用户所属部门
        question_id = int(request_data.get('questionId'))  # 用户消息
        user_answer = str(request_data.get('userAnswer'))  # 消息id
    except Exception as e:
        print(e)
        return formatted_response(success=False, msg="参数解析失败")

    data = {
        "score": 5.0,
        "reference": f'收到了{user_id}对于问题{question_id}的回答，用户回答内容是<{user_answer}>。我们暂时还没有评分，敬请期待！',
    }
    return formatted_response(success=True, msg="回复成功", data=data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=True)

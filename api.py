from flask import Flask, request
from dotenv import load_dotenv
import openai
import os
import yaml

from document_raw.db import VecDBClient
from utils import get_text_embedding, get_openai_response, formatted_response


# ------------------ Load API KEY ------------------
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ------------------ Vector DB Client ------------------
client = VecDBClient(
    url="http://localhost:6333",
    collection_name="inflex_document",
    embedding_dim=1536
)

# ------------------ Load config ------------------
openai_config = yaml.safe_load(open("config.yaml", "r"))['openai']
CHAT_MODEL_NAME = openai_config['chat_model']
EMBEDDING_MODEL_NAME = openai_config['embedding_model']

# ------------------ Flask ------------------
app = Flask(__name__)


@app.route('/dummy/qa', methods=['GET', 'POST'])
def dummy_qa_chat():
    try:
        # 获取 JSON 数据
        request_data = request.get_json()
        # 从 JSON 数据中提取参数
        user_id = int(request_data.get('userId'))  # 用户id
        user_type = str(request_data.get('userType'))  # 用户所属部门
        user_question = str(request_data.get('userQuestion'))  # 用户消息
        message_id = int(request_data.get('messageId'))  # 消息id

        print(f"/qa 接受参数：{user_id} {user_type} {user_question} {message_id}")
    except Exception as e:
        print(e)
        return formatted_response(success=False, msg="参数解析失败")

    data = {
        "answer": f'收到了{user_id}的问题，问题内容是<{user_question}>。我们暂时还没有回答，敬请期待！',
    }
    return formatted_response(success=True, msg="回复成功", data=data)


@app.route('/dummy/mark', methods=['GET', 'POST'])
def dummy_mark_answer():
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
        embedded_query = get_text_embedding(text=user_question, embedding_model_name=EMBEDDING_MODEL_NAME)
        points = client.retrieve_similar_vectors(embedded_query, top_k=2)
        context_text = " ".join([point['page_content'] for point in points])
    except Exception as e:
        print(f"Error: failed to retrieve similar vectors from database. {e}")
        return formatted_response(success=False, msg="向量数据库检索失败")

    """Generate response from LLM"""
    try:
        openai_response = get_openai_response(
            context_text=context_text,
            user_question=user_question,
            llm_model_name=CHAT_MODEL_NAME
        )
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

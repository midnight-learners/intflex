import time
from flask import Flask, request, Response
from dotenv import load_dotenv
import openai
import os
import yaml
import redis

from db import VecDBClient
from utils import get_text_embedding, get_openai_response, formatted_response, get_openai_stream_response

# ------------------ Load API KEY ------------------------------------
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# ------------------ Load config ------------------------------------
config = yaml.safe_load(open("config.yaml", "r"))

# ------------------ Vector DB Client ------------------------------------
qdrant_config = config['qdrant']
QDRANT_URL = qdrant_config["url"]
EMBEDDING_DIM = qdrant_config["embedding_dim"]
COLLECTION_NAME = qdrant_config["document_collection_name"]

vecdb_client = VecDBClient(url=QDRANT_URL, collection_name=COLLECTION_NAME, embedding_dim=EMBEDDING_DIM)

# ------------------ OpenAI config ------------------------------------
openai_config = config['openai']
CHAT_MODEL_NAME = openai_config['chat_model']
EMBEDDING_MODEL_NAME = openai_config['embedding_model']

# openai.proxy = "http://127.0.0.1:7890"

# ------------------ Redis ------------------------------------
redis_config = {
    "host": "localhost",
    "port": 6379,
    "password": ""
}


# ------------------ Flask ------------------------------------
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

    time1 = time.time()
    """Get request parameters"""
    try:
        request_data = request.get_json()  # 获取 JSON 数据
        user_id = str(request_data['userId'])  # 用户id
        # user_type = str(request_data['userType'])  # 用户所属部门
        user_question = str(request_data['userQuestion'])  # 用户消息
        message_id = str(request_data['messageId'])  # 消息id
    except Exception as e:
        print(f"参数解析失败. Exception: {e}")
        return formatted_response(success=False, msg="参数解析失败")

    time2 = time.time()
    print(f"1.参数解析耗时: {time2 - time1}")

    """Retrieve similar vectors from database"""
    try:
        embedded_query = get_text_embedding(text=user_question, embedding_model_name=EMBEDDING_MODEL_NAME)
        points = vecdb_client.retrieve_similar_vectors(embedded_query, top_k=1)
        context_text = " ".join([point['page_content'] for point in points])
    except Exception as e:
        print(f"向量数据库检索失败. Exception: {e}")
        return formatted_response(success=False, msg="向量数据库检索失败")

    ########################################
    # 向量数据库检索超时处理
    ########################################

    time3 = time.time()
    print(f"2.向量数据库检索耗时: {time3 - time2}")
    print(f"\t向量数据库中检索到的文本长度: {len(context_text)}")

    """Generate response from LLM"""
    try:
        openai_response = get_openai_response(
            context_text=context_text,
            user_question=user_question,
            llm_model_name=CHAT_MODEL_NAME
        )
    except Exception as e:
        print(f"LLM接口请求失败. Exception: {e}")
        return formatted_response(success=False, msg="语言模型生成回复失败")

    time4 = time.time()
    print(f"3.语言模型生成回复耗时: {time4 - time3}")
    data = {"answer": openai_response}
    print(f"用户:{user_id}\n问题:{user_question}\n回答:{openai_response}")

    """Redis存储聊天记录"""
    redis_client = redis.StrictRedis(
        host=redis_config["host"],
        port=redis_config["port"],
        db=0
    )


    return formatted_response(success=True, msg="回复成功", data=data)


@app.route('/qa/stream', methods=['GET', 'POST'])
def qa_chat_stream():
    """
    QA chat API.
    :return: Answer
    """

    time1 = time.time()
    """Get request parameters"""
    try:
        request_data = request.get_json()  # 获取 JSON 数据
        user_id = str(request_data['userId'])  # 用户id
        user_question = str(request_data['userQuestion'])  # 用户消息
        message_id = str(request_data['messageId'])  # 消息id
    except Exception as e:
        print(f"参数解析失败. Exception: {e}")
        return formatted_response(success=False, msg="参数解析失败")

    time2 = time.time()
    print(f"1.参数解析耗时: {time2 - time1}")

    """Retrieve similar vectors from database"""
    try:
        embedded_query = get_text_embedding(text=user_question, embedding_model_name=EMBEDDING_MODEL_NAME)
        points = vecdb_client.retrieve_similar_vectors(embedded_query, top_k=1)
        context_text = " ".join([point['page_content'] for point in points])
    except Exception as e:
        print(f"向量数据库检索失败. Exception: {e}")
        return formatted_response(success=False, msg="向量数据库检索失败")

    ########################################
    # 向量数据库检索超时处理
    ########################################

    time3 = time.time()
    print(f"2.向量数据库检索耗时: {time3 - time2}")
    print(f"\t向量数据库中检索到的文本长度: {len(context_text)}")

    """Generate response from LLM"""
    try:
        return Response(
            get_openai_stream_response(
                context_text=context_text,
                user_question=user_question,
                llm_model_name=CHAT_MODEL_NAME,
                chunk_size=70
            ),
            mimetype='text/event-stream'
        )
    except Exception as e:
        print(f"LLM接口请求失败. Exception: {e}")
        return formatted_response(success=False, msg="语言模型生成回复失败")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7001, debug=True)

from flask import Flask, request, jsonify
import json

app = Flask(__name__)


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
    app.run(host='0.0.0.0', port=7000, debug=True)

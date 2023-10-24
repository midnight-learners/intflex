from typing import List, Dict

from redis import StrictRedis


class ChatBotRedisClient(StrictRedis):
    def __init__(self, host, port, password, db):
        super().__init__(
            host=host,
            port=port,
            password=password,
            db=db,
        )
        self.key_chat_history = "qa:{}"

    def get_chat_history(self, user_id: str) -> List[Dict]:
        key = self.key_chat_history.format(user_id)
        chat_history = self.lrange(key, 0, -1)[::-1]  # 左侧入队（最新），倒序后时间顺序为最旧到最新
        chat_history_decoded = [item.decode("utf-8") for item in chat_history]

        if not chat_history_decoded:
            return []

        openai_messages = []
        for idx, message in enumerate(chat_history_decoded):
            role = "user" if idx % 2 == 1 else "assistant"
            openai_messages.append({"role": role, "content": message})

        return openai_messages


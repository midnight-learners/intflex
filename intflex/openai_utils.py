from typing import Generator
import openai
import os
from .schema import ChatMessage

# CHAT_MODEL_NAME = "gpt-3.5-turbo-16k"
CHAT_MODEL_NAME = "gpt-4"
EMBEDDING_MODEL_NAME = "text-embedding-ada-002"

# We will use OpenAI's embedding model
EMBEDDING_DIM = 1536

def openai_chat(
        messages: list[ChatMessage],
        *,
        model_name: str = CHAT_MODEL_NAME,
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

def openai_encode_text(text: str) -> list[float]:
    
    # set API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    response = openai.Embedding.create(
        model=EMBEDDING_MODEL_NAME,
        input=text
    )
    
    embedding = response["data"][0]["embedding"]
    
    return embedding

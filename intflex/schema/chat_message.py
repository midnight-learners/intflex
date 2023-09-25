from typing import Self
from enum import Enum

class ChatRole(Enum):
    
    System = "system"
    User = "user"
    Assistant = "assistant"
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_str(cls, role: str) -> Self:
        
        match role:
            case "system":
                return ChatRole.System
            case "user":
                return ChatRole.User
            case "assistant":
                return ChatRole.Assistant
            case _:
                raise ValueError("Unknown role name")

class ChatMessage:
    
    def __init__(self, *, role: ChatRole, content: str) -> None:
        
        self._role = role
        self._content = content
    
    def __str__(self) -> str:
        
        return "[{role}] {content}".format(
            role=self._role,
            content=self._content
        )
        
    def __repr__(self) -> str:
        return str(self)

    @property
    def role(self) -> ChatRole:
        return self._role
    
    @property
    def content(self) -> str:
        return self._content
    
    def to_dict(self) -> dict:
        
        return {
            "role": str(self.role),
            "content": self.content
        }
    
class SystemMessage(ChatMessage):
    
    def __init__(self, content: str) -> None:
        super().__init__(role=ChatRole.System, content=content)
    
class UserMessage(ChatMessage):
    
    def __init__(self, content: str) -> None:
        super().__init__(role=ChatRole.User, content=content)

class AssistantMessage(ChatMessage):
    
    def __init__(self, content: str) -> None:
        super().__init__(role=ChatRole.Assistant, content=content)

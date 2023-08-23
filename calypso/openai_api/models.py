import enum
from typing import Literal

from pydantic import BaseModel


# ==== completions ====
class CompletionLogProbs(BaseModel):
    tokens: list[str]
    token_logprobs: list[float]
    top_logprobs: list[dict[str, float]]
    text_offset: list[int]


class CompletionChoice(BaseModel):
    text: str
    index: int
    logprobs: CompletionLogProbs | None
    finish_reason: str | None


class CompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Completion(BaseModel):
    id: str
    object: Literal["text_completion"]
    created: int
    model: str
    choices: list[CompletionChoice]
    usage: CompletionUsage

    @property
    def text(self):
        """The text of the top completion."""
        return self.choices[0].text


# ==== chat ====
class ChatRole(enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: ChatRole
    content: str

    class Config:
        use_enum_values = True

    @classmethod
    def system(cls, content):
        return cls(role=ChatRole.SYSTEM, content=content)

    @classmethod
    def user(cls, content):
        return cls(role=ChatRole.USER, content=content)

    @classmethod
    def assistant(cls, content):
        return cls(role=ChatRole.ASSISTANT, content=content)


class ChatCompletionChoice(BaseModel):
    message: ChatMessage
    index: int
    finish_reason: str | None


class ChatCompletion(BaseModel):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    usage: CompletionUsage
    choices: list[ChatCompletionChoice]

    @property
    def message(self):
        return self.choices[0].message

    @property
    def text(self):
        """The text of the most recent chat completion."""
        return self.message.content

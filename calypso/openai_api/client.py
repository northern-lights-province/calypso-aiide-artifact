from typing import overload

import aiohttp
import pydantic

from calypso.utils.httpclient import BaseClient
from .models import ChatCompletion, ChatMessage, Completion


class OpenAIClient(BaseClient):
    SERVICE_BASE = "https://api.openai.com/v1"

    def __init__(self, http: aiohttp.ClientSession, api_key: str):
        super().__init__(http)
        self.api_key = api_key

    async def request(self, method: str, route: str, headers=None, **kwargs):
        if headers is None:
            headers = {}
        headers["Authorization"] = f"Bearer {self.api_key}"
        return await super().request(method, route, headers=headers, **kwargs)

    # ==== completions ====
    @overload
    async def create_completion(
        self,
        model: str,
        prompt: str = "<|endoftext|>",
        suffix: str = None,
        max_tokens: int = 16,
        temperature: float = 1.0,
        top_p: float = 1.0,
        n: int = 1,
        logprobs: int = None,
        echo: bool = False,
        stop: str | list[str] = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        best_of: int = 1,
        logit_bias: dict = None,
        user: str = None,
    ) -> Completion:
        ...

    async def create_completion(self, model: str, **kwargs) -> Completion:
        data = await self.post("/completions", json={"model": model, **kwargs})
        try:
            return Completion.parse_obj(data)
        except pydantic.ValidationError:
            self.logger.exception(f"Failed to deserialize OpenAI response: {data}")

    # ==== chat ====
    @overload
    async def create_chat_completion(
        self,
        model: str,
        messages: list[ChatMessage],
        temperature: float = 1.0,
        top_p: float = 1.0,
        n: int = 1,
        stop: str | list[str] = None,
        max_tokens: int = None,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
        logit_bias: dict = None,
        user: str = None,
    ) -> ChatCompletion:
        ...

    async def create_chat_completion(self, model: str, messages: list[ChatMessage], **kwargs) -> ChatCompletion:
        data = await self.post(
            "/chat/completions", json={"model": model, "messages": [cm.dict() for cm in messages], **kwargs}
        )
        try:
            return ChatCompletion.parse_obj(data)
        except pydantic.ValidationError:
            self.logger.exception(f"Failed to deserialize OpenAI response: {data}")

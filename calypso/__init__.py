import aiohttp
from disnake.ext import commands

from . import config
from .openai_api import OpenAIClient


class Calypso(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.openai = OpenAIClient(aiohttp.ClientSession(loop=self.loop), config.OPENAI_API_KEY)
        self.enc_chatterboxes = dict()

    async def close(self):
        await self.openai.close()
        await super().close()

import disnake
from disnake.ext import commands

from calypso import Calypso
from calypso.openai_api.chatterbox import Chatterbox
from calypso.openai_api.models import ChatMessage
from calypso.utils.functions import send_chunked
from calypso.utils.prompts import chat_prompt


class AIUtils(commands.Cog):
    """Various AI utilities for players and DMs."""

    def __init__(self, bot):
        self.bot: Calypso = bot
        self.chats: dict[int, Chatterbox] = {}

    @commands.slash_command(name="ai", description="AI utilities")
    async def ai(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.channel.id not in self.chats:
            return
        if message.author.bot or message.is_system():
            return

        # do a chat round w/ the chatterbox
        chatter = self.chats[message.channel.id]
        prompt = chat_prompt(message)
        async with message.channel.typing():
            response = await chatter.chat_round(prompt, user=str(message.author.id))
        await send_chunked(message.channel, response, allowed_mentions=disnake.AllowedMentions.none())

        # if this is the first message in the conversation, rename the thread
        if len(chatter.chat_history) <= 2 and isinstance(message.channel, disnake.Thread):
            completion = await self.bot.openai.create_chat_completion(
                "gpt-3.5-turbo",
                [
                    ChatMessage.user("Here is the start of a conversation:"),
                    *chatter.chat_history,
                    ChatMessage.user(
                        "Come up with a punchy title for this conversation.\n\nReply with your answer only and be"
                        " specific."
                    ),
                ],
                user=str(message.author.id),
            )
            thread_title = completion.text.strip(' "')
            await message.channel.edit(name=thread_title)

    @commands.Cog.listener()
    async def on_thread_update(self, _, after: disnake.Thread):
        if after.archived and after.id in self.chats:
            del self.chats[after.id]

    @ai.sub_command(name="chat", description="Chat with Calypso (experimental).")
    async def ai_chat(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        thread_title = "Chat with Calypso"

        # create thread, init chatter
        await inter.send("Making a thread now!")
        thread = await inter.channel.create_thread(
            name=thread_title, type=disnake.ChannelType.public_thread, auto_archive_duration=1440
        )
        chatter = Chatterbox(
            client=self.bot.openai,
            system_prompt=(
                "You are a knowledgeable D&D player. Answer as concisely as possible.\nYou are acting as a friendly fey"
                " being from the Feywild with a mischievous streak. Always reply as this character."
            ),
            always_include_messages=[
                ChatMessage.user(
                    "I want you to act as Calypso, a friendly fey being from the Feywild with a mischievous"
                    " streak.\nEach reply should consist of just Calypso's response, without quotation marks.\nYou"
                    " should stay in character no matter what I say."
                )
            ],
            temperature=1,
            top_p=0.95,
            frequency_penalty=0.3,
        )
        await chatter.load_tokenizer()
        self.chats[thread.id] = chatter
        await thread.add_user(inter.author)


def setup(bot):
    bot.add_cog(AIUtils(bot))

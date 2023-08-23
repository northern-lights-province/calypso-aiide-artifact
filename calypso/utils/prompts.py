import datetime

import disnake


def chat_prompt(message: disnake.Message) -> str:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    prompt = f"{message.author.display_name} | {timestamp}\n{message.clean_content}"
    return prompt

import asyncio
import re

import disnake

__all__ = (
    "chunk_text",
    "smart_trim",
    "multiline_modal",
    "camel_to_title",
    "natural_join",
    "send_chunked",
)


def chunk_text(text, max_chunk_size=1024, chunk_on=("\n\n", "\n", ". ", ", ", " "), chunker_i=0):
    """
    Recursively chunks *text* into a list of str, with each element no longer than *max_chunk_size*.
    Prefers splitting on the elements of *chunk_on*, in order.
    """

    if len(text) <= max_chunk_size:  # the chunk is small enough
        return [text]
    if chunker_i >= len(chunk_on):  # we have no more preferred chunk_on characters
        # optimization: instead of merging a thousand characters, just use list slicing
        return [text[:max_chunk_size], *chunk_text(text[max_chunk_size:], max_chunk_size, chunk_on, chunker_i + 1)]

    # split on the current character
    chunks = []
    split_char = chunk_on[chunker_i]
    for chunk in text.split(split_char):
        chunk = f"{chunk}{split_char}"
        if len(chunk) > max_chunk_size:  # this chunk needs to be split more, recurse
            chunks.extend(chunk_text(chunk, max_chunk_size, chunk_on, chunker_i + 1))
        elif chunks and len(chunk) + len(chunks[-1]) <= max_chunk_size:  # this chunk can be merged
            chunks[-1] += chunk
        else:
            chunks.append(chunk)

    # if the last chunk is just the split_char, yeet it
    if chunks[-1] == split_char:
        chunks.pop()

    # remove extra split_char from last chunk
    chunks[-1] = chunks[-1][: -len(split_char)]
    return chunks


def smart_trim(text, max_len=1024, dots="..."):
    """Uses chunk_text to return a trimmed str."""
    chunks = chunk_text(text, max_len - len(dots))
    out = chunks[0].strip()
    if len(chunks) > 1:
        return f"{chunks[0]}{dots}"
    return out


async def multiline_modal(
    inter: disnake.CommandInteraction, title: str, label: str, max_length: int = None, timeout: int = None
) -> tuple[disnake.ModalInteraction, str]:
    """
    Reply to an interaction with a modal to get some multiline text input because Discord doesn't have this in normal
    parameters for some godforsaken reason

    :param inter: The interaction to reply with a modal to
    :param title: The title for the modal
    :param label: The label for the text field
    :param max_length: The max length of the input
    :param timeout: The max time to wait
    :return: A tuple for the followup interaction and the input
    :raises asyncio.TimeoutError: on timeout
    """
    # Discord pls add multiline text inputs
    # it's been years
    # :(
    await inter.response.send_modal(
        title=title,
        custom_id=str(inter.id),
        components=disnake.ui.TextInput(
            label=label,
            custom_id="value",
            style=disnake.TextInputStyle.paragraph,
            max_length=max_length,
        ),
    )
    try:
        modal_inter: disnake.ModalInteraction = await inter.bot.wait_for(
            "modal_submit", check=lambda mi: mi.custom_id == str(inter.id), timeout=timeout
        )
    except asyncio.TimeoutError:
        raise
    ability_text = modal_inter.text_values["value"]
    return modal_inter, ability_text


def camel_to_title(string):
    return re.sub(r"((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))", r" \1", string).title()


def natural_join(things, between: str):
    if len(things) < 3:
        return f" {between} ".join(things)
    first_part = ", ".join(things[:-1])
    return f"{first_part}, {between} {things[-1]}"


async def send_chunked(dest, msg, **kwargs):
    for chunk in chunk_text(msg, max_chunk_size=2000):
        await dest.send(chunk, **kwargs)

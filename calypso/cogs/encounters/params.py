import disnake
from disnake.ext import commands
from rapidfuzz import fuzz, process

from calypso import db, models
from . import queries


async def biome_autocomplete(_: disnake.ApplicationCommandInteraction, arg: str, key=lambda b: b.name):
    async with db.async_session() as session:
        available_biomes = await queries.get_all_encounter_biomes(session)

    if not arg:
        biome_results = available_biomes[:5]
    else:
        names = [key(d) for d in available_biomes]
        results = process.extract(arg, names, scorer=fuzz.partial_ratio)
        biome_results = [available_biomes[idx] for name, score, idx in results]
    return {b.name: str(b.id) for b in biome_results}


async def biome_converter(_: disnake.ApplicationCommandInteraction, arg: str) -> models.EncounterBiome:
    try:
        biome_id = int(arg)
    except ValueError as e:
        raise ValueError("Invalid biome selection") from e
    async with db.async_session() as session:
        biome = await queries.get_encounter_biome(session, biome_id)
    return biome


def biome_param(default=..., **kwargs) -> commands.Param:
    return commands.Param(default, autocomplete=biome_autocomplete, converter=biome_converter, **kwargs)

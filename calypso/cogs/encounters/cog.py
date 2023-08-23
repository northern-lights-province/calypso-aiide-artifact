import asyncio
import re

import d20
import disnake
from disnake.ext import commands

from calypso import Calypso, db, models
from calypso.utils.functions import multiline_modal, send_chunked
from . import ai, matcha, queries
from .ai import EncounterHelperController
from .params import biome_param


class Encounters(commands.Cog):
    def __init__(self, bot: Calypso):
        self.bot = bot

    # ==== listeners ====
    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        await ai.on_message(self.bot, message)

    @commands.Cog.listener()
    async def on_thread_update(self, _, after: disnake.Thread):
        await ai.on_thread_update(self.bot, after)

    # ==== commands ====
    @commands.slash_command(description="Rolls a random encounter.")
    async def enc(
        self,
        inter: disnake.ApplicationCommandInteraction,
        encounter: str = commands.Param(desc='The text of the encounter (e.g. "{1d4} Kobold").'),
        biome=biome_param(desc="The biome to roll an encounter in."),
    ):
        # render the encounter text
        encounter_text = encounter

        # monster links
        referenced_monsters = matcha.extract_monsters(encounter_text)
        for mon, pos in matcha.list_to_pairs(referenced_monsters):
            encounter_text = encounter_text[:pos] + f"[{mon.name}]({mon.url})" + encounter_text[pos + len(mon.name) :]
        # rolls
        encounter_text = re.sub(r"\{(.+?)}", lambda match: d20.roll(match.group(1)).result, encounter_text)

        # save the encounter to db
        async with db.async_session() as session:
            rolled_encounter = models.RolledEncounter(
                channel_id=inter.channel_id,
                author_id=inter.author.id,
                rendered_text=encounter_text,
                monster_ids=",".join(map(str, (m.id for m, _ in referenced_monsters))),
                biome_name=biome.name,
                biome_text=biome.desc,
            )
            session.add(rolled_encounter)
            await session.commit()

        # send the message, with options for AI assist
        embed = disnake.Embed(
            title="Rolling for random encounter...",
            description=f"**{biome.name}**\nEncounter: {encounter_text}",
            colour=disnake.Colour.random(),
        )

        # set up AI helper
        ai_helper = EncounterHelperController(
            inter.author, encounter=rolled_encounter, monsters=[m for m, _ in referenced_monsters], embed=embed
        )

        # and send message; message control is deferred to the ai controller here
        await inter.send(embed=embed, ephemeral=True, view=ai_helper)

    # ==== admin ====
    @commands.slash_command(name="encadmin", description="Create/remove biomes")
    @commands.default_member_permissions(manage_guild=True)
    async def encadmin(self, inter: disnake.ApplicationCommandInteraction):
        pass

    # ---- channel ----
    @encadmin.sub_command_group(name="biome")
    async def encadmin_channel(self, inter: disnake.ApplicationCommandInteraction):
        pass

    @encadmin_channel.sub_command(name="setup", description="Set up an encounter biome.")
    async def encadmin_channel_setup(
        self,
        inter: disnake.ApplicationCommandInteraction,
        name: str = commands.Param(desc="The name of the biome"),
    ):
        async with db.async_session() as session:
            # get the channel desc
            try:
                inter, desc = await multiline_modal(
                    inter, title=f"{name}: Biome Description", label="Description", max_length=1500, timeout=600
                )
            except asyncio.TimeoutError:
                return

            # set up obj
            new_channel = models.EncounterBiome(name=name, desc=desc)

            # record to db
            session.add(new_channel)
            await session.commit()
        await inter.send(f"OK, created {name}.")

    @encadmin_channel.sub_command(name="list", description="List the encounter biomes.")
    async def encadmin_channel_list(self, inter: disnake.ApplicationCommandInteraction):
        async with db.async_session() as session:
            biomes = await queries.get_all_encounter_biomes(session)
        if not biomes:
            await inter.send("You have no encounter biomes. Make some with `/encadmin biome setup`.")
            return
        await send_chunked(inter, "\n\n".join(f"**{biome.name}**\n{biome.desc}" for biome in biomes))

    @encadmin_channel.sub_command(name="delete", description="Delete a biome")
    async def encadmin_channel_delete(
        self,
        inter: disnake.ApplicationCommandInteraction,
        biome=biome_param(desc="The biome to delete"),
    ):
        async with db.async_session() as session:
            #  delete from db
            await queries.delete_encounter_biome(session, biome.id)
            await session.commit()
        await inter.send(f"Deleted {biome.name}.")

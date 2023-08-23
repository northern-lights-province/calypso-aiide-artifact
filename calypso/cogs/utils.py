import datetime
from math import floor, isfinite

import disnake
from disnake.ext import commands


class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        """Returns the bot's latency to the Discord API."""
        now = datetime.datetime.utcnow()
        await inter.response.defer()  # this makes an API call, we use the RTT of that call as the latency
        delta = datetime.datetime.utcnow() - now
        httping = floor(delta.total_seconds() * 1000)
        wsping = floor(self.bot.latency * 1000) if isfinite(self.bot.latency) else "Unknown"
        await inter.followup.send(f"Pong.\nHTTP Ping = {httping} ms.\nWS Ping = {wsping} ms.")


def setup(bot):
    bot.add_cog(Utils(bot))

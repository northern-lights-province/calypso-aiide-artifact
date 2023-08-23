import logging
import traceback

import disnake
from disnake.ext import commands

from calypso import Calypso, config, db, errors, gamedata

COGS = (
    "calypso.cogs.encounters",
    "calypso.cogs.ai",
    "calypso.cogs.utils",
)

logging.basicConfig(level=logging.INFO)

intents = disnake.Intents.all()
bot = Calypso(
    command_prefix=commands.when_mentioned,
    intents=intents,
    sync_commands_debug=True,
)


# === listeners ===
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")


@bot.event
async def on_slash_command_error(inter, error):
    if isinstance(error, commands.CommandInvokeError):
        error = error.original

    await inter.send(f"Error: {error!s}", ephemeral=True)

    if not isinstance(error, errors.CalypsoError):
        traceback.print_exception(error)


for cog in COGS:
    bot.load_extension(cog)

if __name__ == "__main__":
    gamedata.GamedataRepository.reload()
    bot.loop.create_task(db.init_db())
    bot.run(config.TOKEN)

from .cog import Encounters


def setup(bot):
    weather = Encounters(bot)
    bot.add_cog(weather)

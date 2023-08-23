"""
Typing helpers.
"""
from typing import TYPE_CHECKING

import disnake

if TYPE_CHECKING:
    from calypso import Calypso


class Interaction(disnake.Interaction):
    bot: "Calypso"

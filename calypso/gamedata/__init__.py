import logging

import pydantic

from calypso import utils
from .monster import Monster, MonsterDescription

DATA_DIR = utils.REPO_ROOT / "data"

log = logging.getLogger(__name__)


class GamedataRepository:
    """Singleton class to hold all the gamedata"""

    monsters: list[Monster]
    monster_descriptions: list[MonsterDescription]
    _monster_desc_by_id: dict[int, MonsterDescription]

    @classmethod
    def reload(cls, data_path=DATA_DIR):
        log.info(f"Reloading gamedata...")
        cls.monsters = pydantic.parse_file_as(list[Monster], data_path / "monsters.json")
        cls.monster_descriptions = pydantic.parse_file_as(
            list[MonsterDescription], data_path / "monster_descriptions.json"
        )
        cls._monster_desc_by_id = {m.monster_id: m for m in cls.monster_descriptions}
        log.info(f"Done! Loaded:\nmonsters: {len(cls.monsters)}\nmondescs: {len(cls.monster_descriptions)}")

    @classmethod
    def get_desc_for_monster(cls, mon: Monster) -> MonsterDescription:
        return cls._monster_desc_by_id.get(mon.id)

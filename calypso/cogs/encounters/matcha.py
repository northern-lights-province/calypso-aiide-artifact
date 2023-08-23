"""
Helpers to extract mentioned monsters from rolled encounters and link them to gamedata entities.
🍵
"""
import logging
from collections import namedtuple

from calypso import gamedata

log = logging.getLogger(__name__)

MonsterMatch = namedtuple("MonsterMatch", "monster positions")


def extract_monsters(text) -> list[MonsterMatch]:
    """
    Given a string possibly containing monster names, returns a list of pairs (monster, positions)
    where `positions` are the indexes of `text` where the monster name was found.
    Sorted by length of monster name, descending.
    """
    log.debug(f"Finding monsters for encounter {text!r}")

    matches = []

    potential_matches = find_potential_matches(text)
    if not potential_matches:
        log.info(f"No matches found for {text!r}")
    while potential_matches:
        best_match = potential_matches.pop(0)
        matches.append(best_match)
        monster, poses = best_match
        log.debug(f"\tMatch: {monster.name!r}")

        # replace matches with empty space to keep pos
        monster_name_len = len(monster.name)
        for pos in poses:
            text = text[:pos] + " " * monster_name_len + text[pos + monster_name_len :]

        log.debug(f"\tNext iteration: {text!r}")
        # remove the matches that no longer match
        for match in reversed(potential_matches):
            for pos in reversed(match.positions):
                if not match.monster.name_re.match(text, pos):
                    match.positions.remove(pos)
            if len(match.positions) == 0:
                potential_matches.remove(match)

    return matches


def list_to_pairs(matchlist: list[MonsterMatch]) -> list[tuple[gamedata.Monster, int]]:
    """
    Given a list of monster matches, returns a list of (monster, position) pairs, sorted by position descending.
    """
    out = [(mon, pos) for (mon, poses) in matchlist for pos in poses]
    return sorted(out, key=lambda pair: pair[1], reverse=True)


def find_potential_matches(query: str) -> list[MonsterMatch]:
    """
    Find all potential monsters mentioned in `query`
    Returns a list of MonsterMatches sorted by monster name length descending
    """
    matches = []
    for monster in gamedata.GamedataRepository.monsters:
        if monster.is_legacy:
            continue
        mon_matches = []
        for mon_match in monster.name_re.finditer(query):
            mon_matches.append(mon_match.start())
        if mon_matches:
            matches.append(MonsterMatch(monster, mon_matches))
    return sorted(matches, key=lambda pair: len(pair[0].name), reverse=True)

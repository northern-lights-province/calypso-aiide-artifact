from sqlalchemy import delete, select

from calypso import models


async def get_encounter_biome(session, biome_id: int) -> models.EncounterBiome | None:
    stmt = select(models.EncounterBiome).where(models.EncounterBiome.id == biome_id)
    result = await session.execute(stmt)
    return result.scalar()


async def get_all_encounter_biomes(session) -> list[models.EncounterBiome]:
    stmt = select(models.EncounterBiome)
    result = await session.execute(stmt)
    return result.scalars().all()


async def delete_encounter_biome(session, biome_id: int):
    await session.execute(delete(models.EncounterBiome).where(models.EncounterBiome.id == biome_id))


# ==== ai ====
async def get_summary_by_id(session, summary_id: int) -> models.EncounterAISummary:
    stmt = select(models.EncounterAISummary).where(models.EncounterAISummary.id == summary_id)
    result = await session.execute(stmt)
    summary = result.scalar()
    if summary is None:
        raise ValueError("That summary does not exist")
    return summary

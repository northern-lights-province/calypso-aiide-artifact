import datetime
import re

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .db import Base
from .openai_api.models import ChatRole


class EncounterBiome(Base):
    __tablename__ = "enc_biomes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    desc = Column(String, nullable=False)


class RolledEncounter(Base):
    __tablename__ = "enc_encounter_log"

    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, nullable=False)
    author_id = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    rendered_text = Column(String, nullable=False)
    monster_ids = Column(String, nullable=True)  # comma-separated list of ids (ints)
    biome_name = Column(String, nullable=False)
    biome_text = Column(String, nullable=False)

    @property
    def rendered_text_nolinks(self):
        return re.sub(r"\[(.+?)]\(http.+?\)", r"\1", self.rendered_text)


class EncounterAISummary(Base):
    __tablename__ = "enc_summaries"

    id = Column(Integer, primary_key=True)
    encounter_id = Column(Integer, ForeignKey("enc_encounter_log.id", ondelete="CASCADE"))
    prompt = Column(String, nullable=False)
    generation = Column(String, nullable=False)
    hyperparams = Column(String, nullable=False)
    feedback = Column(Integer, nullable=True)
    prompt_version = Column(Integer, nullable=False)

    encounter = relationship("RolledEncounter")


class EncounterAISummaryFeedback(Base):
    __tablename__ = "enc_summaries_feedback"

    id = Column(Integer, primary_key=True)
    summary_id = Column(Integer, ForeignKey("enc_summaries.id", ondelete="CASCADE"))
    feedback = Column(String, nullable=False)
    edit = Column(String, nullable=False)

    summary = relationship("EncounterAISummary")


class EncounterAIBrainstormSession(Base):
    __tablename__ = "enc_brainstorms"

    id = Column(Integer, primary_key=True)
    encounter_id = Column(Integer, ForeignKey("enc_encounter_log.id", ondelete="CASCADE"))
    prompt = Column(String, nullable=False)
    hyperparams = Column(String, nullable=False)
    thread_id = Column(BigInteger, nullable=False)

    encounter = relationship("RolledEncounter")


class EncounterAIBrainstormMessage(Base):
    __tablename__ = "enc_brainstorm_messages"

    id = Column(Integer, primary_key=True)
    brainstorm_id = Column(Integer, ForeignKey("enc_brainstorms.id", ondelete="CASCADE"))
    role = Column(Enum(ChatRole), nullable=False)
    content = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    brainstorm = relationship("EncounterAIBrainstormSession")

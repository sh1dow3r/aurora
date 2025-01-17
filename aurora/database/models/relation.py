from __future__ import annotations

import sqlalchemy as sql

from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship, backref

from aurora.database import Base

if TYPE_CHECKING:
    from aurora.database.models import Sample  # noqa: F401


class Relation(Base):
    __tablename__ = "relation"

    id = sql.Column(sql.Integer, primary_key=True)
    parent_id = sql.Column(
        sql.Integer, sql.ForeignKey("sample.id"), nullable=False, index=True
    )
    child_id = sql.Column(
        sql.Integer, sql.ForeignKey("sample.id"), nullable=False, index=True
    )
    relation_type = sql.Column(sql.String, nullable=False)
    confidence = sql.Column(sql.Float, nullable=False)

    sql.UniqueConstraint("parent_id", "child_id", "relation_type")

    parent = relationship(
        "Sample", foreign_keys=[parent_id], backref=backref("related_children")
    )
    child = relationship(
        "Sample", foreign_keys=[child_id], backref=backref("related_parents")
    )

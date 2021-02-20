from __future__ import annotations

import enum
import datasketch
import sqlalchemy as sql

from sqlalchemy.orm import relationship

from aurora.database import Base


class MinhashType(str, enum.Enum):
    ASCII_STRINGS = "ASCII_STRINGS"
    WIDE_STRINGS = "WIDE_STRINGS"


class Minhash(Base):
    __tablename__ = "minhash"

    id = sql.Column(sql.Integer, primary_key=True)
    sample_id = sql.Column(sql.Integer, sql.ForeignKey("sample.id"))
    seed = sql.Column(sql.BIGINT, nullable=False)
    hash_values = sql.Column(sql.ARRAY(sql.BIGINT()), nullable=False)
    minhash_type = sql.Column(sql.Enum(MinhashType), nullable=False, index=True)

    sql.UniqueConstraint("sample_id", "analysis_type", name="unique_analysis_sample")

    sample = relationship("Sample", back_populates="minhashes")

    def compare(self, other: Minhash) -> float:
        if self.minhash_type != other.minhash_type:
            return 0.0

        self_minhash = datasketch.LeanMinHash(
            seed=self.seed, hashvalues=self.hash_values
        )
        other_minhash = datasketch.LeanMinHash(
            seed=other.seed, hashvalues=other.hash_values
        )

        return self_minhash.jaccard(other_minhash)

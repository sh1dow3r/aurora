from __future__ import annotations

import sqlalchemy as sql

from fastapi import UploadFile
from typing import TYPE_CHECKING
from sqlalchemy.orm import relationship

from aurora.core import utils
from aurora.database import Base

if TYPE_CHECKING:
    from aurora.database.models import Sample  # noqa: F401


class SsDeep(Base):
    __tablename__ = "ssdeep"

    id = sql.Column(sql.Integer, primary_key=True)
    sample_id = sql.Column(sql.Integer, sql.ForeignKey("sample.id"), unique=True)
    chunksize = sql.Column(sql.Integer, nullable=False)
    ssdeep = sql.Column(sql.String, nullable=False)

    sample = relationship("Sample")

    @staticmethod
    def from_uploadfile(file: UploadFile) -> SsDeep:
        ssdeep_hash = utils.get_ssdeep(file.file)

        chunksize = int(ssdeep_hash.split(":")[0])

        ssdeep = SsDeep(chunksize=chunksize, ssdeep=ssdeep_hash)

        return ssdeep

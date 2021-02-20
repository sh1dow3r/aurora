from typing import List
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import UploadFile

from aurora.database import models
from aurora.core.utils import get_sha256


def get_samples(db: Session) -> List[models.Sample]:
    return db.query(models.Sample).all()


def get_number_of_samples(db: Session) -> int:
    return db.query(models.Sample).count()


def get_sample_by_sha256(db: Session, sha256: str) -> models.Sample:
    return db.query(models.Sample).filter(models.Sample.sha256 == sha256).first()


def get_sample_parents(db: Session, sample: models.Sample) -> List[models.Sample]:
     return db.query(models.Sample).distinct().filter(
        models.Sample.children.any(models.Relation.child_id == sample.id)
    ).all()

def get_sample_children(db: Session, sample: models.Sample) -> List[models.Sample]:
     return db.query(models.Sample).distinct().filter(
        models.Sample.parents.any(models.Relation.parent_id == sample.id)
    ).all()

def get_sample_related(db: Session, sample: models.Sample) -> List[models.Sample]:
    return db.query(models.Sample).distinct().filter(
        or_(
            models.Sample.parents.any(models.Relation.parent_id == sample.id),
            models.Sample.children.any(models.Relation.child_id == sample.id)
        )
    ).all()


def add_sample(db: Session, file: UploadFile) -> models.Sample:
    sha256 = get_sha256(file.file)
    sample = get_sample_by_sha256(db, sha256)

    if not sample:
        sample = models.Sample.from_uploadfile(file)
        db.add(sample)

    return sample


def add_minhash_to_sample(
    db: Session, sample: models.Sample, minhash: models.Minhash
) -> None:

    sample.minhashes.append(minhash)


def add_ssdeep_to_sample(
    db: Session, sample: models.Sample, ssdeep: models.SsDeep
) -> None:
    sample.ssdeep = ssdeep

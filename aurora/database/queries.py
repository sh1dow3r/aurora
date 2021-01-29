import hashlib

from fastapi import UploadFile
from typing import List, Optional
from sqlalchemy.orm import Session

from aurora.database import models
from aurora.core.utils import get_sha256


def get_samples(db: Session) -> List[models.Sample]:
    return db.query(models.Sample).all()


def get_sample(db: Session, sha256: str) -> models.Sample:
    return db.query(models.Sample)\
        .filter(models.Sample.sha256 == sha256)\
        .first()


def get_strings(db: Session) -> List[models.String]:
    return db.query(models.String).all()


def add_sample(db: Session, file: UploadFile) -> models.Sample:
    sha256 = get_sha256(file.file)
    sample = get_sample(db, sha256)

    if not sample:
        sample = models.Sample.from_uploadfile(file)

        db.add(sample)
        db.commit()
        db.refresh(sample)

    return sample


def add_string(db: Session, encoding: str, value: str) -> models.String:
    sha256 = hashlib.sha256(value.encode("utf-8")).hexdigest()
    string = get_string_by_sha256(db, encoding, sha256)

    if not string:
        string = models.String(
            encoding=encoding, value=value, status="NEW", sha256=sha256
        )

        db.add(string)
        db.commit()
        db.refresh(string)
    else:
        # Hardcoded value, will be derived from the number of total samples
        if get_num_of_string_samples(db, string.id) > 10:
            update_string_status(db, string.id, "COMMON")

    return string


def add_sample_string(
    db: Session, sha256: str, encoding: str, value: str
) -> models.String:

    sample = get_sample(db, sha256)
    string = add_string(db, encoding, value)

    sample.strings.append(string)

    db.commit()

    return string


def update_string_status(db: Session, id: int, status: str) -> models.String:
    string = db.query(models.String).filter(models.String.id == id).first()

    string.status = status

    db.commit()

    return string


def get_string_by_sha256(
    db: Session, encoding: str, sha256: str
) -> Optional[models.String]:
    string = (
        db.query(models.String)
        .filter(models.String.encoding == encoding)
        .filter(models.String.value == sha256)
        .first()
    )

    return string


def get_sample_strings(db: Session, sha256: str) -> List:
    sample = get_sample(db, sha256)

    if not sample:
        return None

    return sample.strings


def get_num_of_string_samples(db: Session, id: int) -> int:

    string = db.query(models.String).filter(models.String.id == id).first()

    num_of_samples = len(string.samples)

    return num_of_samples

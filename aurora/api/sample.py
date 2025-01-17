import logging
import hashlib

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from aurora.core import karton
from aurora.core.utils import get_sha256
from aurora.database import get_db, queries, schemas

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/sample",
    tags=["sample"],
)


@router.get("/")
def get_samples(db=Depends(get_db)):
    return queries.sample.get_samples(db)


@router.post("/", response_model=schemas.Sample)
def add_sample(file: UploadFile = File(...), db=Depends(get_db)):
    sha256 = get_sha256(file.file)
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if sample:
        return sample

    sample = queries.sample.add_sample(db, file)
    if not sample.ssdeep:
        ssdeep = queries.ssdeep.add_ssdeep(db, file)
        sample.ssdeep = ssdeep

        try:
            karton.push_ssdeep(sample.sha256, ssdeep.chunksize, ssdeep.ssdeep)
        except RuntimeError:
            logger.exception(f"Couldn't push ssdeep from {sample.sha256} to karton.")

    db.commit()

    try:
        karton.push_file(file, sample.filetype, sample.sha256)
    except RuntimeError:
        logger.exception(f"Couldn't push sample {sample.sha256} to karton")

    return sample


@router.get("/{sha256}", response_model=schemas.Sample)
def get_sample(sha256: str, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return sample


@router.post("/{sha256}/reanalyze")
def reanalyze(sha256: str, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    if sample.minhashes:
        for minhash in sample.minhashes:
            karton.push_minhash(
                sha256, minhash.seed, minhash.hash_values, minhash.minhash_type
            )

    if sample.ssdeep:
        karton.push_ssdeep(sha256, sample.ssdeep.chunksize, sample.ssdeep.ssdeep)

    return "OK"


@router.post("/{sha256}/minhash", response_model=schemas.Minhash)
def add_minhash(sha256: str, minhash: schemas.InputMinhash, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    if sample.minhashes:
        if any(x.minhash_type == minhash.minhash_type for x in sample.minhashes):
            raise HTTPException(
                status_code=500,
                detail=f"Sample {sha256} already contains {minhash.minhash_type} minhash.",
            )

    new_minhash = queries.minhash.add_minhash(
        db, minhash.seed, minhash.hash_values, minhash.minhash_type
    )
    sample.minhashes.append(new_minhash)
    db.commit()

    return new_minhash


@router.get("/{sha256}/minhash", response_model=List[schemas.Minhash])
def get_minhashes(sha256: str, minhash_type: Optional[str] = None, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return queries.minhash.get_sample_minhash(db, sample, minhash_type)


@router.get("/{sha256}/ssdeep", response_model=schemas.SsDeep)
def get_ssdeep(sha256: str, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return sample.ssdeep


@router.post("/{sha256}/string", response_model=schemas.String)
def add_string(sha256: str, string: schemas.InputString, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    sha256_object = hashlib.sha256()
    sha256_object.update(string.value.encode("utf-8"))
    sha256 = sha256_object.hexdigest()

    db_string = queries.string.add_string(db, string.value, sha256, string.heuristic)

    sample.strings.append(db_string)
    db.commit()

    return db_string


@router.get("/{sha256}/string", response_model=List[schemas.String])
def get_strings(sha256: str, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return sample.strings


@router.get("/{sha256}/parents", response_model=List[schemas.Sample])
def get_parents(sha256: str, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return list(queries.sample.get_sample_parents(db, sample))


@router.get("/{sha256}/children", response_model=List[schemas.Sample])
def get_children(sha256: str, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return list(queries.sample.get_sample_children(db, sample))


@router.get("/{sha256}/related", response_model=List[schemas.Sample])
def get_related(sha256: str, db=Depends(get_db)):
    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return list(queries.sample.get_sample_related(db, sample))

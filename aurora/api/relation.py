from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException

from aurora.database import get_db, queries, schemas

router = APIRouter(
    prefix="/relation",
    tags=["relation"],
)


@router.get("/", response_model=List[schemas.Relation])
def get_relations(
    relation_type: Optional[str] = None,
    confidence: Optional[float] = None,
    db=Depends(get_db),
):
    filters = schemas.RelationFilter(relation_type=relation_type, confidence=confidence)

    return queries.relation.get_relations(db, filters)


@router.post("/", response_model=schemas.Relation)
def add_relation(relation_input: schemas.InputRelation, db=Depends(get_db)):
    if relation_input.confidence < 0 or relation_input.confidence > 1:
        raise HTTPException(
            status_code=400,
            detail=f"Confidence must be >= 0 or <= 1. Got {relation_input.confidence}",
        )

    parent = queries.sample.get_sample_by_sha256(db, relation_input.parent_sha256)
    child = queries.sample.get_sample_by_sha256(db, relation_input.child_sha256)
    if not parent:
        raise HTTPException(
            status_code=404, detail=f"Parent {relation_input.parent_sha256} not found."
        )

    if not child:
        raise HTTPException(
            status_code=404, detail=f"Child {relation_input.child_sha256} not found."
        )

    relation = queries.relation.get_exact_relation(
        db, parent, child, relation_input.type
    )
    if not relation:
        relation = queries.relation.add_relation(
            db, parent, child, relation_input.type, relation_input.confidence
        )
        db.commit()

    return relation


@router.get("/parent/{sha256}", response_model=List[schemas.Relation])
def get_relations_by_parent(
    sha256: str,
    relation_type: Optional[str] = None,
    confidence: Optional[float] = None,
    db=Depends(get_db),
):

    filters = schemas.RelationFilter(relation_type=relation_type, confidence=confidence)

    parent = queries.sample.get_sample_by_sha256(db, sha256)
    if not parent:
        raise HTTPException(status_code=404, detail=f"Parent {sha256} not found.")

    return queries.relation.get_relations_by_parent(db, parent, filters)


@router.get("/child/{sha256}", response_model=List[schemas.Relation])
def get_relations_by_child(
    sha256: str,
    relation_type: Optional[str] = None,
    confidence: Optional[float] = None,
    db=Depends(get_db),
):

    filters = schemas.RelationFilter(relation_type=relation_type, confidence=confidence)

    child = queries.sample.get_sample_by_sha256(db, sha256)
    if not child:
        raise HTTPException(status_code=404, detail=f"Child {sha256} not found.")

    return queries.relation.get_relations_by_child(db, child, filters)


@router.get("/{sha256}", response_model=List[schemas.Relation])
def get_relations_by_hash(
    sha256: str,
    relation_type: Optional[str] = None,
    confidence: Optional[float] = None,
    db=Depends(get_db),
):
    filters = schemas.RelationFilter(relation_type=relation_type, confidence=confidence)

    sample = queries.sample.get_sample_by_sha256(db, sha256)
    if not sample:
        raise HTTPException(status_code=404, detail=f"Sample {sha256} not found.")

    return queries.relation.get_relations_by_hash(db, sample, filters)

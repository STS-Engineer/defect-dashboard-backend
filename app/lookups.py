from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import DefectType, WorkerCSL1, WorkerCF
from .config import BU_OPTIONS, POSTE_OPTIONS, EQUIPE_OPTIONS, LIGNE_OPTIONS

router = APIRouter()


@router.get("/static")
def static_lookups():
    return {
        "bu": BU_OPTIONS,
        "poste": POSTE_OPTIONS,
        "equipe": EQUIPE_OPTIONS,
        "ligne": LIGNE_OPTIONS,
    }


@router.get("/defauts")
def get_defauts(db: Session = Depends(get_db)):
    rows = db.query(DefectType).order_by(DefectType.name).all()
    return [
        {
            "value": r.name,
            "label": r.name,
            "monday_item_id": r.monday_item_id,
        }
        for r in rows
    ]


@router.get("/csl1")
def get_csl1(db: Session = Depends(get_db)):
    rows = db.query(WorkerCSL1).order_by(WorkerCSL1.matricule).all()
    return [
        {
            "value": r.matricule,
            "label": f"{r.matricule} - {r.full_name}" if r.full_name else r.matricule,
            "full_name": r.full_name,
            "monday_item_id": r.monday_item_id,
        }
        for r in rows
    ]


@router.get("/cf")
def get_cf(db: Session = Depends(get_db)):
    rows = db.query(WorkerCF).order_by(WorkerCF.matricule).all()
    return [
        {
            "value": r.matricule,
            "label": f"{r.matricule} - {r.full_name}" if r.full_name else r.matricule,
            "full_name": r.full_name,
            "monday_item_id": r.monday_item_id,
        }
        for r in rows
    ]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from .database import get_db
from .models import Defect

router = APIRouter()


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total_defauts = db.query(func.sum(Defect.nombre)).scalar() or 0
    total_rows = db.query(Defect).count()
    total_quantite = db.query(func.sum(Defect.quantite_controlee)).scalar() or 0

    return {
        "total_defauts": int(total_defauts),
        "total_rows": total_rows,
        "total_quantite_controlee": int(total_quantite),
    }


@router.get("/defauts-par-jour")
def defauts_par_jour(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.date_detection.label("date"),
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        Defect.date_detection
    ).order_by(
        Defect.date_detection
    ).all()

    return [{"date": str(r.date), "total": int(r.total or 0)} for r in rows]


@router.get("/defauts-par-semaine")
def defauts_par_semaine(db: Session = Depends(get_db)):
    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("week", Defect.date_detection).label("week"),
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "week"
    ).order_by(
        "year", "week"
    ).all()

    return [
        {
            "semaine": f"{int(r.year)}-S{int(r.week)}",
            "total": int(r.total or 0),
        }
        for r in rows
    ]


@router.get("/defauts-par-mois")
def defauts_par_mois(db: Session = Depends(get_db)):
    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("month", Defect.date_detection).label("month"),
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "month"
    ).order_by(
        "year", "month"
    ).all()

    return [
        {
            "mois": f"{int(r.year)}-{int(r.month):02d}",
            "total": int(r.total or 0),
        }
        for r in rows
    ]


@router.get("/defauts-par-ligne")
def defauts_par_ligne(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).group_by(
        Defect.ligne
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    return [{"ligne": r.ligne or "Non défini", "total": int(r.total or 0)} for r in rows]


@router.get("/defauts-par-poste")
def defauts_par_poste(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.poste,
        func.sum(Defect.nombre).label("total"),
    ).group_by(
        Defect.poste
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    return [{"poste": r.poste or "Non défini", "total": int(r.total or 0)} for r in rows]


@router.get("/pareto-defauts")
def pareto_defauts(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.defaut,
        func.sum(Defect.nombre).label("total"),
    ).group_by(
        Defect.defaut
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    total_all = sum(int(r.total or 0) for r in rows)
    cumulative = 0
    result = []

    for r in rows:
        total = int(r.total or 0)
        cumulative += total

        result.append({
            "defaut": r.defaut or "Non défini",
            "total": total,
            "cumulative_percent": round((cumulative / total_all) * 100, 2) if total_all else 0,
        })

    return result


@router.get("/analyse-operatrice-cf")
def analyse_operatrice_cf(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.prenom_nom_cf,
        func.sum(Defect.nombre).label("total"),
    ).group_by(
        Defect.prenom_nom_cf
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    return [
        {
            "operatrice": r.prenom_nom_cf or "Non défini",
            "total": int(r.total or 0),
        }
        for r in rows
    ]


@router.get("/analyse-operatrice-csl1")
def analyse_operatrice_csl1(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.prenom_nom_csl1,
        func.sum(Defect.nombre).label("total"),
    ).group_by(
        Defect.prenom_nom_csl1
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    return [
        {
            "operatrice": r.prenom_nom_csl1 or "Non défini",
            "total": int(r.total or 0),
        }
        for r in rows
    ]
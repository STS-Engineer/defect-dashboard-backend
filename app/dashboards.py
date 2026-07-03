from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from .database import get_db
from .models import Defect, DefectType, WorkerCSL1, WorkerCF , Quantite, CopieDetection


router = APIRouter()
logger = logging.getLogger(__name__)


def parse_date_value(value):
    if not value:
        return None

    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid date: {value}") from exc


def parse_int_value(value, default=None):
    if value in [None, ""]:
        return default

    try:
        return int(float(str(value).replace(",", ".")))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid number: {value}") from exc


def serialize_quantite(row: Quantite):
    return {
        "id": row.id,
        "monday_group": row.monday_group,
        "item_name": row.item_name,
        "quantite_controlee": row.quantite_controlee,
        "date": str(row.date) if row.date else None,
        "semaine": row.semaine,
        "ligne": row.ligne,
        "bu": row.bu,
        "equipe": row.equipe,
        "mat_csl1": row.mat_csl1,
        "prenom_nom_csl1": row.prenom_nom_csl1,
        "mat_cf": row.mat_cf,
        "prenom_nom_cf": row.prenom_nom_cf,
        "mat_csl2": row.mat_csl2,
    }


def serialize_copie_detection(row: CopieDetection):
    return {
        "id": row.id,
        "monday_group": row.monday_group,
        "item_name": row.item_name,
        "date": str(row.date) if row.date else None,
        "semaine": row.semaine,
        "ligne": row.ligne,
        "bu": row.bu,
        "poste": row.poste,
        "equipe": row.equipe,
        "nombre": row.nombre,
        "mat_cf": row.mat_cf,
    }


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
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        Defect.date_detection,
        Defect.ligne
    ).order_by(
        Defect.date_detection,
        Defect.ligne
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        key = str(r.date)
        if key not in result_dict:
            result_dict[key] = {"date": key}
        ligne = r.ligne or "Non défini"
        result_dict[key][ligne] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/defauts-par-semaine")
def defauts_par_semaine(db: Session = Depends(get_db)):
    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("week", Defect.date_detection).label("week"),
        Defect.bu,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "week", Defect.bu
    ).order_by(
        "year", "week", Defect.bu
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        key = f"{int(r.year)}-S{int(r.week)}"
        if key not in result_dict:
            result_dict[key] = {"semaine": key}
        bu = r.bu or "Non défini"
        result_dict[key][bu] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/defauts-par-mois")
def defauts_par_mois(db: Session = Depends(get_db)):
    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("month", Defect.date_detection).label("month"),
        Defect.bu,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "month", Defect.bu
    ).order_by(
        "year", "month", Defect.bu
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        key = f"{int(r.year)}-{int(r.month):02d}"
        if key not in result_dict:
            result_dict[key] = {"mois": key}
        bu = r.bu or "Non défini"
        result_dict[key][bu] = int(r.total or 0)

    return list(result_dict.values())


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


@router.get("/pareto-defauts-par-ligne")
def pareto_defauts_par_ligne(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.ligne,
        Defect.equipe,
        func.sum(Defect.nombre).label("total"),
    ).group_by(
        Defect.ligne,
        Defect.equipe
    ).order_by(
        func.sum(Defect.nombre).desc(),
        Defect.ligne
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        ligne = r.ligne or "Non défini"
        if ligne not in result_dict:
            result_dict[ligne] = {"ligne": ligne}
        equipe = r.equipe or "Vide"
        result_dict[ligne][equipe] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/nombre-defauts-par-ligne-stacked")
def nombre_defauts_par_ligne_stacked(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).group_by(
        Defect.ligne
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    return [{"ligne": r.ligne or "Non défini", "total": int(r.total or 0)} for r in rows]


@router.get("/analyse-operatrice-cf")
def analyse_operatrice_cf(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.mat_cf,
        Defect.prenom_nom_cf,
        Defect.mat_cf_2,
        Defect.prenom_nom_cf_2,
        Defect.bu,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.mat_cf.isnot(None)
    ).group_by(
        Defect.mat_cf,
        Defect.prenom_nom_cf,
        Defect.mat_cf_2,
        Defect.prenom_nom_cf_2,
        Defect.bu
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        mat_cf = r.mat_cf or "Non défini"
        label = f"{mat_cf}"  # Show only matricule
        if label not in result_dict:
            result_dict[label] = {"operatrice": label, "mat": mat_cf, "name": r.prenom_nom_cf}
        bu = r.bu or "Non défini"
        result_dict[label][bu] = int(r.total or 0)

        if r.mat_cf_2:
            label_2 = f"{r.mat_cf_2}"
            if label_2 not in result_dict:
                result_dict[label_2] = {"operatrice": label_2, "mat": r.mat_cf_2, "name": r.prenom_nom_cf_2}
            result_dict[label_2][bu] = result_dict[label_2].get(bu, 0) + int(r.total or 0)

    # Sort by total descending
    sorted_result = sorted(
        result_dict.values(),
        key=lambda x: sum(x.get(bu, 0) for bu in ["VALEO", "NIDEC"]),
        reverse=True
    )
    
    return sorted_result


@router.get("/analyse-operatrice-csl1")
def analyse_operatrice_csl1(db: Session = Depends(get_db)):
    rows = db.query(
        Defect.mat_csl1,
        Defect.prenom_nom_csl1,
        Defect.bu,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.mat_csl1.isnot(None)
    ).group_by(
        Defect.mat_csl1,
        Defect.prenom_nom_csl1,
        Defect.bu
    ).order_by(
        func.sum(Defect.nombre).desc()
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        mat_csl1 = r.mat_csl1 or "Non défini"
        label = f"{mat_csl1}"  # Show only matricule
        if label not in result_dict:
            result_dict[label] = {"operatrice": label, "mat": mat_csl1, "name": r.prenom_nom_csl1}
        bu = r.bu or "Non défini"
        result_dict[label][bu] = int(r.total or 0)

    # Sort by total descending
    sorted_result = sorted(
        result_dict.values(),
        key=lambda x: sum(x.get(bu, 0) for bu in ["VALEO", "NIDEC"]),
        reverse=True
    )
    
    return sorted_result



@router.get("/workers-cf")
def get_workers_cf(db: Session = Depends(get_db)):
    rows = db.query(WorkerCF).order_by(WorkerCF.matricule).all()
    return [{"id": r.id, "matricule": r.matricule, "full_name": r.full_name, "monday_group": r.monday_group} for r in rows]


@router.post("/workers-cf")
def create_worker_cf(payload: dict = Body(...), db: Session = Depends(get_db)):
    matricule = payload.get("matricule")
    if not matricule:
        raise HTTPException(status_code=400, detail="matricule is required")

    row = WorkerCF(
        monday_item_id=None,
        matricule=str(matricule),
        full_name=payload.get("full_name"),
        monday_group=payload.get("monday_group"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "matricule": row.matricule, "full_name": row.full_name, "monday_group": row.monday_group}


@router.delete("/workers-cf/{item_id}", status_code=204)
def delete_worker_cf(item_id: int, db: Session = Depends(get_db)):
    row = db.query(WorkerCF).filter(WorkerCF.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Worker CF not found")
    db.delete(row)
    db.commit()
    return


@router.get("/workers-csl1")
def get_workers_csl1(db: Session = Depends(get_db)):
    rows = db.query(WorkerCSL1).order_by(WorkerCSL1.matricule).all()
    return [{"id": r.id, "matricule": r.matricule, "full_name": r.full_name, "monday_group": r.monday_group} for r in rows]


@router.post("/workers-csl1")
def create_worker_csl1(payload: dict = Body(...), db: Session = Depends(get_db)):
    matricule = payload.get("matricule")
    if not matricule:
        raise HTTPException(status_code=400, detail="matricule is required")

    row = WorkerCSL1(
        monday_item_id=None,
        matricule=str(matricule),
        full_name=payload.get("full_name"),
        monday_group=payload.get("monday_group"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "matricule": row.matricule, "full_name": row.full_name, "monday_group": row.monday_group}


@router.delete("/workers-csl1/{item_id}", status_code=204)
def delete_worker_csl1(item_id: int, db: Session = Depends(get_db)):
    row = db.query(WorkerCSL1).filter(WorkerCSL1.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Worker CSL1 not found")
    db.delete(row)
    db.commit()
    return


@router.get("/defect-types")
def get_defect_types(db: Session = Depends(get_db)):
    rows = db.query(DefectType).order_by(DefectType.name).all()
    return [{"id": r.id, "name": r.name, "monday_group": r.monday_group} for r in rows]


@router.post("/defect-types")
def create_defect_type(payload: dict = Body(...), db: Session = Depends(get_db)):
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name is required")

    row = DefectType(monday_item_id=None, name=str(name))
    # accept optional monday_group
    row.monday_group = payload.get("monday_group")
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "name": row.name, "monday_group": row.monday_group}



@router.delete("/defect-types/{item_id}", status_code=204)
def delete_defect_type(item_id: int, db: Session = Depends(get_db)):
    row = db.query(DefectType).filter(DefectType.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Defect type not found")
    db.delete(row)
    db.commit()
    return


@router.get("/quantite")
def get_quantite(db: Session = Depends(get_db)):
    rows = db.query(Quantite).order_by(Quantite.id.desc()).limit(2000).all()
    return [serialize_quantite(r) for r in rows]


@router.post("/quantite")
def create_quantite(payload: dict = Body(...), db: Session = Depends(get_db)):
    row = Quantite(
        monday_item_id=None,
        monday_group=payload.get("monday_group"),
        item_name=payload.get("item_name"),
        quantite_controlee=parse_int_value(payload.get("quantite_controlee")),
        date=parse_date_value(payload.get("date")),
        semaine=parse_int_value(payload.get("semaine")),
        ligne=payload.get("ligne"),
        bu=payload.get("bu"),
        equipe=payload.get("equipe"),
        mat_csl1=payload.get("mat_csl1"),
        prenom_nom_csl1=payload.get("prenom_nom_csl1"),
        mat_cf=payload.get("mat_cf"),
        prenom_nom_cf=payload.get("prenom_nom_cf"),
        mat_csl2=payload.get("mat_csl2"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_quantite(row)


@router.delete("/quantite/{item_id}", status_code=204)
def delete_quantite(item_id: int, db: Session = Depends(get_db)):
    row = db.query(Quantite).filter(Quantite.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Quantite row not found")
    db.delete(row)
    db.commit()
    return


@router.get("/copie-detection")
def get_copie_detection(db: Session = Depends(get_db)):
    rows = db.query(CopieDetection).order_by(CopieDetection.id.desc()).limit(2000).all()
    return [serialize_copie_detection(r) for r in rows]


@router.post("/copie-detection")
def create_copie_detection(payload: dict = Body(...), db: Session = Depends(get_db)):
    row = CopieDetection(
        monday_item_id=None,
        monday_group=payload.get("monday_group"),
        item_name=payload.get("item_name"),
        date=parse_date_value(payload.get("date")),
        semaine=parse_int_value(payload.get("semaine")),
        ligne=payload.get("ligne"),
        bu=payload.get("bu"),
        poste=payload.get("poste"),
        equipe=payload.get("equipe"),
        nombre=parse_int_value(payload.get("nombre"), default=0),
        mat_cf=payload.get("mat_cf"),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return serialize_copie_detection(row)


@router.delete("/copie-detection/{item_id}", status_code=204)
def delete_copie_detection(item_id: int, db: Session = Depends(get_db)):
    row = db.query(CopieDetection).filter(CopieDetection.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Copie detection row not found")
    db.delete(row)
    db.commit()
    return


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


@router.get("/defauts-par-mois-ligne")
def defauts_par_mois_ligne(db: Session = Depends(get_db)):
    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("month", Defect.date_detection).label("month"),
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "month", Defect.ligne
    ).order_by(
        "year", "month", Defect.ligne
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        key = f"{int(r.year)}-{int(r.month):02d}"
        if key not in result_dict:
            result_dict[key] = {"mois": key}
        ligne = r.ligne or "Non défini"
        result_dict[key][ligne] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/defauts-par-semaine-poste")
def defauts_par_semaine_poste(db: Session = Depends(get_db)):
    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("week", Defect.date_detection).label("week"),
        Defect.poste,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "week", Defect.poste
    ).order_by(
        "year", "week", Defect.poste
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        key = f"{int(r.year)}-S{int(r.week)}"
        if key not in result_dict:
            result_dict[key] = {"semaine": key}
        poste = r.poste or "Non défini"
        result_dict[key][poste] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/defauts-par-mois-poste")
def defauts_par_mois_poste(db: Session = Depends(get_db)):
    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("month", Defect.date_detection).label("month"),
        Defect.poste,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "month", Defect.poste
    ).order_by(
        "year", "month", Defect.poste
    ).all()

    # Pivot data for stacked chart
    result_dict = {}
    for r in rows:
        key = f"{int(r.year)}-{int(r.month):02d}"
        if key not in result_dict:
            result_dict[key] = {"mois": key}
        poste = r.poste or "Non défini"
        result_dict[key][poste] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/defauts-par-semaine-poste-test-electrique")
def defauts_par_semaine_poste_test_electrique(db: Session = Depends(get_db)):

    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("week", Defect.date_detection).label("week"),
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None),
        Defect.poste == "Test électrique"
    ).group_by(
        "year",
        "week",
        Defect.ligne
    ).order_by(
        "year",
        "week"
    ).all()

    result_dict = {}

    for r in rows:

        semaine = f"{int(r.year)}-S{int(r.week)}"

        if semaine not in result_dict:
            result_dict[semaine] = {"semaine": semaine}

        ligne = r.ligne or "Non défini"

        result_dict[semaine][ligne] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/defauts-par-semaine-poste-cf")
def defauts_par_semaine_poste_cf(db: Session = Depends(get_db)):

    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("week", Defect.date_detection).label("week"),
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None),
        Defect.poste == "CF"
    ).group_by(
        "year",
        "week",
        Defect.ligne
    ).order_by(
        "year",
        "week"
    ).all()

    result_dict = {}

    for r in rows:

        semaine = f"{int(r.year)}-S{int(r.week)}"

        if semaine not in result_dict:
            result_dict[semaine] = {"semaine": semaine}

        ligne = r.ligne or "Non défini"

        result_dict[semaine][ligne] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/defauts-par-semaine-poste-csl1")
def defauts_par_semaine_poste_csl1(db: Session = Depends(get_db)):

    rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("week", Defect.date_detection).label("week"),
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None),
        Defect.poste == "CSL1"
    ).group_by(
        "year",
        "week",
        Defect.ligne
    ).order_by(
        "year",
        "week"
    ).all()

    result_dict = {}

    for r in rows:

        semaine = f"{int(r.year)}-S{int(r.week)}"

        if semaine not in result_dict:
            result_dict[semaine] = {"semaine": semaine}

        ligne = r.ligne or "Non défini"

        result_dict[semaine][ligne] = int(r.total or 0)

    return list(result_dict.values())


@router.get("/pareto-defauts-par-mois")
def pareto_defauts_par_mois(db: Session = Depends(get_db)):
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


@router.get("/quantite-controlee-par-semaine")
def quantite_controlee_par_semaine(db: Session = Depends(get_db)):
    # Get Quantité data by week
    quantite_rows = db.query(
        extract("year", Quantite.date).label("year"),
        extract("week", Quantite.date).label("week"),
        func.sum(Quantite.quantite_controlee).label("total"),
    ).filter(
        Quantite.date.isnot(None),
        Quantite.quantite_controlee.isnot(None)
    ).group_by(
        "year", "week"
    ).all()

    # Get Défauts data by week
    defauts_rows = db.query(
        extract("year", Defect.date_detection).label("year"),
        extract("week", Defect.date_detection).label("week"),
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.date_detection.isnot(None)
    ).group_by(
        "year", "week"
    ).all()

    # Pivot both datasets
    result_dict = {}
    
    for r in quantite_rows:
        key = f"{int(r.year)}-S{int(r.week)}"
        if key not in result_dict:
            result_dict[key] = {"semaine": key}
        result_dict[key]["Quantité"] = int(r.total or 0)

    for r in defauts_rows:
        key = f"{int(r.year)}-S{int(r.week)}"
        if key not in result_dict:
            result_dict[key] = {"semaine": key}
        result_dict[key]["Détection de défauts"] = int(r.total or 0)

    return sorted(result_dict.values(), key=lambda x: x["semaine"])


@router.get("/nombre-defauts-par-defaut")
def nombre_defauts_par_defaut(db: Session = Depends(get_db)):

    rows = db.query(
        Defect.defaut,
        Defect.ligne,
        func.sum(Defect.nombre).label("total"),
    ).filter(
        Defect.defaut.isnot(None)
    ).group_by(
        Defect.defaut,
        Defect.ligne
    ).order_by(
        func.sum(Defect.nombre).desc(),
        Defect.defaut
    ).all()

    # Pivot data for stacked chart
    result_dict = {}

    for r in rows:
        defaut = r.defaut or "Non défini"

        if defaut not in result_dict:
            result_dict[defaut] = {"defaut": defaut}

        ligne = r.ligne or "Non défini"

        result_dict[defaut][ligne] = int(r.total or 0)

    return list(result_dict.values())

@router.get("/nombre-par-semaine")
def nombre_par_semaine(db: Session = Depends(get_db)):
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
            "nombre": int(r.total or 0),
        }
        for r in rows
    ]


@router.get("/quantite-par-ligne-semaine-actuelle")
def quantite_par_ligne_semaine_actuelle(db: Session = Depends(get_db)):
    try:
        return _quantite_par_ligne_semaine_actuelle_impl(db)
    except Exception as exc:
        logger.exception("quantite-par-ligne-semaine-actuelle failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to load current-week quantity by line",
        ) from exc


def _quantite_par_ligne_semaine_actuelle_impl(db: Session):
    today = datetime.today()
    current_year = today.isocalendar()[0]
    current_week = today.isocalendar()[1]
    previous_week = current_week - 1

    logger.info(
        "quantite-par-ligne-semaine-actuelle start: year=%s current_week=%s previous_week=%s",
        current_year,
        current_week,
        previous_week,
    )

    rows = db.query(
        extract("week", Quantite.date).label("week"),
        Quantite.ligne,
        func.sum(Quantite.quantite_controlee).label("total"),
    ).filter(
        extract("year", Quantite.date) == current_year,
        extract("week", Quantite.date).in_([previous_week, current_week]),
        Quantite.quantite_controlee.isnot(None)
    ).group_by(
        "week",
        Quantite.ligne
    ).all()

    logger.info(
        "quantite-par-ligne-semaine-actuelle query returned %s rows",
        len(rows),
    )

    # Calculate Monday-Sunday for each week
    def get_week_range(year, week):
        jan4 = datetime(year, 1, 4)
        week_one_monday = jan4 - timedelta(days=jan4.weekday())
        week_monday = week_one_monday + timedelta(weeks=week-1)
        week_sunday = week_monday + timedelta(days=6)
        return week_monday, week_sunday

    prev_mon, prev_sun = get_week_range(current_year, previous_week)
    curr_mon, curr_sun = get_week_range(current_year, current_week)

    # Pivot data
    result_dict = {}
    for r in rows:
        if r.week is None:
            logger.warning(
                "quantite-par-ligne-semaine-actuelle skipped row with NULL week: ligne=%s total=%s",
                r.ligne,
                r.total,
            )
            continue

        week = int(r.week)
        
        if week == current_week:
            date_label = f"mai {curr_mon.day}-{curr_sun.day}"
        else:
            date_label = f"mai {prev_mon.day}-{prev_sun.day}"
        
        if date_label not in result_dict:
            result_dict[date_label] = {"date": date_label}
        
        ligne = r.ligne or "Non défini"
        result_dict[date_label][ligne] = int(r.total or 0)

    result = sorted(result_dict.values(), key=lambda x: x["date"])
    logger.info(
        "quantite-par-ligne-semaine-actuelle returning %s buckets",
        len(result),
    )
    return result


@router.get("/status-distribution")
def get_status_distribution(db: Session = Depends(get_db)):
    """Get distribution of defects by treatment status"""
    results = (
        db.query(Defect.status, func.count(Defect.id).label("count"))
        .group_by(Defect.status)
        .all()
    )
    
    return [
        {"status": r.status or "HISTORIQUE", "count": r.count}
        for r in results
    ]

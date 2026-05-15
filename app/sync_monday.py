from datetime import datetime
from sqlalchemy.orm import Session

from .models import Defect, DefectType, WorkerCSL1, WorkerCF
from .monday_client import fetch_board_groups, fetch_items_by_group, fetch_board_items
from .config import (
    MONDAY_DETECTION_BOARD_ID,
    MONDAY_TYPE_DEFAUTS_BOARD_ID,
    MONDAY_CSL1_BOARD_ID,
    MONDAY_CF_BOARD_ID,
    MONDAY_DETECTION_GROUPS,
    DETECTION_COLUMN_MAP,
)


def parse_date(value):
    if not value:
        return None

    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_datetime(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def parse_int(value):
    if value is None or value == "":
        return None

    try:
        return int(float(str(value).replace(",", ".")))
    except ValueError:
        return None


def parse_bool(value):
    if isinstance(value, dict):
        return bool(value.get("checked"))

    if isinstance(value, str):
        return value.lower() in ["true", "yes", "checked", "1"]

    return bool(value)


def get_column_value(item, field_name):
    wanted_id = DETECTION_COLUMN_MAP.get(field_name)

    if not wanted_id:
        return None

    for col in item.get("column_values", []):
        if col.get("id") == wanted_id:
            if col.get("display_value") not in [None, ""]:
                return col.get("display_value")

            if col.get("text") not in [None, ""]:
                return col.get("text")

            return col.get("value")

    return None


def sync_detection_defauts(db: Session):
    groups = fetch_board_groups(MONDAY_DETECTION_BOARD_ID)

    selected_groups = {
        g["title"]: g["id"]
        for g in groups
        if g["title"] in MONDAY_DETECTION_GROUPS
    }

    total = 0

    for group_title, group_id in selected_groups.items():
        items = fetch_items_by_group(MONDAY_DETECTION_BOARD_ID, group_id)

        for item in items:
            monday_item_id = item["id"]

            defect = db.query(Defect).filter(
                Defect.monday_item_id == monday_item_id
            ).first()

            data = {
                "monday_item_id": monday_item_id,
                "monday_group": group_title,
                "item_name": item.get("name"),
                "defaut": get_column_value(item, "defaut"),
                "date_detection": parse_date(get_column_value(item, "date_detection")),
                "ligne": get_column_value(item, "ligne"),
                "bu": get_column_value(item, "bu"),
                "poste": get_column_value(item, "poste"),
                "equipe": get_column_value(item, "equipe"),
                "nombre": parse_int(get_column_value(item, "nombre")) or 0,
                "mat_csl1": get_column_value(item, "mat_csl1"),
                "prenom_nom_csl1": get_column_value(item, "prenom_nom_csl1"),
                "mat_cf": get_column_value(item, "mat_cf"),
                "prenom_nom_cf": get_column_value(item, "prenom_nom_cf"),
                "saisie_quantite_totale": parse_bool(get_column_value(item, "saisie_quantite_totale")),
                "created_at_monday": parse_datetime(item.get("created_at")),
                "updated_at_monday": parse_datetime(item.get("updated_at")),
            }

            if defect:
                for key, value in data.items():
                    setattr(defect, key, value)
            else:
                db.add(Defect(**data))

            total += 1

    db.commit()
    return total


def sync_defect_types(db: Session):
    items = fetch_board_items(MONDAY_TYPE_DEFAUTS_BOARD_ID)
    total = 0

    for item in items:
        name = item.get("name")
        monday_item_id = item.get("id")

        if not name:
            continue

        existing = db.query(DefectType).filter(
            DefectType.monday_item_id == monday_item_id
        ).first()

        if existing:
            existing.name = name
        else:
            db.add(DefectType(monday_item_id=monday_item_id, name=name))

        total += 1

    db.commit()
    return total


def sync_workers_csl1(db: Session):
    items = fetch_board_items(MONDAY_CSL1_BOARD_ID)
    total = 0

    for item in items:
        matricule = item.get("name")
        monday_item_id = item.get("id")

        if not matricule:
            continue

        full_name = None

        for col in item.get("column_values", []):
            if col.get("text"):
                full_name = col.get("text")
                break

        existing = db.query(WorkerCSL1).filter(
            WorkerCSL1.monday_item_id == monday_item_id
        ).first()

        if existing:
            existing.matricule = matricule
            existing.full_name = full_name
        else:
            db.add(
                WorkerCSL1(
                    monday_item_id=monday_item_id,
                    matricule=matricule,
                    full_name=full_name,
                )
            )

        total += 1

    db.commit()
    return total


def sync_workers_cf(db: Session):
    items = fetch_board_items(MONDAY_CF_BOARD_ID)
    total = 0

    for item in items:
        matricule = item.get("name")
        monday_item_id = item.get("id")

        if not matricule:
            continue

        full_name = None

        for col in item.get("column_values", []):
            if col.get("text"):
                full_name = col.get("text")
                break

        existing = db.query(WorkerCF).filter(
            WorkerCF.monday_item_id == monday_item_id
        ).first()

        if existing:
            existing.matricule = matricule
            existing.full_name = full_name
        else:
            db.add(
                WorkerCF(
                    monday_item_id=monday_item_id,
                    matricule=matricule,
                    full_name=full_name,
                )
            )

        total += 1

    db.commit()
    return total


def sync_all_from_monday(db: Session):
    return {
        "defects": sync_detection_defauts(db),
        "defect_types": sync_defect_types(db),
        "workers_csl1": sync_workers_csl1(db),
        "workers_cf": sync_workers_cf(db),
    }
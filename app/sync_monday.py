from datetime import datetime
from sqlalchemy.orm import Session

from .monday_client import fetch_board_groups, fetch_items_by_group, fetch_board_items



from .models import Defect, DefectType, WorkerCSL1, WorkerCF, Quantite, CopieDetection
from .config import (
    MONDAY_DETECTION_BOARD_ID,
    MONDAY_TYPE_DEFAUTS_BOARD_ID,
    MONDAY_CSL1_BOARD_ID,
    MONDAY_CF_BOARD_ID,
    MONDAY_QUANTITE_BOARD_ID,
    MONDAY_COPIE_DETECTION_BOARD_ID,
    MONDAY_DETECTION_GROUPS,
    DETECTION_COLUMN_MAP,
    QUANTITE_COLUMN_MAP,
    COPIE_DETECTION_COLUMN_MAP,
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


def resolve_monday_group(item, groups, default="Actif"):
    group_obj = item.get("group") or {}
    group_id = group_obj.get("id")
    monday_group = group_obj.get("title")

    if not monday_group and group_id and groups:
        matching = next((g for g in groups if g.get("id") == group_id), None)
        if matching:
            monday_group = matching.get("title")

    return group_id, monday_group or default


def sync_detection_defauts(db: Session):
    groups = fetch_board_groups(MONDAY_DETECTION_BOARD_ID)

    selected_groups = {
        g["title"]: g["id"]
        for g in groups
        if g["title"] in MONDAY_DETECTION_GROUPS
    }

    total = 0

    for group_title, group_id in selected_groups.items():
        items = fetch_items_by_group(
            MONDAY_DETECTION_BOARD_ID,
            group_id
        )

        for item in items:
            monday_item_id = item["id"]

            defect = db.query(Defect).filter(
                Defect.monday_item_id == monday_item_id
            ).first()

            # -----------------------------
            # DATE
            # -----------------------------
            raw_date = get_column_value(
                item,
                "date_detection"
            )

            date_detection = parse_date(raw_date)

            # -----------------------------
            # ISO WEEK NUMBER
            # -----------------------------
            semaine = None

            if date_detection:
                semaine = date_detection.isocalendar()[1]

            # Use the Monday item group title when available, but fallback to the
            # selected group title for items fetched by group.
            group_id, monday_group = resolve_monday_group(item, groups, default=group_title)

            data = {
                "monday_item_id": monday_item_id,
                "monday_group": monday_group,
                "item_name": item.get("name"),

                "defaut": get_column_value(item, "defaut"),

                "date_detection": date_detection,
                "semaine": semaine,

                "ligne": get_column_value(item, "ligne"),
                "bu": get_column_value(item, "bu"),
                "poste": get_column_value(item, "poste"),
                "equipe": get_column_value(item, "equipe"),

                "nombre": parse_int(
                    get_column_value(item, "nombre")
                ) or 0,

                "mat_csl1": get_column_value(item, "mat_csl1"),
                "prenom_nom_csl1": get_column_value(item, "prenom_nom_csl1"),

                "mat_cf": get_column_value(item, "mat_cf"),
                "prenom_nom_cf": get_column_value(item, "prenom_nom_cf"),

                "saisie_quantite_totale": parse_bool(
                    get_column_value(item, "saisie_quantite_totale")
                ),

                "created_at_monday": parse_datetime(
                    item.get("created_at")
                ),

                "updated_at_monday": parse_datetime(
                    item.get("updated_at")
                ),
            }

            if defect:
                for key, value in data.items():
                    setattr(defect, key, value)
            else:
                db.add(Defect(**data))

            total += 1

    db.commit()

    return total


def sync_workers_csl1(db: Session):
    items = fetch_board_items(MONDAY_CSL1_BOARD_ID)
    groups = fetch_board_groups(MONDAY_CSL1_BOARD_ID)
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

        group_id, monday_group = resolve_monday_group(item, groups)
        print(f"Item: {item.get('name')}, Group ID: {group_id}, Monday Group: {monday_group}")

        if existing:
            existing.matricule = matricule
            existing.full_name = full_name
            existing.monday_group = monday_group
        else:
            db.add(
                WorkerCSL1(
                    monday_item_id=monday_item_id,
                    matricule=matricule,
                    full_name=full_name,
                    monday_group=monday_group,
                )
            )

        total += 1

    db.commit()
    return total


def sync_workers_cf(db: Session):
    items = fetch_board_items(MONDAY_CF_BOARD_ID)
    groups = fetch_board_groups(MONDAY_CF_BOARD_ID)
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

        group_id, monday_group = resolve_monday_group(item, groups)
        print(f"Item: {item.get('name')}, Group ID: {group_id}, Monday Group: {monday_group}")

        if existing:
            existing.matricule = matricule
            existing.full_name = full_name
            existing.monday_group = monday_group
        else:
            db.add(
                WorkerCF(
                    monday_item_id=monday_item_id,
                    matricule=matricule,
                    full_name=full_name,
                    monday_group=monday_group,
                )
            )

        total += 1

    db.commit()
    return total


def sync_defect_types(db: Session):
    items = fetch_board_items(MONDAY_TYPE_DEFAUTS_BOARD_ID)
    groups = fetch_board_groups(MONDAY_TYPE_DEFAUTS_BOARD_ID)
    total = 0

    for item in items:
        monday_item_id = item.get("id")
        name = item.get("name") or None

        group_id, monday_group = resolve_monday_group(item, groups)
        print(f"Item: {item.get('name')}, Group ID: {group_id}, Monday Group: {monday_group}")

        existing = db.query(DefectType).filter(DefectType.monday_item_id == monday_item_id).first()

        data = {
            "monday_item_id": monday_item_id,
            "monday_group": monday_group,
            "name": name,
        }

        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(DefectType(**data))

        total += 1

    db.commit()
    return total









def sync_quantite(db: Session):
    items = fetch_board_items(MONDAY_QUANTITE_BOARD_ID)
    groups = fetch_board_groups(MONDAY_QUANTITE_BOARD_ID)
    total = 0

    for item in items:
        monday_item_id = item["id"]
        
        existing = db.query(Quantite).filter(
            Quantite.monday_item_id == monday_item_id
        ).first()

        group_id, monday_group = resolve_monday_group(item, groups)
        print(f"Item: {item.get('name')}, Group ID: {group_id}, Monday Group: {monday_group}")

        data = {
            "monday_item_id": monday_item_id,
            "monday_group": monday_group,
            "item_name": item.get("name"),
            "quantite_controlee": parse_int(get_column_value_generic(item, "quantite_controlee", QUANTITE_COLUMN_MAP)),
            "date": parse_date(get_column_value_generic(item, "date", QUANTITE_COLUMN_MAP)),
            "semaine": parse_int(get_column_value_generic(item, "semaine", QUANTITE_COLUMN_MAP)),
            "ligne": get_column_value_generic(item, "ligne", QUANTITE_COLUMN_MAP),
            "bu": get_column_value_generic(item, "bu", QUANTITE_COLUMN_MAP),
            "equipe": get_column_value_generic(item, "equipe", QUANTITE_COLUMN_MAP),
            "mat_csl1": get_column_value_generic(item, "mat_csl1", QUANTITE_COLUMN_MAP),
            "prenom_nom_csl1": get_column_value_generic(item, "prenom_nom_csl1", QUANTITE_COLUMN_MAP),
            "mat_cf": get_column_value_generic(item, "mat_cf", QUANTITE_COLUMN_MAP),
            "prenom_nom_cf": get_column_value_generic(item, "prenom_nom_cf", QUANTITE_COLUMN_MAP),
            "mat_csl2": get_column_value_generic(item, "mat_csl2", QUANTITE_COLUMN_MAP),
            "created_at_monday": parse_datetime(item.get("created_at")),
            "updated_at_monday": parse_datetime(item.get("updated_at")),
        }

        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(Quantite(**data))

        total += 1

    db.commit()
    return total


def sync_copie_detection(db: Session):
    items = fetch_board_items(MONDAY_COPIE_DETECTION_BOARD_ID)
    groups = fetch_board_groups(MONDAY_COPIE_DETECTION_BOARD_ID)
    total = 0

    for item in items:
        monday_item_id = item["id"]
        
        existing = db.query(CopieDetection).filter(
            CopieDetection.monday_item_id == monday_item_id
        ).first()

        group_id, monday_group = resolve_monday_group(item, groups)
        print(f"Item: {item.get('name')}, Group ID: {group_id}, Monday Group: {monday_group}")

        data = {
            "monday_item_id": monday_item_id,
            "monday_group": monday_group,
            "item_name": item.get("name"),
            "date": parse_date(get_column_value_generic(item, "date", COPIE_DETECTION_COLUMN_MAP)),
            "semaine": parse_int(get_column_value_generic(item, "semaine", COPIE_DETECTION_COLUMN_MAP)),
            "ligne": get_column_value_generic(item, "ligne", COPIE_DETECTION_COLUMN_MAP),
            "bu": get_column_value_generic(item, "bu", COPIE_DETECTION_COLUMN_MAP),
            "poste": get_column_value_generic(item, "poste", COPIE_DETECTION_COLUMN_MAP),
            "equipe": get_column_value_generic(item, "equipe", COPIE_DETECTION_COLUMN_MAP),
            "nombre": parse_int(get_column_value_generic(item, "nombre", COPIE_DETECTION_COLUMN_MAP)) or 0,
            "mat_cf": get_column_value_generic(item, "mat_cf", COPIE_DETECTION_COLUMN_MAP),
            "created_at_monday": parse_datetime(item.get("created_at")),
            "updated_at_monday": parse_datetime(item.get("updated_at")),
        }

        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(CopieDetection(**data))

        total += 1

    db.commit()
    return total


def get_column_value_generic(item, field_name, column_map):
    """Generic version of get_column_value that accepts a column map"""
    wanted_id = column_map.get(field_name)
    
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

def sync_all_from_monday(db: Session):
    return {
        "defects": sync_detection_defauts(db),
        "defect_types": sync_defect_types(db),
        "workers_csl1": sync_workers_csl1(db),
        "workers_cf": sync_workers_cf(db),
        "quantite": sync_quantite(db),
        "copie_detection": sync_copie_detection(db),
    }
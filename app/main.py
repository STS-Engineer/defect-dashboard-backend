from datetime import date, datetime
from typing import Optional
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from .monday_client import fetch_items_by_group, fetch_board_groups
from .config import MONDAY_DETECTION_BOARD_ID


from .database import Base, engine, get_db, SessionLocal
from .models import Defect, User
from .schemas import (
    DefectCreate,
    DefectOut,
    DefectUpdate,
    ProdValidation,
    ProdRejection,
    QualValidation,
    QualRejection,
    UserLogin,
    ChangePasswordRequest,
    UserResponse,
)
from .sync_monday import sync_all_from_monday
from .dashboards import router as dashboards_router
from .lookups import router as lookups_router
from .monday_client import monday_request
from .config import MONDAY_QUANTITE_BOARD_ID, MONDAY_COPIE_DETECTION_BOARD_ID

DEFAULT_USERS = [
    {
        "username": "superviseur",
        "password": "superviseur123",
        "role": "Superviseur",
        "display_name": "Superviseur",
        "force_password_change": False,
    },
    {
        "username": "kawther.alaya",
        "password": "change123",
        "role": "Data Entry",
        "display_name": "Kawther Alaya",
        "force_password_change": True,
    },
    {
        "username": "abir.channoufi",
        "password": "change123",
        "role": "Data Entry",
        "display_name": "Abir Channoufi",
        "force_password_change": True,
    },
    {
        "username": "awatef.bougatef",
        "password": "change123",
        "role": "Data Entry",
        "display_name": "Awatef Bougatef",
        "force_password_change": True,
    },
    {
        "username": "bilel.bouzidi",
        "password": "change123",
        "role": "Responsable Production",
        "display_name": "Bilel Bouzidi",
        "force_password_change": True,
    },
    {
        "username": "lassaad.charaabi",
        "password": "change123",
        "role": "Responsable Qualite",
        "display_name": "Lassaad CHARAABI",
        "force_password_change": True,
    },
    {
        "username": "ghassen.hajjem",
        "password": "change123",
        "role": "Responsable Qualite",
        "display_name": "Ghassen HAJJEM",
        "force_password_change": True,
    },
    {
        "username": "montassar.benhadj",
        "password": "change123",
        "role": "Responsable Qualite",
        "display_name": "Montassar BEN HADJ MOHAMED",
        "force_password_change": True,
    },
]


def seed_default_users():
    db = SessionLocal()
    try:
        for user_data in DEFAULT_USERS:
            user = db.query(User).filter(
                User.username == user_data["username"]
            ).first()
            
            if user is None:
                db.add(User(**user_data))
                continue

            # Update existing user
            user.password = user_data["password"]
            user.role = user_data["role"]
            user.display_name = user_data["display_name"]
            user.force_password_change = user_data["force_password_change"]
            user.is_active = True

        db.commit()
        print("Users seeded successfully")
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
seed_default_users()

app = FastAPI(title="Zork Defect Dashboard API")

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        logger.info(f"← {request.method} {request.url.path} → {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"❌ Exception on {request.method} {request.url.path}: {str(e)}", exc_info=True)
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.include_router(dashboards_router, prefix="/dashboards", tags=["Dashboards"])
app.include_router(lookups_router, prefix="/lookups", tags=["Lookups"])


@app.get("/")
def root():
    return {"message": "Zork Defect Dashboard API running"}


@app.post("/auth/login")
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .filter(
            User.username == payload.username,
            User.password == payload.password,
            User.is_active.is_(True),
        )
        .first()
    )

    if user is None:
        return {"success": False, "message": "Identifiants incorrects"}

    return {
        "success": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "display_name": user.display_name,
            "force_password_change": user.force_password_change,
        },
    }


@app.put("/auth/change-password")
def change_password(payload: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()

    if user is None:
        return {"success": False, "message": "Utilisateur non trouvé"}

    user.password = payload.new_password
    user.force_password_change = False
    db.commit()

    return {"success": True, "message": "Mot de passe modifié avec succès"}


@app.get("/users/superviseurs", response_model=list[UserResponse])
def get_superviseurs(db: Session = Depends(get_db)):
    return (
        db.query(User)
        .filter(User.role == "Superviseur", User.is_active.is_(True))
        .order_by(User.display_name.asc())
        .all()
    )


@app.get("/users/data-entry", response_model=list[UserResponse])
def get_data_entry_users(db: Session = Depends(get_db)):
    return (
        db.query(User)
        .filter(User.role == "Data Entry", User.is_active.is_(True))
        .order_by(User.display_name.asc())
        .all()
    )


@app.post("/sync/monday")
def sync_monday(db: Session = Depends(get_db)):
    try:
        result = sync_all_from_monday(db)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"message": "sync done", "result": result}


def get_board_column_debug(board_id: int, board_name: str):
    query = """
    query ($board_id: ID!) {
      boards(ids: [$board_id]) {
        columns {
          id
          title
          type
        }
        items_page(limit: 50) {
          items {
            id
            name
            column_values {
              id
              type
              text
              value
              ... on BoardRelationValue {
                display_value
              }
              ... on MirrorValue {
                display_value
              }
              ... on FormulaValue {
                display_value
              }
            }
          }
        }
      }
    }
    """

    try:
        data = monday_request(query, {"board_id": str(board_id)})
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    boards = data.get("boards") or []
    if not boards:
        raise HTTPException(status_code=404, detail=f"Monday board {board_id} not found")

    board = boards[0]
    sample_items = board.get("items_page", {}).get("items", [])
    sample_item = sample_items[0] if sample_items else None
    sample_values = {}

    for item in sample_items:
        for col in item.get("column_values", []):
            column_id = col.get("id")
            sample_value = (
                col.get("display_value")
                or col.get("text")
                or col.get("value")
            )

            if column_id not in sample_values or sample_value not in [None, ""]:
                sample_values[column_id] = {
                    "item_id": item.get("id"),
                    "item_name": item.get("name"),
                    "column": col,
                }

            if sample_value not in [None, ""]:
                continue

    columns = {}
    for column in board.get("columns", []):
        column_id = column.get("id")
        sample_info = sample_values.get(column_id, {})
        sample = sample_info.get("column", {})
        sample_value = (
            sample.get("display_value")
            or sample.get("text")
            or sample.get("value")
        )

        columns[column_id] = {
            "title": column.get("title"),
            "type": column.get("type") or sample.get("type"),
            "sample_value": sample_value,
            "raw_value": sample.get("value"),
            "sample_item_id": sample_info.get("item_id"),
            "sample_item_name": sample_info.get("item_name"),
        }

    return {
        "board_name": board_name,
        "board_id": board_id,
        "sample_item_id": sample_item.get("id") if sample_item else None,
        "sample_item_name": sample_item.get("name") if sample_item else None,
        "columns": columns,
    }


@app.get("/debug/quantite-columns")
def debug_quantite_columns():
    return get_board_column_debug(MONDAY_QUANTITE_BOARD_ID, "Quantite")


@app.get("/debug/copie-detection-columns")
def debug_copie_detection_columns():
    return get_board_column_debug(MONDAY_COPIE_DETECTION_BOARD_ID, "Copie Detection")


@app.get("/defects", response_model=list[DefectOut])
def get_defects(
    status: Optional[str] = None,
    poste: Optional[str] = None,
    equipe: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Defect)
    if status:
        q = q.filter(Defect.status == status)
    if poste:
        q = q.filter(Defect.poste == poste)
    if equipe:
        q = q.filter(Defect.equipe == equipe)

    return q.order_by(Defect.id.desc()).limit(2000).all()


@app.post("/defects", response_model=DefectOut)
def create_defect(payload: DefectCreate, db: Session = Depends(get_db)):
    detection_date = payload.date_detection or date.today()

    defect = Defect(
        monday_item_id=None,
        monday_group=payload.monday_group,
        item_name="App entry",
        form_type=payload.form_type,
        is_nidec=payload.is_nidec,
        defaut=payload.defaut,
        date_detection=detection_date,
        semaine=payload.semaine,
        ligne=payload.ligne,
        bu=payload.bu,
        poste=payload.poste,
        equipe=payload.equipe,
        # Workflow fields
        status="OUVERT",
        securisation=payload.securisation,
        poste_occurrence=payload.poste_occurrence,
        poste_detection=payload.poste_detection,
        root_cause_occurrence=payload.root_cause_occurrence,
        root_cause_non_detection=payload.root_cause_non_detection,
        plan_action_occurrence=payload.plan_action_occurrence,
        plan_action_non_detection=payload.plan_action_non_detection,
        treatment_date=payload.treatment_date,
        treated_by_supervisor=payload.treated_by_supervisor,
        treatment_prod_validation_date=payload.treatment_prod_validation_date,
        prod_validator_name=payload.prod_validator_name,
        prod_validation_comment=payload.prod_validation_comment,
        treatment_quality_validation_date=payload.treatment_quality_validation_date,
        quality_validator_name=payload.quality_validator_name,
        quality_validation_comment=payload.quality_validation_comment,
        nombre=payload.nombre,
        mat_csl1=payload.mat_csl1,
        prenom_nom_csl1=payload.prenom_nom_csl1,
        mat_cf=payload.mat_cf,
        prenom_nom_cf=payload.prenom_nom_cf,
        quantite_controlee=payload.quantite_controlee,
        saisie_quantite_totale=payload.saisie_quantite_totale,
    )

    db.add(defect)
    db.commit()
    db.refresh(defect)

    return defect


@app.patch("/defects/{defect_id}", response_model=DefectOut)
def update_defect(defect_id: int, payload: DefectUpdate, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")

    defect.securisation = payload.securisation
    defect.poste_occurrence = payload.poste_occurrence
    defect.poste_detection = payload.poste_detection
    defect.root_cause_occurrence = payload.root_cause_occurrence
    defect.root_cause_non_detection = payload.root_cause_non_detection
    defect.plan_action_occurrence = payload.plan_action_occurrence
    defect.plan_action_non_detection = payload.plan_action_non_detection
    defect.treatment_date = date.today()
    defect.status = "ATT_VALIDATION_PROD"

    db.commit()
    db.refresh(defect)
    return defect



@app.post("/defects/{defect_id}/validate-production", response_model=DefectOut)
def validate_production(defect_id: int, payload: ProdValidation, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")
    if defect.status != "ATT_VALIDATION_PROD":
        raise HTTPException(status_code=400, detail="Defect not awaiting production validation")

    defect.treatment_prod_validation_date = datetime.utcnow()
    defect.prod_validator_name = payload.prod_validator_name
    defect.status = "ATT_VALIDATION_QUALITE"

    db.commit()
    db.refresh(defect)
    return defect


@app.post("/defects/{defect_id}/reject-production", response_model=DefectOut)
def reject_production(defect_id: int, payload: ProdRejection, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")
    if defect.status != "ATT_VALIDATION_PROD":
        raise HTTPException(status_code=400, detail="Defect not awaiting production validation")

    defect.prod_validator_name = payload.prod_validator_name
    defect.prod_validation_comment = payload.prod_validation_comment
    defect.status = "RETOUR_PRODUCTION"

    db.commit()
    db.refresh(defect)
    return defect


@app.post("/defects/{defect_id}/validate-quality", response_model=DefectOut)
def validate_quality(defect_id: int, payload: QualValidation, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")
    if defect.status != "ATT_VALIDATION_QUALITE":
        raise HTTPException(status_code=400, detail="Defect not awaiting quality validation")

    defect.treatment_quality_validation_date = datetime.utcnow()
    defect.quality_validator_name = payload.quality_validator_name
    defect.status = "CLOTURE"

    db.commit()
    db.refresh(defect)
    return defect


@app.post("/defects/{defect_id}/reject-quality", response_model=DefectOut)
def reject_quality(defect_id: int, payload: QualRejection, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")
    if defect.status != "ATT_VALIDATION_QUALITE":
        raise HTTPException(status_code=400, detail="Defect not awaiting quality validation")

    defect.quality_validator_name = payload.quality_validator_name
    defect.quality_validation_comment = payload.quality_validation_comment
    defect.status = "RETOUR_QUALITE"

    db.commit()
    db.refresh(defect)
    return defect


@app.delete("/defects/{defect_id}", status_code=204)
def delete_defect(defect_id: int, db: Session = Depends(get_db)):
    defect = db.query(Defect).filter(Defect.id == defect_id).first()
    if defect is None:
        raise HTTPException(status_code=404, detail="Defect not found")
    db.delete(defect)
    db.commit()
    return


@app.get("/debug/detection-columns")
def debug_detection_columns():

    groups = fetch_board_groups(MONDAY_DETECTION_BOARD_ID)

    if not groups:
        return {"error": "No groups found"}

    first_group_id = groups[0]["id"]

    items = fetch_items_by_group(
        MONDAY_DETECTION_BOARD_ID,
        first_group_id
    )

    if not items:
        return {"error": "No items found"}

    sample_item = items[0]

    columns = {}

    for col in sample_item.get("column_values", []):
        columns[col["id"]] = {
            "title": col.get("column", {}).get("title"),
            "type": col.get("type"),
            "sample_value": col.get("text"),
            "raw_value": col.get("value"),
        }

    return {
        "board_id": MONDAY_DETECTION_BOARD_ID,
        "sample_item_name": sample_item.get("name"),
        "columns": columns,
    }

from datetime import date
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Defect
from .schemas import DefectCreate, DefectOut
from .sync_monday import sync_all_from_monday
from .dashboards import router as dashboards_router
from .lookups import router as lookups_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Zork Defect Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboards_router, prefix="/dashboards", tags=["Dashboards"])
app.include_router(lookups_router, prefix="/lookups", tags=["Lookups"])


@app.get("/")
def root():
    return {"message": "Zork Defect Dashboard API running"}


@app.post("/sync/monday")
def sync_monday(db: Session = Depends(get_db)):
    result = sync_all_from_monday(db)
    return {"message": "sync done", "result": result}


@app.get("/defects", response_model=list[DefectOut])
def get_defects(db: Session = Depends(get_db)):
    return db.query(Defect).order_by(Defect.id.desc()).limit(2000).all()


@app.post("/defects", response_model=DefectOut)
def create_defect(payload: DefectCreate, db: Session = Depends(get_db)):
    detection_date = payload.date_detection or date.today()

    defect = Defect(
        monday_item_id=None,
        monday_group="App",
        item_name="App entry",
        form_type=payload.form_type,
        is_nidec=payload.is_nidec,
        defaut=payload.defaut,
        date_detection=detection_date,
        ligne=payload.ligne,
        bu=payload.bu,
        poste=payload.poste,
        equipe=payload.equipe,
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
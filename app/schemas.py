from datetime import date
from typing import Optional
from pydantic import BaseModel


class DefectCreate(BaseModel):
    form_type: Optional[str] = None
    is_nidec: bool = False

    defaut: Optional[str] = None
    date_detection: Optional[date] = None

    ligne: Optional[str] = None
    bu: Optional[str] = None
    poste: Optional[str] = None
    equipe: Optional[str] = None
    nombre: Optional[int] = 0

    mat_csl1: Optional[str] = None
    prenom_nom_csl1: Optional[str] = None

    mat_cf: Optional[str] = None
    prenom_nom_cf: Optional[str] = None

    quantite_controlee: Optional[int] = None
    saisie_quantite_totale: bool = False


class DefectOut(DefectCreate):
    id: int
    monday_item_id: Optional[str] = None
    monday_group: Optional[str] = None
    item_name: Optional[str] = None

    class Config:
        from_attributes = True


class LookupOption(BaseModel):
    value: str
    label: str
    extra: Optional[dict] = None
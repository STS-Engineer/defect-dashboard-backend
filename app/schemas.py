from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class UserLogin(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    username: str
    new_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    display_name: Optional[str] = None

    class Config:
        from_attributes = True


class DefectCreate(BaseModel):
    form_type: Optional[str] = None
    is_nidec: bool = False

    defaut: Optional[str] = None
    date_detection: Optional[date] = None
    semaine: Optional[int] = None

    ligne: Optional[str] = None
    bu: Optional[str] = None
    poste: Optional[str] = None
    equipe: Optional[str] = None
    nombre: Optional[int] = 0

    # Workflow fields
    status: Optional[str] = None
    securisation: Optional[str] = None
    poste_occurrence: Optional[str] = None
    poste_detection: Optional[str] = None
    root_cause_occurrence: Optional[str] = None
    root_cause_non_detection: Optional[str] = None
    plan_action_occurrence: Optional[str] = None
    plan_action_non_detection: Optional[str] = None
    treatment_date: Optional[date] = None
    treated_by_supervisor: bool = False
    treatment_prod_validation_date: Optional[datetime] = None
    prod_validator_name: Optional[str] = None
    prod_validation_comment: Optional[str] = None
    treatment_quality_validation_date: Optional[datetime] = None
    quality_validator_name: Optional[str] = None
    quality_validation_comment: Optional[str] = None

    mat_csl1: Optional[str] = None
    prenom_nom_csl1: Optional[str] = None

    mat_cf: Optional[str] = None
    prenom_nom_cf: Optional[str] = None

    monday_group: Optional[str] = None
    quantite_controlee: Optional[int] = None
    saisie_quantite_totale: bool = False


class DefectOut(DefectCreate):
    id: int
    monday_item_id: Optional[str] = None
    monday_group: Optional[str] = None
    item_name: Optional[str] = None
    treatment_status: Optional[str] = None
    superviseur: Optional[str] = None
    created_at_monday: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DefectUpdate(BaseModel):
    date_detection: Optional[date] = None
    bu: Optional[str] = None
    ligne: Optional[str] = None
    poste: Optional[str] = None
    equipe: Optional[str] = None
    defaut: Optional[str] = None
    nombre: Optional[int] = None
    mat_csl1: Optional[str] = None
    prenom_nom_csl1: Optional[str] = None
    mat_cf: Optional[str] = None
    prenom_nom_cf: Optional[str] = None
    quantite_controlee: Optional[int] = None
    # Workflow fields (optional for edit)
    securisation: Optional[str] = None
    poste_occurrence: Optional[str] = None
    poste_detection: Optional[str] = None
    root_cause_occurrence: Optional[str] = None
    root_cause_non_detection: Optional[str] = None
    plan_action_occurrence: Optional[str] = None
    plan_action_non_detection: Optional[str] = None


class ProdValidation(BaseModel):
    prod_validator_name: str


class ProdRejection(BaseModel):
    prod_validator_name: str
    prod_validation_comment: str


class QualValidation(BaseModel):
    quality_validator_name: str


class QualRejection(BaseModel):
    quality_validator_name: str
    quality_validation_comment: str


class LookupOption(BaseModel):
    value: str
    label: str
    extra: Optional[dict] = None


# Defect type schemas
class DefectTypeCreate(BaseModel):
    name: str
    monday_group: Optional[str] = None


class DefectTypeResponse(BaseModel):
    id: int
    monday_item_id: Optional[str] = None
    monday_group: Optional[str] = None
    name: Optional[str] = None


# Worker CSL1 schemas
class WorkerCSL1Create(BaseModel):
    matricule: str
    full_name: Optional[str] = None
    monday_group: Optional[str] = None


class WorkerCSL1Response(BaseModel):
    id: int
    monday_item_id: Optional[str] = None
    monday_group: Optional[str] = None
    matricule: Optional[str] = None
    full_name: Optional[str] = None


# Worker CF schemas
class WorkerCFCreate(BaseModel):
    matricule: str
    full_name: Optional[str] = None
    monday_group: Optional[str] = None


class WorkerCFResponse(BaseModel):
    id: int
    monday_item_id: Optional[str] = None
    monday_group: Optional[str] = None
    matricule: Optional[str] = None
    full_name: Optional[str] = None


# Quantite / CopieDetection responses should include monday_group when returned
class QuantiteResponse(BaseModel):
    id: int
    monday_item_id: Optional[str] = None
    monday_group: Optional[str] = None
    item_name: Optional[str] = None
    quantite_controlee: Optional[int] = None
    date: Optional[date] = None
    semaine: Optional[int] = None
    ligne: Optional[str] = None
    bu: Optional[str] = None
    equipe: Optional[str] = None
    mat_csl1: Optional[str] = None
    prenom_nom_csl1: Optional[str] = None
    mat_cf: Optional[str] = None
    prenom_nom_cf: Optional[str] = None
    mat_csl2: Optional[str] = None


class CopieDetectionResponse(BaseModel):
    id: int
    monday_item_id: Optional[str] = None
    monday_group: Optional[str] = None
    item_name: Optional[str] = None
    date: Optional[date] = None
    semaine: Optional[int] = None
    ligne: Optional[str] = None
    bu: Optional[str] = None
    poste: Optional[str] = None
    equipe: Optional[str] = None
    nombre: Optional[int] = None
    mat_cf: Optional[str] = None

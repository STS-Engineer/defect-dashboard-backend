from datetime import datetime

from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    display_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    force_password_change = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)



class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)

    monday_item_id = Column(String, unique=True, nullable=True)
    monday_group = Column(String, nullable=True)

    form_type = Column(String, nullable=True)
    is_nidec = Column(Boolean, default=False)

    item_name = Column(String, nullable=True)

    defaut = Column(String, nullable=True)
    date_detection = Column(Date, nullable=True)
    semaine = Column(Integer, nullable=True)
    ligne = Column(String, nullable=True)
    bu = Column(String, nullable=True)
    poste = Column(String, nullable=True)
    equipe = Column(String, nullable=True)
    nombre = Column(Integer, default=0)

    # Workflow fields
    status = Column(String, nullable=True)
    securisation = Column(String, nullable=True)
    poste_occurrence = Column(String, nullable=True)
    poste_detection = Column(String, nullable=True)
    root_cause_occurrence = Column(String, nullable=True)
    root_cause_non_detection = Column(String, nullable=True)
    plan_action_occurrence = Column(String, nullable=True)
    plan_action_non_detection = Column(String, nullable=True)
    treatment_date = Column(Date, nullable=True)
    treated_by_supervisor = Column(Boolean, default=False)
    treatment_prod_validation_date = Column(DateTime, nullable=True)
    prod_validator_name = Column(String, nullable=True)
    prod_validation_comment = Column(String, nullable=True)
    treatment_quality_validation_date = Column(DateTime, nullable=True)
    quality_validator_name = Column(String, nullable=True)
    quality_validation_comment = Column(String, nullable=True)

    mat_csl1 = Column(String, nullable=True)
    prenom_nom_csl1 = Column(String, nullable=True)

    mat_cf = Column(String, nullable=True)
    prenom_nom_cf = Column(String, nullable=True)

    quantite_controlee = Column(Integer, nullable=True)
    saisie_quantite_totale = Column(Boolean, default=False)

    created_at_monday = Column(DateTime, nullable=True)
    updated_at_monday = Column(DateTime, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    @property
    def treatment_status(self):
        return self.status

    @property
    def superviseur(self):
        return self.equipe
    


class DefectType(Base):
    __tablename__ = "defect_types"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    monday_group = Column(String, nullable=True)


class WorkerCSL1(Base):
    __tablename__ = "workers_csl1"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    matricule = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    monday_group = Column(String, nullable=True)


class WorkerCF(Base):
    __tablename__ = "workers_cf"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    matricule = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    monday_group = Column(String, nullable=True)


class Quantite(Base):
    __tablename__ = "quantite"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    monday_group = Column(String, nullable=True)
    item_name = Column(String, nullable=True)
    
    quantite_controlee = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    semaine = Column(Integer, nullable=True)
    ligne = Column(String, nullable=True)
    bu = Column(String, nullable=True)
    equipe = Column(String, nullable=True)
    mat_csl1 = Column(String, nullable=True)
    prenom_nom_csl1 = Column(String, nullable=True)
    mat_cf = Column(String, nullable=True)
    prenom_nom_cf = Column(String, nullable=True)
    mat_csl2 = Column(String, nullable=True)
    
    created_at_monday = Column(DateTime, nullable=True)
    updated_at_monday = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CopieDetection(Base):
    __tablename__ = "copie_detection"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    monday_group = Column(String, nullable=True)
    item_name = Column(String, nullable=True)
    
    date = Column(Date, nullable=True)
    semaine = Column(Integer, nullable=True)
    ligne = Column(String, nullable=True)
    bu = Column(String, nullable=True)
    poste = Column(String, nullable=True)
    equipe = Column(String, nullable=True)
    nombre = Column(Integer, default=0)
    mat_cf = Column(String, nullable=True)
    
    created_at_monday = Column(DateTime, nullable=True)
    updated_at_monday = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

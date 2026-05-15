from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base


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
    ligne = Column(String, nullable=True)
    bu = Column(String, nullable=True)
    poste = Column(String, nullable=True)
    equipe = Column(String, nullable=True)
    nombre = Column(Integer, default=0)

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


class DefectType(Base):
    __tablename__ = "defect_types"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)


class WorkerCSL1(Base):
    __tablename__ = "workers_csl1"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    matricule = Column(String, nullable=False)
    full_name = Column(String, nullable=True)


class WorkerCF(Base):
    __tablename__ = "workers_cf"

    id = Column(Integer, primary_key=True, index=True)
    monday_item_id = Column(String, unique=True, nullable=True)
    matricule = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
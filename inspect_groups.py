from app.database import SessionLocal
from app.models import Defect, DefectType, WorkerCSL1, WorkerCF, Quantite, CopieDetection

db = SessionLocal()
for model in [Defect, DefectType, WorkerCSL1, WorkerCF, Quantite, CopieDetection]:
    vals = db.query(model.monday_group).distinct().limit(20).all()
    print(model.__tablename__, [v[0] for v in vals])

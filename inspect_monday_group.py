from app.database import SessionLocal
from app.models import Defect, DefectType, WorkerCSL1, WorkerCF, Quantite, CopieDetection

db = SessionLocal()
for model in [Defect, DefectType, WorkerCSL1, WorkerCF, Quantite, CopieDetection]:
    total = db.query(model).count()
    non_null = db.query(model).filter(model.monday_group.isnot(None)).count()
    print(model.__tablename__, 'total=', total, 'monday_group non-null=', non_null)

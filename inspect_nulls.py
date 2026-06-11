from app.database import SessionLocal
from app.models import WorkerCF, Quantite

db = SessionLocal()
print('workers_cf null monday_group rows')
for r in db.query(WorkerCF).filter(WorkerCF.monday_group.is_(None)).all():
    print(r.id, r.monday_item_id, r.matricule, r.full_name)
print('\nquantite null monday_group rows')
for r in db.query(Quantite).filter(Quantite.monday_group.is_(None)).limit(10).all():
    print(r.id, r.monday_item_id, r.item_name, r.date)

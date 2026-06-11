from time import perf_counter
from app.sync_monday import sync_workers_csl1, sync_workers_cf, sync_defect_types, sync_quantite, sync_copie_detection
from app.database import SessionLocal
import traceback

db = SessionLocal()
for fn in [sync_workers_csl1, sync_workers_cf, sync_defect_types, sync_quantite, sync_copie_detection]:
    t0 = perf_counter()
    try:
        count = fn(db)
        print(fn.__name__, '=>', count, 'in', perf_counter() - t0)
    except Exception as e:
        print(fn.__name__, 'FAILED', type(e).__name__, e)
        traceback.print_exc()

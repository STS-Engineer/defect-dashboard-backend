from app.monday_client import fetch_board_items
from app.config import MONDAY_QUANTITE_BOARD_ID, MONDAY_CF_BOARD_ID

ids = {'quantite': ['12036286711','12037062178','12036497644'], 'workers_cf':['12037470801']}
for board_name, board_id in [('quantite', MONDAY_QUANTITE_BOARD_ID), ('workers_cf', MONDAY_CF_BOARD_ID)]:
    items = fetch_board_items(board_id)
    print('\nboard', board_name, 'total items', len(items))
    for item_id in ids.get(board_name, []):
        found = [item for item in items if item.get('id') == item_id]
        print('id', item_id, 'found', len(found))
        if found:
            item = found[0]
            print('name', item.get('name'))
            print('group', item.get('group'))
            print('cols', [(col.get('id'), col.get('text'), col.get('display_value')) for col in item.get('column_values', [])][:5])

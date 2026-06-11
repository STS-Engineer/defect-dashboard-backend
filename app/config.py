import os
from dotenv import load_dotenv

load_dotenv()

MONDAY_DETECTION_BOARD_ID = int(os.getenv("MONDAY_DETECTION_BOARD_ID", "7323166812"))
MONDAY_TYPE_DEFAUTS_BOARD_ID = int(os.getenv("MONDAY_TYPE_DEFAUTS_BOARD_ID", "7331010926"))
MONDAY_CSL1_BOARD_ID = int(os.getenv("MONDAY_CSL1_BOARD_ID", "7325349457"))
MONDAY_CF_BOARD_ID = int(os.getenv("MONDAY_CF_BOARD_ID", "7325338826"))
MONDAY_QUANTITE_BOARD_ID = int(os.getenv("MONDAY_QUANTITE_BOARD_ID", "7860870973"))
MONDAY_COPIE_DETECTION_BOARD_ID = int(os.getenv("MONDAY_COPIE_DETECTION_BOARD_ID", "7415653956"))

MONDAY_DETECTION_GROUPS = [
    "Semaine",
    "Archive",
    "2024",
]

DETECTION_COLUMN_MAP = {
    "defaut": "connecter_les_tableaux4__1",
    "date_detection": "date__1",
    "semaine": "formule__1",
    "ligne": "statut__1",
    "bu": "statut2__1",
    "poste": "statut5__1",
    "equipe": "status",
    "nombre": "chiffres__1",
    "mat_csl1": "connecter_les_tableaux__1",
    "prenom_nom_csl1": "miroir2__1",
    "mat_cf": "connecter_les_tableaux8__1",
    "prenom_nom_cf": "miroir_10__1",
    "saisie_quantite_totale": "case___cocher__1",
}

BU_OPTIONS = ["VALEO", "NIDEC"]

POSTE_OPTIONS = ["CSL1", "CF", "Test électrique"]

EQUIPE_OPTIONS = ["Matin", "Après-midi", "Nuit"]

LIGNE_OPTIONS = [
    "FLEX 1",
    "FLEX 2",
    "FLEX 3",
    "FP",
    "GEN2 R",
    "GEN2 C",
    "MNG2-1",
    "MNG2-2",
    "CM3",
    "CM4",
    "BUA",
    "VM4 1",
    "VM4 2",
]

QUANTITE_COLUMN_MAP = {
    "quantite_controlee": "chiffres51__1",  # ✅ FIXED
    "date": "date__1",
    "semaine": "formule__1",  # ✅ FIXED
    "ligne": "statut__1",
    "bu": "statut2__1",
    "equipe": "status",
    "mat_csl1": "connecter_les_tableaux__1",
    "prenom_nom_csl1": "miroir2__1",
    "mat_cf": "connecter_les_tableaux8__1",
    "prenom_nom_cf": "miroir_10__1",
    "mat_csl2": "chiffres9__1",  # ✅ FIXED
}

COPIE_DETECTION_COLUMN_MAP = {
    "date": "date__1",
    "semaine": "formule__1",  # ✅ FIXED
    "ligne": "statut__1",
    "bu": "statut2__1",
    "poste": "statut5__1",
    "equipe": "status",
    "nombre": "chiffres__1",
    "mat_cf": "chiffres8__1",  # ✅ FIXED
}
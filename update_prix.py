import openpyxl
import re
import json

FICHIER_EXCEL = 'ELIOS_2026_DB_3.xlsx'
ONGLET        = 'ELIOS_2026_DB'
FICHIER_HTML  = 'index.html'

# Mapping par (categorie, sous_categorie) — prioritaire sur le mapping par catégorie seule
SECTION_MAP_DETAIL = {
    ('Accessoires', 'Couvercles et articles d\'installation')          : 'COUVERCLES ET INSTALLATION',
    ('Accessoires', 'Options électriques')                             : 'OPTIONS ÉLECTRIQUES',
    ('Accessoires', 'Supports au sol')                                 : 'RACK AU SOL',
    ('Accessoires', 'Supports muraux (vendu à l\'unité / 2 requis)')   : 'SUPPORTS MURAUX',
    ('Accessoires', 'Supports muraux et embouts')                      : 'SUPPORTS MURAUX',
    ('Central-Elios UTA', 'Éléments chauffants électriques')           : 'ÉLÉMENTS CHAUFFANTS',
}

# Mapping par catégorie seule (fallback)
SECTION_MAP = {
    'Murale -20C'                      : 'MURALE À -20°C',
    'Murale -30C'                      : 'MURALE À -30°C',
    'Cassette Simple (1 voie)'         : 'CASSETTE SIMPLE',
    'Cassette 4 Voies'                 : 'CASSETTE 4 VOIES',
    'Cassette 4 Voies Commercial Léger': 'CASSETTE COMMERCIAL LÉGER',
    'Gainable Moyenne Pression'        : 'GAINABLE MOYENNE PRESSION',
    'Gainable Commercial Léger'        : 'GAINABLE COMMERCIAL LÉGER',
    'Console (Montage au sol)'         : 'CONSOLE',
    'Central-Elios UTA'                : 'CENTRAL-ELIOS UTA',
    'Accessoires'                      : 'ACCESSOIRES',
}

# Ordre d'affichage des sections dans l'app
SECTION_ORDER = [
    'MURALE À -20°C',
    'MURALE À -30°C',
    'CASSETTE SIMPLE',
    'CASSETTE 4 VOIES',
    'CASSETTE COMMERCIAL LÉGER',
    'GAINABLE MOYENNE PRESSION',
    'GAINABLE COMMERCIAL LÉGER',
    'CONSOLE',
    'CENTRAL-ELIOS UTA',
    'ÉLÉMENTS CHAUFFANTS',
    'GRILLES CASSETTE',
    'COUVERCLES ET INSTALLATION',
    'OPTIONS ÉLECTRIQUES',
    'RACK AU SOL',
    'SUPPORTS MURAUX',
    'ACCESSOIRES',
]

# --- Lecture du Excel ---
wb = openpyxl.load_workbook(FICHIER_EXCEL, data_only=True)
ws = wb[ONGLET]

rows = []
skipped = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    categorie   = row[0]
    sous_cat    = row[1]
    mbh         = row[3]
    no_modele   = row[4]
    description = row[5]
    ahri        = row[6]
    disjoncteur  = row[8]
    lignes_od    = row[9]
    prix_coutant = row[12]
    subvention   = row[13]
    lien_master  = row[14] if len(row) > 14 else None

    if not no_modele or prix_coutant is None:
        skipped += 1
        continue
    try:
        prix_coutant = float(str(prix_coutant).replace(',', '.'))
    except (ValueError, TypeError):
        skipped += 1
        continue

    section  = SECTION_MAP_DETAIL.get((categorie, sous_cat),
               SECTION_MAP.get(categorie, str(categorie).upper() if categorie else 'AUTRE'))
    # Grilles identifiables par le numéro de modèle (peu importe la catégorie Excel)
    if 'GRL' in str(no_modele).upper():
        section = 'GRILLES CASSETTE'
    mbtu     = str(mbh) if mbh and str(mbh).strip() not in ('', '—') else '—'
    ahri_str = str(int(ahri)) if isinstance(ahri, (int, float)) else (str(ahri) if ahri else '—')
    sub      = int(subvention) if isinstance(subvention, (int, float)) and subvention else None
    prix     = round(prix_coutant)

    lien       = str(lien_master).strip() if lien_master else None
    disco      = str(disjoncteur).strip() if disjoncteur else None
    tuyau      = str(lignes_od).strip() if lignes_od else None
    dim        = str(row[10]).strip() if row[10] else None
    type_unite = str(row[2]).strip().lower() if row[2] else ''
    type_ordre = 0 if 'int' in type_unite else 1
    rows.append([section, mbtu, ahri_str, no_modele, description, prix, sub, lien, disco, tuyau, type_ordre, dim])

# --- Tri : section → MBH croissant → AHRI → intérieure avant extérieure ---
def sort_key(r):
    sec_idx = SECTION_ORDER.index(r[0]) if r[0] in SECTION_ORDER else 99
    try:
        mbtu_num = float(str(r[1]).split()[0])
    except Exception:
        mbtu_num = 999
    return (sec_idx, mbtu_num, r[2], r[10])

rows.sort(key=sort_key)
rows = [r[:10] + [r[11]] for r in rows]  # retire le champ type_ordre temporaire, garde dim

# --- Génération du JS ---
def js_row(r):
    section     = json.dumps(r[0], ensure_ascii=False)
    mbtu        = json.dumps(r[1], ensure_ascii=False)
    ahri        = json.dumps(r[2], ensure_ascii=False)
    modele      = json.dumps(r[3], ensure_ascii=False)
    description = json.dumps(r[4], ensure_ascii=False)
    prix        = str(r[5])
    sub         = str(r[6]) if r[6] is not None else 'null'
    lien        = json.dumps(r[7], ensure_ascii=False) if r[7] else 'null'
    disco       = json.dumps(r[8], ensure_ascii=False) if r[8] else 'null'
    tuyau       = json.dumps(r[9], ensure_ascii=False) if r[9] else 'null'
    dim         = json.dumps(r[10], ensure_ascii=False) if r[10] else 'null'
    return f'  [{section},{mbtu},{ahri},{modele},{description},{prix},{sub},{lien},{disco},{tuyau},{dim}]'

# Prix tuyauterie par diamètre ($/pi, base 164 pi)
PRIX_TUYAUX = {
    '1/4': round(300 / 164, 2),   # 1.83 $/pi
    '3/8': round(450 / 164, 2),   # 2.74 $/pi
    '1/2': round(600 / 164, 2),   # 3.66 $/pi
    '5/8': round(790 / 164, 2),   # 4.82 $/pi
}

raw_data_js    = 'const rawData = [\n' + ',\n'.join(js_row(r) for r in rows) + '\n];'
section_ord_js = 'const sectionOrder = ' + json.dumps(SECTION_ORDER, ensure_ascii=False) + ';'
tuyau_prix_js  = 'const tuyauPrix = ' + json.dumps(PRIX_TUYAUX) + ';'

# --- Mise à jour de index.html ---
with open(FICHIER_HTML, 'r', encoding='utf-8') as f:
    html = f.read()

html = re.sub(r'const rawData = \[.*?\];', raw_data_js, html, flags=re.DOTALL)
html = re.sub(r'const sectionOrder = \[.*?\];', section_ord_js, html)
html = re.sub(r'const tuyauPrix = \{.*?\};', tuyau_prix_js, html)

with open(FICHIER_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'OK  {len(rows)} produits importes ({skipped} lignes ignorees)')
print(f'Sections : {", ".join(SECTION_ORDER)}')
print(f'index.html mis a jour -- fais un git push pour publier')

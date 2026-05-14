# ELIOS 2026 — Liste de Prix

Application web interactive de liste de prix pour techniciens, destinée à consulter rapidement les prix et subventions des thermopompes ELIOS.

## Fichiers du projet

| Fichier | Rôle |
|---|---|
| `Liste prix.html` | Application principale (seul fichier à modifier) |
| `ELIOS_2026_v2.xlsx` | Source des données de prix |
| `Elios_R-454B_FEBRUARY_2026_EN.pdf` | Catalogue technique anglais de référence |

## Application principale — `Liste prix.html`

Page HTML autonome (aucune dépendance externe sauf Google Fonts). Toute la logique, les données et le CSS sont dans ce fichier unique.

### Données

Tableau JavaScript `rawData` — chaque ligne : `[section, mbtu, ahri, modèle, description, prix, subvention]`

- `prix` : nombre en CAD (toujours présent)
- `subvention` : nombre en CAD ou `null` si aucune subvention

### Sections de produits (dans l'ordre d'affichage)

1. MURALE (9–36 MBH, 115 V et 230 V)
2. MURALE MULTIZONE (9–33 MBH)
3. CASSETTE SIMPLE (12–18 MBH)
4. CASSETTE 2-4 VOIES (9–18 MBH)
5. CASSETTE 4 VOIES (24 MBH)
6. CASSETTE 3-4 VOIES (36–48 MBH)
7. GRILLE (accessoire cassette)
8. UNITÉ GAINABLE (9–60 MBH)
9. CONSOLE (12 MBH)
10. WALL UTA (18–36 MBH)
11. UTA - ELECTRIC HEATER (accessoire)
12. PANCAKE (18–36 MBH)
13. PANCAKE ELECTRIC HEATER (accessoire)
14. FLOOR CEILING MOUNT (36–48 MBH)

### Interface

**Onglets**
- `📊 Vue Résumé` — produits groupés par section, avec bascule cartes / tableau
- `📋 Liste Complète` — tableau plat de toutes les lignes

**Filtres (barre persistante)**
- Recherche texte libre (modèle, description, AHRI)
- Filtre par section
- Filtre par puissance (MBH)
- Filtre par subvention (avec / sans)
- Bouton réinitialiser

**Affichage des subventions**
- Fond vert mint (`#d4edda`) avec texte vert foncé (`#1a5c2e`)
- Classe CSS `.price-tag.sub` (vue cartes) et `.td-sub` (vue tableau)
- Le compteur dans la barre de stats affiche le nombre de lignes avec subvention en vert

### Design responsive

- Mobile (`≤ 600px`) : padding réduit sur header, filtres et contenu
- Tablette / bureau : grille de cartes auto-fill `minmax(290px, 1fr)`
- Header sticky avec z-index 100
- Polices : DM Sans (interface) + DM Mono (modèles, prix, AHRI)

### Palette de couleurs

| Variable | Valeur | Usage |
|---|---|---|
| `--navy` | `#0f2044` | Header, titres de section |
| `--blue` | `#1a4a8a` | En-têtes tableau |
| `--sky` | `#2d7dd2` | Numéros de modèle |
| `--mint` | `#d4edda` | Fond subvention |
| `--mint-text` | `#1a5c2e` | Texte subvention |
| `--accent` | `#f0a500` | Badge CAD, puissance MBH |

## Informations produit

- Réfrigérant : **R-454B**
- Devise : **CAD**
- Révision : **30 avril 2026**
- Les unités sont vendues par paires (unité intérieure + unité extérieure), regroupées par numéro AHRI

## Modifications courantes

**Ajouter un produit** : ajouter une ligne dans `rawData` en respectant le format `[section, mbtu, ahri, modèle, description, prix, subvention_ou_null]`.

**Modifier une subvention** : trouver la ligne par numéro de modèle dans `rawData`, mettre à jour le 7e élément (index 6).

**Ajouter une section** : ajouter le nom dans le tableau `sectionOrder` à la position désirée pour contrôler l'ordre d'affichage.

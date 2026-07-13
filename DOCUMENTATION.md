# Documentation Technique — AI Report Studio

## Architecture Générale

```
┌──────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│                    http://localhost:3000                          │
│                                                                   │
│  Pages :                                                          │
│    /              → UploadForm (upload CSV/JSON)                  │
│    /history       → ReportHistory (liste des rapports)            │
│    /report/[id]   → ReportDetail (détail d'un rapport)            │
│                                                                   │
│  Les appels fetch("/api/...") sont automatiquement                │
│  redirigés vers le backend via un proxy (next.config.js).         │
├────────────────────── API Proxy (rewrite) ───────────────────────┤
│                                                                   │
│  next.config.js :                                                 │
│    source: "/api/:path*" → destination: "http://localhost:8000/api/:path*"   │
│                                                                   │
│  Avantage : pas de CORS, pas d'URL du backend en dur.            │
│                                                                   │
├───────────────────────── BACKEND (FastAPI) ───────────────────────┤
│                    http://localhost:8000                           │
│                                                                   │
│  main.py            → Routes API                                  │
│  models.py          → Schémas Pydantic (GenerateReportRequest,    │
│                        Dataset, Report, ReportListItem)            │
│  neon_client.py     → Accès à la base Neon (PostgreSQL)           │
│  supabase_client.py → (optionnel) Accès à Supabase Storage        │
│  stats.py           → Calculs mathématiques (moyenne, somme...)   │
│  ai.py              → Génération du texte via Gemini (IA)         │
│  config.py          → Variables d'environnement (.env)            │
│  templates/         → Templates Markdown pour les rapports        │
│  storage/uploads/   → Fichiers CSV/JSON uploadés                  │
│                                                                   │
├────────────────────────── DATABASE (Neon) ────────────────────────┤
│                                                                   │
│  PostgreSQL serverless                                            │
│  Tables : datasets, reports                                       │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Stack Technique

### Backend : FastAPI (Python)

**Qu'est-ce que c'est ?**  
Un framework web Python moderne, rapide (asynchrone), avec validation automatique des données via Pydantic.

**Pourquoi FastAPI ?**
- Support natif de `async/await` → idéal pour les appels à la DB et à l'IA
- Génération automatique de documentation Swagger (http://localhost:8000/docs)
- Validation des entrées/sorties avec Pydantic
- Performances proches de Node.js/Go

**Concepts clés :**
- `@api_router.get("/reports")` → déclare une route GET
- `async def` → fonction asynchrone (peut utiliser `await`)
- `HTTPException` → retourne une erreur HTTP propre
- `UploadFile` → gère l'upload de fichiers

---

### Frontend : Next.js (React + TypeScript)

**Qu'est-ce que c'est ?**  
Framework React avec rendu serveur, routing basé sur le système de fichiers.

**Concepts clés :**
- **App Router** : chaque dossier correspond à une route. Ex : `app/report/[id]/page.tsx` → route `/report/42`
- **"use client"** : composant à exécuter côté navigateur (nécessaire pour `useState`, `useEffect`, `onClick`)
- **Composant serveur (par défaut)** : exécuté côté serveur, parfait pour le fetch initial
- **Proxy API** : `next.config.js` rewrite pour rediriger `/api/*` vers le backend

---

### Base de données : Neon (PostgreSQL serverless)

**Qu'est-ce que c'est ?**  
PostgreSQL hébergé, serverless (pas de serveur à gérer), avec une couche gratuite généreuse.

**Pourquoi Neon ?**
- PostgreSQL standard → SQL classique, fiable
- Serverless → pas de maintenance, scaling automatique
- Compatible avec `asyncpg` (driver Python asynchrone)

**Tables :**

```sql
datasets
├── id          SERIAL PRIMARY KEY   -- Auto-incrémenté
├── filename    VARCHAR(255)         -- Nom du fichier original
├── file_path   VARCHAR(255)         -- Chemin de stockage local
├── columns     JSONB                -- Liste des colonnes du CSV
└── created_at  TIMESTAMP            -- Date d'upload

reports
├── id          SERIAL PRIMARY KEY   -- Auto-incrémenté
├── dataset_id  INTEGER → datasets(id)  -- Clé étrangère
├── template    VARCHAR(50)          -- Template utilisé
├── title       VARCHAR(255)         -- Titre du rapport
├── content     TEXT                 -- Contenu Markdown généré
├── status      VARCHAR(20)          -- completed / pending / failed
├── created_at  TIMESTAMP            -- Date de création
└── updated_at  TIMESTAMP            -- Dernière modification
```

---

### IA : Google Gemini

**Rôle :** Générer le texte narratif du rapport (prose, analyse, recommendations).

**Principe fondamental :**  
> **Python calcule les chiffres, l'IA écrit le texte. L'IA ne fait jamais d'arithmétique.**

1. `stats.py` lit le CSV/JSON et calcule les métriques (moyenne, somme, top produit, comptage...)
2. `ai.py` envoie ces métriques + un template Markdown à Gemini
3. Gemini remplit les `{{placeholders}}` du template avec les vraies valeurs
4. Le résultat est un rapport Markdown complet

---

## Data Flow Détaillé

### Use Case : Upload d'un fichier CSV

```
1. Utilisateur glisse un fichier CSV dans UploadForm
       │
2. UploadForm.tsx → lit le fichier avec FileReader
       │
3. fetch POST /api/datasets (multipart/form-data)
       │  [Next.js proxy → localhost:8000/api/datasets]
       ▼
4. Backend main.py → upload_file()
       │
       ├─ Vérifie l'extension (.csv ou .json)
       ├─ Vérifie la taille (< 10 MB)
       ├─ Détecte les colonnes + 5 premières lignes (preview)
       ├─ Sauvegarde le fichier dans storage/uploads/
       └─ Sauvegarde les métadonnées dans Neon (table datasets)
       │
       ▼
5. Retourne { id, filename, columns, preview }
       │
       ▼
6. Frontend affiche l'aperçu du fichier (colonnes, premières lignes)
```

### Use Case : Génération d'un rapport

```
1. Utilisateur sélectionne un template sur la page d'accueil
       │
2. fetch POST /api/reports  { dataset_id: 7, template: "weekly_digest" }
       │
       ▼
3. Backend main.py → generate_report()
       │
       ├─ Récupère les infos du dataset depuis Neon (get_dataset)
       ├─ Lit le template Markdown (templates/weekly_digest.md)
       ├─ Lit le fichier CSV/JSON depuis storage/uploads/
       ├─ Appelle stats.compute_metrics() → calcule les stats
       ├─ Appelle ai.ask() → envoie stats + template à Gemini
       │     └─ Gemini → retourne le rapport en Markdown
       └─ Sauvegarde le rapport dans Neon (table reports)
       │
       ▼
4. Retourne { id: 1 }
       │
       ▼
5. Frontend redirige vers /report/1
```

### Use Case : Voir le détail d'un rapport

```
1. Utilisateur clique sur l'icône 👁️ dans la liste des rapports
       │
2. Next.js router.push("/report/42")
       │
       ▼
3. page.tsx lit params.id = "42"
       │
4. Affiche <ReportDetail reportId="42" />
       │
       ▼
5. ReportDetail.tsx (composant client)
       │
       ├─ useEffect appelle fetchReport("42")
       │     └─ fetch GET /api/reports/42
       │         └─ Backend : SELECT * FROM reports WHERE id = 42
       │
       ├─ Pendant le chargement : spinner overlay (bg-black/50)
       │
       ├─ Si erreur : message d'erreur
       │
       └─ Si succès : affiche les données
            ├─ Titre (h2)
            ├─ Métadonnées (template, date, status)
            └─ Contenu Markdown (dans une balise <pre>)
```

---

## Détail des Routes API

### `GET /api/health`
**Rôle :** Vérifier que le backend tourne.  
**Retour :** `{ "ok": true }`

### `POST /api/datasets`
**Rôle :** Uploader un fichier CSV/JSON.  
**Entrée :** `multipart/form-data` avec un champ `file`.  
**Validations :**
- Extension : `.csv` ou `.json`
- Taille max : 10 MB  
**Retour :**
```json
{
  "id": 7,
  "filename": "sales_data.csv",
  "columns": ["name", "sales", "region", "date"],
  "preview": [
    { "name": "Product A", "sales": "1200", "region": "North", "date": "2026-07-01" },
    ...
  ]
}
```

### `POST /api/reports`
**Rôle :** Générer un rapport à partir d'un dataset + template.  
**Entrée :**
```json
{
  "dataset_id": 7,
  "template": "weekly_digest"
}
```
**Étapes :**
1. Récupérer le dataset depuis Neon
2. Lire le template Markdown
3. Lire le fichier uploadé
4. Calculer les stats (stats.py)
5. Appeler l'IA (ai.py)
6. Sauvegarder dans Neon
**Retour :** `{ "id": 1 }`

### `GET /api/reports`
**Rôle :** Lister tous les rapports (pour la page d'historique).  
**Retour :** Tableau de rapports.

### `GET /api/reports/{id}`
**Rôle :** Récupérer un rapport spécifique.  
**Paramètre :** `id` → converti en `int` automatiquement par FastAPI.  
**Retour :**
```json
{
  "id": 1,
  "dataset_id": 7,
  "template": "weekly_digest",
  "title": "Report for Dataset #7",
  "content": "# Weekly Digest\n\n## Sales Summary\n- **Total Sales**: $18,100.00\n...",
  "status": "completed",
  "created_at": "2026-07-03T21:34:14.159977",
  "updated_at": "2026-07-03T21:34:14.159977"
}
```

---

## Pièges Courants et Solutions

### 1. `res.json()` sans `await`
```typescript
// ❌ BUG : data = Promise, pas les vraies données
const data = res.json()

// ✅ CORRECT : on attend la résolution de la promesse
const data = await res.json()
```
**Pourquoi ?** `res.json()` lit le flux HTTP (qui arrive en paquets). Ça prend du temps → c'est asynchrone → retourne une Promise.

### 2. `useState(null)` + accès direct aux propriétés
```typescript
const [report, setReport] = useState(null)

// ❌ BUG au premier render : report est null → report.title crash
return <h1>{report.title}</h1>

// ✅ CORRECT : protéger avec un guard
if (!report) return <div>Loading...</div>
return <h1>{report.title}</h1>
```
**Pourquoi ?** React exécute le `return` avant que le fetch soit terminé. `report` est `null` → `null.title` plante.

### 3. Ordre des routes FastAPI
```python
# ❌ BUG : /reports/{report_id} peut être "mangé" par /reports si mal ordonné
@api_router.get("/reports/{report_id}")
@api_router.get("/reports")

# ✅ CORRECT : FastAPI utilise l'ordre de déclaration
# Mettre les routes spécifiques AVANT les routes génériques
```
**Note :** Avec FastAPI, l'ordre n'est normalement pas un problème car FastAPI match les routes les plus spécifiques d'abord. Mais mieux vaut garder une bonne pratique.

### 4. Les dates PostgreSQL
```python
# Les dates retournées par asyncpg sont des objets datetime
# Pas sérialisables directement en JSON → conversion nécessaire
if report.get("created_at"):
    report["created_at"] = report["created_at"].isoformat()
if report.get("updated_at"):
    report["updated_at"] = report["updated_at"].isoformat()
```

---

## Commandes Utiles

```bash
# Démarrer le backend (port 8000)
cd backend
python -m uvicorn main:app --reload

# Démarrer le frontend (port 3000)
cd frontend
npm run dev

# Démarrer les deux en même temps (PowerShell)
.\dev.ps1

# Voir la doc Swagger
# http://localhost:8000/docs

# Build du frontend pour production
cd frontend && npx next build
```

---

## Checklist pour Ajouter une Nouvelle Route

- [ ] Ajouter la route dans `backend/main.py` avec `@api_router`
- [ ] Ajouter la fonction dans `backend/neon_client.py` si accès DB
- [ ] Redémarrer le backend (`--reload` le fait automatiquement)
- [ ] Ajouter le type dans `frontend/types/api.d.ts` si besoin
- [ ] Ajouter la fonction dans `frontend/lib/api.ts` si besoin
- [ ] Utiliser `await res.json()` dans le frontend
- [ ] Gérer l'état loading/error dans le composant
- [ ] Protéger le JSX avec `if (!data) return ...`
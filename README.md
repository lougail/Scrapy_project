# Books Scraper - Système de Veille Concurrentielle

Projet de scraping et d'analyse de données pour books.toscrape.com.

Système automatisé permettant de collecter, nettoyer, stocker et exposer via API les données des livres du site books.toscrape.com.

## Description du projet

Dans le cadre d'une veille concurrentielle pour une enseigne de vente de livres, ce projet met en place un système capable de :

- Collecter automatiquement les informations des livres (titres, prix, notes clients, disponibilité, catégories)
- Nettoyer et homogénéiser les données (formats de prix, conversion des notes, gestion des doublons)
- Stocker les données dans une base relationnelle SQLite
- Exposer les données via une API REST
- Permettre l'analyse des données (prix moyens, top catégories, statistiques)

## Architecture du projet

```
scrapy_project/
├── src/
│   ├── database/              # Module base de données
│   │   ├── connection.py      # Gestion connexion SQLite
│   │   └── book_repository.py # Accès aux données (pattern Repository)
│   │
│   ├── api/                   # Module API REST
│   │   └── main.py            # Application FastAPI
│   │
│   └── scraper/               # Module scraping
│       └── bookstoscrape_Scraper/
│           ├── spiders/       # Spiders Scrapy
│           ├── items.py       # Définition des données
│           ├── pipelines.py   # Nettoyage des données
│           └── settings.py    # Configuration
│
├── data/
│   └── books.db               # Base de données SQLite
│
├── requirements.txt           # Dépendances Python
└── README.md                  # Documentation
```

### Principes d'architecture

Le projet respecte les principes de **Clean Code** et **Clean Architecture** :

- **Séparation des responsabilités** : Chaque module a une fonction claire (scraping, database, API)
- **Orienté objet** : Utilisation de classes avec responsabilités uniques
- **Réutilisabilité** : Code modulaire et facilement testable
- **Pattern Repository** : Abstraction de l'accès aux données

## Installation

### Prérequis

- Python 3.8+
- pip
- Git

### Étapes d'installation

```bash
# 1. Cloner le repository
git clone https://github.com/lougail/Scrapy_project.git
cd scrapy_project

# 2. Créer un environnement virtuel
python -m venv venv

# 3. Activer l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur Mac/Linux :
source venv/bin/activate

# 4. Installer les dépendances
pip install -r requirements.txt
```

## Utilisation

### 1. Scraping des données

Lancer le spider pour collecter les données :

```bash
cd src/scraper/bookstoscrape_Scraper
scrapy crawl booktoscrape_Scraper
```

Le spider va :

- Parcourir toutes les pages du site
- Extraire les données de chaque livre
- Nettoyer automatiquement les données (prix, notes, disponibilité)
- Détecter et éliminer les doublons
- Stocker dans `data/books.db`

**Durée estimée** : ~2-3 minutes pour ~1000 livres

### 2. Lancer l'API REST

Depuis la racine du projet :

```bash
uvicorn src.api.main:app --reload
```

L'API sera accessible sur : <http://localhost:8000>

**Documentation interactive** : <http://localhost:8000/docs>

### 3. Requêtes SQL directes

Pour des analyses personnalisées, vous pouvez interroger directement la base :

```bash
sqlite3 data/books.db

# Exemples de requêtes :
SELECT COUNT(*) FROM books;
SELECT category, COUNT(*) FROM books GROUP BY category;
SELECT * FROM books WHERE prix < 20 AND notation >= 4;
```

## API REST - Endpoints

### Endpoints principaux

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Page d'accueil de l'API |
| GET | `/books` | Liste tous les livres (avec pagination) |
| GET | `/books/{id}` | Détails d'un livre spécifique |
| GET | `/books/search` | Recherche avec filtres multiples |
| GET | `/categories` | Liste toutes les catégories |
| GET | `/categories/{category}/books` | Livres d'une catégorie |
| GET | `/stats` | Statistiques globales |
| GET | `/health` | Statut de l'API |

### Exemples d'utilisation

**Lister les livres (avec pagination)**

```bash
GET http://localhost:8000/books?limit=20&offset=0
```

**Recherche avec filtres**

```bash
GET http://localhost:8000/books/search?category=Fiction&min_price=10&max_price=30&min_rating=4
```

**Statistiques globales**

```bash
GET http://localhost:8000/stats
```

## Schéma de la base de données

**Table : books**

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire auto-incrémentée |
| titre | TEXT | Titre du livre |
| prix | REAL | Prix en livres sterling (£) |
| notation | INTEGER | Note de 0 à 5 étoiles |
| disponibilite | INTEGER | Nombre d'exemplaires en stock |
| description | TEXT | Description du livre |
| upc | TEXT | Code produit unique (UNIQUE) |
| category | TEXT | Catégorie du livre |
| url | TEXT | URL de la page produit |
| image | TEXT | URL de l'image de couverture |
| date_scraping | TEXT | Date/heure du scraping (ISO 8601) |

## Pipeline de nettoyage des données

Le projet utilise 5 pipelines Scrapy pour garantir la qualité des données :

1. **CleanPricePipeline** : Convertit "£51.77" → 51.77 (float)
2. **ConvertRatingPipeline** : Convertit "Three" → 3 (int)
3. **ExtractAvailabilityPipeline** : Extrait "In stock (22 available)" → 22
4. **DuplicatesPipeline** : Détecte les doublons par UPC
5. **SaveToSQLitePipeline** : Sauvegarde dans la base de données

## Dépendances

```
scrapy==2.13.3      # Framework de scraping
fastapi==0.115.0    # Framework API REST
uvicorn==0.32.0     # Serveur ASGI
```

## Technologies utilisées

- **Python 3.13** : Langage principal
- **Scrapy** : Framework de web scraping
- **SQLite** : Base de données relationnelle
- **FastAPI** : Framework API REST moderne et rapide
- **Uvicorn** : Serveur ASGI haute performance

## Fonctionnalités clés

### Scraping

- Scraping récursif avec gestion de la pagination
- Extraction de 10+ champs de données par livre
- Gestion automatique des URLs relatives
- Rate limiting pour respecter les serveurs

### Nettoyage

- Normalisation automatique des prix
- Conversion des notes textuelles en numériques
- Extraction intelligente de la disponibilité
- Détection des doublons par UPC

### API

- Documentation interactive OpenAPI (Swagger)
- Filtres multiples combinables
- Pagination efficace
- Gestion des erreurs HTTP appropriée
- Validation automatique des paramètres

## Auteur

Développé dans le cadre du projet "Scraping de données avec Scrapy" - Certification RNCP Développeur.se en intelligence artificielle

## Licence

Ce projet est à usage éducatif uniquement.

---

**Note** : Ce projet scrape books.toscrape.com, un site créé spécifiquement pour l'apprentissage du web scraping.

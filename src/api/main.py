"""API REST pour accéder aux données des livres scrapés."""
from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import sys
from pathlib import Path

# Ajouter le dossier racine au path Python
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.book_repository import BookRepository

# Créer l'application FastAPI
app = FastAPI(
    title="Books Scraper API",
    description="API REST pour accéder aux données scrapées depuis books.toscrape.com",
    version="1.0.0"
)

# Instance unique du repository (Singleton pattern)
repository = BookRepository()


@app.get("/", tags=["Root"])
def root():
    """Point d'entrée de l'API."""
    return {
        "message": "Bienvenue sur l'API Books Scraper",
        "documentation": "/docs",
        "endpoints": {
            "Liste des livres": "/books",
            "Détail d'un livre": "/books/{id}",
            "Recherche": "/books/search",
            "Catégories": "/categories",
            "Statistiques": "/stats"
        }
    }


@app.get("/books", tags=["Books"])
def list_books(
    limit: int = Query(50, ge=1, le=200, description="Nombre de résultats"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """
    Liste tous les livres avec pagination.
    
    - **limit**: Nombre maximum de résultats (1-200)
    - **offset**: Point de départ pour la pagination
    """
    books = repository.get_all_books(limit=limit, offset=offset)
    return {
        "count": len(books),
        "limit": limit,
        "offset": offset,
        "books": books
    }


@app.get("/books/search", tags=["Books"])
def search_books(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    min_price: Optional[float] = Query(None, ge=0, description="Prix minimum"),
    max_price: Optional[float] = Query(None, ge=0, description="Prix maximum"),
    min_rating: Optional[int] = Query(None, ge=0, le=5, description="Note minimum (0-5)"),
    limit: int = Query(50, ge=1, le=200, description="Nombre de résultats")
):
    """
    Recherche de livres avec filtres multiples.
    
    Tous les paramètres sont optionnels et peuvent être combinés.
    """
    books = repository.search_books(
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        limit=limit
    )
    
    return {
        "count": len(books),
        "filters": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "min_rating": min_rating
        },
        "books": books
    }


@app.get("/books/{book_id}", tags=["Books"])
def get_book(book_id: int):
    """
    Récupère les détails d'un livre spécifique par son ID.
    """
    book = repository.get_book_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Livre avec l'ID {book_id} introuvable"
        )
    
    return book


@app.get("/categories", tags=["Categories"])
def list_categories():
    """
    Liste toutes les catégories disponibles.
    """
    categories = repository.get_all_categories()
    top_categories = repository.get_top_categories(limit=10)
    
    return {
        "total": len(categories),
        "categories": categories,
        "top_10": top_categories
    }


@app.get("/categories/{category}/books", tags=["Categories"])
def get_books_by_category(category: str):
    """
    Récupère tous les livres d'une catégorie spécifique.
    """
    books = repository.get_books_by_category(category)
    
    if not books:
        raise HTTPException(
            status_code=404,
            detail=f"Aucun livre trouvé pour la catégorie '{category}'"
        )
    
    return {
        "category": category,
        "count": len(books),
        "books": books
    }


@app.get("/stats", tags=["Statistics"])
def get_statistics():
    """
    Statistiques globales sur l'ensemble des livres.
    
    Retourne :
    - Statistiques générales (total, moyenne, etc.)
    - Prix moyens par catégorie
    - Top catégories
    """
    global_stats = repository.get_statistics()
    price_by_category = repository.get_price_stats_by_category()
    top_cats = repository.get_top_categories(limit=10)
    
    return {
        "global": global_stats,
        "prix_par_categorie": price_by_category,
        "top_categories": top_cats
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint pour vérifier que l'API fonctionne."""
    try:
        # Test de connexion à la base
        stats = repository.get_statistics()
        return {
            "status": "healthy",
            "database": "connected",
            "total_books": stats['total_livres']
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service indisponible: {str(e)}"
        )
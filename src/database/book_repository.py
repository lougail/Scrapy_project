"""Repository pour gérer les opérations sur les livres."""
from typing import List, Optional, Dict
from .connection import DatabaseConnection


class BookRepository:
    """Classe pour accéder aux données des livres."""
    
    def __init__(self):
        self.db = DatabaseConnection()
    
    def get_all_books(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Récupère tous les livres avec pagination."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM books LIMIT ? OFFSET ?",
            (limit, offset)
        )
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return books
    
    def get_book_by_id(self, book_id: int) -> Optional[Dict]:
        """Récupère un livre par son ID."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM books WHERE id = ?",
            (book_id,)
        )
        book = cursor.fetchone()
        conn.close()
        return dict(book) if book else None
    
    def get_books_by_category(self, category: str) -> List[Dict]:
        """Récupère les livres d'une catégorie."""
        conn = self.db.get_connection()
        cursor = conn.execute(
            "SELECT * FROM books WHERE category = ?",
            (category,)
        )
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return books
    
    def search_books(
        self,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_rating: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Recherche de livres avec filtres."""
        conn = self.db.get_connection()
        
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if min_price is not None:
            query += " AND prix >= ?"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND prix <= ?"
            params.append(max_price)
        
        if min_rating is not None:
            query += " AND notation >= ?"
            params.append(min_rating)
        
        query += f" LIMIT {limit}"
        
        cursor = conn.execute(query, params)
        books = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return books
    
    def get_statistics(self) -> Dict:
        """Calcule les statistiques globales."""
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT 
                COUNT(*) as total_livres,
                COUNT(DISTINCT category) as nb_categories,
                ROUND(AVG(prix), 2) as prix_moyen,
                ROUND(AVG(notation), 2) as note_moyenne,
                SUM(disponibilite) as stock_total
            FROM books
        """)
        stats = dict(cursor.fetchone())
        conn.close()
        return stats
    
    def get_price_stats_by_category(self) -> List[Dict]:
        """Prix moyen, min, max par catégorie."""
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT 
                category,
                COUNT(*) as nb_livres,
                ROUND(AVG(prix), 2) as prix_moyen,
                ROUND(MIN(prix), 2) as prix_min,
                ROUND(MAX(prix), 2) as prix_max
            FROM books
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY prix_moyen DESC
        """)
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_top_categories(self, limit: int = 10) -> List[Dict]:
        """Top catégories avec le plus de livres."""
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT 
                category,
                COUNT(*) as nb_livres
            FROM books
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY nb_livres DESC
            LIMIT ?
        """, (limit,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_all_categories(self) -> List[str]:
        """Liste toutes les catégories."""
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT DISTINCT category 
            FROM books 
            WHERE category IS NOT NULL
            ORDER BY category
        """)
        categories = [row['category'] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_price_evolution(self, upc: str) -> List[Dict]:
        """Évolution du prix d'un livre dans le temps."""
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT titre, prix, date_scraping
            FROM scraping_history
            WHERE upc = ?
            ORDER BY date_scraping ASC
        """, (upc,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_price_changes(self, min_variation: float = 5.0) -> List[Dict]:
        """Livres dont le prix a varié significativement."""
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT 
                h1.upc,
                h1.titre,
                MIN(h1.prix) as prix_min,
                MAX(h1.prix) as prix_max,
                MAX(h1.prix) - MIN(h1.prix) as variation
            FROM scraping_history h1
            GROUP BY h1.upc, h1.titre
            HAVING variation >= ?
            ORDER BY variation DESC
        """, (min_variation,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_scraping_dates(self) -> List[str]:
        """Liste toutes les dates de scraping."""
        conn = self.db.get_connection()
        cursor = conn.execute("""
            SELECT DISTINCT date_scraping
            FROM scraping_history
            ORDER BY date_scraping DESC
        """)
        dates = [row[0] for row in cursor.fetchall()]
        conn.close()
        return dates
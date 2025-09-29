"""Gestion de la connexion à la base de données."""
import sqlite3
from pathlib import Path


class DatabaseConnection:
    """Classe pour gérer la connexion SQLite."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Remonte à la racine du projet
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / 'data' / 'books.db'
        
        self.db_path = str(db_path)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Vérifie que la base existe."""
        if not Path(self.db_path).exists():
            raise FileNotFoundError(
                f"Base de données introuvable: {self.db_path}\n"
                "Lancez d'abord le scraper pour créer la base."
            )
    
    def get_connection(self):
        """Retourne une connexion à la base."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
"""Tests unitaires du repository."""
import sys
from pathlib import Path

# Ajouter le dossier racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.book_repository import BookRepository


def test_get_statistics():
    """Test des statistiques globales."""
    print("\n=== Test : Statistiques globales ===")
    repo = BookRepository()
    stats = repo.get_statistics()
    
    assert stats is not None, "Les statistiques ne doivent pas être None"
    assert stats['total_livres'] > 0, "Il doit y avoir au moins un livre"
    assert stats['nb_categories'] > 0, "Il doit y avoir au moins une catégorie"
    
    print(f"✓ {stats['total_livre  s']} livres trouvés")
    print(f"✓ {stats['nb_categories']} catégories trouvées")
    print("✓ Test réussi")


def test_get_all_books():
    """Test de récupération des livres."""
    print("\n=== Test : Récupération des livres ===")
    repo = BookRepository()
    books = repo.get_all_books(limit=10)
    
    assert len(books) > 0, "Il doit y avoir au moins un livre"
    assert 'titre' in books[0], "Les livres doivent avoir un titre"
    assert 'prix' in books[0], "Les livres doivent avoir un prix"
    
    print(f"✓ {len(books)} livres récupérés")
    print(f"✓ Premier livre : {books[0]['titre']}")
    print("✓ Test réussi")


def test_scraping_history():
    """Test de l'historique de scraping."""
    print("\n=== Test : Historique de scraping ===")
    repo = BookRepository()
    dates = repo.get_scraping_dates()
    
    assert len(dates) > 0, "Il doit y avoir au moins une date de scraping"
    
    print(f"✓ {len(dates)} scraping(s) effectué(s)")
    print(f"✓ Dernière date : {dates[0]}")
    print("✓ Test réussi")


if __name__ == "__main__":
    try:
        test_get_statistics()
        test_get_all_books()
        test_scraping_history()
        print("\n" + "="*50)
        print("TOUS LES TESTS SONT PASSÉS ✓")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ Test échoué : {e}")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
"""Script pour tester et afficher les requêtes SQL."""
import sys
from pathlib import Path

# Ajouter la racine du projet au path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.book_repository import BookRepository


def main():
    repo = BookRepository()
    
    print("=" * 50)
    print("STATISTIQUES GLOBALES")
    print("=" * 50)
    stats = repo.get_statistics()
    print(f"Total livres: {stats['total_livres']}")
    print(f"Catégories: {stats['nb_categories']}")
    print(f"Prix moyen: £{stats['prix_moyen']}")
    print(f"Note moyenne: {stats['note_moyenne']}/5")
    print(f"Stock total: {stats['stock_total']} exemplaires")
    
    print("\n" + "=" * 50)
    print("TOP 10 CATÉGORIES")
    print("=" * 50)
    for cat in repo.get_top_categories(10):
        print(f"{cat['category']}: {cat['nb_livres']} livres")
    
    print("\n" + "=" * 50)
    print("PRIX MOYEN PAR CATÉGORIE (Top 5)")
    print("=" * 50)
    for item in repo.get_price_stats_by_category()[:5]:
        print(f"{item['category']}: £{item['prix_moyen']} "
              f"(min: £{item['prix_min']}, max: £{item['prix_max']})")


if __name__ == "__main__":
    main()
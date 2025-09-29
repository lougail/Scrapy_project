# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import re
import sqlite3
import os
from typing import Optional
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class CleanPricePipeline:
    """Pipeline 1 : Nettoie et convertit les prix."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        prix_text = adapter.get('prix_original')
        
        if prix_text:
            prix_clean = re.sub(r'[^\d.]', '', prix_text)
            try:
                adapter['prix'] = float(prix_clean)
            except ValueError:
                adapter['prix'] = None
                spider.logger.warning(f"Impossible de convertir le prix: {prix_text}")
        else:
            adapter['prix'] = None
        
        return item


class ConvertRatingPipeline:
    """Pipeline 2 : Convertit les notes en chiffres."""
    
    RATING_MAP = {
        'Zero': 0,
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        rating_text = adapter.get('notation_originale')
        
        if rating_text:
            rating_number = self.RATING_MAP.get(rating_text)
            adapter['notation'] = rating_number if rating_number is not None else None
            if rating_number is None:
                spider.logger.warning(f"Note inconnue: {rating_text}")
        else:
            adapter['notation'] = None
        
        return item


class ExtractAvailabilityPipeline:
    """Pipeline 3 : Extrait le nombre d'exemplaires disponibles."""
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        availability_text = adapter.get('disponibilite_texte')
        
        if availability_text:
            match = re.search(r'(\d+)', availability_text)
            if match:
                try:
                    adapter['disponibilite'] = int(match.group(1))
                except ValueError:
                    adapter['disponibilite'] = 0
            else:
                adapter['disponibilite'] = 1 if 'in stock' in availability_text.lower() else 0
        else:
            adapter['disponibilite'] = 0
        
        return item


class DuplicatesPipeline:
    """Pipeline 4 : Détecte les doublons basés sur l'UPC."""
    
    def __init__(self):
        self.upcs_seen = set()
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        upc = adapter.get('upc')
        
        if upc:
            if upc in self.upcs_seen:
                spider.logger.warning(f"Doublon détecté: {upc}")
                raise DropItem(f"Doublon: {upc}")
            else:
                self.upcs_seen.add(upc)
        
        return item


class SaveToSQLitePipeline:
    """Pipeline 5 : Sauvegarde les données dans SQLite avec historique."""
    
    def __init__(self):
        self.conn: Optional[sqlite3.Connection] = None
        self.cursor: Optional[sqlite3.Cursor] = None
    
    def open_spider(self, spider):
        """Appelé quand le spider démarre."""
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file)))))
        data_dir = os.path.join(project_root, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        db_path = os.path.join(data_dir, 'books.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # Table principale : état actuel des livres
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT,
                prix REAL,
                notation INTEGER,
                disponibilite INTEGER,
                description TEXT,
                upc TEXT UNIQUE,
                category TEXT,
                url TEXT,
                image TEXT,
                date_scraping TEXT
            )
        ''')
        
        # Table historique : trace de chaque scraping
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scraping_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upc TEXT,
                titre TEXT,
                prix REAL,
                notation INTEGER,
                disponibilite INTEGER,
                category TEXT,
                date_scraping TEXT,
                FOREIGN KEY (upc) REFERENCES books(upc)
            )
        ''')
        
        self.conn.commit()
        spider.logger.info(f"✅ Base de données avec historique initialisée: {db_path}")
    
    def close_spider(self, spider):
        """Appelé quand le spider se termine."""
        if self.conn:
            self.conn.close()
        spider.logger.info("✅ Connexion à la base fermée")
    
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        if not self.cursor or not self.conn:
            spider.logger.error("❌ Connexion à la base non initialisée")
            return item
        
        try:
            # 1. Mettre à jour la table books (état actuel)
            self.cursor.execute('''
                INSERT OR REPLACE INTO books 
                (titre, prix, notation, disponibilite, description, upc, category, url, image, date_scraping)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                adapter.get('titre'),
                adapter.get('prix'),
                adapter.get('notation'),
                adapter.get('disponibilite'),
                adapter.get('description'),
                adapter.get('upc'),
                adapter.get('category'),
                adapter.get('url'),
                adapter.get('image'),
                adapter.get('date_scraping')
            ))
            
            # 2. Insérer dans l'historique (jamais d'écrasement)
            self.cursor.execute('''
                INSERT INTO scraping_history 
                (upc, titre, prix, notation, disponibilite, category, date_scraping)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                adapter.get('upc'),
                adapter.get('titre'),
                adapter.get('prix'),
                adapter.get('notation'),
                adapter.get('disponibilite'),
                adapter.get('category'),
                adapter.get('date_scraping')
            ))
            
            self.conn.commit()
        except sqlite3.Error as e:
            spider.logger.error(f"❌ Erreur SQLite: {e}")
        
        return item
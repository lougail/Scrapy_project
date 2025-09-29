import scrapy


class BookItem(scrapy.Item):
    """
    Définit la structure d'un livre scrapé.
    """
    # Informations principales
    titre = scrapy.Field()
    prix = scrapy.Field()
    prix_original = scrapy.Field()
    
    # Évaluation
    notation = scrapy.Field()
    notation_originale = scrapy.Field()
    
    # Disponibilité
    disponibilite = scrapy.Field()
    disponibilite_texte = scrapy.Field()
    
    # Détails
    description = scrapy.Field()
    upc = scrapy.Field()
    category = scrapy.Field()
    
    # Métadonnées
    url = scrapy.Field()
    image = scrapy.Field()
    date_scraping = scrapy.Field()
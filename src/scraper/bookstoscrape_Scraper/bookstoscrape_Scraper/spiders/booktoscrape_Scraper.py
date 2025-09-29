import scrapy
from datetime import datetime
from bookstoscrape_Scraper.items import BookItem

class BooktoscrapeScraperSpider(scrapy.Spider):
    name = "booktoscrape_Scraper"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        """Parse la page de liste de livres"""
        products = response.css('article.product_pod')  # ✅ product_pod
        
        # Pour chaque livre on récupère le lien et on va sur la page détaillée
        for product in products:
            product_link = product.css("h3 a::attr(href)").get()
            if product_link:
                yield response.follow(product_link, callback=self.parse_product)
            
        # Gestion de la pagination
        next_page = response.css("li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
            
    def parse_product(self, response):
        """Parse la page détaillée d'un livre"""
        
        # Créer une instance de BookItem
        item = BookItem()
        
        # Récupération de la disponibilité
        availability_raw = response.css('p.instock.availability::text').getall()
        availability_text = availability_raw[-1].strip() if availability_raw else None
        
        # Récupération de la notation
        rating_class = response.css('p.star-rating::attr(class)').get()
        rating_original = rating_class.replace('star-rating ', '') if rating_class else None
        
        # Image
        image_url = response.css('div.item.active img::attr(src)').get()
        
        # Prix original
        prix_text = response.css('p.price_color::text').get()
        
        # Remplir l'item avec les données BRUTES
        item['titre'] = response.css('div.product_main h1::text').get()
        item['prix_original'] = prix_text
        item['prix'] = prix_text  # Sera nettoyé dans le pipeline
        item['notation_originale'] = rating_original
        item['notation'] = rating_original  # Sera converti dans le pipeline
        item['disponibilite_texte'] = availability_text
        item['disponibilite'] = availability_text  # Sera extrait dans le pipeline
        item['description'] = response.css('#product_description + p::text').get()
        item['upc'] = response.css('table.table tr:nth-child(1) td::text').get()
        item['category'] = response.css('ul.breadcrumb li:nth-child(3) a::text').get()
        item['url'] = response.url
        item['image'] = response.urljoin(image_url) if image_url else None
        item['date_scraping'] = datetime.now().isoformat()
        
        yield item
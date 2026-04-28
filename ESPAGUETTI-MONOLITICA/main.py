import sys
import os

# Asegurar que el path raíz está disponible para las importaciones de módulos
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from scrapy.crawler import CrawlerProcess
from infrastructure.spiders.tia_spider import TiaSpider

def main():
    print("Iniciando el proceso de extracción (Arquitectura por Capas)...")
    process = CrawlerProcess()
    process.crawl(TiaSpider)
    process.start()
    print("Extracción completada. Revisa el archivo tia_productos.json en la raíz.")

if __name__ == "__main__":
    main()

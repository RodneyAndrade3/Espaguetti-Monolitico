import scrapy
from datetime import datetime
from pathlib import Path
import sys
import os

# Se añade el directorio principal al sys.path para importaciones absolutas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from domain.models import Producto
from application.services import ProductProcessorService

OUTPUT_FILE = Path(__file__).resolve().parent.parent.parent / "tia_productos.json"

class TiaSpider(scrapy.Spider):
    name = "tia"
    allowed_domains = ["tia.com.ec"]
    MAX_ITEMS = 20
    # Iniciamos en la sección general de supermercado
    start_urls = ["https://www.tia.com.ec/supermercado"]
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
    )

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,
        'DOWNLOAD_DELAY': 1.5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0,
        'USER_AGENT': user_agent,
        'COOKIES_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-EC,es;q=0.9,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
        },
        'FEEDS': {
            str(OUTPUT_FILE): {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 2,
                'overwrite': True,
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(TiaSpider, self).__init__(*args, **kwargs)
        # Instanciar servicio de aplicación
        self.processor = ProductProcessorService()
        self.items_scraped = 0

    def parse(self, response):
        productos = response.css('li.item.product.product-item')

        for producto in productos:
            nombre_raw = producto.css('a.product-item-link::text').get()
            url_producto = producto.css('a.product-item-link::attr(href)').get()
            img_url = producto.css('img.product-image-photo::attr(src)').get()
            
            # Capa de Aplicación: Filtrar comida
            if nombre_raw and not self.processor.es_producto_comida(nombre_raw):
                continue
            
            # Tratamiento de imágenes
            if img_url:
                if 'placeholder' in img_url:
                    img_url = "N/A"
                else:
                    img_url = img_url.replace('height=200', 'height=700').replace('width=200', 'width=700').replace('canvas=200:200', 'canvas=700:700')

            # Precios crudos
            p_final = producto.css('.price-box-normal [data-price-type="finalPrice"] .price::text').get()
            p_viejo = producto.css('.price-box-normal [data-price-type="oldPrice"] .price::text').get()

            if not p_final:
                p_final = producto.css('[data-price-type="finalPrice"] .price::text').get()

            # Capa de Aplicación: Limpieza y validación de precios
            if p_viejo:
                precio_normal = self.processor.limpiar_precio(p_viejo)
                precio_oferta = self.processor.limpiar_precio(p_final)
            else:
                precio_normal = self.processor.limpiar_precio(p_final)
                precio_oferta = 0.0

            # Capa de Dominio: Instanciar modelo
            producto_domain = Producto(
                imagen_url=img_url if img_url else "N/A",
                fecha_descarga=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                tienda="Tía",
                product_url=url_producto if url_producto else "N/A",
                nombre=nombre_raw.strip() if nombre_raw else "N/A",
                unidades_medida=self.processor.extraer_unidad(nombre_raw),
                sku=self.processor.extraer_sku(url_producto),
                precio_normal=precio_normal,
                precio_oferta=precio_oferta,
                fecha_fin_oferta="N/A",
                descuento_porcentaje="N/A",
            )

            self.items_scraped += 1
            # Scrapy Pipeline requiere diccionario (Item)
            yield producto_domain.to_dict()
            
            if self.items_scraped >= self.MAX_ITEMS:
                return

        # Paginación
        siguiente = response.css('a.next::attr(href)').get()
        if siguiente:
            yield response.follow(siguiente, callback=self.parse)

    def start_requests(self):
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-EC,es;q=0.9,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.tia.com.ec/',
        }

        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse, dont_filter=True)

import scrapy
import re
from datetime import datetime
from pathlib import Path


OUTPUT_FILE = Path(__file__).with_name("tia_productos.json")

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

    # Palabras clave para identificar productos de COMIDA
    FOOD_KEYWORDS = {
        'comestibles', 'alimento', 'comida', 'bebida', 'bebidas',
        'snack', 'golosina', 'chocolate', 'galleta', 'pan', 'panadería',
        'pasta', 'arroz', 'legumbre', 'conserva', 'enlatado',
        'lácteo', 'queso', 'mantequilla', 'yogur', 'leche',
        'carne', 'pollo', 'pescado', 'marisco', 'congelado',
        'helado', 'postre', 'fruta', 'verdura', 'hortaliza',
        'aceite', 'condimento', 'salsa', 'especias', 'sal', 'azúcar',
        'café', 'té', 'jugo', 'agua', 'refresco', 'cerveza', 'vino', 'licor',
        'desayuno', 'cereal', 'muesli', 'granola', 'avena',
    }

    # Palabras clave para EXCLUIR (no alimentos)
    EXCLUDED_KEYWORDS = {
        'limpieza', 'lavado', 'insecticida', 'desechable', 'higiene',
        'cuidado', 'hogar', 'ropa', 'jabón', 'detergente', 'toallita',
        'papel higienico', 'papel higiénico', 'pañal', 'cosmético', 'medicamento', 'vitamina',
        'mascotas', 'electrodoméstico', 'zapato', 'accesorio', 'esponja',
        'salvaunas', 'check', 'lavavajilla', 'encera', 'desinfectante',
        'bicarbonato', 'muebles', 'cristal', 'copa', 'vaso', 'plastiutil',
        'paño', 'pano', 'antipelusa', 'servilleta', 'servilletas',
        'multiusos', 'portacomida', 'porta comida', 'toalla', 'funda',
        'empaque', 'descartable', 'bolsa basura', 'basura', 'guante',
        'aceite para muebles', 'aceite rojo', 'aceite para', 'cera',
        'ambientador', 'repuesto', 'glade', 'ambiental', 'plato', 'cubierto',
        'aromatizante', 'fragancia', 'perfumador',
    }

    custom_settings = {
        'CONCURRENT_REQUESTS': 4,   # Optimized for AWS Free Tier
        'DOWNLOAD_DELAY': 1.5,      # Balanced for better performance
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

    def parse(self, response):
        # Selector del contenedor principal de cada producto
        productos = response.css('li.item.product.product-item')

        for producto in productos:
            nombre_raw = producto.css('a.product-item-link::text').get()
            url_producto = producto.css('a.product-item-link::attr(href)').get()
            img_url = producto.css('img.product-image-photo::attr(src)').get()
            
            # FILTRO: Verificar si es un producto de COMIDA
            if nombre_raw and not self.es_producto_comida(nombre_raw):
                continue
            
            # 1. TRATAMIENTO DE IMÁGENES (Filtro y Alta Resolución)
            if img_url:
                if 'placeholder' in img_url:
                    img_url = "N/A" # Evita el logo gris de Magento
                else:
                    # Forzamos la resolución a 700x700 para mejor calidad visual
                    img_url = img_url.replace('height=200', 'height=700').replace('width=200', 'width=700').replace('canvas=200:200', 'canvas=700:700')

            # 2. LÓGICA DE PRECIOS Y OFERTAS
            # Usar solo el bloque de precios NORMAL (evita CrediTia/duplicados)
            p_final = producto.css('.price-box-normal [data-price-type="finalPrice"] .price::text').get()
            # 'oldPrice' solo existe si el producto tiene rebaja
            p_viejo = producto.css('.price-box-normal [data-price-type="oldPrice"] .price::text').get()

            # Fallback si el bloque normal no existe
            if not p_final:
                p_final = producto.css('[data-price-type="finalPrice"] .price::text').get()

            # Normalización de precios
            if p_viejo:
                # Hay oferta: precio_normal es el viejo (tachado), precio_oferta es el actual
                precio_normal = self.limpiar_precio(p_viejo)
                precio_oferta = self.limpiar_precio(p_final)
            else:
                # No hay oferta: precio_normal es el actual, precio_oferta = 0
                precio_normal = self.limpiar_precio(p_final)
                precio_oferta = 0.0

            item = {
                "imagen_url": img_url if img_url else "N/A",
                "fecha_descarga": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tienda": "Tía",
                "product_url": url_producto if url_producto else "N/A",
                "nombre": nombre_raw.strip() if nombre_raw else "N/A",
                "unidades_medida": self.extraer_unidad(nombre_raw),
                "sku": self.extraer_sku(url_producto),
                "precio_normal": precio_normal,
                "precio_oferta": precio_oferta,
                "fecha_fin_oferta": "N/A",
                "descuento_porcentaje": "N/A",
            }

            # contador de items para prueba rápida
            self.items_scraped = getattr(self, 'items_scraped', 0) + 1
            yield item
            if self.items_scraped >= self.MAX_ITEMS:
                return

        # 3. PAGINACIÓN AUTOMÁTICA
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

    # --- FUNCIONES DE LIMPIEZA Y EXTRACCIÓN ---

    def es_producto_comida(self, nombre):
        """Verifica si el producto es comida según palabras clave"""
        if not nombre:
            return False
        
        nombre_lower = nombre.lower()
        nombre_normalizado = re.sub(r'[^a-z0-9áéíóúñ]+', ' ', nombre_lower)
        nombre_normalizado = re.sub(r'\s+', ' ', nombre_normalizado).strip()
        
        # Primero verificar si está en palabras excluidas
        for keyword_excluida in self.EXCLUDED_KEYWORDS:
            if ' ' in keyword_excluida:
                if keyword_excluida in nombre_normalizado:
                    return False
            else:
                if re.search(rf'\b{re.escape(keyword_excluida)}\b', nombre_normalizado):
                    return False
        
        # Luego verificar si está en palabras de comida
        for keyword_comida in self.FOOD_KEYWORDS:
            if keyword_comida in nombre_lower:
                return True
        
        # Si no coincide con ninguna categoría, no es comida
        return False

    def limpiar_precio(self, texto):
        if not texto: return 0.0
        # Convierte formatos como $0,76 a 0.76 para cálculos
        nums = re.findall(r'\d+\.?\d*', texto.replace(',', '.'))
        return float(nums[0]) if nums else 0.0

    def extraer_sku(self, url):
        if not url: return "N/A"
        # Extrae el código numérico único antes de la extensión .html
        match = re.search(r'-(\d+)\.html$', url)
        return match.group(1) if match else "N/A"

    def extraer_unidad(self, nombre):
        if not nombre: return "N/A"
        # Busca patrones de peso/volumen (ej: 200 G, 1 KG, 500 ML)
        match = re.search(r'(\d+\s?(?:G|KG|L|ML|LB|UN|GR))', nombre, re.I)
        return match.group(1).upper() if match else "N/A"


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess()
    process.crawl(TiaSpider)
    process.start()
import re

class ProductProcessorService:
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

    def es_producto_comida(self, nombre: str) -> bool:
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

    def limpiar_precio(self, texto: str) -> float:
        if not texto: return 0.0
        # Convierte formatos como $0,76 a 0.76 para cálculos
        nums = re.findall(r'\d+\.?\d*', texto.replace(',', '.'))
        return float(nums[0]) if nums else 0.0

    def extraer_sku(self, url: str) -> str:
        if not url: return "N/A"
        # Extrae el código numérico único antes de la extensión .html
        match = re.search(r'-(\d+)\.html$', url)
        return match.group(1) if match else "N/A"

    def extraer_unidad(self, nombre: str) -> str:
        if not nombre: return "N/A"
        # Busca patrones de peso/volumen (ej: 200 G, 1 KG, 500 ML)
        match = re.search(r'(\d+\s?(?:G|KG|L|ML|LB|UN|GR))', nombre, re.I)
        return match.group(1).upper() if match else "N/A"

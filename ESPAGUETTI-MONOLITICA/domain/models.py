from dataclasses import dataclass, asdict

@dataclass
class Producto:
    imagen_url: str
    fecha_descarga: str
    tienda: str
    product_url: str
    nombre: str
    unidades_medida: str
    sku: str
    precio_normal: float
    precio_oferta: float
    fecha_fin_oferta: str
    descuento_porcentaje: str
    
    def to_dict(self):
        return asdict(self)

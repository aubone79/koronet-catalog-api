from fastapi import FastAPI, Query
from sqlalchemy import create_engine, Column, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuración de la conexión a PostgreSQL
DATABASE_URL = "postgresql://koronet_catalog_user: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@dpg-cv69pk7noe9s73bt9ls0-a.oregon-postgres.render.com/koronet_catalog"   
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo de base de datos
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Text, primary_key=True, index=True)  # Índice para optimizar búsqueda por ID
    product_name = Column(Text, index=True)  # Índice para búsqueda rápida por nombre
    scientific_name = Column(Text)
    cultivar = Column(Text)
    classification = Column(Text, index=True)  # Índice para búsqueda rápida por categoría
    attributes = Column(JSON)
    regional_availability = Column(JSON)
    supplier_details = Column(JSON)
    industry_classifications = Column(JSON)
    metadata_info = Column("metadata", JSON)

# Iniciar FastAPI
app = FastAPI()

# Ruta para listar productos con múltiples filtros y paginación
@app.get("/products")
def get_products(
    name: str = Query(None, description="Filtra por nombre"),
    category: str = Query(None, description="Filtra por categoría"),
    supplier: str = Query(None, description="Filtra por proveedor"),
    color: str = Query(None, description="Filtra por color"),
    stem_length_min: int = Query(None, description="Longitud de tallo mínima"),
    stem_length_max: int = Query(None, description="Longitud de tallo máxima"),
    country: str = Query(None, description="Filtra por país de disponibilidad"),
    limit: int = Query(50, description="Número de productos por página (máx. 100)"),
    offset: int = Query(0, description="Número de productos a omitir (para paginación)")
):
    session = SessionLocal()
    query = session.query(Product)

    if name:
        query = query.filter(Product.product_name.ilike(f"%{name}%"))
    if category:
        query = query.filter(Product.classification.ilike(f"%{category}%"))
    if supplier:
        query = query.filter(Product.supplier_details.cast(Text).ilike(f"%{supplier}%"))
    if color:
        query = query.filter(Product.attributes["color"].astext.ilike(f"%{color}%"))
    if stem_length_min:
        query = query.filter(Product.attributes["stem_length_cm"].astext.cast(Text).ilike(f"%{stem_length_min}%"))
    if stem_length_max:
        query = query.filter(Product.attributes["stem_length_cm"].astext.cast(Text).ilike(f"%{stem_length_max}%"))
    if country:
        query = query.filter(Product.regional_availability.cast(Text).ilike(f"%{country}%"))

    # Aplicar paginación
    results = query.limit(min(limit, 100)).offset(offset).all()

    session.close()
    return results

# Ruta para obtener un producto por ID
@app.get("/products/{product_id}")
def get_product(product_id: str):
    session = SessionLocal()
    product = session.query(Product).filter(Product.id == product_id).first()
    session.close()
    if product:
        return product
    return {"error": "Product not found"}

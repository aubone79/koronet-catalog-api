from fastapi import FastAPI, Query
from sqlalchemy import create_engine, Column, Text, JSON, Integer, cast
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
import os

# Configuración de la conexión a PostgreSQL
DATABASE_URL = "postgresql://koronet_catalog_user:XIoF38hYTWXUeddLg3wcpqgKOihxbiA4@dpg-cv69pk7noe9s73bt9ls0-a.oregon-postgres.render.com:5432/koronet_catalog"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modelo de base de datos
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    id = Column(Text, primary_key=True, index=True)
    product_name = Column(Text, index=True)
    scientific_name = Column(Text)
    cultivar = Column(Text)
    classification = Column(Text, index=True)
    attributes = Column(JSONB)  # Cambiado a JSONB para mejorar consultas
    regional_availability = Column(JSONB)
    supplier_details = Column(JSONB)
    industry_classifications = Column(JSONB)
    metadata_info = Column("metadata", JSONB)

# Iniciar FastAPI
app = FastAPI()

# Ruta para listar productos con filtros mejorados
@app.get("/products")
def get_products(
    name: str = Query(None, description="Filtra por nombre"),
    scientific_name: str = Query(None, description="Filtra por nombre científico"),
    cultivar: str = Query(None, description="Filtra por variedad"),
    category: str = Query(None, description="Filtra por categoría"),
    supplier: str = Query(None, description="Filtra por proveedor"),
    color: str = Query(None, description="Filtra por color"),
    grade: str = Query(None, description="Filtra por calidad"),
    stem_length_min: int = Query(None, description="Longitud de tallo mínima"),
    stem_length_max: int = Query(None, description="Longitud de tallo máxima"),
    vase_life_min: int = Query(None, description="Duración mínima en florero"),
    vase_life_max: int = Query(None, description="Duración máxima en florero"),
    country: str = Query(None, description="Filtra por país de disponibilidad"),
    limit: int = Query(50, description="Número de productos por página (máx. 100)"),
    offset: int = Query(0, description="Número de productos a omitir (para paginación)")
):
    session = SessionLocal()
    query = session.query(Product)

    # Aplicar filtros
    if name:
        query = query.filter(Product.product_name.ilike(f"%{name}%"))
    if scientific_name:
        query = query.filter(Product.scientific_name.ilike(f"%{scientific_name}%"))
    if cultivar:
        query = query.filter(Product.cultivar.ilike(f"%{cultivar}%"))
    if category:
        query = query.filter(Product.classification.ilike(f"%{category}%"))
    if supplier:
        query = query.filter(Product.supplier_details.cast(Text).ilike(f"%{supplier}%"))
    if color:
        query = query.filter(cast(Product.attributes["color"], Text).ilike(f"%{color}%"))
    if grade:
        query = query.filter(cast(Product.attributes["grade"], Text).ilike(f"%{grade}%"))
    if stem_length_min is not None:
        query = query.filter(cast(Product.attributes["stem_length_cm"], Text).ilike(f"%{stem_length_min}%"))
    if stem_length_max is not None:
        query = query.filter(cast(Product.attributes["stem_length_cm"], Text).ilike(f"%{stem_length_max}%"))
    if vase_life_min is not None:
        query = query.filter(Product.attributes["vase_life_days"].as_integer() >= vase_life_min)
    if vase_life_max is not None:
        query = query.filter(Product.attributes["vase_life_days"].as_integer() <= vase_life_max)
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

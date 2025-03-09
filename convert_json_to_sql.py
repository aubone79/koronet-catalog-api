import json

# Ruta del archivo JSON (ajusta según tu ubicación)
json_file_path = "flower_catalog_v1.json"
sql_output_file = "insert_products.sql"

# Nombre de la tabla en PostgreSQL
table_name = "products"

# Leer el JSON
with open(json_file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

# Función para limpiar strings y manejar valores vacíos
def clean_string(value):
    if isinstance(value, str):
        return value.replace("'", "''")  # Escapa comillas para SQL
    return value

# Generar comandos SQL INSERT
sql_statements = []
for item in data:
    sql_statements.append(
        f"INSERT INTO {table_name} (id, product_name, scientific_name, cultivar, classification, attributes, regional_availability, supplier_details, industry_classifications, metadata) VALUES ("
        f"'{item['metadata']['id']}', "
        f"'{clean_string(item.get('product_name', ''))}', "
        f"'{clean_string(item.get('scientific_name', ''))}', "
        f"'{clean_string(item.get('cultivar', ''))}', "
        f"'{clean_string(item.get('classification', ''))}', "
        f"'{json.dumps(item.get('attributes', {}))}', "
        f"'{json.dumps(item.get('regional_availability', []))}', "
        f"'{json.dumps(item.get('supplier_details', []))}', "
        f"'{json.dumps(item.get('industry_classifications', {}))}', "
        f"'{json.dumps(item.get('metadata', {}))}'"
        ");"
    )

# Guardar en un archivo SQL
with open(sql_output_file, "w", encoding="utf-8") as file:
    file.write("\n".join(sql_statements))

print(f"Archivo SQL generado: {sql_output_file}")

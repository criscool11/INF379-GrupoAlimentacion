import pandas as pd

# 1. Mapeo de regiones para Flourish
region_ids = {
    "Región de Arica y Parinacota": "CLAP",
    "Región de Tarapacá": "CLTA",
    "Región de Antofagasta": "CLAN",
    "Región de Atacama": "CLAT",
    "Región de Coquimbo": "CLCO",
    "Región de Valparaíso": "CLVS",
    "Región Metropolitana de Santiago": "CLRM",
    "Región del Libertador General Bernardo O'Higgins": "CLLI",
    "Región del Maule": "CLML",
    "Región de Ñuble": "CLNB",
    "Región del Biobío": "CLBI",
    "Región de La Araucanía": "CLAR",
    "Región de Los Ríos": "CLLR",
    "Región de Los Lagos": "CLLL",
    "Región de Aysén del General Carlos Ibáñez del Campo": "CLAI",
    "Región de Magallanes y de la Antártica Chilena": "CLMA",
    # Variaciones comunes por si ODEPA las escribe distinto
    "Región de Magallanes y Antártica Chilena": "CLMA",
    "Región de Aysén del Gral. Carlos Ibáñez del Campo": "CLAI"
}

print("Cargando datos de ODEPA...")

# 2. Carga segura del archivo (manejo de tildes y caracteres especiales)
try:
    df = pd.read_csv('precio_consumidor_2026.csv', sep=',', encoding='utf-8')
except UnicodeDecodeError:
    df = pd.read_csv('precio_consumidor_2026.csv', sep=',', encoding='latin-1')

# 3. Limpieza profunda y prevención de errores
df.columns = df.columns.str.strip()
df['Precio promedio'] = df['Precio promedio'].astype(str).str.replace(',', '.').str.strip()
df['Precio promedio'] = pd.to_numeric(df['Precio promedio'], errors='coerce')

# Eliminar filas basura
df = df.dropna(subset=['Region', 'Grupo', 'Producto', 'Precio promedio'])

# Limpiar espacios extra
df['Grupo'] = df['Grupo'].astype(str).str.strip()
df['Producto'] = df['Producto'].astype(str).str.strip()
df['Region'] = df['Region'].astype(str).str.strip()

# 4. Determinar los 3 productos más comunes a nivel nacional por grupo
canasta_estandar = {}
grupos_totales = df['Grupo'].unique()

print("\n--- Productos seleccionados para la canasta ---")
for grupo in grupos_totales:
    df_grupo = df[df['Grupo'] == grupo]
    conteo_cobertura = df_grupo.groupby('Producto')['Region'].nunique()
    
    top_3_productos = conteo_cobertura.nlargest(3).index.tolist()
    canasta_estandar[grupo] = top_3_productos
    print(f"[{grupo}]: {', '.join(top_3_productos)}")

# 5. Construir la tabla con columnas de productos individuales
regiones = df['Region'].unique()
resultados = []

print("\nProcesando precios individuales por región...")
for region in regiones:
    
    # ---> ESTA ES LA LÍNEA QUE FALTABA <---
    df_region = df[df['Region'] == region]
    
    datos_region = {
        "id": region_ids.get(region, "SIN_ID"),
        "name": region
    }
    precio_total_canasta = 0
    
    for grupo, productos_objetivo in canasta_estandar.items():
        df_grupo_region = df_region[df_region['Grupo'] == grupo]
        
        for prod in productos_objetivo:
            df_prod = df_grupo_region[df_grupo_region['Producto'] == prod]
            nombre_columna = f"{grupo}: {prod}"
            
            if not df_prod.empty:
                precio = df_prod['Precio promedio'].mean()
                datos_region[nombre_columna] = round(precio, 2)
                precio_total_canasta += precio
            else:
                datos_region[nombre_columna] = 0

    datos_region["Promedio Total Canasta"] = round(precio_total_canasta, 2)
    resultados.append(datos_region)

# 6. Crear DataFrame y organizar columnas
df_final = pd.DataFrame(resultados)

# Dejar ID, Name y el Promedio Total al principio
cols_principales = ['id', 'name', 'Promedio Total Canasta']
cols_productos = [col for col in df_final.columns if col not in cols_principales]
df_final = df_final[cols_principales + cols_productos]

# Guardar resultado
df_final.to_csv('canasta_productos_individuales.csv', index=False)
print("\n✅ ¡Listo! Archivo 'canasta_productos_individuales.csv' generado sin errores.")

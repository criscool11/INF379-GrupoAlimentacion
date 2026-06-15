import pandas as pd

# 1. Mapeo de regiones (IDs de Flourish)
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
    "Región de Magallanes y de la Antártica Chilena": "CLMA"
}

print("Cargando y procesando datos...")

# 2. Leer archivo y limpiar datos
df = pd.read_csv('precio_consumidor_2026.csv', sep=',')
df['Precio promedio'] = df['Precio promedio'].astype(str).str.replace(',', '.').astype(float)

# 3. CREAR LA CANASTA ESTÁNDAR (El Top 3 de productos más comunes por grupo)
canasta_estandar = {}
grupos_totales = df['Grupo'].unique()

print("\n--- Definiendo Canasta Estándar Nacional ---")
for grupo in grupos_totales:
    df_grupo = df[df['Grupo'] == grupo]
    # Cuenta en cuántas regiones distintas aparece cada producto
    conteo_cobertura = df_grupo.groupby('Producto')['Region'].nunique()
    # Selecciona los 3 productos con mayor cobertura nacional
    top_3_productos = conteo_cobertura.nlargest(3).index.tolist()
    canasta_estandar[grupo] = top_3_productos
    print(f"[{grupo}]: {', '.join(top_3_productos)}")

print("\n--- Analizando Faltantes por Región ---")

# 4. Procesamiento estricto por región
regiones = df['Region'].unique()
resultados = []

for region in regiones:
    df_region = df[df['Region'] == region]
    precio_total_region = 0
    datos_region = {
        "id": region_ids.get(region, "SIN_ID"),
        "name": region
    }
    
    productos_faltantes = []

    for grupo, productos_objetivo in canasta_estandar.items():
        df_grupo_region = df_region[df_region['Grupo'] == grupo]
        suma_grupo = 0
        
        for prod in productos_objetivo:
            df_prod = df_grupo_region[df_grupo_region['Producto'] == prod]
            
            if not df_prod.empty:
                # Si el producto existe en esta región, promediar (por si hay varios puntos de monitoreo)
                precio = df_prod['Precio promedio'].mean()
                suma_grupo += precio
            else:
                # Si el producto exacto no existe en la región, registrarlo
                productos_faltantes.append(f"{prod} ({grupo})")
                
        precio_total_region += suma_grupo
        datos_region[grupo] = round(suma_grupo, 2)
        
    # Guardar el valor total 
    datos_region["Promedio"] = round(precio_total_region, 2)
    resultados.append(datos_region)
    
    # Imprimir alertas si la región no tiene la canasta completa
    if productos_faltantes:
        print(f"⚠️ {region} no tiene: {', '.join(productos_faltantes)}")

# 5. Generar y exportar el DataFrame final
df_final = pd.DataFrame(resultados)

# Ordenar columnas al estilo Flourish (id, name, Promedio, y luego los grupos)
cols = ['id', 'name', 'Promedio'] + [col for col in df_final.columns if col not in ['id', 'name', 'Promedio']]
df_final = df_final[cols]

# Exportar a CSV
df_final.to_csv('canasta_flourish_precisa.csv', index=False)
print("\n✅ Proceso terminado. Archivo 'canasta_flourish_precisa.csv' generado.")

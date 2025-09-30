import requests
import pandas as pd
import folium
from datetime import datetime
import schedule
import mysql.connector

# Configuración
DB_CONFIG = {
    "host": "bsoc7uhsw5gjn4zf9ves-mysql.services.clever-cloud.com",
    "database": "bsoc7uhsw5gjn4zf9ves",
    "user": "u27hjw3jfjaengp4",
    "password": "yIUyH5vqgcH507V4HuZY",
    "port": 3306
}

API_KEYS = {
    "trafico": "Q9n4jfzUJ8S32eAwzEEtkvBNGevA0Z28",
    "ruta": "wvYEt70EmwoIsqblGepQjlgwCb5BmNIL"
}

ZONAS = {
    "Start": (3.260345, -76.558729),
    "Point 1": (3.268444, -76.557621),
    "Point 2": (3.276224, -76.556545),
    "Point 3": (3.282640, -76.552424),
    "Point 4": (3.287327, -76.546453),
    "Point 5": (3.295010, -76.544032),
    "Point 6": (3.305124, -76.540869),
    "Point 7": (3.312282, -76.538440),
    "Point 8": (3.319838, -76.535761),
    "Point 9": (3.330306, -76.532753),
    "End": (3.342223, -76.530967)
}

# Funciones de API
def obtener_velocidad(lat, lon, api_key):
    url = f'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/6/json?point={lat},{lon}&key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()['flowSegmentData']
        return {
            "velocidad_actual": data['currentSpeed'],
            "flujo_libre": data['freeFlowSpeed'],
            "congestion": round(1 - data['currentSpeed'] / data['freeFlowSpeed'], 2),
            "confianza": data['confidence']
        }
    except Exception as e:
        print(f"Error al obtener velocidad: {e}")
        return {}

def obtener_ruta(api_key):
    url = f'https://api.tomtom.com/routemonitoring/3/routes/81564/details?key={api_key}'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {
            "distancia_ruta": data['routeLength'],
            "duracion_ruta": data['travelTime'],
            "demora_ruta": data['delayTime']
        }
    except Exception as e:
        print(f"Error al obtener ruta: {e}")
        return {}

# Inserción en MySQL
def insertar_trafico_mysql(resultados, tabla="trafico_cali"):
    try:
        with mysql.connector.connect(**DB_CONFIG) as conexion:
            with conexion.cursor() as cursor:
                cursor.executemany(f"""
                    INSERT INTO {tabla} (zona, lat, lon, timestamp, velocidad_actual, flujo_libre, congestion, confianza, distancia_ruta, duracion_ruta, demora_ruta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, resultados)
                conexion.commit()
                print(f"Insertados {cursor.rowcount} registros en {tabla}")
    except mysql.connector.Error as err:
        print(f"Error al insertar datos: {err}")

# Dataset
def generar_dataset(zonas, api_keys):
    try:
        df = pd.read_csv('trafico_cali.csv', index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame()

    datos_ruta = obtener_ruta(api_keys["ruta"])
    resultados = []

    for nombre, (lat, lon) in zonas.items():
        datos = obtener_velocidad(lat, lon, api_keys["trafico"])
        if datos:
            datos.update({
                "zona": nombre,
                "lat": lat,
                "lon": lon,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                **datos_ruta
            })
            resultados.append((
                datos["zona"],
                datos["lat"],
                datos["lon"],
                datos["timestamp"],
                datos["velocidad_actual"],
                datos["flujo_libre"],
                datos["congestion"],
                datos["confianza"],
                datos["distancia_ruta"],
                datos["duracion_ruta"],
                datos["demora_ruta"]
            ))


    if resultados:
        insertar_trafico_mysql(resultados)
        df = pd.concat([df, pd.DataFrame([dict(zip([
            "zona", "lat", "lon", "timestamp", "velocidad_actual", "flujo_libre", "congestion", "confianza",
            "distancia_ruta", "duracion_ruta", "demora_ruta"
        ], r)) for r in resultados])])
        df.drop(columns=[col for col in df.columns if col.startswith('Unnamed')], inplace=True)
        df.to_csv('trafico_cali.csv')
    return df

# Mapa
def generar_mapa(df, archivo_html="trafico_canasgordas.html"):
    mapa = folium.Map(location=[3.295010, -76.544032], zoom_start=12)
    for _, row in df.iterrows():
        color = 'red' if row['congestion'] > 0.5 else 'orange' if row['congestion'] > 0.2 else 'green'
        popup = folium.Popup(
            f"{row['zona']}<br>Velocidad: {row['velocidad_actual']} km/h<br>Congestión: {row['congestion']*100:.0f}%<br>Confianza: {row['confianza']}",
            max_width=300
        )
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            popup=popup,
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(mapa)
    mapa.save(archivo_html)
    print(f"Mapa actualizado: {archivo_html}")

# Monitoreo
def data_generation():
    print(f"\n Sensando tráfico: {datetime.now().strftime('%H:%M:%S')}")
    df = generar_dataset(ZONAS, API_KEYS)
    if not df.empty:
        print(df[["zona", "velocidad_actual", "flujo_libre", "congestion", "confianza", "distancia_ruta", "duracion_ruta", "demora_ruta"]])
        generar_mapa(df)

# Scheduler
schedule.every(1).minutes.do(data_generation)

if __name__ == "__main__":
    print(" Iniciando monitoreo de tráfico...")
    while True:
        schedule.run_pending()
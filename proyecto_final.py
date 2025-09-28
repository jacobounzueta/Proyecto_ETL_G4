#https://developer.tomtom.com/user/me/apps

#esto es una prueba

import requests
import pandas as pd
import folium
from datetime import datetime
import time
import schedule
import mysql.connector

DB_HOST = 'bsoc7uhsw5gjn4zf9ves-mysql.services.clever-cloud.com'
DB_NAME = 'bsoc7uhsw5gjn4zf9ves'
DB_USER = 'u27hjw3jfjaengp4'
DB_PASSWORD = 'yIUyH5vqgcH507V4HuZY'
DB_PORT = 3306
Connection_URI = 'mysql://u27hjw3jfjaengp4:yIUyH5vqgcH507V4HuZY@bsoc7uhsw5gjn4zf9ves-mysql.services.clever-cloud.com:3306/bsoc7uhsw5gjn4zf9ves'
MySQL_CLI = 'mysql -h bsoc7uhsw5gjn4zf9ves-mysql.services.clever-cloud.com -P 3306 -u u27hjw3jfjaengp4 -p bsoc7uhsw5gjn4zf9ves'

# API TomTom
API_KEY = 'G1Kx7s7TNR8FRXYcF9UHD06gFOXVuzCb'
API_KEY_2 = 'Q9n4jfzUJ8S32eAwzEEtkvBNGevA0Z28'
# Puntos estratégicos de cali
ZONAS = {
    #"Centro": (4.653, -74.083),
    # "Zona T": (4.667, -74.057),
    # "Usaquén": (4.702, -74.030),
    # "Kennedy": (4.631, -74.157),
    # "Suba": (4.748, -74.093),
    # "Chapinero": (4.645, -74.065),
    # "Fontibón": (4.678, -74.140),
    # "VALLE DE LILI": (3.374263, -76.524778),
    # "POPAYAN BARRIO": (2.437848, -76.602808)
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

try:
    connection = mysql.connector.connect(
        user = DB_USER,
        password = DB_PASSWORD,
        host = DB_HOST,
        port = DB_PORT,
        database = DB_NAME
    )
    cursor = connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS trafico_cali (id INT AUTO_INCREMENT PRIMARY KEY, zona VARCHAR(50), lat FLOAT, lon FLOAT, timestamp DATETIME, velocidad_actual FLOAT, flujo_libre FLOAT, congestion FLOAT, confianza INT, distancia_ruta FLOAT, duracion_ruta FLOAT, demora_ruta FLOAT)')
    print('Conexion exitosa')
    cursor.close()
    connection.close()
except mysql.connector.Error as err:
    print(f'Error: {err}')


#  Función para consultar tráfico
def obtener_velocidad(lat, lon, api_key):
    url = (
        f'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/6/json'
        f'?point={lat},{lon}&key={api_key}'
    )    
    """"
    - currentSpeed: velocidad promedio actual en el segmento (km/h).
    - freeFlowSpeed: velocidad esperada en condiciones óptimas (sin tráfico).
    - congestion: proporción de pérdida de velocidad, entre 0 (flujo libre) y 1 (tráfico detenido).

    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()['flowSegmentData']
            return {
                "velocidad_actual": data['currentSpeed'],
                "flujo_libre": data['freeFlowSpeed'],
                "congestion": round(1 - data['currentSpeed'] / data['freeFlowSpeed'], 2),
                "confianza": data['confidence']
            }
        else:
            return {"error": response.status_code}
    except Exception as e:
        return {"error": str(e)}

# Funcion para consultar distancia y tiempo de ruta
def obtener_ruta(api_key):
    url2 = (f'https://api.tomtom.com/routemonitoring/3/routes/81564/details?key=wvYEt70EmwoIsqblGepQjlgwCb5BmNIL')
    """"
    - routeLength: longitud del segmento (metros).
    - travelTime: tiempo estimado para recorrer el segmento (segundos).
    - delayTime: tiempo adicional debido al tráfico (segundos).
    """
    try:
        response = requests.get(url2)
        if response.status_code == 200:
            data_ruta = response.json()
            return {
                "distancia_ruta": data_ruta['routeLength'],
                "duracion_ruta": data_ruta['travelTime'],
                "demora_ruta": data_ruta['delayTime']
            }
        else:
            return {"error": response.status_code}
    except Exception as e:
        return {"error": str(e)}

#  Generar DataFrame
def generar_dataset(zonas, api_key):
    try:
        df = pd.read_csv('trafico_cali.csv', index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame()
    finally:
        datos_ruta = obtener_ruta(api_key)
        resultados = []
        for nombre, (lat, lon) in zonas.items():
            datos = obtener_velocidad(lat, lon, API_KEY_2)
            datos.update({
                "zona": nombre,
                "lat": lat,
                "lon": lon,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "distancia_ruta": datos_ruta.get("distancia_ruta"),
                "duracion_ruta": datos_ruta.get("duracion_ruta"),
                "demora_ruta": datos_ruta.get("demora_ruta")
            })
            resultados.append(datos)
            # Insert data into MySQL
            try:
                connection = mysql.connector.connect(
                    user = DB_USER,
                    password = DB_PASSWORD,
                    host = DB_HOST,
                    port = DB_PORT,
                    database = DB_NAME
                )
                cursor = connection.cursor()
                cursor.execute(
                    'INSERT INTO trafico_cali (zona, lat, lon, timestamp, velocidad_actual, flujo_libre, congestion, confianza, distancia_ruta, duracion_ruta, demora_ruta) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (nombre, lat, lon, datos['timestamp'], datos['velocidad_actual'], datos['flujo_libre'], datos['congestion'], datos['confianza'], datos_ruta.get("distancia_ruta"), datos_ruta.get("duracion_ruta"), datos_ruta.get("demora_ruta"))
                )
                connection.commit()
                cursor.close()
                connection.close()
            except Exception as e:
                pass
        df = pd.concat([df, pd.DataFrame(resultados)])
        cols_to_drop = [col for col in df.columns if col.startswith('Unnamed')]
        df.drop(columns=cols_to_drop, inplace=True)
        df.to_csv('trafico_cali.csv')
    return df

#  Visualizar en mapa interactivo
def generar_mapa(df, archivo_html="trafico_canasgordas.html"):
    mapa = folium.Map(location=[3.295010, -76.544032], zoom_start=12)
    for _, row in df.iterrows():
        color = 'red' if row['congestion'] > 0.5 else 'orange' if row['congestion'] > 0.2 else 'green'
        popup_text = (
            f"{row['zona']}<br>"
            f"Velocidad actual: {row['velocidad_actual']} km/h<br>"
            f"Congestión: {row['congestion']*100:.0f}%<br>"
            f"Confianza: {row['confianza']}"
        )
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=8,
            popup=popup_text,
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(mapa)
    mapa.save(archivo_html)
    print(f" Mapa actualizado: {archivo_html}")

#  Bucle de monitoreo continuo
def data_generation():
    try:
        print(f"\n Sensando tráfico: {datetime.now().strftime('%H:%M:%S')}")
        df_trafico = generar_dataset(ZONAS, API_KEY)
        print(df_trafico[["zona", "velocidad_actual", "flujo_libre", "congestion", "confianza","distancia_ruta","duracion_ruta","demora_ruta"]])
        generar_mapa(df_trafico)
    except KeyboardInterrupt:
        print("\n Monitoreo detenido por el usuario.")
# Schedule every minute
schedule.every(5).minutes.do(lambda: data_generation())
while True:
    schedule.run_pending()
    
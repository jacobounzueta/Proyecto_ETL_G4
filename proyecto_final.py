#https://developer.tomtom.com/user/me/apps

#esto es una prueba

import requests
import pandas as pd
import folium
from datetime import datetime
import time
import schedule

# API TomTom
API_KEY = 'G1Kx7s7TNR8FRXYcF9UHD06gFOXVuzCb'

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
    "Start": (3.260246, -76.558757),
    "Point 1": (3.266395, -76.557887),
    "Point 2": (3.276911, -76.556449),
    "Point 3": (3.280842, -76.555205),
    "Point 4": (3.292055, -76.544980),
    "Point 5": (3.306039, -76.540577),
    "Point 6": (3.310819, -76.538956),
    "Point 7": (3.325761, -76.533661),
    "Point 8": (3.332542, -76.532629),
    "Point 9": (3.336233, -76.531903),
    "Point 10": (3.338965, -76.531319),
    "End": (3.342193, -76.530978)
}

#  Función para consultar tráfico
def obtener_trafico(lat, lon, api_key):
    url = (
        f'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json'
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

#  Generar DataFrame
def generar_dataset(zonas, api_key):
    try:
        df = pd.read_csv('trafico_cali.csv')
    except FileNotFoundError:
        df = pd.DataFrame()
    finally:
        resultados = []
        for nombre, (lat, lon) in zonas.items():
            datos = obtener_trafico(lat, lon, api_key)
            datos.update({
                "zona": nombre,
                "lat": lat,
                "lon": lon,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            resultados.append(datos)
        df = pd.concat([df, pd.DataFrame(resultados)])
        df.to_csv('trafico_cali.csv')
    return df

#  Visualizar en mapa interactivo
def generar_mapa(df, archivo_html="trafico_bogota.html"):
    mapa = folium.Map(location=[4.653, -74.083], zoom_start=12)
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
        print(df_trafico[["zona", "velocidad_actual", "flujo_libre", "congestion", "confianza"]])
        generar_mapa(df_trafico)
    except KeyboardInterrupt:
        print("\n Monitoreo detenido por el usuario.")
# Schedule every minute
schedule.every(1).minutes.do(lambda: data_generation())
while True:
    schedule.run_pending()
    # time.sleep(1)
# if __name__ == "__main__":
#     try:
#         while True:
#             print(f"\n Sensando tráfico: {datetime.now().strftime('%H:%M:%S')}")
#             df_trafico = generar_dataset(ZONAS, API_KEY)
#             print(df_trafico[["zona", "velocidad_actual", "flujo_libre", "congestion", "confianza"]])
#             generar_mapa(df_trafico)
#             time.sleep(5)  # Espera 5 segundos antes del siguiente ciclo
#     except KeyboardInterrupt:
#         print("\n Monitoreo detenido por el usuario.")

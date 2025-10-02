import requests
import pandas as pd
import folium
from datetime import datetime
import streamlit as st
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# 🔁 Refrescar cada 5 segundos
st_autorefresh(interval=5000, limit=None, key="trafico_refresh")

# 🔐 API TomTom
API_KEY = '2TMm2dGQyjGHlyNTexX0S0GJfl3iRlBm'

# 📍 Puntos estratégicos
ZONAS = {
    "Centro": (4.653, -74.083),
    "Zona T": (4.667, -74.057),
    "Usaquén": (4.702, -74.030),
    "Kennedy": (4.631, -74.157),
    "Suba": (4.748, -74.093),
    "Chapinero": (4.645, -74.065),
    "Fontibón": (4.678, -74.140)
}

# 🔄 Consulta tráfico
def obtener_trafico(lat, lon, api_key):
    url = (
        f'https://api.tomtom.com/traffic/services/4/flowSegmentData/relative0/10/json'
        f'?point={lat},{lon}&key={api_key}'
    )
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

# 📊 Dataset
def generar_dataset(zonas, api_key):
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
    return pd.DataFrame(resultados)

# 🗺️ Mapa Folium
def generar_mapa(df):
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
    return mapa

# 🧭 Interfaz Streamlit
st.title("🚦 Monitoreo de tráfico en Bogotá")
st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

df_trafico = generar_dataset(ZONAS, API_KEY)

# 📊 Tabla de datos
st.subheader("📊 Datos por zona")
st.dataframe(df_trafico[["zona", "velocidad_actual", "flujo_libre", "congestion", "confianza"]])

# 🗺️ Mapa interactivo
st.subheader("🗺️ Mapa de congestión")
mapa = generar_mapa(df_trafico)
st_folium(mapa, width=700, height=500)

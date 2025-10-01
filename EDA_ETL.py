#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
#%%
data = pd.DataFrame()
for file in os.listdir():
    if file.startswith('Tabla_Trafico'):
        df = pd.read_csv(file)
        data = pd.concat([data, df], ignore_index=True)
        # data.drop_duplicates(inplace=True)
        data = data.drop(columns=['id'])
        data['timestamp'] = pd.to_datetime(data['timestamp'], format='%Y-%m-%d %H:%M:%S')
        # data.set_index('timestamp', inplace=True)
        data.sort_index(inplace=True)
        data.reset_index(drop=True, inplace=True)

#%%
data.info()
data.describe()

#%%
# Cols lat, lon and timestamp are not needed for the analysis
df = data.drop(columns=['lat', 'lon', 'timestamp'])
# Let's see the distribution of the numeric columns
for var in df.select_dtypes(include=np.number).columns:
    plt.figure(figsize=(10, 5))
    sns.histplot(df[var], kde=True)
    plt.title(f'Distribution of {var}')
    plt.show()
# %%
# Analyze numerical variables by hour
df['hour'] = data['timestamp'].dt.hour
for var in df.select_dtypes(include=np.number).columns:
    plt.figure(figsize=(10, 5))
    sns.lineplot(x='hour', y=var, data=df)
    plt.title(f'{var} by Hour')
    plt.show()
# %%
# Gráficos de velocidad_actual por zona en el tiempo
for zona in data['zona'].unique():
    plt.figure(figsize=(10, 5))
    df_zona = data[data['zona'] == zona]
    df_zona = df_zona.sort_values(by='timestamp')
    df_zona.set_index('timestamp', inplace=True)
    plt.plot(df_zona['velocidad_actual'])
    plt.title(f'Velocidad Actual in {zona}')
    plt.xlabel('Index')
    plt.ylabel('Velocidad Actual')
    plt.show()

#%% Comparación de velocidad_actual entre zonas boxplot
plt.figure(figsize=(12, 6))
sns.boxplot(x='zona', y='velocidad_actual', data=df)
plt.title("Velocidad Actual por Zona")
plt.xticks(rotation=45)
plt.show()
# %%
# Correlación entre variables numéricas
plt.figure(figsize=(10, 6))
corr = df[['velocidad_actual','flujo_libre','congestion',
           'distancia_ruta','duracion_ruta','demora_ruta']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Correlation Matrix")
plt.show()
#%% Pairplot
sns.pairplot(df[['velocidad_actual','congestion','duracion_ruta','demora_ruta']],
             diag_kind="kde")
plt.suptitle("Relaciones entre variables clave", y=1.02)
plt.show()
#%% Travel Time Index
df['tti'] = df['duracion_ruta'] / df['flujo_libre']
plt.figure(figsize=(12, 6))
sns.lineplot(x='hour', y='tti', data=df)
plt.title("Travel Time Index (TTI) por hora")
plt.show()
#%% STD de velocidad_actual por hora
std_by_hour = df.groupby('hour')['velocidad_actual'].std()
plt.figure(figsize=(12, 6))
std_by_hour.plot(marker='o')
plt.title("Desviación estándar de velocidad por hora")
plt.ylabel("Std Velocidad")
plt.show()
#%% Ranking de zonas por velocidad_actual promedio
ranking = df.groupby('zona')['velocidad_actual'].mean().sort_values()
plt.figure(figsize=(10, 5))
ranking.plot(kind='barh', color='red')
plt.title("Ranking de zonas con menor velocidad promedio")
plt.xlabel("Velocidad Promedio")
plt.show()
#%%
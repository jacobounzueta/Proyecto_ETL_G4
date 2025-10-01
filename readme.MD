# Entrega de proyecto final ETL
## Universidad Autónoma de Occidente
### Profesor: Juan Manuel Núñez Velasco
### Autores:
- Eliana Cardona
- Sergio Pantoja
- Rommel Prieto
- Jacobo Unzueta


# Objetivo del proyecto
Extraer información sobre el tráfico de ruta en la Avenida Cañasgordas de Santiago de Cali, Colombia, utilizando dos servicios de la API de TomTom como fuentes de datos.

# Stack tecnológico:
- Python (Pandas, Folium, Numpy, Matplotlib, Seaborn)
- Google LookerStudio
- MySQL
- GitHub

# Instalación de librerías
Las librerías requeridas para la ejecución de este proyecto se pueden instalar por medio de pip. 
1. pip install pandas
2. pip install numpy
3. pip install folium
4. pip install mysql-connector-python
5. pip install seaborn

# Ejecución
Este proyecto se ejecuta corriendo el script **proyecto_final.py** como script de ETL de los datos de ambos servicios de TomTom. Está programado para ejecutar la lectura de las APIs cada cinco minutos y escribir en la base de datos MySQL y un archivo local .csv.

# Hallazgos clave
- Temporalmente, se encuentra que en la mayoría de puntos del recorrido la hora en la que menor velocidad promedio hay es alrededor de las 7 AM. Después de las 8 y durante el resto de la mañana esta tiende a aumentar.
- El punto 6, cercano al cruce del rio es el punto donde mayor velocidad promedio hay independientemente de la hora.
- A las 8 A.M. se encuentra la mayor variabilidad en posibles indicadores de tráfico, principalmente en la velocidad promedio, con una desviación estándar de 13.7 km/h
- Los puntos 1 y 3 muestran el mayor nivel de tráfico general del recorrido. Estos puntos pueden ser estratégicos para la intervención y el mejoramiento del desempeño del tiempo de viaje en la zona.
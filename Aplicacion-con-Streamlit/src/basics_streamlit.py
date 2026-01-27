import streamlit as st #Herramienta para hacer interfaces Virtuales para Datos
from PIL import Image #Cargar Imagenes
import pandas as pd #Data convertir a Dataframes
import time #Para ver el tiempo de demora o para hacer delays

#import torch
#Yo asumo que el ingeniero de ML ya me ha dado el Modelo entrenado y me ha pedido deployar este modelo.
import joblib #Herramienta en la cual se encuentra mi modelo de ML
import numpy as np #Matematica
import matplotlib.pyplot as plt #Ploteos

#---------------------------------------------------------------------------------------------------------------------------
#Estas librerias son necesarias para mi MODELO de ML. Estas me las debió dar el Ingeniero de ML ----------------------------
from feature_engine.imputation import CategoricalImputer, MeanMedianImputer, AddMissingIndicator
from feature_engine.encoding import OrdinalEncoder, RareLabelEncoder
from sklearn.preprocessing import MinMaxScaler, Binarizer
from sklearn.pipeline import Pipeline

import input.preprocessors as pp
#----------------------------------------------------------------------------------------------------------------------------

#Creo una  carpeta y archivo de configuraciones para mantener un Orden en las variables que esta usando el Modelo
#Esto quiere decir que el Ing de ML ya me ha transferido las variables importantes para el Modelo.
# Importar las variables del archivo config.py
from configuraciones import config

#def prediccion_o_inferencia(modelo, datos_de_test):
def prediccion_o_inferencia(pipeline_de_test, datos_de_test):
    #Dropeamos
    datos_de_test.drop('Id', axis=1, inplace=True)
    # Cast MSSubClass as object
    datos_de_test['MSSubClass'] = datos_de_test['MSSubClass'].astype('O')
    datos_de_test = datos_de_test[config.FEATURES] #Aquí estoy aplicando mi SELECTED FEATURES

    new_vars_with_na = [
        var for var in config.FEATURES
        if var not in config.CATEGORICAL_VARS_WITH_NA_FREQUENT +
        config.CATEGORICAL_VARS_WITH_NA_MISSING +
        config.NUMERICAL_VARS_WITH_NA
        and datos_de_test[var].isnull().sum() > 0]

    datos_de_test.dropna(subset=new_vars_with_na, inplace=True)

    predicciones = pipeline_de_test.predict(datos_de_test)
    predicciones_sin_escalar = np.exp(predicciones)
    return predicciones, predicciones_sin_escalar, datos_de_test

# Designing the interface
st.title("Proyecto - Jessica Santizo  ")

image = Image.open('./src/images/CERTUS_LOGO.png')
st.image(image, use_column_width=True)

st.sidebar.write("Suba el archivo CSV Correspondiente para realizar la predicción")

#-------------------------------------------------------------------------------------------------
# Cargar el archivo CSV desde la barra lateral
uploaded_file = st.sidebar.file_uploader(" ", type=['csv'])

if uploaded_file is not None:
    # Leer el archivo CSV
    df_de_los_datos_subidos = pd.read_csv(uploaded_file)
    
    # Mostrar el contenido del archivo CSV
    st.write('Contenido del archivo CSV:')
    st.dataframe(df_de_los_datos_subidos)
#-------------------------------------------------------------------------------------------------
#Cargar el modelo
#modelo = torch.load('./modelos/melhor_modelo.pt')

#Cargar Pipeline
pipeline_de_produccion = joblib.load('precio_casas_pipeline.joblib')

if st.sidebar.button("Click aqui para enviar el CSV al Pipeline"):
    if uploaded_file is None:
        st.sidebar.write("No se cargó correctamente el archivo, subalo de nuevo")
    else:
        with st.spinner('Pipeline y Modelo procesando...'):

            #prediction = prediccion_o_inferencia(modelo, df_de_los_datos_subidos)
            prediction,prediction_sin_escalar, datos_procesados = prediccion_o_inferencia(pipeline_de_produccion, df_de_los_datos_subidos)
            time.sleep(3)
            st.success('Listo!')

            # Mostrar los resultados de la predicción
            st.write('Resultados de la predicción:')
            st.write(prediction) #Dataframe - 1 sola Columna
            st.write(prediction_sin_escalar) #Dataframe - 1 sola Columna

            # Graficar los precios de venta predichos
            fig, ax = plt.subplots()
            pd.Series(np.exp(prediction)).hist(bins=50, ax=ax)
            ax.set_title('Histograma de los precios de venta predichos')
            ax.set_xlabel('Precio')
            ax.set_ylabel('Frecuencia')

            # Mostrar la gráfica en Streamlit
            st.pyplot(fig)

            #Proceso para descargar todo el archivo con las predicciones
            #----------------------------------------------------------------------------------
            # Concatenar predicciones con el archivo original subido
            df_resultado = datos_procesados.copy()
            df_resultado['Predicción Escalada'] = prediction
            df_resultado['Predicción Sin Escalar'] = prediction_sin_escalar
            
            # Mostrar el DataFrame concatenado
            st.write('Datos originales con predicciones:')
            st.dataframe(df_resultado)

            # Crear archivo CSV para descargar
            csv = df_resultado.to_csv(index=False).encode('utf-8')

            # Botón para descargar el CSV
            st.download_button(
                label="Descargar archivo CSV con predicciones",
                data=csv,
                file_name='predicciones_casas.csv',
                mime='text/csv',
            )
            #----------------------------------------------------------------------------------

#streamlit run basics_streamlit.py
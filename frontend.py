import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración de la página
st.set_page_config(page_title="Reconocimiento de Dígitos", layout="centered")

st.title("Reconocimiento de Dígitos")

# Tamaño del lienzo
CANVAS_SIZE = 280

# Crear el lienzo para dibujar
canvas_result = st_canvas(
    fill_color="black",  # Color de fondo del lienzo
    stroke_width=20,     # Grosor del trazo
    stroke_color="white",# Color del trazo
    background_color="black", # Fondo negro para simular una pizarra
    width=CANVAS_SIZE,
    height=CANVAS_SIZE,
    drawing_mode="freedraw",
    key="canvas",
)

# Función para preprocesar la imagen
def preprocess_image(image: Image.Image) -> dict:
    image = image.resize((28, 28))  # Redimensionar a 28x28
    
    image = image.convert("L")      # Convertir a escala de grises
    image_array = np.array(image)# / 255.0  # Normalizar los píxeles

    # Construir el diccionario con las coordenadas "fila x columna"
    structured_data = {
        f"{i+1}x{j+1}": float(image_array[i, j])
        for i in range(28)
        for j in range(28)
    }

    return {"Inputs": {"data": [structured_data]}, "GlobalParameters": {"method": "predict"}}

# URL del endpoint del modelo en Azure

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT","http://fc1d22e3-b5e6-4b41-ade7-25ac40329b5f.eastus2.azurecontainer.io/score")

# Botón para realizar la predicción
if st.button("Predecir"):
    if canvas_result.image_data is not None:
        # Convertir la imagen del lienzo a un objeto PIL
        #st.image(canvas_result.image_data, caption="Imagen Dibujada", use_column_width=True)

        image = Image.fromarray((canvas_result.image_data))
        
        # Preprocesar la imagen
        payload = preprocess_image(image)

        # Encabezados de la solicitud
        headers = {
            "Content-Type": "application/json",
        }

        # Realizar la solicitud al endpoint de Azure
        response = requests.post(AZURE_ENDPOINT, headers=headers, data=json.dumps(payload))

        # Mostrar el resultado de la predicción
        if response.status_code == 200:
            result = response.json()
            st.success(f"Predicción: {result['Results'][0]}")
        else:
            st.error("Error al realizar la predicción.")
    else:
        st.warning("Por favor, dibuja un número en el lienzo.")
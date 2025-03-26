from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socket
import threading
import binascii
from datetime import datetime

app = FastAPI()

# Habilitar CORS para permitir peticiones desde el HTML
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite cualquier origen (ajústalo si es necesario)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables para almacenar datos recibidos
received_data = ""

# Constantes definidas (corrigiendo nombres)
LATITUD = 7.141126
LONGITUD = -73.12289
AZIMUT = 0
ELEVACION = 90
ALTITUD = 959
DESCRIPCION = "Lugar aquí"
FINICIAL = 1421000000  # Hz
FPASO = 1000  # Hz
NDATOS = 4096

def listen_gnuradio(ip="0.0.0.0", port=52001):
    """
    Escucha datos de GNU Radio a través de UDP.
    """
    global received_data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    print(f"🔵 Escuchando UDP en {ip}:{port}...")

    while True:
        try:
            data, addr = sock.recvfrom(4096)  # Recibe hasta 4096 bytes
            if data:
                try:
                    received_data = data.decode("utf-8").strip()
                except UnicodeDecodeError:
                    received_data = binascii.hexlify(data).decode("utf-8")
                print(f"📩 Datos recibidos de {addr}: {received_data}")
        except Exception as e:
            print(f"⚠️ Error recibiendo datos: {e}")

# Iniciar el hilo para escuchar UDP sin bloquear la ejecución del servidor
udp_thread = threading.Thread(target=listen_gnuradio, daemon=True)
udp_thread.start()

@app.get("/datos")
def get_data():
    """
    Devuelve los datos recibidos por UDP en formato JSON con los encabezados en el orden correcto.
    """
    global received_data

    # Convertimos los datos en una lista (separados por comas)
    datos_lista = received_data.split(",") if received_data else []

    return {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Fecha y hora actual
        "Latitud": LATITUD,
        "Longitud": LONGITUD,
        "Azimut": AZIMUT,
        "Elevacion": ELEVACION,
        "Altitud": ALTITUD,
        "Descripcion": DESCRIPCION,
        "Finicial": FINICIAL,  # Corregido el nombre
        "Fpaso": FPASO,  # Corregido el nombre
        "N": NDATOS,
        "Datos": datos_lista
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

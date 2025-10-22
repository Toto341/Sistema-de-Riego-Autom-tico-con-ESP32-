import network
import time

SSID = 'te'  # Poné tu SSID correcto
PASSWORD = '12345678'  # Poné tu contraseña correcta

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)

print("Conectando al WiFi...")

for _ in range(20):  # Espera máximo 20 segundos para conexión
    if station.isconnected():
        break
    time.sleep(1)

if station.isconnected():
    print("Conectado!")
    print("Configuración de red:", station.ifconfig())
    import main
else:
    print("No se pudo conectar al WiFi")
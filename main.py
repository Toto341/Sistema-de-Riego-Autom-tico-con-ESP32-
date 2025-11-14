import socket
from machine import Pin
import dht
import time
from machine import ADC

# --- Variables de control de la bomba ---
bomba_encendida = False
bomba_tiempo = 0
MAX_TIEMPO_BOMBA = 8000  # Tiempo máximo de encendido en milisegundos (8 segundos)
MIN_TIEMPO_BOMBA = 3000  # tiempo mínimo en milisegundos (3 segundos)
# Variable global para confirmar suelo seco de forma estable
muestras_secas = 0
# Variables globales para almacenar los últimos valores
last_temp = None
last_hum = None
last_read_time = 0

# 🚨 Ajustá el pin del DHT11 (ej: 14, 27, etc.)
sensor = dht.DHT11(Pin(14))

# --- Sensor de humedad del suelo ---
soilPin = 32  # pin ADC donde conectás el sensor
dryValue = 1023  # valor calibrado suelo seco
wetValue = 430   # valor calibrado suelo húmedo

adc = ADC(Pin(soilPin))
adc.atten(ADC.ATTN_11DB)    # rango hasta 3.3V
adc.width(ADC.WIDTH_10BIT)  # resolución 10 bits (0-1023)

# --- Relé para bomba ---
relay = Pin(26, Pin.OUT)
relay.value(0)  # apagado al iniciar

# Límites de humedad del suelo (%)
LOW_THRESHOLD = 55  # debajo de este valor, se enciende la bomba
HIGH_THRESHOLD = 75 # por encima de este valor, se apaga la bomba

def read_sensor():
    global last_temp, last_hum, last_read_time
    current_time = time.ticks_ms()

    # Solo volver a medir si pasaron más de 2 segundos
    if time.ticks_diff(current_time, last_read_time) > 2000:
        try:
            sensor.measure()
            last_temp = sensor.temperature()
            last_hum = sensor.humidity()
            last_read_time = current_time
        except OSError:
            pass  # deja los valores anteriores si falla la lectura

    return last_temp, last_hum

def read_sensor_json():
    temp, hum = read_sensor()
    soil = read_soil_moisture()
    if temp is None:
        return '{"temp": null, "hum": null, "soil": %s}' % soil
    else:
        return '{"temp": %s, "hum": %s, "soil": %s}' % (temp, hum, soil)
    
def read_soil_moisture():
    sensorReading = adc.read()
    # Mapear valor del rango [dryValue, wetValue] a [0, 100]
    moisturePercentage = int((sensorReading - dryValue) * (100 - 0) / (wetValue - dryValue) + 0)

    # Limitar entre 0 y 100
    if moisturePercentage < 0:
        moisturePercentage = 0
    if moisturePercentage > 100:
        moisturePercentage = 100

    return moisturePercentage

def control_bomba(moisture):
    """
    Controla el encendido y apagado automático de la bomba de agua
    evitando falsos arranques por lecturas inestables.
    """
    global bomba_encendida, bomba_tiempo, muestras_secas
    ahora = time.ticks_ms()

    # --- Lógica para encendido ---
    if not bomba_encendida:
        # Si el suelo está seco, aumentamos el contador
        if moisture < (LOW_THRESHOLD - 3):
            muestras_secas += 1
        else:
            muestras_secas = 0  # se reinicia si vuelve a estar húmedo

        # Solo enciende si hay 3 lecturas consecutivas de suelo seco
        if muestras_secas >= 3:
            relay.value(1)
            bomba_encendida = True
            bomba_tiempo = ahora
            muestras_secas = 0
            print("💧 Bomba encendida (humedad baja estable)")

    # --- Lógica para apagado ---
    elif bomba_encendida:
        tiempo_encendida = time.ticks_diff(ahora, bomba_tiempo)
        if (moisture > (HIGH_THRESHOLD + 3) and tiempo_encendida > MIN_TIEMPO_BOMBA) or tiempo_encendida > MAX_TIEMPO_BOMBA:
            relay.value(0)
            bomba_encendida = False
            print("🚫 Bomba apagada (humedad suficiente o tiempo cumplido)")


def web_page():
    temp, hum = read_sensor()
    if temp is None:
        html = """<html><body><h1>Error leyendo DHT11</h1></body></html>"""
    else:
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title></title>

    <style>
        *{{
            margin: 0;
            padding: 0;
        }}
        body{{
            font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            font-size: 0.8rem;
            background-color:#BBD4EC;
            margin: 0;
            padding: 0;
        }}
        main {{
            padding: 20px;
        }}

        header {{
            padding: 20px;
            text-align: center;
        }}

        header h3{{
            margin-top: 20px;
        }}

        .card_container{{
            display: flex;
            flex-direction: row;
            justify-content:space-between;
            margin-top: 30px;
        }}
        .card {{
            width: 170px;
            height: 250px;
            background-color:#F7FBFF;
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            justify-content: center; /* centra verticalmente */
            align-items: center;     /* centra horizontalmente */
        }}

         .card2 {{
            width: 390px;
            height: 250px;
            background-color:#F7FBFF;
            border-radius: 20px;
            margin-top: 1.5rem;
            display: flex;
            flex-direction: column;
            justify-content: center; /* centra verticalmente */
            align-items: center;    /* centra horizontalmente */
        }}

        .card p {{
            margin: 0; 
            padding: 0;
        }}
        
        .card .temp {{
            font-size: 2rem;
            margin-bottom: 2rem;
        }}

        .card .log {{
            font-size: 4rem;
            margin-bottom: 2rem;
        }}

        .card .text {{ 
            font-size: 1.5rem;
            
        }}
         .card2 p {{
            margin: 0; 
            padding: 0;
        }}
        

         .card2 .temp {{
            font-size: 2rem;
            margin-bottom: 2rem;
        }}

        .card2 .log {{
            font-size: 4rem;
            margin-bottom: 2rem;
        }}

        .card2 .text {{ 
            font-size: 1.5rem;
            
        }}

        .texto{{
            text-align: justify;
            font-size: 1rem;

        }}
        .texto h3{{
            margin-top: 1rem;
            margin-bottom: 1rem;
        }}

        .texto p {{
            margin-top: 2rem;
            margin-bottom: 2rem;
        }}
        body h2 {{
            margin-top: 2rem;
        }}
        

        .foot{{
            background-color: #F7FBFF;
            width: 100%;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .list {{
            margin-bottom: 1.5rem;
            margin-left: 1rem;
        }}
        .listado{{
            margin-right: 1.5rem;
        }}

        .container {{
            text-align: center;
        }}

        .img {{
            max-width: 100%;
            border-radius: 30px;
            height: 250px;
            width: 300px;
            margin-bottom: 0.5rem;
        }}

        .content{{
            margin-bottom: 1rem;
            margin-top: 2rem;
        }}

        .pip p {{
            margin-top: 1.5rem;
        }}

        .content h3 {{
            margin-bottom: 2rem;
        }}

        /* Desktop */
        @media (min-width: 800px) {{
        /* Estilos para escritorio (desktop) */
            .container {{
                margin: 0 auto;
                display: flex;
                flex-direction: column;                                
                max-width: 800px;               
            }}
            .card_container{{
                justify-content:center;
                gap: 2rem;
            }}
            .card2_container {{
                display: flex;
                justify-content: center;
            }}
            .head {{ 
                background-color: #F7FBFF;
                width: 100%;
                padding: 1.5rem;
                text-align: center;
              
            }}
    
            body{{
            font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;
            font-size: 0.8rem;
            background-color:#BBD4EC;
             }}
            main {{
                padding: 20px;
            }}
            
            .card {{
                width: 400px;
                height: 500px;
                background-color:#F7FBFF;
                border-radius: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center; /* centra verticalmente */
                align-items: center;     /* centra horizontalmente */
            }}

            .card2 {{
                width: 3470px;
                height: 300px;
                background-color:#F7FBFF;
                border-radius: 20px;
                margin-top: 1.5rem;
                display: flex;
                flex-direction: column;
                justify-content: center; /* centra verticalmente */
                align-items: center;    /* centra horizontalmente */
            }}

            .card p {{
                margin: 0; 
                padding: 0;
            }}
            
            .card .temp {{
                font-size: 3rem;
                margin-bottom: 3rem;
            }}

            .card .log {{
                font-size: 5rem;
                margin-bottom: 3rem;
            }}

            .card .text {{ 
                font-size: 2rem;
                
            }}
            .card2 p {{
                margin: 0; 
                padding: 0;
            }}
            

            .card2 .temp {{
                font-size: 3rem;
                margin-bottom: 3rem;
            }}

            .card2 .log {{
                font-size: 4rem;
                margin-bottom: 2rem;
            }}

            .card2 .text {{ 
                font-size: 2rem;
                
            }}

            .texto{{
                text-align: justify;
                font-size: 1rem;
            

            }}
            body h2 {{
                margin-top: 2rem;
            }}

            .foot{{
                background-color: #F7FBFF;
                width: 100%;
                height: 40px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .list {{
                margin-bottom: 1.5rem;
            }}
            .listado{{
                margin-right: 1.5rem;
            }}

            .container {{
                text-align: center;
            }}

            .img {{
                max-width: 100%;
                border-radius: 30px;
                margin-bottom: 0.5rem;
            }}

            .content{{
                margin-bottom: 1rem;
                margin-top: 2rem;
                display: flex;
                background-color:#ffffff;
                border-radius: 20px ;
                padding: 2rem;
                gap: 2rem;
            }}
            
            .card3{{
                width: 720px;
                height: 520px;
                background-color:#F7FBFF;
                border-radius: 20px;
                display: flex;
                flex-direction: column;
                justify-content: center; /* centra verticalmente */
                align-items:center; 
                margin-top: 2rem;
                padding: 2.5rem;
            }}
             .texto h2 {{
            text-align: center;
            margin-bottom: 2rem;
        }}
            .texto p {{
                margin-top: 2rem;
                margin-bottom: 1rem;
            }}

            .texto h3 {{
                margin-top: 2rem;
            }}

            .pip {{
                display: flex;
                
            }}
            .pip img {{ 
                margin-right: 2rem;
            }}

            .util {{ 
                display: flex;
                background-color: #F7FBFF;
                margin-top: 2rem;
                border-radius: 20px;
                width: 250px;
                
            
            }}

            .util h2 {{ 
                margin: 1rem;
            }}
        }}
            

        .texto h2 {{
            text-align: center;
            margin-bottom: 1rem;
        }}

    </style>
</head>
<body>
    <header class="head">
        <h1>Consulta la temperatura y humedad en tiempo real</h1>
        <h3>Datos confiables directamente desde nuestra estación meteorológica</h3>
    </header>

    <main class="container">
        <div class="card_container">

            <div class="card">
              <p class="log">&#9728;</p>  
              <p class="temp">{} °C</p>
              <p class="text">Temperatura</p>
            </div>

            <div class="card">
                <p class="log">&#128167;</p>
                <p class="temp">{} %</p>
                <p class="text">Humedad</p>
            </div>

        </div>
    

    <section class="card2_container">
        <div class="card2">
            <p class="log">&#128167;</p>
            <p class="temp"> {}%</p>
            <p class="text">Humedad del suelo</p>
        </div>
    </section>

    <section >
        <div class="card3">
            <div class="texto">
                    <h2>Sobre la estación meteorológica</h2>
                    <p>Nuestra estación meteorológica está basada en un microcontrolador ESP32, 
                que permite medir la temperatura, la humedad ambiental
                y la humedad del suelo en tiempo real. 
                Los datos se procesan y envían a esta plataforma web, brindando información precisa 
                sobre las condiciones locales de manera simple y confiable.</p>
            </div>

            <div class="texto" >
                <h3>¿Cómo funciona?</h3>
                <p>Nuestra estación meteorológica combina simplicidad y utilidad real.</p>
                <ul class="listado">
                    <li class="list">Sensores confiables: utilizamos un DHT11 para medir la temperatura y la humedad del aire, y un sensor capacitivo para conocer la humedad del suelo.</li>
                    <li class="list">Cerebro conectado: un microcontrolador ESP32 procesa la información y la envía directamente a esta plataforma web en tiempo real</li>
                    <li class="list">Acción práctica: cuando el sensor detecta que el suelo está seco, se activa el riego automático de la planta, asegurando que nunca le falte agua.</li>
                </ul>
            </div>
        </div>
        <div>
            <div class="util">
                <h2>Elementos utilizados</h2>
             </div>
            <div class="content">
                <h3>ESP32</h3>
                <div class="pip">
                    <img src="https://cotena.net/toto/01.jpeg" alt=""  class="img">
                <p class="texto">La ESP32 es una placa electrónica compacta y potente que combina microcontrolador y conectividad WiFi/Bluetooth. Permite leer sensores, controlar dispositivos y enviar datos a Internet, lo que la hace ideal para proyectos de IoT, como estaciones meteorológicas, domótica o automatización de sistemas. Además, es compatible con MicroPython, Arduino y otros entornos de programación, facilitando el desarrollo de soluciones inteligentes y conectadas.</p>
                </div>
            </div>

            <div class="content">
                <h3>DHT11</h3>
                <div class="pip">
                    <img src="https://cotena.net/toto/02.jpeg" alt=""  class="img">
                
                    <p class="texto">El DHT11 es un sensor electrónico diseñado para medir temperatura y humedad ambiental de manera sencilla y precisa. Es muy utilizado en proyectos de IoT y domótica, estaciones meteorológicas y monitoreo ambiental.
                                Gracias a su compatibilidad con placas como ESP32 o Arduino, permite capturar datos en tiempo real y enviarlos a sistemas conectados, ayudando a crear soluciones inteligentes para el control del clima y la automatización de espacios.</p>
                </div>
            </div>

             <div class="content">
                <h3>Sensor capacitivo</h3>
                <div class="pip">
                    <img src="https://cotena.net/toto/03.jpeg" alt=""  class="img">
                    <p class="texto">El sensor capacitivo de humedad del suelo mide la cantidad de agua en la tierra detectando cambios en la capacitancia del material entre sus electrodos. Cuando el suelo está más húmedo, su capacitancia aumenta; cuando está seco, disminuye. Estos cambios se traducen en señales eléctricas que la placa (ESP32, Arduino, etc.) puede leer para decidir si activar o no el riego.</p>
                </div>
            </div>

             <div class="content">
                <h3>Módulo relé</h3>
                <div class="pip">
                    <img src="https://cotena.net/toto/04.jpeg" alt=""  class="img">
                    <p class="texto">El módulo relé es un interruptor electrónico que permite controlar dispositivos de mayor potencia usando señales de bajo voltaje de una placa como ESP32. En un sistema de riego automatizado, el relé actúa como puente entre la placa y la bomba de agua, encendiéndola o apagándola según las mediciones del sensor de humedad, garantizando un riego seguro y automatizado.</p>
                </div>
            </div>

             <div class="content">
                <h3>Bomba de agua</h3>
                <div class="pip">
                    <img src="https://cotena.net/toto/05.jpeg" alt=""  class="img">
                    <p class="texto">La bomba de agua es el componente que transporta el agua hacia las plantas en un sistema de riego automatizado. Controlada mediante el módulo relé, se activa solo cuando el sensor de humedad detecta que la tierra necesita agua, permitiendo un riego eficiente, programado y sin intervención manual, ideal para mantener jardines y cultivos saludables.</p>
                </div>
            </div>
        </div>
    </section>

    </main>

    <footer>
        <div class="foot">
            <p>© 2025 Estación Meteorológica | Proyecto Montajes</p>
        </div>
    </footer>
        <script>
            function updateData() {{
                fetch("/data")
                .then(response => response.json())
                .then(function(data) {{
                    document.querySelector(".card_container .card:nth-child(1) .temp").textContent = data.temp + " °C";
                    document.querySelector(".card_container .card:nth-child(2) .temp").textContent = data.hum + " %";
                    document.querySelector(".card2 .temp").textContent = data.soil + " %"; // 🌱 Nuevo dato
                }});
            }}
            setInterval(updateData, 3000);
            updateData(); 
</script>
</body>
</html>""".format(temp, hum, read_soil_moisture())
    return html

# Crear servidor
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # evita EADDRINUSE
s.bind(addr)
s.listen(5)

print("🌐 Servidor HTTP escuchando en puerto 80...")

# Mensaje inicial
print("🔧 Inicializando sensores y sistema de riego...")
time.sleep(2)  # pequeña pausa visual

TIEMPO_ESPERA_INICIAL = 20000  # 10 segundos
inicio_bomba = time.ticks_ms()
print("⏳ Esperando {} segundos antes de activar el control automático de la bomba...".format(TIEMPO_ESPERA_INICIAL / 1000))
control_activo = False
while True:

    soil = read_soil_moisture()
    if not control_activo and time.ticks_diff(time.ticks_ms(), inicio_bomba) > TIEMPO_ESPERA_INICIAL:
        control_activo = True
        print("✅ Control automático de bomba activado.")
    
    if control_activo:
        control_bomba(soil)
    try:
        cl, addr = s.accept()
        print('Cliente conectado desde', addr)
        cl_file = cl.makefile('rwb', 0)

        request_line = cl_file.readline().decode()
        if not request_line:
            cl.close()
            continue

        try:
            path = request_line.split(' ')[1]
        except IndexError:
            path = '/'

        # Descarta las demás líneas del header
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break

        if path == '/data':
            soil = read_soil_moisture()
            # Control automático de la bomba
            response = read_sensor_json()
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: application/json\r\n')
            cl.send('Connection: close\r\n\r\n')
            cl.sendall(response)
        else:
            response = web_page()
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: text/html\r\n')
            cl.send('Connection: close\r\n\r\n')
            cl.sendall(response)

    except Exception as e:
        print("⚠️ Error manejando cliente:", e)

    finally:
        try:
            cl.close()
        except:
            pass

    time.sleep_ms(10)
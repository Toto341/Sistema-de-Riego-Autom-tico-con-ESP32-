# RiegoAutomtico-ESP32
🌱 Control de Humedad del Suelo con ESP32

Este proyecto permite medir y automatizar el riego de plantas mediante un sensor capacitivo de humedad del suelo, controlado por una placa ESP32.
El sistema analiza la humedad en tiempo real y, cuando detecta que el suelo está seco, activa una bomba de agua a través de un módulo relé de 5 V, garantizando el riego automático.

⚙️ Componentes principales

ESP32 – Controlador principal del sistema.

Sensor capacitivo de humedad del suelo (5 V) – Detecta el nivel de humedad.

Divisor resistivo (10 kΩ y 22 kΩ) – Protege el pin ADC del ESP32 al reducir el voltaje.

Capacitor cerámico de 100 nF (50 V) – Filtra el ruido para obtener lecturas estables.

Módulo relé de 5 V (1 canal) – Controla la bomba de agua.

Bomba de agua 5 V – Encargada del riego.

🔍 Funcionamiento

El sensor capacitivo mide la humedad del suelo y envía una señal analógica al ESP32.

El ESP32 convierte esa lectura en un porcentaje de humedad.

Según el valor, el sistema determina el estado del suelo: seco, ideal o muy húmedo.

Si el suelo está seco, el ESP32 activa el relé, encendiendo la bomba de agua.

Una vez que el nivel de humedad se estabiliza, la bomba se apaga automáticamente.

💡 Características

Lecturas filtradas y estables gracias al capacitor cerámico.

Protección del ADC con divisor resistivo.

Compatible con monitoreo en tiempo real vía consola o interfaz web.

Ideal para automatizar el riego en macetas o pequeños huertos.

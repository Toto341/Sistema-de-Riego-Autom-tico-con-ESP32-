# RiegoAutomtico-ESP32
🌱 Control de Humedad del Suelo con ESP32

Este proyecto utiliza un ESP32 para medir la humedad del suelo con un sensor capacitivo, controlar el riego mediante una bomba de agua y un módulo relé, y visualizar los datos en tiempo real a través de un servidor web integrado.
El sistema busca automatizar el riego de plantas de forma eficiente, precisa y económica.

🔌 Hardware utilizado
 - ESP32 – Controlador principal del sistema.
 - Sensor capacitivo de humedad del suelo (5 V) – Detecta el nivel de humedad.
 - Sensor de temperatura + gumedad del ambiente – Permite medir la humedad y temperatura del ambiente.
 - Módulo relé de 5 V (1 canal) – Controla la bomba de agua.
 - Bomba de agua 5 V – Encargada del riego.

⚙️ Funcionamiento
El sensor capacitivo envía una señal analógica al ESP32, que convierte ese valor en un porcentaje de humedad del suelo.
De forma simultánea, un sensor DHT11 mide la temperatura y humedad ambiental.
Con esta información, el ESP32 evalúa el estado del suelo:
Si la humedad es baja, activa la bomba mediante el módulo relé para regar.
Si la humedad es adecuada o alta, mantiene la bomba apagada.
Todos los valores medidos se muestran en una interfaz web local, accesible desde cualquier dispositivo conectado a la misma red Wi-Fi. La página se actualiza en tiempo real y presenta los datos de forma clara y visual.

# Bug Hunter Arcade [BHA]

Shooter arcade espacial en **pixel art** desarrollado en **Python** con **Pygame**, con telemetría táctica, comunicaciones de radio de dos líneas, apoyo de la EEI (ISS) y reinicio rápido pensado para partidas y transmisiones en vivo (LIVEs).

## Características principales
- **Sistema solar y EEI (ISS):** Planetas y Sol en pixel art junto a la Estación Espacial Internacional con soporte y abastecimiento de escudos.
- **Radio táctica (máx. 2 líneas):** Mensajes breves con barra de lectura y tono de enlace sintetizado en memoria sin depender de archivos externos.
- **Naves nodrizas colosales y telemetría:** Detección previa en radar, combate contra entidades de gran escala y datos de tamaño, distancia y velocidad.
- **Dron secreto hacia la Tierra:** La nave nodriza puede desplegar un dron sigiloso rumbo a la Tierra; si llega, activa **Game Over** con reinicio instantáneo al pulsar **ENTER**.

## Controles
- **ESPACIO:** Disparar cañones principales.
- **ENTER:** Reiniciar la misión tras un Game Over.
- **ESC:** Salir del juego.

## Instalación y ejecución
```bash
pip install pygame
python bha_main.py

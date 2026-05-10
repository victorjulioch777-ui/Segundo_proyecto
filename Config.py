"""
Contiene todas las constantes globales del juego Laberinto Dinámico.
Centralizar estos valores aquí permite modificar el comportamiento del juego
sin tener que buscar en múltiples archivos.
"""

import os

# Tamaños permitidos para el mapa del juego (filas x columnas)
TAMANOS_MAPA = [10, 20, 30]

# Porcentaje de obstáculos al generar una nueva fila
PORCENTAJE_OBSTACULOS = 0.60  # 60%

# Valores que representarán los elementos en la matriz (mapa lógico)
CELDA_LIBRE = 0
CELDA_OBSTACULO = 1

# Tiempo inicial en segundos que tarda el mapa en desplazarse una fila hacia abajo
INTERVALO_DESPLAZAMIENTO_INICIAL = 2.0

# Cada cuántos segundos de juego se debe aumentar la dificultad
INTERVALO_AUMENTO_DIFICULTAD = 15.0

# Cuánto disminuye el intervalo de desplazamiento por cada aumento de dificultad
DISMINUCION_TIEMPO = 0.1

# Tiempo de aparición de nuevos elementos (monedas, bombas, etc.) en segundos
INTERVALO_APARICION_ELEMENTOS = 5.0

# Tiempo de vida útil de un poder o elemento en el mapa antes de desaparecer
TIEMPO_VIDA_PODER = 10.0

# Tamaño en píxeles de cada celda al ser dibujada en pantalla
TAMANO_CELDA_GUI = 30

# Colores usados en el lienzo (Canvas)
COLOR_FONDO = "#2E2E2E"        # Color de fondo general
COLOR_CELDA_LIBRE = "#D3D3D3"  # Gris claro
COLOR_OBSTACULO = "#4A4A4A"    # Gris oscuro / muro
COLOR_JUGADOR = "#1E90FF"      # Azul claro
COLOR_MONEDA_NORMAL = "#FFD700" # Dorado
COLOR_MONEDA_ESPECIAL = "#FF8C00" # Naranja
COLOR_BOMBA = "#FF0000"        # Rojo
COLOR_PASO_FANTASMA = "#DA70D6" # Orquídea/Morado claro
COLOR_TEXTO = "#FFFFFF"        # Blanco para textos informativos
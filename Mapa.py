import random

from Config import (
    CELDA_LIBRE,
    CELDA_OBSTACULO,
    PORCENTAJE_OBSTACULOS,
    TIPO_BOMBA,
    TIPO_MONEDA_ESPECIAL,
    TIPO_MONEDA_NORMAL,
    TIPO_PASO_FANTASMA,
    VALOR_MONEDA_ESPECIAL,
    VALOR_MONEDA_NORMAL,
)


class Mapa:
    """
    Representa el mapa dinámico del laberinto, que actúa como el entorno principal del juego.

    El mapa mantiene siempre una matriz cuadrada de un tamaño fijo definido por el jugador. 
    Al inicio sus celdas están vacías, y a medida que el juego avanza, se generan nuevas 
    filas con obstáculos desde la parte superior, empujando todo el contenido hacia abajo.
    Además, es el responsable de mantener y administrar los elementos (poderes y recompensas).
    """

    def __init__(self, tamano):
        self.tamano = tamano
        self.celdas = []
        self.elementos = {}
        self.filas_generadas = 0
        self.generar_vacio()

    def generar_vacio(self):
        """
        Crea una matriz libre para comenzar la construccion progresiva.
        """
        self.celdas = [
            [CELDA_LIBRE for _ in range(self.tamano)]
            for _ in range(self.tamano)
        ]
        self.elementos = {}
        self.filas_generadas = 0

    def crear_fila(self):
        """
        Crea una fila con cerca de 60% de obstaculos y sin mas de dos libres seguidas.
        """
        obstaculos_objetivo = round(self.tamano * PORCENTAJE_OBSTACULOS)
        libres_objetivo = self.tamano - obstaculos_objetivo
        obstaculos_restantes = obstaculos_objetivo
        libres_restantes = libres_objetivo
        libres_consecutivas = 0
        fila = []

        for indice in range(self.tamano):
            posiciones_restantes = self.tamano - indice

            if libres_consecutivas >= 2 and obstaculos_restantes > 0:
                celda = CELDA_OBSTACULO
            elif obstaculos_restantes == 0:
                celda = CELDA_LIBRE
            elif libres_restantes == 0:
                celda = CELDA_OBSTACULO
            elif obstaculos_restantes >= posiciones_restantes:
                celda = CELDA_OBSTACULO
            else:
                probabilidad_obstaculo = obstaculos_restantes / posiciones_restantes
                celda = CELDA_OBSTACULO if random.random() < probabilidad_obstaculo else CELDA_LIBRE

            if celda == CELDA_LIBRE:
                libres_restantes -= 1
                libres_consecutivas += 1
            else:
                obstaculos_restantes -= 1
                libres_consecutivas = 0

            fila.append(celda)

        return fila

    def desplazar(self):
        """
        Inserta una nueva fila de obstáculos en la parte superior (índice 0) y 
        elimina la fila inferior. Todos los elementos presentes en el mapa también 
        desplazan su posición visual hacia abajo para mantenerse sincronizados.
        """
        self.celdas.insert(0, self.crear_fila())
        self.celdas.pop()
        self.filas_generadas = min(self.tamano, self.filas_generadas + 1)

        elementos_desplazados = {}
        for (fila, columna), datos in self.elementos.items():
            nueva_fila = fila + 1
            if nueva_fila < self.tamano:
                elementos_desplazados[(nueva_fila, columna)] = datos

        self.elementos = elementos_desplazados

    def es_posicion_valida(self, fila, columna):
        """
        Indica si el jugador puede caminar a una posicion libre dentro del mapa.
        """
        if fila < 0 or fila >= self.tamano:
            return False
        if columna < 0 or columna >= self.tamano:
            return False

        return self.celdas[fila][columna] == CELDA_LIBRE

    def obtener_posicion_libre(self, posicion_jugador=None):
        """
        Busca una celda libre sin elementos para colocar recompensas o poderes.
        """
        posiciones = []
        for fila in range(self.tamano):
            for columna in range(self.tamano):
                posicion = (fila, columna)
                if posicion == posicion_jugador:
                    continue
                if self.celdas[fila][columna] == CELDA_LIBRE and posicion not in self.elementos:
                    posiciones.append(posicion)

        if not posiciones:
            return None

        return random.choice(posiciones)

    def agregar_elemento_aleatorio(self, tiempo_actual, posicion_jugador=None):
        """
        Agrega una moneda o poder aleatorio en una celda libre.
        """
        tipo = random.choices(
            [TIPO_MONEDA_NORMAL, TIPO_MONEDA_ESPECIAL, TIPO_BOMBA, TIPO_PASO_FANTASMA],
            weights=[35, 20, 25, 20],
            k=1,
        )[0]
        return self.agregar_elemento(tipo, tiempo_actual, posicion_jugador)

    def agregar_elemento(self, tipo, tiempo_actual, posicion_jugador=None):
        """
        Agrega un elemento especifico en una celda libre.
        """
        posicion = self.obtener_posicion_libre(posicion_jugador)
        if posicion is None:
            return None

        self.elementos[posicion] = {"tipo": tipo, "creado": tiempo_actual}
        return tipo

    def contar_elementos(self, tipo_buscado):
        """
        Cuenta cuantas instancias visibles hay de un tipo de elemento.
        """
        return sum(
            1
            for datos in self.elementos.values()
            if datos["tipo"] == tipo_buscado
        )

    def eliminar_elementos_expirados(self, tiempo_actual, tiempo_vida):
        """
        Elimina elementos que exceden su tiempo de vida.
        """
        self.elementos = {
            posicion: datos
            for posicion, datos in self.elementos.items()
            if tiempo_actual - datos["creado"] <= tiempo_vida
        }

    def obtener_elementos_visibles(self):
        """
        Retorna los elementos en un formato simple para la interfaz.
        """
        return {
            posicion: datos["tipo"]
            for posicion, datos in self.elementos.items()
        }

    def recoger_elemento(self, jugador):
        """
        Recoge el elemento donde esta el jugador y aplica puntos si es moneda.
        """
        posicion = (jugador.fila, jugador.columna)
        datos = self.elementos.pop(posicion, None)
        if datos is None:
            return None

        tipo = datos["tipo"]
        if tipo == TIPO_MONEDA_NORMAL:
            jugador.puntaje += VALOR_MONEDA_NORMAL
        elif tipo == TIPO_MONEDA_ESPECIAL:
            jugador.puntaje += VALOR_MONEDA_ESPECIAL

        return tipo

    def destruir_obstaculo(self, fila, columna, direccion):
        """
        Destruye el primer obstaculo adyacente en la direccion indicada.
        """
        destino_fila = fila + direccion[0]
        destino_columna = columna + direccion[1]

        if destino_fila < 0 or destino_fila >= self.tamano:
            return False
        if destino_columna < 0 or destino_columna >= self.tamano:
            return False
        if self.celdas[destino_fila][destino_columna] != CELDA_OBSTACULO:
            return False

        self.celdas[destino_fila][destino_columna] = CELDA_LIBRE
        return True

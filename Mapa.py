import random

from Config import CELDA_LIBRE, CELDA_OBSTACULO, PORCENTAJE_OBSTACULOS
from Elementos import VALOR_MONEDA_ESPECIAL, VALOR_MONEDA_NORMAL
from Utilidades import TIPO_BOMBA, TIPO_PASO_FANTASMA


TIPO_MONEDA_NORMAL = "moneda_normal"
TIPO_MONEDA_ESPECIAL = "moneda_especial"


class Mapa:
    """
    Representa el mapa logico del laberinto.
    """

    def __init__(self, tamano):
        self.tamano = tamano
        self.celdas = []
        self.elementos = {}
        self.generar()

    def generar(self):
        """
        Crea un mapa nuevo con obstaculos y algunos elementos.
        """
        self.celdas = []
        self.elementos = {}

        for fila in range(self.tamano):
            nueva_fila = []
            for columna in range(self.tamano):
                es_borde_inicio = fila == self.tamano - 1 and columna == self.tamano // 2
                if es_borde_inicio or random.random() > PORCENTAJE_OBSTACULOS:
                    nueva_fila.append(CELDA_LIBRE)
                else:
                    nueva_fila.append(CELDA_OBSTACULO)
            self.celdas.append(nueva_fila)

        self.agregar_elementos()

    def agregar_elementos(self):
        """
        Coloca monedas y poderes en posiciones libres.
        """
        cantidades = {
            TIPO_MONEDA_NORMAL: max(3, self.tamano // 2),
            TIPO_MONEDA_ESPECIAL: max(1, self.tamano // 5),
            TIPO_BOMBA: max(1, self.tamano // 6),
            TIPO_PASO_FANTASMA: 1,
        }

        for tipo, cantidad in cantidades.items():
            for _ in range(cantidad):
                posicion = self.obtener_posicion_libre()
                if posicion is not None:
                    self.elementos[posicion] = tipo

    def obtener_posicion_libre(self):
        """
        Busca una celda libre que no tenga otro elemento.
        """
        posiciones = []
        for fila in range(self.tamano):
            for columna in range(self.tamano):
                posicion = (fila, columna)
                if self.celdas[fila][columna] == CELDA_LIBRE and posicion not in self.elementos:
                    posiciones.append(posicion)

        if not posiciones:
            return None

        return random.choice(posiciones)

    def es_posicion_valida(self, fila, columna):
        """
        Indica si el jugador puede caminar a una posicion.
        """
        if fila < 0 or fila >= self.tamano:
            return False
        if columna < 0 or columna >= self.tamano:
            return False

        return self.celdas[fila][columna] == CELDA_LIBRE

    def recoger_elemento(self, jugador):
        """
        Aplica el efecto del elemento donde esta parado el jugador.
        """
        posicion = (jugador.fila, jugador.columna)
        tipo = self.elementos.pop(posicion, None)

        if tipo == TIPO_MONEDA_NORMAL:
            jugador.puntaje += VALOR_MONEDA_NORMAL
        elif tipo == TIPO_MONEDA_ESPECIAL:
            jugador.puntaje += VALOR_MONEDA_ESPECIAL

        return tipo

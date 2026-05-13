class Jugador:
    """
    Guarda la posicion y el puntaje del jugador dentro del mapa.
    """
    
    def __init__(self, fila, columna):
        self.fila = fila
        self.columna = columna
        self.puntaje = 0
        self.direccion = (-1, 0)

    def mover(self, direccion_fila, direccion_columna, mapa):
        """
        Mueve el jugador si la nueva posicion esta dentro del mapa y no es muro.
        """
        nueva_fila = self.fila + direccion_fila
        nueva_columna = self.columna + direccion_columna
        self.direccion = (direccion_fila, direccion_columna)

        if mapa.es_posicion_valida(nueva_fila, nueva_columna):
            self.fila = nueva_fila
            self.columna = nueva_columna
            return True

        return False

from .paredes import colocar_parede
from .movimentos import andar
from .utilidade import calcular_utilidade
from .print import imprimir_tabuleiro


class JogoQuoridor:
    def __init__(self):
        self.jogadores = {"J1": (0, 4), "J2": (8, 4)}
        self.paredes_horizontais = [[False] * 8 for _ in range(8)]
        self.paredes_verticais = [[False] * 8 for _ in range(8)]
        self.paredes_restantes = {"J1": 10, "J2": 10}

    def colocar_parede(self, notacao, turno):
        return colocar_parede(self, notacao, turno)

    def imprimir_tabuleiro(self):
        imprimir_tabuleiro(self)

    def andar(self, direcao, turno):
        return andar(self, direcao, turno)

    def verificar_vitoria(self):
        if self.jogadores["J1"][0] == 8:
            print("Player 1 venceu!")
            return True
        if self.jogadores["J2"][0] == 0:
            print("Player 2 venceu!")
            return True
        return False

    def serializar_estado(self):
        return (
            tuple(self.jogadores["J1"]),
            tuple(self.jogadores["J2"]),
            tuple(tuple(linha) for linha in self.paredes_horizontais),
            tuple(tuple(linha) for linha in self.paredes_verticais),
            self.paredes_restantes["J1"],
            self.paredes_restantes["J2"],
        )

    def calcular_utilidade(self, estado, jogador):
        return calcular_utilidade(estado, jogador)

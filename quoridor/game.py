from .paredes import colocar_parede
from .movimentos import andar
from .utilidade import calcular_utilidade
from .print import imprimir_tabuleiro


from .square import Square
from .constantes import LINHAS, COLUNAS

class JogoQuoridor:
    def __init__(self):
        self.jogadores = {"J1": (0, 4), "J2": (8, 4)}
        # Apenas usa a matriz do tabuleiro
        self.tabuleiro = [[Square() for _ in range(COLUNAS)] for _ in range(LINHAS)]
        # Define as posições iniciais dos jogadores no tabuleiro
        j1_linha, j1_coluna = self.jogadores["J1"]
        j2_linha, j2_coluna = self.jogadores["J2"]
        self.tabuleiro[j1_linha][j1_coluna].has_player = True
        self.tabuleiro[j2_linha][j2_coluna].has_player = True

    def colocar_parede(self, notacao, turno):
        return colocar_parede(self, notacao, turno)

    def imprimir_tabuleiro(self):
        imprimir_tabuleiro(self)

    def andar(self, direcao, turno):
        return andar(self, direcao, turno)

    def verificar_vitoria(self):
        if self.jogadores["J1"][0] == 8:
            print("Jogador 1 venceu!")
            return True
        if self.jogadores["J2"][0] == 0:
            print("Jogador 2 venceu!")
            return True
        return False

    def serializar_estado(self):
        return (
            tuple(self.jogadores["J1"]),
            tuple(self.jogadores["J2"]),
        )

    def calcular_utilidade(self, estado, jogador):
        return calcular_utilidade(estado, jogador)

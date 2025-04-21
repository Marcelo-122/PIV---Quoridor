from .paredes import colocar_parede
from .movimentos import andar
from .utilidade import calcular_utilidade
from .print import imprimir_tabuleiro


from .square import Square
from .constantes import LINHAS, COLUNAS

class JogoQuoridor:
    def __init__(self):
        self.jogadores = {"J1": (0, 4), "J2": (8, 4)}
        # Cada jogador começa com 10 paredes
        self.paredes_restantes = {"J1": 10, "J2": 10}
        # Apenas usa a matriz do tabuleiro
        self.tabuleiro = [[Square() for _ in range(COLUNAS)] for _ in range(LINHAS)]
        # Define as posições iniciais dos jogadores no tabuleiro
        j1_linha, j1_coluna = self.jogadores["J1"]
        j2_linha, j2_coluna = self.jogadores["J2"]
        self.tabuleiro[j1_linha][j1_coluna].tem_jogador = True
        self.tabuleiro[j2_linha][j2_coluna].tem_jogador = True

    def colocar_parede(self, notacao, turno):
        jogador = "J1" if turno == 0 else "J2"
        if self.paredes_restantes[jogador] <= 0:
            print(f"{jogador} não tem mais paredes!")
            return False
        sucesso = colocar_parede(self, notacao, turno)
        if sucesso:
            self.paredes_restantes[jogador] -= 1
        return sucesso

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
            self.paredes_restantes["J1"],
            self.paredes_restantes["J2"]
        )

    def calcular_utilidade(self, estado, jogador, **kwargs):
        return calcular_utilidade(estado, jogador, self.tabuleiro, **kwargs)

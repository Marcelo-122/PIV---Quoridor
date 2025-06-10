from .paredes import colocar_parede
from .movimentos import andar
from .utilidade import calcular_utilidade, shortest_path_length
from ..utils.print import imprimir_tabuleiro

import numpy as np
from .square import Square
from .constantes import LINHAS, COLUNAS
from .movimento_util import gerar_movimentos_possiveis

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
        # Tentativamente coloca a parede (isso modifica self.tabuleiro diretamente)
        # A função importada 'colocar_parede' já faz verificações de sobreposição e cruzamento.
        sucesso_colocacao_basica = colocar_parede(self, notacao, turno)

        if sucesso_colocacao_basica:
            # Verificar se algum jogador ficou sem caminho
            path_j1_exists = shortest_path_length("J1", self.jogadores["J1"], self.tabuleiro) < 99 # 99 indica sem caminho
            path_j2_exists = shortest_path_length("J2", self.jogadores["J2"], self.tabuleiro) < 99

            if not path_j1_exists or not path_j2_exists:
                print("Colocação de parede inválida: bloquearia o caminho de um jogador.")
                # Reverter a colocação da parede
                letra_coluna, numero_linha, direcao_parede = notacao
                col_idx = ord(letra_coluna) - ord('a')
                linha_idx = int(numero_linha) - 1

                if direcao_parede == 'h':
                    self.tabuleiro[linha_idx - 1][col_idx].pode_mover_para_baixo = True
                    self.tabuleiro[linha_idx - 1][col_idx + 1].pode_mover_para_baixo = True
                    self.tabuleiro[linha_idx][col_idx].pode_mover_para_cima = True
                    self.tabuleiro[linha_idx][col_idx + 1].pode_mover_para_cima = True
                elif direcao_parede == 'v':
                    self.tabuleiro[linha_idx][col_idx - 1].pode_mover_para_direita = True
                    self.tabuleiro[linha_idx + 1][col_idx - 1].pode_mover_para_direita = True
                    self.tabuleiro[linha_idx][col_idx].pode_mover_para_esquerda = True
                    self.tabuleiro[linha_idx + 1][col_idx].pode_mover_para_esquerda = True
                return False # Falha na colocação da parede
            else:
                # Se os caminhos existem, a colocação é válida
                self.paredes_restantes[jogador] -= 1
                return True # Sucesso na colocação da parede
        else:
            # A colocação básica já falhou (sobreposição, cruzamento, etc.)
            return False

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
        # Pass tabuleiro only if it's not already in kwargs
        if 'tabuleiro' not in kwargs:
            return calcular_utilidade(estado, jogador, tabuleiro=self.tabuleiro, **kwargs)
        return calcular_utilidade(estado, jogador, **kwargs)

    def get_dqn_state_vector(self, turno):
        """
        Gera um vetor numérico de tamanho fixo representando o estado atual do jogo para uma DQN.
        Características do vetor de estado (135 no total):
        - Posição J1 (linha, col): 2
        - Posição J2 (linha, col): 2
        - Paredes restantes J1: 1
        - Paredes restantes J2: 1
        - Paredes horizontais (grade 8x8): 64 (1 se existe parede, 0 caso contrário)
        - Paredes verticais (grade 8x8): 64 (1 se existe parede, 0 caso contrário)
        - Jogador atual (0 para J1, 1 para J2): 1
        """
        pos_j1 = self.jogadores["J1"]
        pos_j2 = self.jogadores["J2"]
        paredes_restantes_j1 = self.paredes_restantes["J1"]
        paredes_restantes_j2 = self.paredes_restantes["J2"]

        paredes_h = np.zeros((8, 8), dtype=np.float32)
        for linha in range(8):
            for coluna in range(8):
                if not self.tabuleiro[linha][coluna].pode_mover_para_baixo:
                    paredes_h[linha, coluna] = 1.0

        paredes_v = np.zeros((8, 8), dtype=np.float32)
        for linha in range(8):
            for coluna in range(8):
                if not self.tabuleiro[linha][coluna].pode_mover_para_direita:
                    paredes_v[linha, coluna] = 1.0

        indicador_jogador_atual = float(turno)  # 0.0 para J1, 1.0 para J2

        vetor_estado = np.concatenate(
            [
                np.array([pos_j1[0], pos_j1[1]], dtype=np.float32),
                np.array([pos_j2[0], pos_j2[1]], dtype=np.float32),
                np.array([paredes_restantes_j1], dtype=np.float32),
                np.array([paredes_restantes_j2], dtype=np.float32),
                paredes_h.flatten(),
                paredes_v.flatten(),
                np.array([indicador_jogador_atual], dtype=np.float32),
            ]
        )

        return vetor_estado


    def calcular_recompensa_dqn(self, jogador_dqn):
        """
        Calcula a recompensa para o agente DQN com base no estado atual do jogo.
        Esta função deve ser chamada APÓS o estado do jogo (incluindo self.jogo_terminado
        e o vencedor) ter sido atualizado devido à última ação.

        Args:
            jogador_dqn (str): O identificador do jogador DQN ("J1" ou "J2").

        Returns:
            float: A recompensa calculada.
        """
        # Presume-se que self.jogo_terminado e self.verificar_vitoria()
        # refletem o estado APÓS a última ação.
        vencedor = self.verificar_vitoria()  # Retorna 'J1', 'J2', ou None

        if self.jogo_terminado:
            if vencedor == jogador_dqn:
                return 100.0  # Recompensa grande por vencer
            elif vencedor is not None:  # O outro jogador venceu
                return -100.0  # Penalidade grande por perder
            else:
                # Jogo terminou, mas não há vencedor (ex: empate, se implementado).
                # Para Quoridor, um jogo terminado geralmente tem um vencedor.
                # Se for um empate genuíno, 0.0 pode ser apropriado.
                return 0.0
        else:
            # Jogo não terminou: penalidade pequena por cada movimento para incentivar jogos mais curtos
            # e evitar estagnação.
            return -1.0

    def gerar_movimentos_possiveis(self, turno):
        return gerar_movimentos_possiveis(self, turno)
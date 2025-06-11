from .paredes import colocar_parede
from .movimentos import andar
from .utilidade import calcular_utilidade, shortest_path_length

import numpy as np
from .square import Square
from .constantes import LINHAS, COLUNAS
from .movimento_util import gerar_movimentos_possiveis

# No início da classe JogoQuoridor em src/core/game.py


class JogoQuoridor:
    def __init__(self):
        # Guarda as configurações iniciais para poder resetar
        self.estado_inicial_jogadores = {
            "J1": (0, 4),
            "J2": (8, 4),
        }  # J1 começa em (linha 0, col 4), J2 em (linha 8, col 4)
        self.estado_inicial_paredes_restantes = {"J1": 10, "J2": 10}
        self.resetar_jogo()  # Chama resetar_jogo para configurar o estado inicial

    def resetar_jogo(self):
        """Reseta o jogo para o estado inicial para um novo episódio."""
        self.jogadores = self.estado_inicial_jogadores.copy()
        self.paredes_restantes = self.estado_inicial_paredes_restantes.copy()
        self.tabuleiro = [[Square() for _ in range(COLUNAS)] for _ in range(LINHAS)]

        j1_linha, j1_coluna = self.jogadores["J1"]
        j2_linha, j2_coluna = self.jogadores["J2"]
        self.tabuleiro[j1_linha][j1_coluna].tem_jogador = True
        self.tabuleiro[j2_linha][j2_coluna].tem_jogador = True

        self.jogo_terminado = False
        self.vencedor = None  # Pode ser 'J1', 'J2', ou None para indicar que o jogo não acabou ou é empate
        # O turno inicial pode ser definido aqui ou gerenciado pelo loop de treinamento
        # self.turno_atual_idx = 0 # Exemplo: J1 (índice 0) começa

    def colocar_parede(self, notacao, turno):
        jogador = "J1" if turno == 0 else "J2"
        if self.paredes_restantes[jogador] <= 0:
            # print(f"{jogador} não tem mais paredes!")
            return False
        # Tentativamente coloca a parede (isso modifica self.tabuleiro diretamente)
        # A função importada 'colocar_parede' já faz verificações de sobreposição e cruzamento.
        sucesso_colocacao_basica = colocar_parede(self, notacao, turno)

        if sucesso_colocacao_basica:
            # Verificar se algum jogador ficou sem caminho
            path_j1_exists = shortest_path_length("J1", self.jogadores["J1"], self.tabuleiro) < 99 # 99 indica sem caminho
            path_j2_exists = shortest_path_length("J2", self.jogadores["J2"], self.tabuleiro) < 99

            if not path_j1_exists or not path_j2_exists:
                #print("Colocação de parede inválida: bloquearia o caminho de um jogador.")
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

    def andar(self, direcao, turno):
        return andar(self, direcao, turno)

    # Dentro da classe JogoQuoridor

    def verificar_vitoria(self):
        """
        Verifica se algum jogador alcançou a linha de chegada.
        Atualiza self.jogo_terminado e self.vencedor.
        Retorna o vencedor ('J1', 'J2') ou None se o jogo não terminou ou não há vencedor ainda.
        """
        if self.vencedor:  # Se um vencedor já foi determinado, não reavalia
            return self.vencedor

        # J1 vence se alcançar a linha LINHAS - 1 (linha 8 para um tabuleiro 9x9)
        if self.jogadores["J1"][0] == LINHAS - 1:
            self.jogo_terminado = True
            self.vencedor = "J1"
            return "J1"

        # J2 vence se alcançar a linha 0
        if self.jogadores["J2"][0] == 0:
            self.jogo_terminado = True
            self.vencedor = "J2"
            return "J2"

        return None  # Nenhum vencedor ainda

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


    def calcular_recompensa_dqn(
        self, movimento, jogador_dqn, meu_caminho_antes, caminho_oponente_antes
    ):
        """
        Calcula a recompensa para o agente DQN com base na MUDANÇA no estado do jogo.

        Args:
            jogador_dqn (str): O jogador DQN ("J1" ou "J2").
            meu_caminho_antes (int): Comprimento do caminho do DQN antes do movimento.
            caminho_oponente_antes (int): Comprimento do caminho do oponente antes do movimento.

        Returns:
            float: A recompensa calculada.
        """
        vencedor = self.verificar_vitoria()
        if self.jogo_terminado:
            if vencedor == jogador_dqn:
                return 100.0  # Recompensa máxima por vencer
            elif vencedor is not None:
                return -100.0  # Penalidade máxima por perder
            else:
                return 0.0

        # Calcula os comprimentos dos caminhos DEPOIS do movimento
        oponente_dqn = "J2" if jogador_dqn == "J1" else "J1"
        pos_minha = self.jogadores[jogador_dqn]
        pos_oponente = self.jogadores[oponente_dqn]

        meu_caminho_depois = shortest_path_length(jogador_dqn, pos_minha, self.tabuleiro)
        caminho_oponente_depois = shortest_path_length(
            oponente_dqn, pos_oponente, self.tabuleiro
        )

        # Trata caminhos bloqueados (None)
        if meu_caminho_depois is None:
            meu_caminho_depois = 99
        if caminho_oponente_depois is None:
            caminho_oponente_depois = 99
        if meu_caminho_antes is None:
            meu_caminho_antes = 99
        if caminho_oponente_antes is None:
            caminho_oponente_antes = 99

        # Calcula a MUDANÇA (delta) nos caminhos
        delta_meu_caminho = meu_caminho_depois - meu_caminho_antes
        delta_caminho_oponente = caminho_oponente_depois - caminho_oponente_antes

        # Recompensa baseada nos deltas: incentiva diminuir nosso caminho e aumentar o do oponente
        recompensa = 0

        # Incentivar o bloqueio do oponente (tão importante quanto avançar)
        recompensa += delta_caminho_oponente * 1.8

        # Incentivar o avanço do próprio peão (maior prioridade)
        recompensa -= delta_meu_caminho * 2.0

        # Penalidade por usar uma parede, diferenciando entre úteis e inúteis.
        tipo_movimento, _ = movimento
        if tipo_movimento == 'wall':
            # Se a parede for inútil (não aumenta o caminho do oponente), a penalidade é massiva.
            if delta_caminho_oponente <= 0:
                recompensa -= 3  # Penalidade por desperdiçar um recurso E um turno.
            else:
                # Se a parede for útil, aplicamos apenas o custo de oportunidade.
                recompensa -= 0.5

        # Adiciona uma pequena penalidade constante a cada movimento para incentivar a eficiência
        recompensa -= 0.01

        return recompensa

    def gerar_movimentos_possiveis(self, turno):
        return gerar_movimentos_possiveis(self, turno)

    # Dentro da classe JogoQuoridor

    def aplicar_movimento(self, movimento_tupla, turno_idx):
        """
        Aplica um movimento ao jogo e atualiza o estado.

        Args:
            movimento_tupla (tuple): O movimento a ser aplicado, ex: ('move', 's') ou ('wall', 'e5h').
            turno_idx (int): 0 para J1, 1 para J2.

        Returns:
            bool: True se o movimento foi bem-sucedido, False caso contrário.
                  O estado do jogo (self.jogo_terminado, self.vencedor) é atualizado internamente.
        """
        if self.jogo_terminado:
            # print("Tentativa de aplicar movimento em jogo já terminado.")
            return False  # Não permite movimentos se o jogo já terminou

        tipo_movimento, valor_movimento = movimento_tupla
        sucesso_movimento = False

        if tipo_movimento == "move":
            sucesso_movimento = self.andar(valor_movimento, turno_idx)
        elif tipo_movimento == "wall":
            sucesso_movimento = self.colocar_parede(valor_movimento, turno_idx)

        if sucesso_movimento:
            # Após um movimento bem-sucedido, verifica se houve um vencedor
            self.verificar_vitoria()

        return sucesso_movimento
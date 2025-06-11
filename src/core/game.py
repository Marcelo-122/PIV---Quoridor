import numpy as np

from .constantes import COLUNAS, LINHAS
from .movimento_util import gerar_movimentos_possiveis
from .movimentos import andar
from .paredes import colocar_parede
from .square import Square
from .utilidade import calcular_utilidade, shortest_path_length

# Constantes para Cálculo de Recompensa DQN Intermediária
# Progresso Pessoal
FATOR_PROGRESSO_PESSOAL = 30.0  # Multiplica a redução no caminho próprio
FATOR_REGRESSO_PESSOAL = 25.0   # Multiplica o aumento no caminho próprio (penalidade)
RECOMPENSA_DESBLOQUEIO_PROPRIO = 10.0 # Recompensa por encontrar um caminho quando antes estava bloqueado
PENALIDADE_AUTOBLOQUEIO = -35.0      # Penalidade por se bloquear

# Impacto no Oponente (principalmente por paredes)
FATOR_PREJUIZO_OPONENTE = 15.0  # Multiplica o aumento no caminho do oponente
FATOR_AJUDA_OPONENTE = 15.0     # Multiplica a redução no caminho do oponente (penalidade)
RECOMPENSA_BLOQUEIO_OPONENTE = 25.0 # Recompensa por bloquear o oponente
PENALIDADE_DESBLOQUEIO_OPONENTE = -35.0 # Penalidade se sua parede desbloqueou o oponente

# Custos/Incentivos Base de Ação
CUSTO_COLOCAR_PAREDE = -10.0  # Custo fixo por colocar uma parede
RECOMPENSA_MOVER_PEAO = 5.0  # Incentivo fixo por mover um peão

# Penalidade por usar paredes cedo demais
PENALIDADE_PAREDE_CEDO = -5.0  # Penalidade adicional por colocar parede tendo muitas restantes
# Se, APÓS colocar uma parede, o jogador ainda tiver o numero do limite, aplica-se a penalidade.
# Ex: Se LIMITE = 8, e o jogador coloca uma parede e fica com 8 (tinha 9), ele é penalizado.
LIMITE_PAREDES_PARA_PENALIDADE_CEDO = 8

LIMITE_RECOMPENSA_INTERMEDIARIA_MIN = -30.0 # Para evitar que recompensas intermediárias sejam extremas
LIMITE_RECOMPENSA_INTERMEDIARIA_MAX = 30.0

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
            path_j1_exists = (
                shortest_path_length("J1", self.jogadores["J1"], self.tabuleiro) < 99
            )  # 99 indica sem caminho
            path_j2_exists = (
                shortest_path_length("J2", self.jogadores["J2"], self.tabuleiro) < 99
            )

            if not path_j1_exists or not path_j2_exists:
                # print("Colocação de parede inválida: bloquearia o caminho de um jogador.")
                # Reverter a colocação da parede
                letra_coluna, numero_linha, direcao_parede = notacao
                col_idx = ord(letra_coluna) - ord("a")
                linha_idx = int(numero_linha) - 1

                if direcao_parede == "h":
                    self.tabuleiro[linha_idx - 1][col_idx].pode_mover_para_baixo = True
                    self.tabuleiro[linha_idx - 1][
                        col_idx + 1
                    ].pode_mover_para_baixo = True
                    self.tabuleiro[linha_idx][col_idx].pode_mover_para_cima = True
                    self.tabuleiro[linha_idx][col_idx + 1].pode_mover_para_cima = True
                elif direcao_parede == "v":
                    self.tabuleiro[linha_idx][
                        col_idx - 1
                    ].pode_mover_para_direita = True
                    self.tabuleiro[linha_idx + 1][
                        col_idx - 1
                    ].pode_mover_para_direita = True
                    self.tabuleiro[linha_idx][col_idx].pode_mover_para_esquerda = True
                    self.tabuleiro[linha_idx + 1][
                        col_idx
                    ].pode_mover_para_esquerda = True
                return False  # Falha na colocação da parede
            else:
                # Se os caminhos existem, a colocação é válida
                self.paredes_restantes[jogador] -= 1
                return True  # Sucesso na colocação da parede
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
            self.paredes_restantes["J2"],
        )

    def calcular_utilidade(self, estado, jogador, **kwargs):
        # Pass tabuleiro only if it's not already in kwargs
        if "tabuleiro" not in kwargs:
            return calcular_utilidade(
                estado, jogador, tabuleiro=self.tabuleiro, **kwargs
            )
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
        Calcula a recompensa intermediária para o agente DQN com base na mudança no estado do jogo.
        As recompensas de vitória/derrota/empate são tratadas separadamente no loop de treinamento.

        Args:
            movimento (tuple or str): O movimento realizado. Ex: ('n', 'e', 's', 'w') ou ('a1h', 'b2v', etc.)
            jogador_dqn (str): O jogador DQN ("J1" ou "J2").
            meu_caminho_antes (int): Comprimento do caminho do DQN antes do movimento (99+ se bloqueado).
            caminho_oponente_antes (int): Comprimento do caminho do oponente antes do movimento (99+ se bloqueado).

        Returns:
            float: A recompensa intermediária calculada.
        """
        recompensa_total = 0.0

        oponente_dqn = "J2" if jogador_dqn == "J1" else "J1"
        pos_minha_depois = self.jogadores[jogador_dqn]
        pos_oponente_depois = self.jogadores[oponente_dqn]

        meu_caminho_depois = shortest_path_length(jogador_dqn, pos_minha_depois, self.tabuleiro)
        caminho_oponente_depois = shortest_path_length(oponente_dqn, pos_oponente_depois, self.tabuleiro)

        # --- 1. Recompensa/Penalidade por Progresso/Regresso Pessoal ---
        # Considera caminhos válidos (menor que 99)
        if meu_caminho_depois < 99:  # Se o agente ainda tem um caminho
            if meu_caminho_antes < 99:  # E tinha um caminho antes
                diff_meu_caminho = meu_caminho_antes - meu_caminho_depois
                if diff_meu_caminho > 0: # Progrediu
                    recompensa_total += diff_meu_caminho * FATOR_PROGRESSO_PESSOAL
                else: # Regrediu ou ficou no mesmo lugar (diff_meu_caminho <= 0)
                    recompensa_total += diff_meu_caminho * FATOR_REGRESSO_PESSOAL # diff é negativo ou zero, FATOR_REGRESSO_PESSOAL é positivo
            else:  # Não tinha caminho antes (>=99), mas agora tem (<99) (desbloqueou-se)
                recompensa_total += RECOMPENSA_DESBLOQUEIO_PROPRIO
        else:  # Agente não tem mais caminho (meu_caminho_depois >= 99)
            if meu_caminho_antes < 99:  # Tinha um caminho antes, mas se bloqueou
                recompensa_total += PENALIDADE_AUTOBLOQUEIO

        # --- 2. Recompensa/Penalidade por Impacto no Oponente e Custo da Ação ---
        # Verifica se o movimento foi uma parede: tupla ('a','1','h')
        foi_parede = isinstance(movimento, tuple) and len(movimento) == 3 and \
                     isinstance(movimento[0], str) and isinstance(movimento[1], str) and \
                     isinstance(movimento[2], str)

        if foi_parede:
            recompensa_total += CUSTO_COLOCAR_PAREDE

            # --- Penalidade Adicional por Usar Parede Cedo ---
            # self.paredes_restantes[jogador_dqn] aqui é o valor APÓS a parede ser colocada.
            if self.paredes_restantes[jogador_dqn] >= LIMITE_PAREDES_PARA_PENALIDADE_CEDO:
                recompensa_total += PENALIDADE_PAREDE_CEDO
                # Opcional: print para debug
                # print(f"    [{jogador_dqn} Penalidade Parede Cedo Aplicada] Paredes restantes: {self.paredes_restantes[jogador_dqn]} >= {LIMITE_PAREDES_PARA_PENALIDADE_CEDO}")
            # --- Fim da Penalidade Adicional ---

            if caminho_oponente_depois < 99: # Se oponente ainda tem caminho
                if caminho_oponente_antes < 99: # E oponente tinha caminho antes
                    diff_caminho_oponente = caminho_oponente_depois - caminho_oponente_antes # Positivo se caminho do oponente aumentou
                    if diff_caminho_oponente > 0: # Prejudicou o oponente (caminho dele aumentou)
                        recompensa_total += diff_caminho_oponente * FATOR_PREJUIZO_OPONENTE
                    else: # Ajudou o oponente ou não afetou (caminho dele diminuiu ou manteve)
                        recompensa_total += diff_caminho_oponente * FATOR_AJUDA_OPONENTE # diff é negativo ou zero
                else: # Oponente não tinha caminho (>=99), mas sua parede o desbloqueou (<99) (muito ruim)
                    recompensa_total += PENALIDADE_DESBLOQUEIO_OPONENTE
            else: # Oponente não tem mais caminho (caminho_oponente_depois >= 99)
                if caminho_oponente_antes < 99: # Oponente tinha caminho, mas foi bloqueado pela parede
                    recompensa_total += RECOMPENSA_BLOQUEIO_OPONENTE
        else:  # Foi movimento de peão
            recompensa_total += RECOMPENSA_MOVER_PEAO

        # Limitar a recompensa intermediária para não ofuscar as recompensas terminais
        recompensa_total = np.clip(recompensa_total, LIMITE_RECOMPENSA_INTERMEDIARIA_MIN, LIMITE_RECOMPENSA_INTERMEDIARIA_MAX)

        return recompensa_total

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

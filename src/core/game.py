# import numpy removido - não mais necessário

from .movimento_util import gerar_movimentos_possiveis
from .movimentos import andar
from .paredes import colocar_parede
from .square import Square
from .utilidade import calcular_utilidade, shortest_path_length

# Constantes e configurações DQN removidas

# Custos/Incentivos Base de Ação
CUSTO_COLOCAR_PAREDE = -10.0  # Custo fixo por colocar uma parede
RECOMPENSA_MOVER_PEAO = 5.0  # Incentivo fixo por mover um peão

# Penalidade por usar paredes cedo demais
PENALIDADE_PAREDE_CEDO = (
    -5.0
)  # Penalidade adicional por colocar parede tendo muitas restantes
# Se, APÓS colocar uma parede, o jogador ainda tiver o numero do limite, aplica-se a penalidade.
# Ex: Se LIMITE = 8, e o jogador coloca uma parede e fica com 8 (tinha 9), ele é penalizado.
LIMITE_PAREDES_PARA_PENALIDADE_CEDO = 8

LIMITE_RECOMPENSA_INTERMEDIARIA_MIN = (
    -30.0
)  # Para evitar que recompensas intermediárias sejam extremas
LIMITE_RECOMPENSA_INTERMEDIARIA_MAX = 30.0


class JogoQuoridor:
    def __init__(self, linhas=9, colunas=9, total_paredes_jogador=10):
        """Inicializa o jogo Quoridor com tamanho de tabuleiro e número de paredes configuráveis.

        Args:
            linhas (int, opcional): Número de linhas no tabuleiro. Padrão é 9.
            colunas (int, opcional): Número de colunas no tabuleiro. Padrão é 9.
            total_paredes_jogador (int, opcional): Número total de paredes por jogador. Padrão é 10.
        """
        # Guarda as configurações iniciais para poder resetar
        self.linhas = linhas
        self.colunas = colunas

        # Define as posições iniciais no centro do tabuleiro
        coluna_centro = colunas // 2
        self.estado_inicial_jogadores = {
            "J1": (0, coluna_centro),  # J1 começa na primeira linha, coluna do meio
            "J2": (
                linhas - 1,
                coluna_centro,
            ),  # J2 começa na última linha, coluna do meio
        }
        self.estado_inicial_paredes_restantes = {
            "J1": total_paredes_jogador,
            "J2": total_paredes_jogador,
        }
        self.resetar_jogo()  # Chama resetar_jogo para configurar o estado inicial

    def resetar_jogo(self):
        """Reseta o jogo para o estado inicial para um novo episódio."""
        self.jogadores = self.estado_inicial_jogadores.copy()
        self.paredes_restantes = self.estado_inicial_paredes_restantes.copy()
        self.tabuleiro = [
            [Square() for _ in range(self.colunas)] for _ in range(self.linhas)
        ]

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

    def verificar_vitoria_jogador(self, jogador):
        """Verifica se o jogador alcançou o lado oposto do tabuleiro"""
        linha, coluna = self.jogadores[jogador]
        # J1 vence ao alcançar a última linha (linha = self.linhas - 1)
        # J2 vence ao alcançar a primeira linha (linha = 0)
        if jogador == "J1":
            venceu = linha == self.linhas - 1
            if venceu:
                print(f"[VITÓRIA] J1 alcançou linha {linha} (última linha)")
            return venceu
        elif jogador == "J2":
            venceu = linha == 0
            if venceu:
                print(f"[VITÓRIA] J2 alcançou linha {linha} (primeira linha)")
            return venceu
        return False

    def verificar_vitoria(self):
        """Verifica se algum jogador alcançou a linha de chegada."""
        vencedor = None
        if self.verificar_vitoria_jogador("J1"):
            vencedor = "J1"
        elif self.verificar_vitoria_jogador("J2"):
            vencedor = "J2"

        if vencedor:
            print(f"[VITÓRIA] Jogo terminado! Vencedor: {vencedor}")
            self.jogo_terminado = True
            self.vencedor = vencedor
        return vencedor

    def serializar_estado(self):
        return (
            tuple(self.jogadores["J1"]),
            tuple(self.jogadores["J2"]),
            self.paredes_restantes["J1"],
            self.paredes_restantes["J2"],
        )

    def get_estado_tupla(self, turno_idx):
        """
        Cria uma representação hashable do estado atual do jogo para uso na Q-tabela.

        Args:
            turno_idx (int): 0 para J1, 1 para J2

        Returns:
            tuple: Uma tupla contendo:
                - pos_j1 (tuple): Posição do jogador J1 (linha, coluna)
                - pos_j2 (tuple): Posição do jogador J2 (linha, coluna)
                - paredes_h (frozenset): Conjunto de coordenadas de paredes horizontais (linha, coluna)
                - paredes_v (frozenset): Conjunto de coordenadas de paredes verticais (linha, coluna)
                - paredes_j1 (int): Número de paredes restantes para J1
                - paredes_j2 (int): Número de paredes restantes para J2
                - jogador_atual (int): 0 para J1, 1 para J2
        """
        pos_j1 = tuple(self.jogadores["J1"])
        pos_j2 = tuple(self.jogadores["J2"])
        paredes_restantes_j1 = self.paredes_restantes["J1"]
        paredes_restantes_j2 = self.paredes_restantes["J2"]

        # Coletar posições de paredes horizontais e verticais
        paredes_horizontais = set()
        paredes_verticais = set()

        for linha in range(
            self.linhas - 1
        ):  # -1 porque não pode colocar parede na última linha
            for coluna in range(
                self.colunas - 1
            ):  # -1 porque não pode colocar parede na última coluna
                # Verificar parede horizontal (impede movimento para baixo)
                if not self.tabuleiro[linha][coluna].pode_mover_para_baixo:
                    paredes_horizontais.add((linha, coluna))

                # Verificar parede vertical (impede movimento para direita)
                if not self.tabuleiro[linha][coluna].pode_mover_para_direita:
                    paredes_verticais.add((linha, coluna))

        # Converter para frozenset para torná-los hashable
        paredes_h_frozen = frozenset(paredes_horizontais)
        paredes_v_frozen = frozenset(paredes_verticais)

        # Criar a tupla de estado
        estado_tupla = (
            pos_j1,
            pos_j2,
            paredes_h_frozen,
            paredes_v_frozen,
            paredes_restantes_j1,
            paredes_restantes_j2,
            turno_idx,
        )

        return estado_tupla

    def calcular_utilidade(self, estado, jogador, **kwargs):
        # Pass tabuleiro only if it's not already in kwargs
        if "tabuleiro" not in kwargs:
            return calcular_utilidade(
                estado, jogador, tabuleiro=self.tabuleiro, **kwargs
            )
        return calcular_utilidade(estado, jogador, **kwargs)

    def gerar_movimentos_possiveis(self, turno):
        return gerar_movimentos_possiveis(self, turno)

    # Dentro da classe JogoQuoridor

    def aplicar_movimento(self, movimento_tupla, turno_idx):
        """
        Aplica um movimento ao jogo e atualiza o estado.

        Args:
            movimento_tupla (tuple): O movimento a ser aplicado, podendo ser:
                - ('mover', (nova_linha, nova_coluna)) para mover peão
                - ('parede', (linha, coluna, orientacao)) para colocar parede
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

        if tipo_movimento == "mover":
            direcao = None
            # Se o valor for uma string (como 'w', 's'), é um movimento da GUI
            if isinstance(valor_movimento, str):
                direcao = valor_movimento
            # Se for uma tupla, é um movimento do agente (coordenadas)
            elif isinstance(valor_movimento, tuple):
                nova_linha, nova_coluna = valor_movimento
                jogador = "J1" if turno_idx == 0 else "J2"
                linha_atual, coluna_atual = self.jogadores[jogador]

                # Determinar direção baseado na diferença de posições
                if nova_linha < linha_atual:
                    direcao = "w"
                elif nova_linha > linha_atual:
                    direcao = "s"
                elif nova_coluna < coluna_atual:
                    direcao = "a"
                elif nova_coluna > coluna_atual:
                    direcao = "d"

            if direcao:
                sucesso_movimento = self.andar(direcao, turno_idx)
            else:
                sucesso_movimento = False
        elif tipo_movimento == "parede":
            # O valor do movimento pode ser uma tupla (formato antigo) ou uma string (formato da IA/GUI)
            if isinstance(valor_movimento, str):
                notacao_parede = valor_movimento
            elif isinstance(valor_movimento, tuple):
                # Converte a tupla para a notação de string
                linha, coluna, orientacao = valor_movimento
                coluna_letra = chr(ord('a') + coluna)
                linha_numero = str(linha + 1)
                notacao_parede = coluna_letra + linha_numero + orientacao
            else:
                notacao_parede = None

            if notacao_parede:
                sucesso_movimento = self.colocar_parede(notacao_parede, turno_idx)
            else:
                sucesso_movimento = False

        if sucesso_movimento:
            # Após um movimento bem-sucedido, verifica se houve um vencedor
            self.verificar_vitoria()

        return sucesso_movimento

    def get_acoes_validas(self, turno_idx):
        movimentos = gerar_movimentos_possiveis(self, turno_idx, ordenar=False)

        # Converter movimentos para o formato de ação
        acoes = []
        for tipo, valor in movimentos:
            if tipo == "move":
                # Obter coordenadas do movimento
                jogador = "J1" if turno_idx == 0 else "J2"
                linha, coluna = self.jogadores[jogador]

                # Mapear direção para coordenadas
                direcoes = {"w": (-1, 0), "s": (1, 0), "a": (0, -1), "d": (0, 1)}
                d_linha, d_coluna = direcoes[valor]
                nova_pos = (linha + d_linha, coluna + d_coluna)

                acoes.append(("mover", nova_pos))
            elif tipo == "parede":
                # Converter notação de parede para coordenadas
                letra = valor[0]
                numero = int(valor[1])
                orientacao = valor[2]

                coluna = ord(letra) - ord("a")
                linha = numero - 1  # Ajuste para índice 0-based

                acoes.append(("parede", (linha, coluna, orientacao)))

        return acoes

    def serializar_tabuleiro(self):
        """
        Cria uma cópia serializável do estado atual do tabuleiro para poder restaurá-lo depois.

        Returns:
            dict: Um dicionário contendo o estado do tabuleiro, posições dos jogadores e paredes restantes
        """
        # Serializar o tabuleiro (armazenando as propriedades de cada Square)
        tabuleiro_serializado = []
        for linha in range(self.linhas):
            linha_serializada = []
            for coluna in range(self.colunas):
                square = self.tabuleiro[linha][coluna]
                square_dict = {
                    "pode_mover_para_cima": square.pode_mover_para_cima,
                    "pode_mover_para_baixo": square.pode_mover_para_baixo,
                    "pode_mover_para_esquerda": square.pode_mover_para_esquerda,
                    "pode_mover_para_direita": square.pode_mover_para_direita,
                    "tem_jogador": square.tem_jogador,
                }
                linha_serializada.append(square_dict)
            tabuleiro_serializado.append(linha_serializada)

        # Salvar posições dos jogadores e paredes restantes
        return {
            "tabuleiro": tabuleiro_serializado,
            "jogadores": self.jogadores.copy(),
            "paredes_restantes": self.paredes_restantes.copy(),
        }

    def restaurar_tabuleiro(self, estado_serializado):
        """
        Restaura o tabuleiro para um estado serializado anteriormente.

        Args:
            estado_serializado (dict): Dicionário com o estado do tabuleiro criado por serializar_tabuleiro()
        """
        # Restaurar tabuleiro
        for linha in range(self.linhas):
            for coluna in range(self.colunas):
                square_dict = estado_serializado["tabuleiro"][linha][coluna]
                square = self.tabuleiro[linha][coluna]

                square.pode_mover_para_cima = square_dict["pode_mover_para_cima"]
                square.pode_mover_para_baixo = square_dict["pode_mover_para_baixo"]
                square.pode_mover_para_esquerda = square_dict[
                    "pode_mover_para_esquerda"
                ]
                square.pode_mover_para_direita = square_dict["pode_mover_para_direita"]
                square.tem_jogador = square_dict["tem_jogador"]

        # Restaurar posições dos jogadores e paredes restantes
        self.jogadores = estado_serializado["jogadores"].copy()
        self.paredes_restantes = estado_serializado["paredes_restantes"].copy()

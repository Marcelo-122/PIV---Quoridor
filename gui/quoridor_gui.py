import os
import sys
from enum import Enum, auto

import pygame
from src.ai.q_learning_agent import AgenteQLearningTabular
from src.ai.minimax import escolher_movimento_ai
from src.core.constantes import (
    LARGURA,  # Apenas LARGURA é usada diretamente aqui para botões  # noqa: E402
)
from src.core.game import JogoQuoridor  # noqa: E402

from . import (
    gui_config as config,  # Use o alias config para o novo módulo  # noqa: E402
)
from . import gui_drawing  # Importa o novo módulo de desenho  # noqa: E402

# Adiciona o diretório raiz do projeto ao sys.path para garantir que `src` seja encontrado.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
    
class GameState(Enum):
    TITLE_SCREEN = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class GameMode(Enum):
    HUMAN_VS_HUMAN = "Humano vs Humano"
    HUMAN_VS_MINIMAX = "Humano vs Minimax"
    HUMAN_VS_Q_LEARNING = "Humano vs Q-Learning"
    Q_LEARNING_VS_MINIMAX = "Q-Learning vs Minimax"


class QuoridorGUI:
    def __init__(self):
        """Inicializa a GUI, focada no estado e na lógica do jogo."""
        pygame.init()
        self.screen = pygame.display.set_mode((config.LARGURA_TELA, config.ALTURA_TELA))
        pygame.display.set_caption("Quoridor com IA")
        self.clock = pygame.time.Clock()
        self.game_state = GameState.TITLE_SCREEN
        self.game_mode = None
        self.jogo = None
        self.mensagem = ""
        self.human_players = []
        self.turno = 0  # 0 para Jogador 1, 1 para Jogador 2
        self.buttons = self._create_title_buttons()

        # Estado para colocação de paredes pelo jogador humano
        self.colocando_parede = False
        self.parede_orientacao = 'h'  # 'h' para horizontal, 'v' para vertical
        self.parede_temp_pos = None  # Posição (col, row) para preview da parede
        self.ai_is_thinking = False  # Trava para impedir chamadas repetidas da IA

        # Inicializa os agentes de IA
        self.q_learning_agent = self._carregar_q_learning_agent()

    def _create_title_buttons(self):
        """Cria os retângulos e textos para os botões da tela de título."""
        buttons = {}
        button_width, button_height = 400, 60
        start_y = 250
        spacing = 80
        center_x = LARGURA // 2 - button_width // 2  # Usa LARGURA de constantes.py

        for i, mode in enumerate(GameMode):
            y_pos = start_y + i * spacing
            buttons[mode] = {
                "rect": pygame.Rect(center_x, y_pos, button_width, button_height),
                "text": mode.value,
                "mode": mode,
            }
        return buttons

    def _carregar_q_learning_agent(self):
        """Carrega o agente Q-Learning treinado mais recente a partir de um arquivo."""
        pasta_modelos = "saved_models_q_tabular"
        try:
            if not os.path.exists(pasta_modelos):
                print(f"ERRO: A pasta de modelos '{pasta_modelos}' não foi encontrada.")
                return None

            lista_arquivos = [os.path.join(pasta_modelos, f) for f in os.listdir(pasta_modelos) if f.endswith(".pkl")]

            if not lista_arquivos:
                print(f"ERRO: Nenhum modelo Q-Learning encontrado na pasta {pasta_modelos}")
                return None

            caminho_modelo_recente = max(lista_arquivos, key=os.path.getmtime)

            agent = AgenteQLearningTabular(
                taxa_aprendizado=0, epsilon=0, fator_desconto=0
            )
            agent.carregar_q_tabela(caminho_modelo_recente)
            return agent

        except Exception as e:
            print(f"ERRO: Falha ao carregar o agente Q-Learning: {e}")
            return None

    def _start_game(self, mode: GameMode):
        self.game_mode = mode
        # Usar tabuleiro 5x5 com 3 paredes por jogador, consistente com o script de treinamento
        self.jogo = JogoQuoridor(linhas=5, colunas=5, total_paredes_jogador=3)
        self.turno = 0
        self.mensagem = f"Modo: {mode.value}"
        self.ai_is_thinking = False

        if mode == GameMode.HUMAN_VS_HUMAN:
            self.human_players = [0, 1]
        elif mode == GameMode.HUMAN_VS_MINIMAX:
            self.human_players = [0]  # Humano é J1 (índice 0)
        elif mode == GameMode.HUMAN_VS_Q_LEARNING:
            self.human_players = [0]  # Humano é J1 (índice 0)
        elif mode == GameMode.Q_LEARNING_VS_MINIMAX:
            self.human_players = []  # Nenhum jogador humano
        else:
            # Garante um estado padrão seguro se o modo for desconhecido
            self.human_players = [0, 1]
            self.mensagem = f"Modo '{mode.value}' desconhecido. Padrão para H vs H."

        self.game_state = GameState.PLAYING

    def _handle_title_screen_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn_info in self.buttons.values():
                if btn_info["rect"].collidepoint(event.pos):
                    self._start_game(btn_info["mode"])
                    break

    def _handle_game_input(self, event):
        if self.turno not in self.human_players or self.jogo.jogo_terminado:
            return

        # --- Manipulação de Eventos --- #

        # 1. Movimento do mouse para preview da parede
        if event.type == pygame.MOUSEMOTION and self.colocando_parede:
            mx, my = event.pos
            ox, oy = config.BOARD_OFFSET_X, config.BOARD_OFFSET_Y
            cs = config.CELL_SIZE
            col = (mx - ox) // cs
            row = (my - oy) // cs

            # A parede deve começar dentro da grade de 8x8 de posições de parede
            if 0 <= col < 8 and 0 <= row < 8:
                self.parede_temp_pos = (col, row)
            else:
                self.parede_temp_pos = None

        # 2. Clique do mouse para colocar a parede
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.colocando_parede:
            if self.parede_temp_pos:
                col, row = self.parede_temp_pos
                letra_coluna = chr(ord('a') + col)
                numero_linha = str(row + 1)
                notacao_parede = f"{letra_coluna}{numero_linha}{self.parede_orientacao}"
                movimento_tupla = ('parede', notacao_parede)

                if self.jogo.aplicar_movimento(movimento_tupla, self.turno):
                    self.mensagem = f"Jogador {self.turno + 1} colocou uma parede."
                    self.turno = 1 - self.turno
                else:
                    self.mensagem = "Posição de parede inválida."

                # Sai do modo de colocação de parede após a tentativa
                self.colocando_parede = False
                self.parede_temp_pos = None

        # 3. Teclado para modos e movimento
        elif event.type == pygame.KEYDOWN:
            # Tecla 'p' para entrar/sair do modo de colocação de parede
            if event.key == pygame.K_p:
                self.colocando_parede = not self.colocando_parede
                self.parede_temp_pos = None  # Limpa o preview ao mudar de modo
                if self.colocando_parede:
                    self.mensagem = "Modo Parede: 'r' para girar, clique para colocar."
                else:
                    self.mensagem = ""
                return

            # Tecla 'r' para girar a parede
            if event.key == pygame.K_r and self.colocando_parede:
                self.parede_orientacao = 'v' if self.parede_orientacao == 'h' else 'h'
                return

            # Movimento do peão (só se não estiver colocando parede)
            if not self.colocando_parede:
                movimento_str = None
                if event.key == pygame.K_w:
                    movimento_str = "w"
                elif event.key == pygame.K_s:
                    movimento_str = "s"
                elif event.key == pygame.K_a:
                    movimento_str = "a"
                elif event.key == pygame.K_d:
                    movimento_str = "d"

                if movimento_str:
                    movimento_tupla = ('mover', movimento_str)
                    if self.jogo.aplicar_movimento(movimento_tupla, self.turno):
                        self.mensagem = f"Jogador {self.turno + 1} moveu o peão."
                        self.turno = 1 - self.turno
                    else:
                        self.mensagem = "Movimento de peão inválido."

    def _update_game(self):
        # Se um vencedor foi encontrado e o estado da GUI ainda não foi atualizado
        if self.jogo.verificar_vitoria() and self.game_state != GameState.GAME_OVER:
            self.game_state = GameState.GAME_OVER
            vencedor_num = 1 if self.jogo.vencedor == "J1" else 2
            self.mensagem = f"Fim de Jogo! Vencedor: Jogador {vencedor_num}"
            return  # Fim do update, o jogo acabou.

        # Log de depuração para verificar o estado do turno e dos jogadores humanos
        #print(f"[DEBUG] Verificando turno: self.turno={self.turno}, self.human_players={self.human_players}")

        if self.turno not in self.human_players and not self.ai_is_thinking:
            self._ai_turn()
            pygame.time.wait(200)  # Pausa para visualizar jogada da IA

    def _draw(self):
        """Desenha a tela com base no estado atual do jogo."""
        self.screen.fill(config.COR_FUNDO)

        if self.game_state == GameState.TITLE_SCREEN:
            gui_drawing.draw_title_screen(self.screen, self.buttons)
        else:
            # Garante que o jogo não é None antes de tentar desenhar
            if self.jogo:
                gui_drawing.draw_game(
                    self.screen,
                    self.jogo,
                    self.turno,  # jogador_atual
                    self.colocando_parede,
                    self.parede_orientacao,
                    self.parede_temp_pos,
                    self.mensagem,
                    self.jogo.paredes_restantes  # Adicionado paredes_restantes
                )

        pygame.display.flip()

    def _ai_turn(self):
        """Executa o movimento de uma das IAs, dependendo do modo de jogo."""
        self.ai_is_thinking = True
        movimento_tupla = None
        jogador_idx = self.turno
        agent_name = ""

        try:
            # Modo: Humano vs. Minimax
            if self.game_mode == GameMode.HUMAN_VS_MINIMAX and jogador_idx == 1:
                agent_name = "Minimax"
                print(f"Turno do {agent_name} (Jogador {jogador_idx + 1})")
                movimento_tupla = escolher_movimento_ai(self.jogo, jogador_idx, profundidade=2)

            # Modo: Humano vs. Q-Learning
            elif self.game_mode == GameMode.HUMAN_VS_Q_LEARNING and jogador_idx == 1:
                agent_name = "Q-Learning"
                if self.q_learning_agent:
                    print(f"Turno do {agent_name} (Jogador {jogador_idx + 1})")
                    estado = self.jogo.get_estado_tupla(jogador_idx)
                    acoes_validas = self.jogo.get_acoes_validas(jogador_idx)
                    movimento_tupla = self.q_learning_agent.escolher_acao(estado, acoes_validas)
                else:
                    print("ERRO: Agente Q-Learning não foi carregado.")

            # Modo: Q-Learning vs. Minimax
            elif self.game_mode == GameMode.Q_LEARNING_VS_MINIMAX:
                if jogador_idx == 0:  # Vez do Q-Learning (J1)
                    agent_name = "Q-Learning"
                    if self.q_learning_agent:
                        print(f"Turno do {agent_name} (Jogador {jogador_idx + 1})")
                        estado = self.jogo.get_estado_tupla(jogador_idx)
                        acoes_validas = self.jogo.get_acoes_validas(jogador_idx)
                        movimento_tupla = self.q_learning_agent.escolher_acao(estado, acoes_validas)
                    else:
                        print("ERRO: Agente Q-Learning não foi carregado.")
                else:  # Vez do Minimax (J2)
                    agent_name = "Minimax"
                    print(f"Turno do {agent_name} (Jogador {jogador_idx + 1})")
                    movimento_tupla = escolher_movimento_ai(self.jogo, jogador_idx, profundidade=2)

            # Aplica o movimento se um foi escolhido pela IA
            if movimento_tupla:
                sucesso = self.jogo.aplicar_movimento(movimento_tupla, jogador_idx)
                if sucesso:
                    tipo_mov, valor_mov = movimento_tupla
                    acao_desc = f"moveu para {valor_mov}" if tipo_mov == 'mover' else f"colocou parede em {valor_mov}"
                    self.mensagem = f"IA ({agent_name}) jogou: {acao_desc}"
                    self.turno = 1 - self.turno
                else:
                    self.mensagem = f"ERRO CRÍTICO: IA ({agent_name}) gerou mov. inválido: {movimento_tupla}"
                    print(self.mensagem)
            elif agent_name:  # Se um agente deveria jogar mas não retornou movimento
                self.mensagem = f"AVISO: {agent_name} não retornou um movimento. Passando o turno."
                print(self.mensagem)
                self.turno = 1 - self.turno  # Passa o turno para evitar loop infinito

        finally:
            self.ai_is_thinking = False  # Libera a trava da IA, aconteça o que acontecer

    def run(self):
        """Loop principal do jogo."""
        running = True
        while running:
            # --- Processamento de Eventos ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.game_state == GameState.TITLE_SCREEN:
                    self._handle_title_screen_input(event)
                else:
                    self._handle_game_input(event)

            if self.game_state == GameState.PLAYING:
                self._update_game()

            self._draw()
            self.clock.tick(30)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    gui = QuoridorGUI()
    gui.run()

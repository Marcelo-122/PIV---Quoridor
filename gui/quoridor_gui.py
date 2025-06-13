import os
import sys
from enum import Enum, auto


# Adiciona o diretório raiz do projeto ao sys.path para garantir que `src` seja encontrado.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import pygame
# Importações do projeto e da GUI devem vir após a manipulação do sys.path,
# mas todas as importações devem ser agrupadas o máximo possível.
from src.ai.minimax import escolher_movimento_ai  # noqa: E402
from src.core.constantes import (
    LARGURA,  # Apenas LARGURA é usada diretamente aqui para botões  # noqa: E402
)
from src.core.game import JogoQuoridor  # noqa: E402

from . import (
    gui_config as config,  # Use o alias config para o novo módulo  # noqa: E402
)
from . import gui_drawing  # Importa o novo módulo de desenho  # noqa: E402


    
class GameState(Enum):
    TITLE_SCREEN = auto()
    PLAYING = auto()
    GAME_OVER = auto()


class GameMode(Enum):
    HUMAN_VS_HUMAN = "Humano vs Humano"
    HUMAN_VS_MINIMAX = "Humano vs Minimax"

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

    def _start_game(self, mode: GameMode):
        self.game_mode = mode
        self.jogo = JogoQuoridor()
        self.human_players = []
        self.turno = 0
        self.mensagem = f"Modo: {mode.value}"

        if mode == GameMode.HUMAN_VS_HUMAN:
            self.human_players = [0, 1]
        elif mode == GameMode.HUMAN_VS_MINIMAX:
            self.human_players = [0]  # Humano é J1 (índice 0)

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
                if self.parede_orientacao == 'h':
                    letra_coluna = chr(ord('a') + col)
                    numero_linha = str(row + 1)
                else: # 'v'
                    letra_coluna = chr(ord('a') + col + 1) # A coluna da parede vertical é a da célula à direita
                    numero_linha = str(row + 1)
                movimento_tupla = ('wall', (letra_coluna, numero_linha, self.parede_orientacao))

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
                    movimento_tupla = ('move', movimento_str)
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

        if self.turno not in self.human_players:
            self._ai_turn()
            if ( not self.jogo.jogo_terminado):
                pygame.time.wait(200)  # Pausa menor para agilizar

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
                    self.mensagem,
                    self.turno,
                    self.colocando_parede,
                    self.parede_orientacao,
                    self.parede_temp_pos,
                )

        pygame.display.flip()

    def _ai_turn(self):
        """Executa o movimento de uma das IAs."""
        movimento_tupla = None
        jogador_idx = self.turno

        is_minimax_turn = (
            self.game_mode == GameMode.HUMAN_VS_MINIMAX and jogador_idx == 1
        ) 
        
        if is_minimax_turn:
            print(f"Turno do Minimax (Jogador {jogador_idx + 1})")
            movimento_tupla = escolher_movimento_ai(
                self.jogo, jogador_idx, profundidade=2
            )

        if not movimento_tupla:
            self.mensagem = (
                f"AVISO: IA (Jogador {jogador_idx + 1}) não encontrou movimento válido."
            )
            print(f"AVISO: IA (Jogador {jogador_idx + 1}) não retornou movimento.")
            return

        print(f"IA (Jogador {jogador_idx + 1}) tentando movimento: {movimento_tupla}")
        if self.jogo.aplicar_movimento(movimento_tupla, jogador_idx):
            self.mensagem = f"IA (Jogador {jogador_idx + 1}) jogou: {movimento_tupla}"
            self.turno = 1 - self.turno
        else:
            self.mensagem = f"ERRO: IA (Jogador {jogador_idx + 1}) tentou mov. inválido: {movimento_tupla}"

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

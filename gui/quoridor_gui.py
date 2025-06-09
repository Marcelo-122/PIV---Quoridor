import os
import sys

# Add the project root to sys.path
# This must be at the very top to ensure subsequent imports work correctly when the script is run directly.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import time  # noqa: E402

import pygame  # noqa: E402

from src.ai.minimax import escolher_movimento_ai  # noqa: E402
from src.core.constantes import (  # noqa: E402
    ALTURA,
    BLACK,
    COLUNAS,
    LACUNA_TAMANHO,
    LARGURA,
    LINHAS,
)
from src.core.game import JogoQuoridor  # noqa: E402

# Initialize pygame
pygame.init()

# Set up display
screen = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Quoridor Game")
clock = pygame.time.Clock()

# Game settings
USAR_PODA_ALFABETA = True
USAR_ITERATIVE_DEEPENING = True
TEMPO_LIMITE_AI = 2.0
PROFUNDIDADE_PADRAO = 4

# Colors
PLAYER1_COLOR = (0, 0, 255)  # Blue
PLAYER2_COLOR = (255, 0, 0)  # Red
WALL_COLOR = (139, 69, 19)  # Brown
GRID_COLOR = (200, 200, 200)  # Light gray
BG_COLOR = (240, 240, 240)  # Off-white
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow for highlighting
LABEL_COLOR = (50, 50, 50)  # Dark gray for labels

# Font
font = pygame.font.SysFont("Arial", 20)
label_font = pygame.font.SysFont("Arial", 16)


class QuoridorGUI:
    def __init__(self):
        self.jogo = JogoQuoridor()
        self.turno = 0  # 0 = Jogador 1 (human), 1 = Jogador 2 (AI)
        self.jogo_terminado = False
        self.mensagem = "Quoridor: Jogador 1 (humano) vs Jogador 2 (IA)"
        self.colocando_parede = False
        self.parede_temp = None
        self.parede_orientacao = "h"  # Default wall orientation
        self.cell_size = LACUNA_TAMANHO
        self.wall_thickness = 10
        self.selected_cell = None

        # Add margin for labels
        self.margin = 30
        self.board_offset_x = self.margin
        self.board_offset_y = self.margin

    def draw_board(self):
        # Fill background
        screen.fill(BG_COLOR)

        # Draw row and column labels
        for i in range(LINHAS):
            # Row numbers (1-9)
            row_label = label_font.render(str(i + 1), True, LABEL_COLOR)
            screen.blit(
                row_label,
                (
                    self.board_offset_x - 20,
                    self.board_offset_y
                    + i * self.cell_size
                    + self.cell_size // 2
                    - row_label.get_height() // 2,
                ),
            )

            # Column letters (a-i)
            col_label = label_font.render(chr(ord("a") + i), True, LABEL_COLOR)
            screen.blit(
                col_label,
                (
                    self.board_offset_x
                    + i * self.cell_size
                    + self.cell_size // 2
                    - col_label.get_width() // 2,
                    self.board_offset_y - 20,
                ),
            )

        # Draw grid
        for i in range(LINHAS):
            for j in range(COLUNAS):
                # Draw cell
                pygame.draw.rect(
                    screen,
                    GRID_COLOR,
                    (
                        self.board_offset_x + j * self.cell_size,
                        self.board_offset_y + i * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    ),
                    1,
                )

                # Highlight selected cell if any
                if self.selected_cell and self.selected_cell == (i, j):
                    pygame.draw.rect(
                        screen,
                        HIGHLIGHT_COLOR,
                        (
                            self.board_offset_x + j * self.cell_size,
                            self.board_offset_y + i * self.cell_size,
                            self.cell_size,
                            self.cell_size,
                        ),
                        3,
                    )

        # Draw walls
        for i in range(LINHAS):
            for j in range(COLUNAS):
                square = self.jogo.tabuleiro[i][j]

                # Draw horizontal wall segment below square (i,j) if movement down is blocked
                if not square.pode_mover_para_baixo and i < LINHAS - 1:
                    pygame.draw.rect(
                        screen,
                        WALL_COLOR,
                        (
                            self.board_offset_x + j * self.cell_size,
                            self.board_offset_y
                            + (i + 1) * self.cell_size
                            - self.wall_thickness // 2,
                            self.cell_size,  # Wall segment is 1 cell wide
                            self.wall_thickness,
                        ),
                    )

                # Draw vertical wall segment to the right of square (i,j) if movement right is blocked
                if not square.pode_mover_para_direita and j < COLUNAS - 1:
                    pygame.draw.rect(
                        screen,
                        WALL_COLOR,
                        (
                            self.board_offset_x
                            + (j + 1) * self.cell_size
                            - self.wall_thickness // 2,
                            self.board_offset_y + i * self.cell_size,
                            self.wall_thickness,
                            self.cell_size,  # Wall segment is 1 cell high
                        ),
                    )

        # Draw temporary wall being placed
        if self.colocando_parede and self.parede_temp:
            col, row = self.parede_temp
            if self.parede_orientacao == "h":
                pygame.draw.rect(
                    screen,
                    (WALL_COLOR[0], WALL_COLOR[1], WALL_COLOR[2], 128),
                    (
                        self.board_offset_x + col * self.cell_size,
                        self.board_offset_y
                        + (row + 1) * self.cell_size
                        - self.wall_thickness // 2,
                        self.cell_size * 2,
                        self.wall_thickness,
                    ),
                )
            else:  # vertical
                pygame.draw.rect(
                    screen,
                    (WALL_COLOR[0], WALL_COLOR[1], WALL_COLOR[2], 128),
                    (
                        self.board_offset_x
                        + (col + 1) * self.cell_size
                        - self.wall_thickness // 2,
                        self.board_offset_y + row * self.cell_size,
                        self.wall_thickness,
                        self.cell_size * 2,
                    ),
                )

        # Draw players
        j1_linha, j1_coluna = self.jogo.jogadores["J1"]
        j2_linha, j2_coluna = self.jogo.jogadores["J2"]

        # Player 1 (human)
        pygame.draw.circle(
            screen,
            PLAYER1_COLOR,
            (
                self.board_offset_x + j1_coluna * self.cell_size + self.cell_size // 2,
                self.board_offset_y + j1_linha * self.cell_size + self.cell_size // 2,
            ),
            self.cell_size // 3,
        )

        # Player 2 (AI)
        pygame.draw.circle(
            screen,
            PLAYER2_COLOR,
            (
                self.board_offset_x + j2_coluna * self.cell_size + self.cell_size // 2,
                self.board_offset_y + j2_linha * self.cell_size + self.cell_size // 2,
            ),
            self.cell_size // 3,
        )

        # Draw remaining walls count
        p1_walls = font.render(
            f"P1 Walls: {self.jogo.paredes_restantes['J1']}", True, PLAYER1_COLOR
        )
        p2_walls = font.render(
            f"P2 Walls: {self.jogo.paredes_restantes['J2']}", True, PLAYER2_COLOR
        )
        screen.blit(p1_walls, (10, ALTURA - 60))
        screen.blit(p2_walls, (10, ALTURA - 30))

        # Draw current turn and message
        turn_text = font.render(
            f"Turno: {'Jogador 1' if self.turno == 0 else 'IA'}", True, BLACK
        )
        message_text = font.render(self.mensagem, True, BLACK)
        screen.blit(turn_text, (LARGURA - 200, ALTURA - 60))
        screen.blit(
            message_text, (LARGURA // 2 - message_text.get_width() // 2, ALTURA - 30)
        )

        # Draw controls help
        if self.turno == 0 and not self.jogo_terminado:
            if self.colocando_parede:
                help_text = font.render(
                    "Clique para colocar parede, R para rotacionar, ESC para cancelar",
                    True,
                    BLACK,
                )
            else:
                help_text = font.render(
                    "WASD/Setas para mover, P para colocar parede", True, BLACK
                )
            screen.blit(help_text, (LARGURA // 2 - help_text.get_width() // 2, 10))

    def get_cell_from_pos(self, pos):
        x, y = pos
        # Adjust for board offset
        x -= self.board_offset_x
        y -= self.board_offset_y

        col = x // self.cell_size
        row = y // self.cell_size
        if 0 <= col < COLUNAS and 0 <= row < LINHAS:
            return row, col
        return None

    def place_wall(self, pos):
        cell = self.get_cell_from_pos(pos)
        if not cell:
            return False

        row, col = cell
        # Convert to game notation (e.g., "e5h")
        col_letter = chr(ord("a") + col)
        row_num = row + 1
        notation = f"{col_letter}{row_num}{self.parede_orientacao}"

        # Try to place the wall
        return self.jogo.colocar_parede(notation, self.turno)

    def ai_turn(self):
        self.mensagem = "IA está pensando..."
        self.draw_board()
        pygame.display.flip()

        inicio = time.time()
        movimento = escolher_movimento_ai(
            self.jogo,
            self.turno,
            profundidade=PROFUNDIDADE_PADRAO,
            usar_poda=USAR_PODA_ALFABETA,
            usar_iterative_deepening=USAR_ITERATIVE_DEEPENING,
            tempo_limite=TEMPO_LIMITE_AI,
        )
        tempo_total = time.time() - inicio

        if movimento is None:
            self.mensagem = "IA não encontrou movimento válido. Fim de jogo."
            self.jogo_terminado = True
            return

        tipo, valor = movimento
        if tipo == "move":
            direcoes = {"w": "cima", "a": "esquerda", "s": "baixo", "d": "direita"}
            direcao_texto = direcoes.get(valor, valor)
            self.jogo.andar(valor, self.turno)
            self.mensagem = (
                f"IA moveu para {direcao_texto} ({valor}) em {tempo_total:.2f}s"
            )
        elif tipo == "wall":
            self.jogo.colocar_parede(valor, self.turno)
            self.mensagem = (
                f"IA colocou parede na posição {valor} em {tempo_total:.2f}s"
            )

        # Check for victory
        if self.jogo.verificar_vitoria():
            self.jogo_terminado = True

    def run(self):
        running = True

        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if not self.jogo_terminado:
                    if self.turno == 0:  # Human player's turn
                        if event.type == pygame.KEYDOWN:
                            if not self.colocando_parede:
                                # Movement controls
                                if event.key in [pygame.K_w, pygame.K_UP]:
                                    if self.jogo.andar("w", self.turno):
                                        self.mensagem = "Jogador 1 moveu para cima"
                                        self.turno = (self.turno + 1) % 2
                                elif event.key in [pygame.K_s, pygame.K_DOWN]:
                                    if self.jogo.andar("s", self.turno):
                                        self.mensagem = "Jogador 1 moveu para baixo"
                                        self.turno = (self.turno + 1) % 2
                                elif event.key in [pygame.K_a, pygame.K_LEFT]:
                                    if self.jogo.andar("a", self.turno):
                                        self.mensagem = "Jogador 1 moveu para esquerda"
                                        self.turno = (self.turno + 1) % 2
                                elif event.key in [pygame.K_d, pygame.K_RIGHT]:
                                    if self.jogo.andar("d", self.turno):
                                        self.mensagem = "Jogador 1 moveu para direita"
                                        self.turno = (self.turno + 1) % 2
                                # Wall placement mode
                                elif event.key == pygame.K_p:
                                    if self.jogo.paredes_restantes["J1"] > 0:
                                        self.colocando_parede = True
                                        self.mensagem = (
                                            "Selecione onde colocar a parede"
                                        )
                                    else:
                                        self.mensagem = "Você não tem mais paredes!"
                            else:  # In wall placement mode
                                if event.key == pygame.K_r:  # Rotate wall
                                    self.parede_orientacao = (
                                        "v" if self.parede_orientacao == "h" else "h"
                                    )
                                elif (
                                    event.key == pygame.K_ESCAPE
                                ):  # Cancel wall placement
                                    self.colocando_parede = False
                                    self.parede_temp = None
                                    self.mensagem = "Colocação de parede cancelada"

                        elif event.type == pygame.MOUSEMOTION and self.colocando_parede:
                            # Update temporary wall position
                            cell = self.get_cell_from_pos(event.pos)
                            if cell:
                                row, col = cell
                                self.parede_temp = (col, row)

                        elif (
                            event.type == pygame.MOUSEBUTTONDOWN
                            and self.colocando_parede
                        ):
                            # Try to place the wall
                            if self.place_wall(event.pos):
                                self.mensagem = "Parede colocada com sucesso"
                                self.colocando_parede = False
                                self.parede_temp = None
                                self.turno = (self.turno + 1) % 2
                            else:
                                self.mensagem = "Não é possível colocar a parede aqui"

            # AI turn
            if not self.jogo_terminado and self.turno == 1:
                self.ai_turn()
                self.turno = (self.turno + 1) % 2

            # Check for victory
            if not self.jogo_terminado and self.jogo.verificar_vitoria():
                self.jogo_terminado = True
                winner = (
                    "Jogador 1"
                    if self.jogo.jogadores["J1"][0] == 8
                    else "Jogador 2 (IA)"
                )
                self.mensagem = f"{winner} venceu o jogo!"

            # Draw everything
            self.draw_board()

            # Update display
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    game = QuoridorGUI()
    game.run()

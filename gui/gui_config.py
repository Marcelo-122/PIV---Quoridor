import os
import pygame

# Adiciona o diretório raiz do projeto ao sys.path para encontrar o `src`
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Importa constantes do core
from src.core.constantes import LARGURA, ALTURA  # noqa: E402

# Define constantes de tela para serem usadas pela GUI
LARGURA_TELA = LARGURA
ALTURA_TELA = ALTURA

# --- Inicialização do Pygame e Fontes ---
pygame.init()
pygame.font.init()

# --- Constantes de Tela e Fontes ---
SCREEN = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
FONT_DEFAULT = pygame.font.SysFont("Arial", 24)
FONT_TITULO = pygame.font.SysFont("Arial", 48, bold=True)
FONT_BOTAO = pygame.font.SysFont("Arial", 32)

# Diretório de modelos removido

# --- Cores ---
BG_COLOR = (240, 240, 240)
BTN_COLOR = (100, 180, 255)
BTN_HOVER_COLOR = (150, 210, 255)
TEXT_COLOR = (10, 10, 10)
COR_PAREDE = (139, 69, 19)  # Marrom
COR_PAREDE_PREVIEW = (139, 69, 19, 128) # Marrom semitransparente para preview
COR_J1 = (0, 0, 255)
COR_J2 = (255, 0, 0)
COR_GRADE = (200, 200, 200)
PRETO = (0, 0, 0)
COR_FUNDO = (240, 240, 240)
COR_TEXTO = (10, 10, 10)
COR_BOTAO = (100, 180, 255)
COR_BOTAO_HOVER = (150, 210, 255)
COR_BOTAO_CLICK = (100, 180, 255)

# --- Configurações de Desenho do Tabuleiro ---
CELL_SIZE = 60
WALL_THICKNESS = 10
BOARD_MARGIN = 50
BOARD_OFFSET_X = BOARD_MARGIN
BOARD_OFFSET_Y = BOARD_MARGIN

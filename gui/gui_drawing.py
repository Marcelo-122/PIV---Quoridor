import pygame
from . import gui_config as config
from src.core.constantes import LINHAS, COR_MSG_VITORIA, COR_MSG_ERRO, LARGURA, ALTURA

def draw_title_screen(screen, buttons):
    """Desenha a tela de título com os botões de modo de jogo."""
    screen.fill(config.COR_FUNDO)
    # Título
    title_text = config.FONT_TITULO.render("Quoridor AI", True, config.COR_TEXTO)
    screen.blit(
        title_text,
        (LARGURA // 2 - title_text.get_width() // 2, 100),
    )
    # Subtítulo
    subtitle_text = config.FONT_DEFAULT.render(
        "Selecione um modo de jogo", True, config.COR_TEXTO
    )
    screen.blit(
        subtitle_text,
        (LARGURA // 2 - subtitle_text.get_width() // 2, 200),
    )

    # Botões
    mouse_pos = pygame.mouse.get_pos()
    for btn_info in buttons.values():
        rect = btn_info["rect"]
        color = config.COR_BOTAO_HOVER if rect.collidepoint(mouse_pos) else config.COR_BOTAO
        pygame.draw.rect(screen, color, rect, border_radius=10)

        btn_text = config.FONT_BOTAO.render(btn_info["text"], True, config.COR_TEXTO)
        screen.blit(
            btn_text,
            (
                rect.centerx - btn_text.get_width() // 2,
                rect.centery - btn_text.get_height() // 2,
            ),
        )

def draw_game(screen, jogo, mensagem, turno, colocando_parede, parede_orientacao, parede_temp_pos):
    """Desenha o tabuleiro, peões, paredes e informações do jogo."""
    screen.fill(config.COR_FUNDO)

    # --- Desenha Legendas (letras e números) ---
    label_font = pygame.font.SysFont("Arial", 16)
    for i in range(LINHAS):
        row_label = label_font.render(str(i + 1), True, config.COR_TEXTO)
        screen.blit(row_label, (config.BOARD_OFFSET_X - 25, config.BOARD_OFFSET_Y + i * config.CELL_SIZE + config.CELL_SIZE // 2 - row_label.get_height() // 2))
        col_label = label_font.render(chr(ord("a") + i), True, config.COR_TEXTO)
        screen.blit(col_label, (config.BOARD_OFFSET_X + i * config.CELL_SIZE + config.CELL_SIZE // 2 - col_label.get_width() // 2, config.BOARD_OFFSET_Y - 25))

    # --- Desenha a Grade e Paredes ---
    for i in range(LINHAS):
        for j in range(LINHAS):
            square = jogo.tabuleiro[i][j]
            pygame.draw.rect(screen, config.COR_GRADE, (config.BOARD_OFFSET_X + j * config.CELL_SIZE, config.BOARD_OFFSET_Y + i * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE), 1)
            if not square.pode_mover_para_baixo and i < LINHAS - 1:
                pygame.draw.rect(screen, config.COR_PAREDE, (config.BOARD_OFFSET_X + j * config.CELL_SIZE, config.BOARD_OFFSET_Y + (i + 1) * config.CELL_SIZE - config.WALL_THICKNESS // 2, config.CELL_SIZE, config.WALL_THICKNESS))
            if not square.pode_mover_para_direita and j < LINHAS - 1:
                pygame.draw.rect(screen, config.COR_PAREDE, (config.BOARD_OFFSET_X + (j + 1) * config.CELL_SIZE - config.WALL_THICKNESS // 2, config.BOARD_OFFSET_Y + i * config.CELL_SIZE, config.WALL_THICKNESS, config.CELL_SIZE))

    # --- Desenha Preview da Parede ---
    if colocando_parede and parede_temp_pos:
        col, row = parede_temp_pos
        preview_rect = pygame.Rect(0,0,0,0)
        if parede_orientacao == 'h':
            preview_rect = pygame.Rect(
                config.BOARD_OFFSET_X + col * config.CELL_SIZE,
                config.BOARD_OFFSET_Y + (row + 1) * config.CELL_SIZE - config.WALL_THICKNESS // 2,
                config.CELL_SIZE * 2,  # Parede horizontal tem 2 células de largura
                config.WALL_THICKNESS
            )
        else:  # 'v'
            preview_rect = pygame.Rect(
                config.BOARD_OFFSET_X + (col + 1) * config.CELL_SIZE - config.WALL_THICKNESS // 2,
                config.BOARD_OFFSET_Y + row * config.CELL_SIZE,
                config.WALL_THICKNESS,
                config.CELL_SIZE * 2  # Parede vertical tem 2 células de altura
            )
        # Desenha um retângulo semi-transparente para o preview
        s = pygame.Surface(preview_rect.size, pygame.SRCALPHA)
        s.fill(config.COR_PAREDE_PREVIEW)
        screen.blit(s, preview_rect.topleft)

    # --- Desenha Peões ---
    j1_linha, j1_coluna = jogo.jogadores["J1"]
    j2_linha, j2_coluna = jogo.jogadores["J2"]
    pygame.draw.circle(screen, config.COR_J1, (config.BOARD_OFFSET_X + j1_coluna * config.CELL_SIZE + config.CELL_SIZE // 2, config.BOARD_OFFSET_Y + j1_linha * config.CELL_SIZE + config.CELL_SIZE // 2), config.CELL_SIZE // 3)
    pygame.draw.circle(screen, config.COR_J2, (config.BOARD_OFFSET_X + j2_coluna * config.CELL_SIZE + config.CELL_SIZE // 2, config.BOARD_OFFSET_Y + j2_linha * config.CELL_SIZE + config.CELL_SIZE // 2), config.CELL_SIZE // 3)

    # --- Desenha Informações ---
    msg_color = COR_MSG_VITORIA if jogo.jogo_terminado else config.COR_TEXTO
    if "inválid" in mensagem or "ERRO" in mensagem or "AVISO" in mensagem:
        msg_color = COR_MSG_ERRO
    msg_text = config.FONT_DEFAULT.render(mensagem, True, msg_color)
    screen.blit(msg_text, (20, 10))

    turno_str = f"Turno: Jogador {turno + 1}" if not jogo.jogo_terminado else "Fim de Jogo"
    turno_text = config.FONT_DEFAULT.render(turno_str, True, config.COR_TEXTO)
    screen.blit(turno_text, (LARGURA - turno_text.get_width() - 20, 10))

    p1_walls = config.FONT_DEFAULT.render(f"Paredes J1: {jogo.paredes_restantes['J1']}", True, config.COR_J1)
    p2_walls = config.FONT_DEFAULT.render(f"Paredes J2: {jogo.paredes_restantes['J2']}", True, config.COR_J2)
    screen.blit(p1_walls, (20, ALTURA - 40))
    screen.blit(p2_walls, (LARGURA - p2_walls.get_width() - 20, ALTURA - 40))

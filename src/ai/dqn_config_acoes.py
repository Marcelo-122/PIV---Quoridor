# --- Definições do Espaço de Ação ---
NUM_ACOES_PEAO = 4
# Movimentos: 0: 'w' (cima), 1: 's' (baixo), 2: 'a' (esquerda), 3: 'd' (direita)
ACOES_PEAO_MAP = {0: "w", 1: "s", 2: "a", 3: "d"}
ACOES_PEAO_INV_MAP = {
    v: k for k, v in ACOES_PEAO_MAP.items()
}  # Para mapeamento inverso

NUM_POSICOES_PAREDE_HORIZONTAL = 64  # Grade 8x8
NUM_POSICOES_PAREDE_VERTICAL = 64  # Grade 8x8

TOTAL_ACOES = (
    NUM_ACOES_PEAO + NUM_POSICOES_PAREDE_HORIZONTAL + NUM_POSICOES_PAREDE_VERTICAL
)
# Total = 4 + 64 + 64 = 132

# --- Funções de Mapeamento Ação <-> Movimento do Jogo ---

def indice_para_movimento(indice_acao):
    """
    Converte um índice de ação (0-131) para uma tupla de movimento do jogo.
    Ex: (tipo_movimento, valor_movimento) -> ('move', 's') ou ('wall', 'e5h')
    """
    if not (0 <= indice_acao < TOTAL_ACOES):
        raise ValueError(
            f"Índice de ação inválido: {indice_acao}. Deve estar entre 0 e {TOTAL_ACOES - 1}."
        )

    # Ações de Peão (índices 0-3)
    if indice_acao < NUM_ACOES_PEAO:
        direcao = ACOES_PEAO_MAP[indice_acao]
        return ("move", direcao)

    # Ações de Parede Horizontal (índices 4 a 4 + 64 - 1 = 67)
    elif indice_acao < NUM_ACOES_PEAO + NUM_POSICOES_PAREDE_HORIZONTAL:
        indice_parede_h = indice_acao - NUM_ACOES_PEAO
        # Converte índice linear (0-63) para coordenadas da grade 8x8
        linha_grid = (
            indice_parede_h // 8
        )  # 0-7 (corresponde à linha do tabuleiro *acima* da parede)
        coluna_grid = (
            indice_parede_h % 8
        )  # 0-7 (corresponde à coluna do tabuleiro onde a parede começa à esquerda)

        # Converte coordenadas da grade para notação do jogo (ex: 'a1h' a 'h8h')
        # Linha na notação é 1-indexada (linha_grid + 1)
        # Coluna na notação é 'a'-'h' (chr(ord('a') + coluna_grid))
        notacao_coluna = chr(ord("a") + coluna_grid)
        notacao_linha = str(linha_grid + 1)
        notacao_parede = f"{notacao_coluna}{notacao_linha}h"
        return ("wall", notacao_parede)

    # Ações de Parede Vertical (índices 68 a 68 + 64 - 1 = 131)
    else:
        indice_parede_v = indice_acao - (
            NUM_ACOES_PEAO + NUM_POSICOES_PAREDE_HORIZONTAL
        )
        # Converte índice linear (0-63) para coordenadas da grade 8x8
        linha_grid = (
            indice_parede_v // 8
        )  # 0-7 (corresponde à linha do tabuleiro onde a parede começa no topo)
        coluna_grid = (
            indice_parede_v % 8
        )  # 0-7 (corresponde à coluna do tabuleiro *à esquerda* da parede)

        # Converte coordenadas da grade para notação do jogo (ex: 'a1v' a 'h8v')
        notacao_coluna = chr(ord("a") + coluna_grid)
        notacao_linha = str(linha_grid + 1)
        notacao_parede = f"{notacao_coluna}{notacao_linha}v"
        return ("wall", notacao_parede)


def movimento_para_indice(tipo_movimento, valor_movimento):
    """
    Converte uma tupla de movimento do jogo para um índice de ação (0-131).
    """
    if tipo_movimento == "move":
        if valor_movimento not in ACOES_PEAO_INV_MAP:
            raise ValueError(f"Direção de movimento inválida: {valor_movimento}")
        return ACOES_PEAO_INV_MAP[valor_movimento]

    elif tipo_movimento == "wall":
        if not (
            len(valor_movimento) == 3
            and "a" <= valor_movimento[0] <= "h"
            and "1" <= valor_movimento[1] <= "8"
            and valor_movimento[2] in ["h", "v"]
        ):
            raise ValueError(f"Notação de parede inválida: {valor_movimento}")

        coluna_notacao = valor_movimento[0]
        linha_notacao = valor_movimento[1]
        tipo_parede = valor_movimento[2]

        coluna_grid = ord(coluna_notacao) - ord("a")  # 0-7
        linha_grid = int(linha_notacao) - 1  # 0-7

        if tipo_parede == "h":
            indice_parede_h = linha_grid * 8 + coluna_grid  # Índice linear (0-63)
            return NUM_ACOES_PEAO + indice_parede_h
        elif tipo_parede == "v":
            indice_parede_v = linha_grid * 8 + coluna_grid  # Índice linear (0-63)
            return NUM_ACOES_PEAO + NUM_POSICOES_PAREDE_HORIZONTAL + indice_parede_v
    else:
        raise ValueError(f"Tipo de movimento desconhecido: {tipo_movimento}")

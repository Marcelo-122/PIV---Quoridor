from collections import deque

def existe_caminho(jogador, linha_inicial, coluna_inicial, board):
    visitado = [[False for _ in range(9)] for _ in range(9)]
    fila = deque()
    fila.append((linha_inicial, coluna_inicial))

    while fila:
        linha, coluna = fila.popleft()

        if visitado[linha][coluna]:
            continue

        visitado[linha][coluna] = True

        # Condição de vitória
        if (jogador == "J1" and linha == 8) or (jogador == "J2" and linha == 0):
            return True

        # Verificações de movimento usando board
        # CIMA
        if (
            linha > 0
            and board[linha][coluna].can_move_up
            and not visitado[linha - 1][coluna]
        ):
            fila.append((linha - 1, coluna))
        # BAIXO
        if (
            linha < 8
            and board[linha][coluna].can_move_down
            and not visitado[linha + 1][coluna]
        ):
            fila.append((linha + 1, coluna))
        # ESQUERDA
        if (
            coluna > 0
            and board[linha][coluna].can_move_left
            and not visitado[linha][coluna - 1]
        ):
            fila.append((linha, coluna - 1))
        # DIREITA
        if (
            coluna < 8
            and board[linha][coluna].can_move_right
            and not visitado[linha][coluna + 1]
        ):
            fila.append((linha, coluna + 1))

    return False  # Nenhum caminho encontrado

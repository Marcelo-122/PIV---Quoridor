from collections import deque

def existe_caminho(jogador, linha_inicial, coluna_inicial, tabuleiro):
    # Determinar as dimensões do tabuleiro dinamicamente
    num_linhas = len(tabuleiro)
    num_colunas = len(tabuleiro[0]) if num_linhas > 0 else 0
    
    visitado = [[False for _ in range(num_colunas)] for _ in range(num_linhas)]
    fila = deque()
    fila.append((linha_inicial, coluna_inicial))

    while fila:
        linha, coluna = fila.popleft()

        if visitado[linha][coluna]:
            continue

        visitado[linha][coluna] = True

        # Condição de vitória
        if (jogador == "J1" and linha == num_linhas - 1) or (jogador == "J2" and linha == 0):
            return True

        # Verificações de movimento usando tabuleiro
        # CIMA
        if (
            linha > 0
            and tabuleiro[linha][coluna].pode_mover_para_cima
            and not visitado[linha - 1][coluna]
        ):
            fila.append((linha - 1, coluna))
        # BAIXO
        if (
            linha < num_linhas - 1
            and tabuleiro[linha][coluna].pode_mover_para_baixo
            and not visitado[linha + 1][coluna]
        ):
            fila.append((linha + 1, coluna))
        # ESQUERDA
        if (
            coluna > 0
            and tabuleiro[linha][coluna].pode_mover_para_esquerda
            and not visitado[linha][coluna - 1]
        ):
            fila.append((linha, coluna - 1))
        # DIREITA
        if (
            coluna < num_colunas - 1
            and tabuleiro[linha][coluna].pode_mover_para_direita
            and not visitado[linha][coluna + 1]
        ):
            fila.append((linha, coluna + 1))

    return False  # Nenhum caminho encontrado

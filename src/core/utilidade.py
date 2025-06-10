from collections import deque

def shortest_path_length(jogador, pos, tabuleiro):
    visitado = [[False for _ in range(9)] for _ in range(9)]
    fila = deque()
    fila.append((pos[0], pos[1], 0))  # (linha, coluna, distancia)
    objetivo = 8 if jogador == "J1" else 0

    while fila:
        linha, coluna, dist = fila.popleft()
        if visitado[linha][coluna]:
            continue
        visitado[linha][coluna] = True

        # Condição de vitória
        if (jogador == "J1" and linha == objetivo) or (jogador == "J2" and linha == objetivo):
            return dist

        # Movimentos possíveis
        if linha > 0 and tabuleiro[linha][coluna].pode_mover_para_cima and not visitado[linha-1][coluna]:
            fila.append((linha-1, coluna, dist+1))
        if linha < 8 and tabuleiro[linha][coluna].pode_mover_para_baixo and not visitado[linha+1][coluna]:
            fila.append((linha+1, coluna, dist+1))
        if coluna > 0 and tabuleiro[linha][coluna].pode_mover_para_esquerda and not visitado[linha][coluna-1]:
            fila.append((linha, coluna-1, dist+1))
        if coluna < 8 and tabuleiro[linha][coluna].pode_mover_para_direita and not visitado[linha][coluna+1]:
            fila.append((linha, coluna+1, dist+1))
    return 99  # No path (should not happen)

def calcular_utilidade(estado, jogador, tabuleiro=None):
    """
    Calcula a utilidade de um estado do jogo para o Minimax de forma estratégica.

    A utilidade é calculada com base em dois fatores principais:
    1.  **Diferença de Caminho (Peso 2.5):** O fator mais importante. Incentiva a IA a
        priorizar o bloqueio do oponente, pois aumentar o caminho dele em 2 casas
        (pontuação +5.0) é muito mais valioso do que avançar o próprio peão em 1 casa
        (pontuação +2.5).
    2.  **Diferença de Paredes (Peso 0.1):** Um fator secundário usado para desempate,
        incentivando a IA a ser econômica com suas paredes.

    Args:
        estado (tuple): (pos_j1, pos_j2, paredes_j1, paredes_j2).
        jogador (str): O jogador para o qual a utilidade está sendo calculada ('J1' ou 'J2').
        tabuleiro: O estado atual do tabuleiro de jogo.

    Returns:
        float: O valor de utilidade calculado para o estado do jogo.
    """
    posicao_j1, posicao_j2, paredes_j1, paredes_j2 = estado
    if tabuleiro is None:
        raise ValueError("O tabuleiro deve ser fornecido para o cálculo do caminho mais curto.")

    j1_path = shortest_path_length("J1", posicao_j1, tabuleiro)
    j2_path = shortest_path_length("J2", posicao_j2, tabuleiro)

    # Um peso maior para a diferença de caminhos força a IA a ser mais estratégica.
    peso_caminho = 2.5
    # Um peso menor para as paredes, usado como critério de desempate.
    peso_parede = 0.1

    if jogador == "J1":
        diff_caminho = j2_path - j1_path
        diff_paredes = paredes_j1 - paredes_j2
    else:  # jogador == "J2"
        diff_caminho = j1_path - j2_path
        diff_paredes = paredes_j2 - paredes_j1

    utilidade = (diff_caminho * peso_caminho) + (diff_paredes * peso_parede)

    return utilidade
# Função de utilidade aprimorada para Quoridor: shortest path, wall count, wall penalty, and pawn advancement bonus.

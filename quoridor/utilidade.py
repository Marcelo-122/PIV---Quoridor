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

def calcular_utilidade(estado, jogador, tabuleiro=None, move_info=None):
    """
    estado: (pos_j1, pos_j2, paredes_j1, paredes_j2)
    jogador: 'J1' ou 'J2'
    tabuleiro: estado do tabuleiro
    move_info: dict opcional, usado para penalizar paredes inúteis
    """
    posicao_j1, posicao_j2, paredes_j1, paredes_j2 = estado
    if tabuleiro is None:
        raise ValueError("Tabuleiro must be provided for shortest path calculation.")
    j1_path = shortest_path_length("J1", posicao_j1, tabuleiro)
    j2_path = shortest_path_length("J2", posicao_j2, tabuleiro)

    # Wall count bonus (small weight)
    wall_bonus = (paredes_j1 - paredes_j2) * 0.5 if jogador == "J1" else (paredes_j2 - paredes_j1) * 0.5

    # Penalty for useless wall (if info provided)
    useless_wall_penalty = 0
    if move_info and move_info.get('tipo') == 'wall':
        # move_info must have 'opponent_path_before' and 'opponent_path_after'
        opp_before = move_info.get('opponent_path_before')
        opp_after = move_info.get('opponent_path_after')
        if opp_after is not None and opp_before is not None:
            if opp_after <= opp_before:
                useless_wall_penalty = -2  # Penalize useless wall

    if jogador == "J1":
        return (j2_path - j1_path) + wall_bonus + useless_wall_penalty
    else:
        return (j1_path - j2_path) + wall_bonus + useless_wall_penalty
# Função de utilidade aprimorada para Quoridor: shortest path, wall count, and wall penalty.

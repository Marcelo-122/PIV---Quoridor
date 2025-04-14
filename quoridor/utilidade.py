def calcular_utilidade(estado, jogador):
    posicao_j1, posicao_j2, _, _, paredes_j1, paredes_j2 = estado
    objetivo_j1 = 8
    objetivo_j2 = 0

    if jogador == "J1":
        distancia_jogador = abs(posicao_j1[0] - objetivo_j1)
        distancia_oponente = abs(posicao_j2[0] - objetivo_j2)
        paredes_jogador = paredes_j1
    else:
        distancia_jogador = abs(posicao_j2[0] - objetivo_j2)
        distancia_oponente = abs(posicao_j1[0] - objetivo_j1)
        paredes_jogador = paredes_j2

    return -distancia_jogador + distancia_oponente + 10 * paredes_jogador

import copy
from quoridor.caminho import existe_caminho
from quoridor.utilidade import shortest_path_length

# Representa um movimento: (tipo, valor)
# tipo: 'move' ou 'wall'
# valor: para 'move', direcao ('w', 'a', 's', 'd'); para 'wall', notacao (ex: 'e7h')

DIRECOES = ['w', 'a', 's', 'd']
LINHAS, COLUNAS = 9, 9

# Gera todos os movimentos possíveis para o jogador atual
# turno: 0 (J1), 1 (J2)
def gerar_movimentos_possiveis(jogo, turno):
    movimentos = []
    jogador = 'J1' if turno == 0 else 'J2'
    
    # Movimentos de peão
    for direcao in DIRECOES:
        jogo_copia = copy.deepcopy(jogo)
        if jogo_copia.andar(direcao, turno):
            movimentos.append(('move', direcao))
    
    # Tentativas de colocar parede
    for linha in range(1, LINHAS+1):
        for coluna in range(COLUNAS):
            letra_coluna = chr(ord('a') + coluna)
            for direcao in ['h', 'v']:
                notacao = f"{letra_coluna}{linha}{direcao}"
                jogo_copia = copy.deepcopy(jogo)
                if jogo_copia.colocar_parede(notacao, turno):
                    # Checa se ambos jogadores ainda têm caminho ao objetivo
                    if existe_caminho('J1', jogo_copia.jogadores['J1'][0], jogo_copia.jogadores['J1'][1], jogo_copia.tabuleiro) and \
                       existe_caminho('J2', jogo_copia.jogadores['J2'][0], jogo_copia.jogadores['J2'][1], jogo_copia.tabuleiro):
                        movimentos.append(('wall', notacao))
    return movimentos

# Aplica um movimento ao jogo (muda o estado!)
def aplicar_movimento(jogo, movimento, turno):
    tipo, valor = movimento
    if tipo == 'move':
        jogo.andar(valor, turno)
    elif tipo == 'wall':
        jogo.colocar_parede(valor, turno)
    return jogo

# Cria informações adicionais sobre o movimento para a função de utilidade
def criar_move_info(jogo, movimento, turno):
    tipo, valor = movimento
    move_info = {'tipo': tipo}
    
    if tipo == 'wall':
        # Calcular caminho do oponente antes e depois da parede
        estado_antes = jogo.serializar_estado()
        oponente = 'J2' if turno == 0 else 'J1'
        pos_oponente = estado_antes[1] if oponente == 'J2' else estado_antes[0]
        path_before = shortest_path_length(oponente, pos_oponente, jogo.tabuleiro)
        move_info['opponent_path_before'] = path_before
    elif tipo == 'move':
        # Informações sobre avanço do peão
        estado_antes = jogo.serializar_estado()
        pawn_row_before = estado_antes[0][0] if turno == 0 else estado_antes[1][0]
        move_info['pawn_row_before'] = pawn_row_before
    
    return move_info

# Atualiza informações do movimento após aplicá-lo
def atualizar_move_info(jogo, move_info, turno):
    if move_info['tipo'] == 'wall':
        estado_depois = jogo.serializar_estado()
        oponente = 'J2' if turno == 0 else 'J1'
        pos_oponente = estado_depois[1] if oponente == 'J2' else estado_depois[0]
        path_after = shortest_path_length(oponente, pos_oponente, jogo.tabuleiro)
        move_info['opponent_path_after'] = path_after
    elif move_info['tipo'] == 'move':
        estado_depois = jogo.serializar_estado()
        pawn_row_after = estado_depois[0][0] if turno == 0 else estado_depois[1][0]
        move_info['pawn_row_after'] = pawn_row_after
    
    return move_info

# Minimax com profundidade limitada
def minimax(jogo, profundidade, turno_max, jogador, profundidade_maxima=4):
    # Se o jogo acabou ou se a profundidade é máxima
    if jogo.verificar_vitoria() or profundidade == 0:
        return jogo.calcular_utilidade(jogo.serializar_estado(), jogador)

    if turno_max:  # turno do MAX
        melhor_valor = float("-inf")  # Menos infinito é o menor valor
        for movimento in gerar_movimentos_possiveis(jogo, 0 if jogador == 'J1' else 1):
            jogo_copia = copy.deepcopy(jogo)
            move_info = criar_move_info(jogo_copia, movimento, 0 if jogador == 'J1' else 1)
            aplicar_movimento(jogo_copia, movimento, 0 if jogador == 'J1' else 1)
            move_info = atualizar_move_info(jogo_copia, move_info, 0 if jogador == 'J1' else 1)
            
            utilidade = minimax(
                jogo_copia, profundidade - 1, False, jogador, profundidade_maxima
            )
            
            # Recalcular utilidade com informações de movimento
            utilidade = jogo_copia.calcular_utilidade(
                jogo_copia.serializar_estado(), jogador, move_info=move_info
            )
            
            melhor_valor = max(utilidade, melhor_valor)  # movimento com o maior valor
        return melhor_valor
    else:  # turno no MIN
        pior_valor = float("inf")  # Mais infinito é o maior valor
        oponente = 'J2' if jogador == 'J1' else 'J1'
        for movimento in gerar_movimentos_possiveis(jogo, 0 if oponente == 'J1' else 1):
            jogo_copia = copy.deepcopy(jogo)
            move_info = criar_move_info(jogo_copia, movimento, 0 if oponente == 'J1' else 1)
            aplicar_movimento(jogo_copia, movimento, 0 if oponente == 'J1' else 1)
            move_info = atualizar_move_info(jogo_copia, move_info, 0 if oponente == 'J1' else 1)
            
            utilidade = minimax(
                jogo_copia, profundidade - 1, True, jogador, profundidade_maxima
            )
            
            # Recalcular utilidade com informações de movimento
            utilidade = jogo_copia.calcular_utilidade(
                jogo_copia.serializar_estado(), jogador, move_info=move_info
            )
            
            pior_valor = min(utilidade, pior_valor)  # movimento com o menor valor
        return pior_valor

# Minimax com poda alfa-beta
def minimax_alfabeta(
    jogo,
    profundidade,
    turno_max,
    jogador,
    profundidade_maxima=4,
    alfa=float("-inf"),
    beta=float("inf"),
):
    # Se o jogo acabou ou se a profundidade é máxima
    if jogo.verificar_vitoria() or profundidade == 0:
        return jogo.calcular_utilidade(jogo.serializar_estado(), jogador)

    if turno_max:  # turno do MAX
        valor = float("-inf")
        for movimento in gerar_movimentos_possiveis(jogo, 0 if jogador == 'J1' else 1):
            jogo_copia = copy.deepcopy(jogo)
            move_info = criar_move_info(jogo_copia, movimento, 0 if jogador == 'J1' else 1)
            aplicar_movimento(jogo_copia, movimento, 0 if jogador == 'J1' else 1)
            move_info = atualizar_move_info(jogo_copia, move_info, 0 if jogador == 'J1' else 1)
            
            utilidade = minimax_alfabeta(
                jogo_copia,
                profundidade - 1,
                False,
                jogador,
                profundidade_maxima,
                alfa,
                beta,
            )
            
            # Recalcular utilidade com informações de movimento
            utilidade = jogo_copia.calcular_utilidade(
                jogo_copia.serializar_estado(), jogador, move_info=move_info
            )
            
            valor = max(valor, utilidade)
            alfa = max(alfa, valor)
            if beta <= alfa:
                break  # Poda beta
        return valor
    else:  # turno no MIN
        valor = float("inf")
        oponente = 'J2' if jogador == 'J1' else 'J1'
        for movimento in gerar_movimentos_possiveis(jogo, 0 if oponente == 'J1' else 1):
            jogo_copia = copy.deepcopy(jogo)
            move_info = criar_move_info(jogo_copia, movimento, 0 if oponente == 'J1' else 1)
            aplicar_movimento(jogo_copia, movimento, 0 if oponente == 'J1' else 1)
            move_info = atualizar_move_info(jogo_copia, move_info, 0 if oponente == 'J1' else 1)
            
            utilidade = minimax_alfabeta(
                jogo_copia,
                profundidade - 1,
                True,
                jogador,
                profundidade_maxima,
                alfa,
                beta,
            )
            
            # Recalcular utilidade com informações de movimento
            utilidade = jogo_copia.calcular_utilidade(
                jogo_copia.serializar_estado(), jogador, move_info=move_info
            )
            
            valor = min(valor, utilidade)
            beta = min(beta, valor)
            if beta <= alfa:
                break  # Poda alfa
        return valor

# Encontrar o melhor movimento do computador usando minimax
def melhor_jogada_agente(jogo, turno, profundidade_maxima=4):
    jogador = 'J1' if turno == 0 else 'J2'
    melhor_valor = float("-inf")
    melhor_jogada = None
    
    for movimento in gerar_movimentos_possiveis(jogo, turno):
        jogo_copia = copy.deepcopy(jogo)
        move_info = criar_move_info(jogo_copia, movimento, turno)
        aplicar_movimento(jogo_copia, movimento, turno)
        move_info = atualizar_move_info(jogo_copia, move_info, turno)
        
        utilidade = minimax(
            jogo_copia, profundidade_maxima - 1, False, jogador, profundidade_maxima
        )
        
        # Recalcular utilidade com informações de movimento
        utilidade = jogo_copia.calcular_utilidade(
            jogo_copia.serializar_estado(), jogador, move_info=move_info
        )
        
        if utilidade > melhor_valor:
            melhor_valor = utilidade
            melhor_jogada = movimento
    
    return melhor_jogada

# Encontrar o melhor movimento do computador usando minimax com poda alfa-beta
def melhor_jogada_agente_poda(jogo, turno, profundidade_maxima=4):
    jogador = 'J1' if turno == 0 else 'J2'
    melhor_valor = float("-inf")
    melhor_jogada = None
    alfa = float("-inf")
    beta = float("inf")
    
    for movimento in gerar_movimentos_possiveis(jogo, turno):
        jogo_copia = copy.deepcopy(jogo)
        move_info = criar_move_info(jogo_copia, movimento, turno)
        aplicar_movimento(jogo_copia, movimento, turno)
        move_info = atualizar_move_info(jogo_copia, move_info, turno)
        
        utilidade = minimax_alfabeta(
            jogo_copia, profundidade_maxima - 1, False, jogador, profundidade_maxima, alfa, beta
        )
        
        # Recalcular utilidade com informações de movimento
        utilidade = jogo_copia.calcular_utilidade(
            jogo_copia.serializar_estado(), jogador, move_info=move_info
        )
        
        if utilidade > melhor_valor:
            melhor_valor = utilidade
            melhor_jogada = movimento
        
        alfa = max(alfa, melhor_valor)
    
    return melhor_jogada

# Função para o AI escolher o melhor movimento (usando poda alfa-beta por padrão)
def escolher_movimento_ai(jogo, turno, profundidade=3, usar_poda=True):
    if usar_poda:
        return melhor_jogada_agente_poda(jogo, turno, profundidade)
    else:
        return melhor_jogada_agente(jogo, turno, profundidade)

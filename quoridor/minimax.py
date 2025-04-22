import copy
import time
from quoridor.caminho import existe_caminho
from quoridor.utilidade import shortest_path_length

# Representa um movimento: (tipo, valor)
# tipo: 'move' ou 'wall'
# valor: para 'move', direcao ('w', 'a', 's', 'd'); para 'wall', notacao (ex: 'e7h')

DIRECOES = ['w', 'a', 's', 'd']
LINHAS, COLUNAS = 9, 9

# Tabela de transposição para armazenar estados já calculados
# Formato: {hash_estado: (profundidade, valor, melhor_movimento)}
transposition_table = {}

# Melhores primeiras jogadas para otimização de abertura
# Baseado em análise de jogos de Quoridor
BEST_FIRST_MOVES = {
    'J1': [('move', 's'), ('wall', 'e5h'), ('wall', 'd5h')],  # Movimento para frente ou paredes centrais
    'J2': [('move', 'w'), ('wall', 'e5h'), ('wall', 'd5h')]   # Movimento para frente ou paredes centrais
}

# Função para gerar um hash para o estado do jogo (para a tabela de transposição)
def hash_estado(estado):
    pos_j1, pos_j2, paredes_j1, paredes_j2 = estado
    return hash((pos_j1, pos_j2, paredes_j1, paredes_j2))

# Avaliação rápida de um movimento para ordenação
def avaliar_movimento_rapido(jogo, movimento, turno, jogador):
    tipo, valor = movimento
    
    # Movimentos de peão são avaliados pela distância ao objetivo
    if tipo == 'move':
        jogo_copia = copy.deepcopy(jogo)
        aplicar_movimento(jogo_copia, movimento, turno)
        estado = jogo_copia.serializar_estado()
        pos = estado[0] if jogador == 'J1' else estado[1]
        
        # Distância ao objetivo (linha 8 para J1, linha 0 para J2)
        objetivo = 8 if jogador == 'J1' else 0
        distancia = abs(pos[0] - objetivo)
        
        # Quanto menor a distância, melhor o movimento
        return -distancia
    
    # Paredes são avaliadas pelo impacto no caminho do oponente
    elif tipo == 'wall':
        jogo_copia = copy.deepcopy(jogo)
        estado_antes = jogo_copia.serializar_estado()
        oponente = 'J2' if jogador == 'J1' else 'J1'
        pos_oponente = estado_antes[1] if oponente == 'J2' else estado_antes[0]
        caminho_antes = shortest_path_length(oponente, pos_oponente, jogo_copia.tabuleiro)
        
        aplicar_movimento(jogo_copia, movimento, turno)
        estado_depois = jogo_copia.serializar_estado()
        pos_oponente_depois = estado_depois[1] if oponente == 'J2' else estado_depois[0]
        caminho_depois = shortest_path_length(oponente, pos_oponente_depois, jogo_copia.tabuleiro)
        
        # Quanto maior o aumento no caminho do oponente, melhor a parede
        return caminho_depois - caminho_antes
    
    return 0

# Gera todos os movimentos possíveis para o jogador atual com ordenação
# turno: 0 (J1), 1 (J2)
def gerar_movimentos_possiveis(jogo, turno, ordenar=True):
    movimentos = []
    jogador = 'J1' if turno == 0 else 'J2'
    
    # Verifica se é a primeira jogada e usa movimentos otimizados de abertura
    if len(transposition_table) < 2:  # Aproximação para primeira jogada
        posicao_inicial_j1 = (0, 4)
        posicao_inicial_j2 = (8, 4)
        
        # Se os jogadores estão nas posições iniciais, use movimentos de abertura
        if jogo.jogadores['J1'] == posicao_inicial_j1 and jogo.jogadores['J2'] == posicao_inicial_j2:
            print(f"Usando movimentos otimizados de abertura para {jogador}")
            return BEST_FIRST_MOVES[jogador]
    
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
    
    # Ordena os movimentos se solicitado
    if ordenar and movimentos:
        # Avalia e ordena os movimentos (melhores primeiro)
        movimentos.sort(key=lambda m: avaliar_movimento_rapido(jogo, m, turno, jogador), reverse=True)
    
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

# Minimax com profundidade limitada e tabela de transposição
def minimax(jogo, profundidade, turno_max, jogador, profundidade_maxima=4):
    # Verifica a tabela de transposição
    estado = jogo.serializar_estado()
    estado_hash = hash_estado(estado)
    
    if estado_hash in transposition_table:
        prof_armazenada, valor, _ = transposition_table[estado_hash]
        if prof_armazenada >= profundidade:
            return valor
    
    # Se o jogo acabou ou se a profundidade é máxima
    if jogo.verificar_vitoria() or profundidade == 0:
        valor = jogo.calcular_utilidade(estado, jogador)
        transposition_table[estado_hash] = (profundidade, valor, None)
        return valor

    melhor_movimento = None
    
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
            
            if utilidade > melhor_valor:
                melhor_valor = utilidade
                melhor_movimento = movimento
        
        # Armazena na tabela de transposição
        transposition_table[estado_hash] = (profundidade, melhor_valor, melhor_movimento)
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
            
            if utilidade < pior_valor:
                pior_valor = utilidade
                melhor_movimento = movimento
        
        # Armazena na tabela de transposição
        transposition_table[estado_hash] = (profundidade, pior_valor, melhor_movimento)
        return pior_valor

# Minimax com poda alfa-beta e tabela de transposição
def minimax_alfabeta(
    jogo,
    profundidade,
    turno_max,
    jogador,
    profundidade_maxima=4,
    alfa=float("-inf"),
    beta=float("inf"),
):
    # Verifica a tabela de transposição
    estado = jogo.serializar_estado()
    estado_hash = hash_estado(estado)
    
    if estado_hash in transposition_table:
        prof_armazenada, valor, _ = transposition_table[estado_hash]
        if prof_armazenada >= profundidade:
            return valor
    
    # Se o jogo acabou ou se a profundidade é máxima
    if jogo.verificar_vitoria() or profundidade == 0:
        valor = jogo.calcular_utilidade(estado, jogador)
        transposition_table[estado_hash] = (profundidade, valor, None)
        return valor

    melhor_movimento = None
    
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
            
            if utilidade > valor:
                valor = utilidade
                melhor_movimento = movimento
                
            alfa = max(alfa, valor)
            if beta <= alfa:
                break  # Poda beta
        
        # Armazena na tabela de transposição
        transposition_table[estado_hash] = (profundidade, valor, melhor_movimento)
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
            
            if utilidade < valor:
                valor = utilidade
                melhor_movimento = movimento
                
            beta = min(beta, valor)
            if beta <= alfa:
                break  # Poda alfa
        
        # Armazena na tabela de transposição
        transposition_table[estado_hash] = (profundidade, valor, melhor_movimento)
        return valor

# Implementação de aprofundamento iterativo (iterative deepening)
def iterative_deepening(jogo, turno, tempo_limite=2.0, profundidade_maxima=6, usar_poda=True):
    """
    Realiza busca com aprofundamento iterativo até atingir o tempo limite ou a profundidade máxima.
    
    Args:
        jogo: Estado atual do jogo
        turno: Turno atual (0 para J1, 1 para J2)
        tempo_limite: Tempo máximo em segundos para a busca
        profundidade_maxima: Profundidade máxima de busca
        usar_poda: Se True, usa minimax com poda alfa-beta; se False, usa minimax padrão
    
    Returns:
        Melhor movimento encontrado até o momento
    """
    jogador = 'J1' if turno == 0 else 'J2'
    melhor_jogada_global = None
    tempo_inicio = time.time()
    
    # Limpar a tabela de transposição para cada nova busca
    transposition_table.clear()
    
    # Verifica se é a primeira jogada e usa movimentos otimizados de abertura
    posicao_inicial_j1 = (0, 4)
    posicao_inicial_j2 = (8, 4)
    if jogo.jogadores['J1'] == posicao_inicial_j1 and jogo.jogadores['J2'] == posicao_inicial_j2:
        print(f"Usando movimentos otimizados de abertura para {jogador}")
        return BEST_FIRST_MOVES[jogador][0]  # Retorna o primeiro movimento da lista de melhores aberturas
    
    # Começa com profundidade 1 e vai aumentando
    for profundidade in range(1, profundidade_maxima + 1):
        # Verifica se ainda há tempo disponível
        if time.time() - tempo_inicio > tempo_limite:
            print(f"Tempo limite atingido na profundidade {profundidade-1}")
            break
        
        print(f"Buscando na profundidade {profundidade}...")
        
        # Escolhe a função de busca apropriada
        if usar_poda:
            melhor_jogada, valor = melhor_jogada_agente_poda_com_valor(jogo, turno, profundidade)
        else:
            melhor_jogada, valor = melhor_jogada_agente_com_valor(jogo, turno, profundidade)
        
        # Atualiza o melhor movimento global
        if melhor_jogada is not None:
            melhor_jogada_global = melhor_jogada
            print(f"Profundidade {profundidade}: melhor movimento = {melhor_jogada}, valor = {valor:.2f}")
    
    tempo_total = time.time() - tempo_inicio
    print(f"Busca concluída em {tempo_total:.2f} segundos")
    print(f"Tamanho da tabela de transposição: {len(transposition_table)} estados")
    
    return melhor_jogada_global

# Encontrar o melhor movimento do computador usando minimax (retorna também o valor)
def melhor_jogada_agente_com_valor(jogo, turno, profundidade_maxima=4):
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
    
    return melhor_jogada, melhor_valor

# Encontrar o melhor movimento do computador usando minimax
def melhor_jogada_agente(jogo, turno, profundidade_maxima=4):
    melhor_jogada, _ = melhor_jogada_agente_com_valor(jogo, turno, profundidade_maxima)
    return melhor_jogada

# Encontrar o melhor movimento do computador usando minimax com poda alfa-beta (retorna também o valor)
def melhor_jogada_agente_poda_com_valor(jogo, turno, profundidade_maxima=4):
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
    
    return melhor_jogada, melhor_valor

# Encontrar o melhor movimento do computador usando minimax com poda alfa-beta
def melhor_jogada_agente_poda(jogo, turno, profundidade_maxima=4):
    melhor_jogada, _ = melhor_jogada_agente_poda_com_valor(jogo, turno, profundidade_maxima)
    return melhor_jogada

# Função para o AI escolher o melhor movimento
def escolher_movimento_ai(jogo, turno, profundidade=3, usar_poda=True, usar_iterative_deepening=True, tempo_limite=1.5):
    """
    Escolhe o melhor movimento para o AI usando diferentes estratégias de busca.
    
    Args:
        jogo: Estado atual do jogo
        turno: Turno atual (0 para J1, 1 para J2)
        profundidade: Profundidade máxima de busca se não usar iterative deepening
        usar_poda: Se True, usa minimax com poda alfa-beta; se False, usa minimax padrão
        usar_iterative_deepening: Se True, usa aprofundamento iterativo com limite de tempo
        tempo_limite: Tempo máximo em segundos para a busca com iterative deepening
    
    Returns:
        Melhor movimento encontrado
    """
    # Documentação sobre a profundidade ideal
    # Profundidade 3-4 é um bom equilíbrio entre tempo de computação e qualidade da jogada
    # Com a poda alfa-beta e a tabela de transposição, podemos ir até profundidade 5-6 em tempo razoável
    # Iterative deepening permite encontrar a melhor jogada possível dentro do tempo disponível
    
    if usar_iterative_deepening:
        return iterative_deepening(jogo, turno, tempo_limite, profundidade_maxima=6, usar_poda=usar_poda)
    elif usar_poda:
        return melhor_jogada_agente_poda(jogo, turno, profundidade)
    else:
        return melhor_jogada_agente(jogo, turno, profundidade)

import copy
from quoridor.caminho import existe_caminho
from quoridor.utilidade import shortest_path_length

# Representa um movimento: (tipo, valor)
# tipo: 'move' ou 'wall'
# valor: para 'move', direcao ('w', 'a', 's', 'd'); para 'wall', notacao (ex: 'e7h')

DIRECOES = ['w', 'a', 's', 'd']
LINHAS, COLUNAS = 9, 9

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
def gerar_movimentos_possiveis(jogo, turno, ordenar=True, transposition_table=None):
    movimentos = []
    jogador = 'J1' if turno == 0 else 'J2'
    
    # Verifica se é a primeira jogada e usa movimentos otimizados de abertura
    if transposition_table is not None and len(transposition_table) < 2:  # Aproximação para primeira jogada
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

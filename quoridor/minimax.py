import copy
from quoridor.caminho import existe_caminho

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

# Minimax simples com profundidade limitada
def minimax(jogo, profundidade, maximizando, turno):
    if profundidade == 0 or jogo.verificar_vitoria():
        jogador = 'J1' if maximizando else 'J2'
        return jogo.calcular_utilidade(jogo.serializar_estado(), jogador), None
    
    movimentos = gerar_movimentos_possiveis(jogo, turno)
    melhor_mov = None
    if maximizando:
        max_eval = float('-inf')
        for mov in movimentos:
            jogo_copia = copy.deepcopy(jogo)
            move_info = None
            if mov[0] == 'wall':
                # Calculate opponent path before and after wall placement
                estado_antes = jogo_copia.serializar_estado()
                oponente = 'J2' if turno == 0 else 'J1'
                pos_oponente = estado_antes[1] if oponente == 'J2' else estado_antes[0]
                path_before = jogo_copia.calcular_utilidade(estado_antes, oponente)
                aplicar_movimento(jogo_copia, mov, turno)
                estado_depois = jogo_copia.serializar_estado()
                pos_oponente_after = estado_depois[1] if oponente == 'J2' else estado_depois[0]
                from quoridor.utilidade import shortest_path_length
                path_after = shortest_path_length(oponente, pos_oponente_after, jogo_copia.tabuleiro)
                move_info = {
                    'tipo': 'wall',
                    'opponent_path_before': path_before,
                    'opponent_path_after': path_after
                }
            else:
                aplicar_movimento(jogo_copia, mov, turno)
            eval, _ = minimax(jogo_copia, profundidade-1, False, 1-turno)
            # Re-evaluate utility with move_info for wall penalty
            if mov[0] == 'wall':
                jogador = 'J1' if maximizando else 'J2'
                eval = jogo_copia.calcular_utilidade(jogo_copia.serializar_estado(), jogador, move_info=move_info)
            if eval > max_eval:
                max_eval = eval
                melhor_mov = mov
        return max_eval, melhor_mov
    else:
        min_eval = float('inf')
        for mov in movimentos:
            jogo_copia = copy.deepcopy(jogo)
            move_info = None
            if mov[0] == 'wall':
                estado_antes = jogo_copia.serializar_estado()
                oponente = 'J2' if turno == 0 else 'J1'
                pos_oponente = estado_antes[1] if oponente == 'J2' else estado_antes[0]
                path_before = jogo_copia.calcular_utilidade(estado_antes, oponente)
                aplicar_movimento(jogo_copia, mov, turno)
                estado_depois = jogo_copia.serializar_estado()
                pos_oponente_after = estado_depois[1] if oponente == 'J2' else estado_depois[0]
                from quoridor.utilidade import shortest_path_length
                path_after = shortest_path_length(oponente, pos_oponente_after, jogo_copia.tabuleiro)
                move_info = {
                    'tipo': 'wall',
                    'opponent_path_before': path_before,
                    'opponent_path_after': path_after
                }
            else:
                aplicar_movimento(jogo_copia, mov, turno)
            eval, _ = minimax(jogo_copia, profundidade-1, True, 1-turno)
            if mov[0] == 'wall':
                jogador = 'J1' if not maximizando else 'J2'
                eval = jogo_copia.calcular_utilidade(jogo_copia.serializar_estado(), jogador, move_info=move_info)
            if eval < min_eval:
                min_eval = eval
                melhor_mov = mov
        return min_eval, melhor_mov

# Função para o AI escolher o melhor movimento
def escolher_movimento_ai(jogo, turno, profundidade=2):
    _, mov = minimax(jogo, profundidade, True, turno)
    return mov

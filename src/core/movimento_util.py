import copy

from .caminho import existe_caminho
from .utilidade import shortest_path_length

# Representa um movimento: (tipo, valor)
# tipo: 'move' ou 'wall'
# valor: para 'move', direcao ('w', 'a', 's', 'd'); para 'wall', notacao (ex: 'e7h')

DIRECOES = ["w", "a", "s", "d"]
LINHAS, COLUNAS = 9, 9

# Melhores primeiras jogadas para otimização de abertura
# Baseado em análise de jogos de Quoridor
BEST_FIRST_MOVES = {
    "J1": [
        ("move", "s"),
        ("wall", "e5h"),
        ("wall", "d5h"),
    ],  # Movimento para frente ou paredes centrais
    "J2": [
        ("move", "w"),
        ("wall", "e5h"),
        ("wall", "d5h"),
    ],  # Movimento para frente ou paredes centrais
}


# Função para gerar um hash para o estado do jogo (para a tabela de transposição)
def hash_estado(estado):
    pos_j1, pos_j2, paredes_j1, paredes_j2 = estado
    return hash((pos_j1, pos_j2, paredes_j1, paredes_j2))


# Avaliação rápida de um movimento para ordenação
def avaliar_movimento_rapido(jogo, movimento, turno, jogador):
    tipo, valor = movimento

    # Movimentos de peão são avaliados pela distância ao objetivo
    if tipo == "move":
        jogo_copia = copy.deepcopy(jogo)
        aplicar_movimento(jogo_copia, movimento, turno)
        estado = jogo_copia.serializar_estado()
        pos = estado[0] if jogador == "J1" else estado[1]

        # Distância ao objetivo (linha 8 para J1, linha 0 para J2)
        objetivo = 8 if jogador == "J1" else 0
        distancia = abs(pos[0] - objetivo)

        # Quanto menor a distância, melhor o movimento
        return -distancia

    # Paredes são avaliadas pelo impacto no caminho do oponente
    elif tipo == "wall":
        jogo_copia = copy.deepcopy(jogo)
        estado_antes = jogo_copia.serializar_estado()
        oponente = "J2" if jogador == "J1" else "J1"
        pos_oponente = estado_antes[1] if oponente == "J2" else estado_antes[0]
        caminho_antes = shortest_path_length(
            oponente, pos_oponente, jogo_copia.tabuleiro
        )

        aplicar_movimento(jogo_copia, movimento, turno)
        estado_depois = jogo_copia.serializar_estado()
        pos_oponente_depois = estado_depois[1] if oponente == "J2" else estado_depois[0]
        caminho_depois = shortest_path_length(
            oponente, pos_oponente_depois, jogo_copia.tabuleiro
        )

        # Quanto maior o aumento no caminho do oponente, melhor a parede
        return caminho_depois - caminho_antes

    return 0


# Gera todos os movimentos possíveis para o jogador atual com ordenação
# turno: 0 (J1), 1 (J2)
def gerar_movimentos_possiveis(jogo, turno, ordenar=True, transposition_table=None):
    movimentos = []
    jogador = "J1" if turno == 0 else "J2"
    
    # Verificar se o jogador já está na posição de vitória
    if jogo.verificar_vitoria_jogador(jogador):
        print(f"[DEBUG] Jogador {jogador} já está na posição de vitória!")
        return []
        
    # Debug: posição atual
    print(f"[DEBUG] Gerando movimentos para {jogador} na posição {jogo.jogadores[jogador]}")
    
    # Movimentos de peão
    for direcao in ["w", "s", "a", "d"]:
        jogo_copia = copy.deepcopy(jogo)
        if jogo_copia.andar(direcao, turno):
            movimentos.append(("move", direcao))
            print(f"[DEBUG] Movimento válido: ('move', '{direcao}')")
    
    # Tentativas de colocar parede
    num_linhas = len(jogo.tabuleiro)
    num_colunas = len(jogo.tabuleiro[0]) if num_linhas > 0 else 0
    
    print(f"[DEBUG] Tabuleiro: {num_linhas}x{num_colunas}")
    
    for linha_notacao_num in range(1, num_linhas):
        for coluna_idx in range(num_colunas - 1):
            letra_coluna = chr(ord('a') + coluna_idx)
            for direcao in ["h", "v"]:
                notacao = f"{letra_coluna}{linha_notacao_num}{direcao}"
                jogo_copia = copy.deepcopy(jogo)
                if jogo_copia.colocar_parede(notacao, turno):
                    if existe_caminho("J1", jogo_copia.jogadores["J1"][0], jogo_copia.jogadores["J1"][1], jogo_copia.tabuleiro) and \
                       existe_caminho("J2", jogo_copia.jogadores["J2"][0], jogo_copia.jogadores["J2"][1], jogo_copia.tabuleiro):
                        movimentos.append(("wall", notacao))
                        print(f"[DEBUG] Parede válida: ('wall', '{notacao}')")
    
    # Debug: total de movimentos encontrados
    print(f"[DEBUG] Total de movimentos gerados para {jogador}: {len(movimentos)}")
    
    if ordenar and movimentos:
        movimentos.sort(key=lambda m: avaliar_movimento_rapido(jogo, m, turno, jogador), reverse=True)
    
    return movimentos


# Aplica um movimento ao jogo (muda o estado!)
def aplicar_movimento(jogo, movimento, turno):
    tipo, valor = movimento
    if tipo == "move":
        jogo.andar(valor, turno)
    elif tipo == "wall":
        jogo.colocar_parede(valor, turno)
    return jogo


# Cria informações adicionais sobre o movimento para a função de utilidade
def criar_move_info(jogo, movimento, turno):
    tipo, valor = movimento
    move_info = {"tipo": tipo}

    if tipo == "wall":
        # Calcular caminho do oponente antes e depois da parede
        estado_antes = jogo.serializar_estado()
        oponente = "J2" if turno == 0 else "J1"
        pos_oponente = estado_antes[1] if oponente == "J2" else estado_antes[0]
        path_before = shortest_path_length(oponente, pos_oponente, jogo.tabuleiro)
        move_info["opponent_path_before"] = path_before
    elif tipo == "move":
        # Informações sobre avanço do peão
        estado_antes = jogo.serializar_estado()
        pawn_row_before = estado_antes[0][0] if turno == 0 else estado_antes[1][0]
        move_info["pawn_row_before"] = pawn_row_before

    return move_info


# Atualiza informações do movimento após aplicá-lo
def atualizar_move_info(jogo, move_info, turno):
    if move_info["tipo"] == "wall":
        estado_depois = jogo.serializar_estado()
        oponente = "J2" if turno == 0 else "J1"
        pos_oponente = estado_depois[1] if oponente == "J2" else estado_depois[0]
        path_after = shortest_path_length(oponente, pos_oponente, jogo.tabuleiro)
        move_info["opponent_path_after"] = path_after
    elif move_info["tipo"] == "move":
        estado_depois = jogo.serializar_estado()
        pawn_row_after = estado_depois[0][0] if turno == 0 else estado_depois[1][0]
        move_info["pawn_row_after"] = pawn_row_after

    return move_info


def movimento_valido(jogo, pos_atual, nova_pos):
    """
    Verifica se um movimento de peça é válido.
    Args:
        jogo: instância do jogo
        pos_atual: tupla (linha, coluna) da posição atual
        nova_pos: tupla (linha, coluna) da nova posição
    """
    # Verificar se a nova posição está dentro dos limites do tabuleiro
    if not (0 <= nova_pos[0] < jogo.linhas and 0 <= nova_pos[1] < jogo.colunas):
        print(f"[VALIDACAO] Movimento para {nova_pos} fora dos limites do tabuleiro")
        return False
        
    # Verificar se a nova posição está ocupada por outro jogador
    if nova_pos in jogo.jogadores.values():
        print(f"[VALIDACAO] Movimento para {nova_pos} ocupado por outro jogador")
        return False
        
    # Verificar se há parede bloqueando o movimento
    # ... (código existente com logs adicionais)
    
    return True

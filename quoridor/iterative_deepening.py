import time
import copy
from quoridor.movimento_util import gerar_movimentos_possiveis, criar_move_info, aplicar_movimento, atualizar_move_info, BEST_FIRST_MOVES

# Implementação de aprofundamento iterativo (iterative deepening)
def iterative_deepening(jogo, turno, minimax_alfabeta_func, transposition_table, tempo_limite=2.0, profundidade_maxima=6):
    """
    Realiza busca com aprofundamento iterativo até atingir o tempo limite ou a profundidade máxima.
    
    Args:
        jogo: Estado atual do jogo
        turno: Turno atual (0 para J1, 1 para J2)
        minimax_alfabeta_func: Função minimax com poda alfa-beta a ser usada
        transposition_table: Tabela de transposição para armazenar estados já calculados
        tempo_limite: Tempo máximo em segundos para a busca
        profundidade_maxima: Profundidade máxima de busca
    
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
        
        # Busca o melhor movimento para a profundidade atual
        melhor_jogada, valor = melhor_jogada_agente_poda_com_valor(
            jogo, turno, profundidade, minimax_alfabeta_func, transposition_table
        )
        
        # Atualiza o melhor movimento global
        if melhor_jogada is not None:
            melhor_jogada_global = melhor_jogada
            print(f"Profundidade {profundidade}: melhor movimento = {melhor_jogada}, valor = {valor:.2f}")
    
    tempo_total = time.time() - tempo_inicio
    print(f"Busca concluída em {tempo_total:.2f} segundos")
    print(f"Tamanho da tabela de transposição: {len(transposition_table)} estados")
    
    return melhor_jogada_global

# Encontrar o melhor movimento do computador usando minimax com poda alfa-beta (retorna também o valor)
def melhor_jogada_agente_poda_com_valor(jogo, turno, profundidade_maxima, minimax_alfabeta_func, transposition_table):
    jogador = 'J1' if turno == 0 else 'J2'
    melhor_valor = float("-inf")
    melhor_jogada = None
    alfa = float("-inf")
    beta = float("inf")
    
    for movimento in gerar_movimentos_possiveis(jogo, turno, transposition_table=transposition_table):
        jogo_copia = copy.deepcopy(jogo)
        move_info = criar_move_info(jogo_copia, movimento, turno)
        aplicar_movimento(jogo_copia, movimento, turno)
        move_info = atualizar_move_info(jogo_copia, move_info, turno)
        
        utilidade = minimax_alfabeta_func(
            jogo_copia, profundidade_maxima - 1, False, jogador, profundidade_maxima, alfa, beta, transposition_table
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

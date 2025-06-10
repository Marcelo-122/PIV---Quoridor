import time
from src.core.movimento_util import gerar_movimentos_possiveis, criar_move_info, aplicar_movimento, atualizar_move_info, hash_estado, BEST_FIRST_MOVES
from .minimax_core import melhor_jogada_agente_poda_com_valor

# Tabela de transposição para armazenar estados já calculados
# Formato: {hash_estado: (profundidade, valor, melhor_movimento)}
transposition_table = {}

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
        movimento_otimizado = BEST_FIRST_MOVES[jogador][0]
        movimentos_legais = gerar_movimentos_possiveis(jogo, turno, ordenar=False) # Não precisa ordenar aqui

        if movimento_otimizado in movimentos_legais:
            print(f"Usando movimento otimizado de abertura para {jogador}: {movimento_otimizado}")
            return movimento_otimizado
        else:
            print(f"Movimento otimizado {movimento_otimizado} bloqueado. Buscando a melhor jogada..." )
    
    # Começa com profundidade 1 e vai aumentando
    for profundidade in range(1, profundidade_maxima + 1):
        # Verifica se ainda há tempo disponível
        if time.time() - tempo_inicio > tempo_limite:
            print(f"Tempo limite atingido na profundidade {profundidade-1}")
            break
        
        print(f"Buscando na profundidade {profundidade}...")
        
        # Busca o melhor movimento para a profundidade atual
        melhor_jogada, valor = melhor_jogada_agente_poda(jogo, turno, profundidade)
        
        # Atualiza o melhor movimento global
        if melhor_jogada is not None:
            melhor_jogada_global = melhor_jogada
            print(f"Profundidade {profundidade}: melhor movimento = {melhor_jogada}, valor = {valor:.2f}")
    
    tempo_total = time.time() - tempo_inicio
    print(f"Busca concluída em {tempo_total:.2f} segundos")
    print(f"Tamanho da tabela de transposição: {len(transposition_table)} estados")
    
    return melhor_jogada_global

# Encontrar o melhor movimento do computador usando minimax com poda alfa-beta
def melhor_jogada_agente_poda(jogo, turno, profundidade_maxima=4):
    """
    Encontra o melhor movimento para o jogador atual usando minimax com poda alfa-beta.
    
    Args:
        jogo: Estado atual do jogo
        turno: Turno atual (0 para J1, 1 para J2)
        profundidade_maxima: Profundidade máxima de busca
    
    Returns:
        Tupla (melhor_jogada, valor) com o melhor movimento encontrado e seu valor
    """
    return melhor_jogada_agente_poda_com_valor(
        jogo, 
        turno, 
        profundidade_maxima, 
        transposition_table,
        gerar_movimentos_possiveis,
        criar_move_info,
        aplicar_movimento,
        atualizar_move_info,
        hash_estado
    )

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
    else:
        melhor_jogada, _ = melhor_jogada_agente_poda(jogo, turno, profundidade)
        return melhor_jogada

import time
from src.core.game import JogoQuoridor
from src.core.caminho import existe_caminho
from src.ai.minimax import escolher_movimento_ai

# Configurações da IA
USAR_PODA_ALFABETA = True  # Usar poda alfa-beta para melhor desempenho
USAR_ITERATIVE_DEEPENING = True  # Usar aprofundamento iterativo para melhor qualidade
TEMPO_LIMITE_AI = 2.0  # Tempo limite em segundos para a busca da IA
PROFUNDIDADE_PADRAO = 4  # Profundidade padrão se não usar iterative deepening

# Início do jogo
jogo = JogoQuoridor()
turno = 0  # 0 = Jogador 1, 1 = Jogador 2
jogo_terminado = False

print("=== Quoridor com IA Minimax ===")
print("Jogador 1 (humano) vs Jogador 2 (IA)")
print("Movimentos: w (cima), a (esquerda), s (baixo), d (direita)")
print("Paredes: notacao alfanumérica (ex: e5h para parede horizontal na posição e5)")
print("=================================\n")

while not jogo_terminado:
    jogo.imprimir_tabuleiro()
    
    jogador_nome = "Jogador 1" if turno == 0 else "Jogador 2 (IA)"
    print(f"Turno atual: {jogador_nome}")

    if turno == 1:
        print("IA está pensando...")
        inicio = time.time()
        movimento = escolher_movimento_ai(
            jogo, 
            turno, 
            profundidade=PROFUNDIDADE_PADRAO, 
            usar_poda=USAR_PODA_ALFABETA,
            usar_iterative_deepening=USAR_ITERATIVE_DEEPENING,
            tempo_limite=TEMPO_LIMITE_AI
        )
        tempo_total = time.time() - inicio
        
        if movimento is None:
            print("IA não encontrou movimento válido. Fim de jogo.")
            break
            
        tipo, valor = movimento
        if tipo == 'move':
            direcoes = {'w': 'cima', 'a': 'esquerda', 's': 'baixo', 'd': 'direita'}
            direcao_texto = direcoes.get(valor, valor)
            jogo.andar(valor, turno)
            print(f"IA moveu para {direcao_texto} ({valor})")
        elif tipo == 'wall':
            jogo.colocar_parede(valor, turno)
            print(f"IA colocou parede na posição {valor}")
            
        print(f"Tempo de decisão: {tempo_total:.2f} segundos")
    else:
        print("\nOpções: ")
        print("1 - Colocar Parede")
        print("2 - Mover Peão")
        tipo_jogada = input("Escolha sua ação (1 ou 2): ")
        
        if tipo_jogada == "1":
            parede_input = input("Digite a posição da parede (ex: e7h): ")
            if not jogo.colocar_parede(parede_input, turno):
                if not existe_caminho('J1', jogo.jogadores['J1'][0], jogo.jogadores['J1'][1], jogo.tabuleiro):
                    print("Movimento inválido: J1 ficaria preso.")
                    continue  
        elif tipo_jogada == "2":
            movimento_input = input("Digite o movimento (ex: w, a, s, d): ").lower()
            if movimento_input not in ['w', 'a', 's', 'd']:
                print("Entrada inválida. Movimento deve ser 'w', 'a', 's' ou 'd'.")
                continue
            if not jogo.andar(movimento_input, turno):
                if not existe_caminho('J2', jogo.jogadores['J2'][0], jogo.jogadores['J2'][1], jogo.tabuleiro):
                    print("Movimento inválido: J2 ficaria preso.")
                    continue  
        else:
            print("Entrada inválida. Escolha 1 (Parede) ou 2 (Andar).")
            continue

    if jogo.verificar_vitoria():
        jogo_terminado = True
        
    print(jogo.calcular_utilidade(jogo.serializar_estado(),"J1"))
    print(jogo.calcular_utilidade(jogo.serializar_estado(),"J2"))

    turno = (turno + 1) % 2
import datetime
import os
import sys

from src.ai import minimax as minimax_logic
from src.ai.dqn_agent import AgenteDQN
from src.ai.dqn_config_acoes import TAMANHO_ESTADO, TOTAL_ACOES
from src.core.game import JogoQuoridor
from src.core.utilidade import shortest_path_length

# Garante que o diretório raiz do projeto esteja no sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Configurações e Hiperparâmetros ---
NUM_EPISODIOS = 110  # Reduzido para teste rápido coloque 10, para a apresentaçao vai ser 1000
MODO_TREINAMENTO = "self_play"  # Opções: 'self_play' ou 'vs_minimax' para o treinamento

# Parâmetros para AgenteDQN
NUM_ACOES = TOTAL_ACOES  # 132 ações possíveis
LEARNING_RATE = 0.001
GAMMA = 0.99
EPSILON_INICIAL = 1.0
MIN_EPSILON = 0.01
EPSILON_DECAY = 0.9995  # Ajustar conforme necessário para decair mais lentamente/rápido
CAPACIDADE_BUFFER = 100000
BATCH_SIZE = 64
FREQUENCIA_ATUALIZACAO_ALVO = (
    100  # A cada quantos passos de aprendizado atualiza a rede alvo
)

# Parâmetros para AgenteMinimax (se MODO_TREINAMENTO == 'vs_minimax')
PROFUNDIDADE_MINIMAX = 1  # Ajuste conforme a dificuldade desejada para o oponente (Por algum motivo 1 é muito forte contra uma DQN iniciante)

# Salvamento de Modelo
PASTA_MODELOS = "saved_models_dqn"
NOME_BASE_MODELO = "quoridor_dqn"
SALVAR_MODELO_A_CADA_N_EPISODIOS = 500
CARREGAR_MODELO_J1 = False
CAMINHO_MODELO_J1_CARREGAR = f"{PASTA_MODELOS}/modelo_j1_episodio_XXXX.h5"
CARREGAR_MODELO_J2_SELFPLAY = False  # Se MODO_TREINAMENTO == 'self_play'
CAMINHO_MODELO_J2_CARREGAR = f"{PASTA_MODELOS}/modelo_j2_episodio_XXXX.h5"

MAX_MOVIMENTOS_POR_EPISODIO = 250  # Para evitar jogos excessivamente longos

PENALIDADE_REPETICAO = -5.0  # Penalidade por movimento repetitivo sem progresso
JANELA_HISTORICO_REPETICAO = 5  # Quantos dos últimos (pos_j1, pos_j2, meu_caminho) lembrar


# --- Wrapper para o Agente Minimax ---
class AgenteMinimaxWrapper:
    """Classe wrapper para adaptar a interface do módulo minimax à esperada pelo loop de treinamento."""

    def __init__(self, profundidade_max, jogador_idx):
        self.profundidade = profundidade_max
        self.jogador_idx = jogador_idx
        # Para um oponente de dificuldade fixa, é melhor não usar aprofundamento iterativo com tempo limite
        self.usar_iterative_deepening = False

    def escolher_jogada(self, jogo, turno):
        """Chama a função principal do módulo minimax para obter a jogada."""
        # A função em minimax.py é 'escolher_movimento_ai'
        return minimax_logic.escolher_movimento_ai(
            jogo,
            turno,
            profundidade=self.profundidade,
            usar_iterative_deepening=self.usar_iterative_deepening,
        )


def treinar():
    print("Iniciando treinamento DQN para Quoridor.", flush=True)
    print(f"Modo de Treinamento: {MODO_TREINAMENTO}")
    print(f"Número de Episódios: {NUM_EPISODIOS}")

    # Cria a pasta para salvar modelos, se não existir
    os.makedirs(PASTA_MODELOS, exist_ok=True)

    # Inicializa o jogo
    jogo = JogoQuoridor()

    # Inicializa Agente DQN para Jogador 1
    agente_dqn_j1 = AgenteDQN(
        tamanho_estado=TAMANHO_ESTADO,
        tamanho_acao=NUM_ACOES,
        taxa_aprendizado=LEARNING_RATE,
        gama=GAMMA,
        epsilon=EPSILON_INICIAL,
        epsilon_min=MIN_EPSILON,
        epsilon_decay=EPSILON_DECAY,
        capacidade_buffer=CAPACIDADE_BUFFER,
        tamanho_lote=BATCH_SIZE,
        freq_atualizacao_alvo=FREQUENCIA_ATUALIZACAO_ALVO,
    )
    if CARREGAR_MODELO_J1 and CAMINHO_MODELO_J1_CARREGAR:
        try:
            agente_dqn_j1.carregar_modelo(CAMINHO_MODELO_J1_CARREGAR)
            print(f"Modelo carregado para J1 de {CAMINHO_MODELO_J1_CARREGAR}")
        except Exception as e:
            print(f"Erro ao carregar modelo para J1: {e}. Iniciando com modelo novo.")

    # Inicializa o Oponente (Jogador 2)
    oponente = None
    if MODO_TREINAMENTO == "self_play":
        agente_dqn_j2 = AgenteDQN(
            tamanho_estado=TAMANHO_ESTADO,
            tamanho_acao=NUM_ACOES,
            taxa_aprendizado=LEARNING_RATE,  # Pode ter LR diferente se desejado
            gama=GAMMA,
            epsilon=EPSILON_INICIAL,
            epsilon_min=MIN_EPSILON,
            epsilon_decay=EPSILON_DECAY,
            capacidade_buffer=CAPACIDADE_BUFFER,
            tamanho_lote=BATCH_SIZE,
            freq_atualizacao_alvo=FREQUENCIA_ATUALIZACAO_ALVO,
        )
        if CARREGAR_MODELO_J2_SELFPLAY and CAMINHO_MODELO_J2_CARREGAR:
            try:
                agente_dqn_j2.carregar_modelo(CAMINHO_MODELO_J2_CARREGAR)
                print(
                    f"Modelo carregado para J2 (self-play) de {CAMINHO_MODELO_J2_CARREGAR}"
                )
            except Exception as e:
                print(
                    f"Erro ao carregar modelo para J2: {e}. Iniciando com modelo novo."
                )
        oponente = agente_dqn_j2
        print("Oponente: AgenteDQN (Self-Play)")
    elif MODO_TREINAMENTO == "vs_minimax":
        print("[DEBUG] Criando agente_j2 (AgenteMinimaxWrapper)", flush=True)
        oponente = AgenteMinimaxWrapper(
            profundidade_max=PROFUNDIDADE_MINIMAX, jogador_idx=1
        )  # Minimax é J2 (idx 1)
        print(f"Oponente: AgenteMinimax (Profundidade: {PROFUNDIDADE_MINIMAX})")
    else:
        raise ValueError(
            "Modo de treinamento inválido. Escolha 'self_play' ou 'vs_minimax'."
        )

    historico_recompensas_j1 = []
    historico_vitorias_j1 = []  # 1 para vitória, 0 para derrota/empate
    if MODO_TREINAMENTO == "self_play":
        historico_recompensas_j2 = []
        historico_vitorias_j2 = []

    # Loop de Episódios
    print("[DEBUG] Antes do loop de episódios", flush=True)
    for episodio in range(1, NUM_EPISODIOS + 1):
        jogo.resetar_jogo()
        # Para rastrear repetições dentro do episódio
        historico_posicoes_caminhos_j1 = [] # Lista de tuplas: (pos_j1, pos_j2, meu_caminho_j1)
        if MODO_TREINAMENTO == "self_play":
            historico_posicoes_caminhos_j2 = [] # Lista de tuplas: (pos_j2, pos_j1, meu_caminho_j2)
        print(f"\n--- Episódio {episodio} ---")
        estado_j1 = jogo.get_dqn_state_vector(0)  # Turno 0 para J1
        if MODO_TREINAMENTO == "self_play":
            estado_j2 = jogo.get_dqn_state_vector(1)  # Turno 1 para J2

        terminado = False
        recompensa_acumulada_j1 = 0
        if MODO_TREINAMENTO == "self_play":
            recompensa_acumulada_j2 = 0

        num_movimentos_episodio = 0

        print(f"[DEBUG] Episódio {episodio} - Antes do loop de turnos", flush=True)
        while not terminado and num_movimentos_episodio < MAX_MOVIMENTOS_POR_EPISODIO:

            # --- Turno do Jogador 1 (Agente DQN) ---
            # Medir caminhos ANTES do movimento do J1
            pos_j1_antes = jogo.jogadores["J1"]
            pos_j2_antes = jogo.jogadores["J2"]
            meu_caminho_antes_j1 = shortest_path_length("J1", pos_j1_antes, jogo.tabuleiro)
            caminho_oponente_antes_j1 = shortest_path_length("J2", pos_j2_antes, jogo.tabuleiro)

            # A função escolher_acao já retorna tanto o índice quanto o movimento
            acao_idx_j1, movimento_j1 = agente_dqn_j1.escolher_acao(
                estado_j1, jogo, 0
            )  # 0 para J1

            if movimento_j1 is None:
                print("[AVISO] Nenhum movimento válido retornado para J1. Encerrando episódio.")
                terminado = True # Encerrar episódio se não houver movimentos
                continue

            jogo.aplicar_movimento(movimento_j1, 0)
            print(f"  Turno {num_movimentos_episodio}: J1 (DQN) -> {movimento_j1}")

            recompensa_j1 = jogo.calcular_recompensa_dqn(
                movimento_j1, "J1", meu_caminho_antes_j1, caminho_oponente_antes_j1
            )

            # --- Lógica de Penalidade por Repetição para J1 ---
            penalidade_por_repeticao_j1 = 0.0
            pos_atual_j1_tupla = tuple(jogo.jogadores["J1"])
            pos_atual_oponente_para_j1_tupla = tuple(jogo.jogadores["J2"])
            caminho_atual_j1_apos_mov = shortest_path_length("J1", jogo.jogadores["J1"], jogo.tabuleiro)

            for i in range(len(historico_posicoes_caminhos_j1) -1, -1, -1):
                if len(historico_posicoes_caminhos_j1) - i > JANELA_HISTORICO_REPETICAO:
                    break
                
                pos_ant_j1, pos_ant_op_j1, caminho_ant_j1 = historico_posicoes_caminhos_j1[i]
                if pos_atual_j1_tupla == pos_ant_j1 and pos_atual_oponente_para_j1_tupla == pos_ant_op_j1:
                    if caminho_atual_j1_apos_mov >= caminho_ant_j1: # Não houve melhora no caminho
                        penalidade_por_repeticao_j1 = PENALIDADE_REPETICAO
                        print(f"    [J1 Repetição Penalizada] Posições: {pos_atual_j1_tupla},{pos_atual_oponente_para_j1_tupla}. Caminho atual: {caminho_atual_j1_apos_mov}, Caminho anterior: {caminho_ant_j1}")
                        break
            
            recompensa_j1 += penalidade_por_repeticao_j1

            historico_posicoes_caminhos_j1.append((pos_atual_j1_tupla, pos_atual_oponente_para_j1_tupla, caminho_atual_j1_apos_mov))
            if len(historico_posicoes_caminhos_j1) > JANELA_HISTORICO_REPETICAO + 5: 
                historico_posicoes_caminhos_j1.pop(0)
            # --- Fim da Lógica de Penalidade por Repetição para J1 ---

            proximo_estado_j1 = jogo.get_dqn_state_vector(0)
            terminado = jogo.jogo_terminado or num_movimentos_episodio >= MAX_MOVIMENTOS_POR_EPISODIO

            # Adiciona recompensa terminal (vitória, derrota ou empate/timeout)
            if terminado:
                if jogo.vencedor == "J1":
                    recompensa_j1 += 20
                elif jogo.vencedor == "J2":
                    recompensa_j1 -= 20
                else:  # Jogo terminou sem vencedor (limite de movimentos)
                    recompensa_j1 -= 20

            agente_dqn_j1.armazenar_experiencia(
                estado_j1, acao_idx_j1, recompensa_j1, proximo_estado_j1, terminado
            )
            agente_dqn_j1.aprender()
            estado_j1 = proximo_estado_j1
            recompensa_acumulada_j1 += recompensa_j1
            num_movimentos_episodio += 1

            if terminado:
                break

            # --- Turno do Jogador 2 (Oponente) ---
            if MODO_TREINAMENTO == "self_play":
                agente_dqn_j2 = oponente
                # Medir caminhos ANTES do movimento do J2
                pos_j1_antes_j2 = jogo.jogadores["J1"]
                pos_j2_antes_j2 = jogo.jogadores["J2"]
                meu_caminho_antes_j2 = shortest_path_length("J2", pos_j2_antes_j2, jogo.tabuleiro)
                caminho_oponente_antes_j2 = shortest_path_length("J1", pos_j1_antes_j2, jogo.tabuleiro)

                acao_idx_j2, movimento_j2 = agente_dqn_j2.escolher_acao(estado_j2, jogo, 1)

                if movimento_j2 is None:
                    terminado = True
                    continue
                
                jogo.aplicar_movimento(movimento_j2, 1)
                print(f"  Turno {num_movimentos_episodio}: J2 (DQN) -> {movimento_j2}")

                recompensa_j2 = jogo.calcular_recompensa_dqn(
                    movimento_j2, "J2", meu_caminho_antes_j2, caminho_oponente_antes_j2
                )

                # --- Lógica de Penalidade por Repetição para J2 ---
                penalidade_por_repeticao_j2 = 0.0
                pos_atual_j2_tupla = tuple(jogo.jogadores["J2"])
                pos_atual_oponente_para_j2_tupla = tuple(jogo.jogadores["J1"])
                caminho_atual_j2_apos_mov = shortest_path_length("J2", jogo.jogadores["J2"], jogo.tabuleiro)

                for i in range(len(historico_posicoes_caminhos_j2) -1, -1, -1):
                    if len(historico_posicoes_caminhos_j2) - i > JANELA_HISTORICO_REPETICAO:
                        break
                    
                    pos_ant_j2, pos_ant_op_j2, caminho_ant_j2 = historico_posicoes_caminhos_j2[i]
                    if pos_atual_j2_tupla == pos_ant_j2 and pos_atual_oponente_para_j2_tupla == pos_ant_op_j2:
                        if caminho_atual_j2_apos_mov >= caminho_ant_j2: # Não houve melhora
                            penalidade_por_repeticao_j2 = PENALIDADE_REPETICAO
                            print(f"    [J2 Repetição Penalizada] Posições: {pos_atual_j2_tupla},{pos_atual_oponente_para_j2_tupla}. Caminho atual: {caminho_atual_j2_apos_mov}, Caminho anterior: {caminho_ant_j2}")
                            break
                
                recompensa_j2 += penalidade_por_repeticao_j2

                historico_posicoes_caminhos_j2.append((pos_atual_j2_tupla, pos_atual_oponente_para_j2_tupla, caminho_atual_j2_apos_mov))
                if len(historico_posicoes_caminhos_j2) > JANELA_HISTORICO_REPETICAO + 5:
                    historico_posicoes_caminhos_j2.pop(0)
                # --- Fim da Lógica de Penalidade por Repetição para J2 ---

                proximo_estado_j2 = jogo.get_dqn_state_vector(1)
                terminado = jogo.jogo_terminado or num_movimentos_episodio >= MAX_MOVIMENTOS_POR_EPISODIO

                # --- INÍCIO DO BLOCO DE DEBUG J2 ---
                # Neste ponto, 'recompensa_j2' contém a recompensa intermediária + penalidade de repetição.
                # 'terminado' reflete o estado do jogo APÓS o movimento atual de J2.
                print(f"                [DEBUG J2] Movimento: {movimento_j2}")
                # Para mostrar a recompensa original de game.py, subtraímos a penalidade de repetição que já foi somada
                recompensa_de_game_py = recompensa_j2 - penalidade_por_repeticao_j2
                print(f"                [DEBUG J2] Recompensa Bruta (de game.py): {recompensa_de_game_py:.2f}")
                print(f"                [DEBUG J2] Penalidade Repetição Aplicada: {penalidade_por_repeticao_j2:.2f}")
                print(f"                [DEBUG J2] Recompensa J2 (após repetição, ANTES da recompensa terminal): {recompensa_j2:.2f}")
                
                if terminado: # 'terminado' é o da linha acima, reflete o estado atual
                    # Esta é uma simulação da recompensa terminal para fins de debug, baseada na lógica que se seguirá
                    recompensa_terminal_para_debug = 0
                    if jogo.vencedor == "J2":
                        recompensa_terminal_para_debug = 20 # Idealmente, usar constante (ex: RECOMPENSA_VITORIA_JOGO)
                    elif jogo.vencedor == "J1":
                        recompensa_terminal_para_debug = -20 # Idealmente, usar constante (ex: PENALIDADE_DERROTA_JOGO)
                    else: # Jogo terminou sem vencedor (limite de movimentos)
                        recompensa_terminal_para_debug = -20 # Idealmente, usar constante (ex: PENALIDADE_TIMEOUT_JOGO)
                    print(f"                [DEBUG J2] Recompensa Terminal (que SERÁ adicionada na prox. etapa): {recompensa_terminal_para_debug}")
                # --- FIM DO BLOCO DE DEBUG J2 ---

                # Adiciona recompensa terminal (vitória, derrota ou empate/timeout)
                if terminado:
                    if jogo.vencedor == "J2":
                        recompensa_j2 += 20
                    elif jogo.vencedor == "J1":
                        recompensa_j2 -= 20
                    else: # Jogo terminou sem vencedor (limite de movimentos)
                        recompensa_j2 -= 20

                agente_dqn_j2.armazenar_experiencia(
                    estado_j2, acao_idx_j2, recompensa_j2, proximo_estado_j2, terminado
                )
                agente_dqn_j2.aprender()

                estado_j2 = proximo_estado_j2
                recompensa_acumulada_j2 += recompensa_j2
                num_movimentos_episodio += 1

            elif MODO_TREINAMENTO == "vs_minimax":
                agente_minimax = oponente
                movimento_j2 = agente_minimax.escolher_jogada(
                    jogo, 1
                )  # Minimax é J2 (idx 1)

                if (
                    movimento_j2 is None
                ):  # Minimax não encontrou movimento (raro, mas possível em estados finais)
                    print(
                        f"Episódio {episodio}: Minimax não retornou movimento. Jogo pode estar em estado estranho."
                    )
                    terminado = True  # Considera o jogo terminado
                else:
                    jogo.aplicar_movimento(movimento_j2, 1)
                    print(f"  Turno {num_movimentos_episodio}: J2 (MiniMax) -> {movimento_j2}")
                    terminado = jogo.jogo_terminado

            num_movimentos_episodio += 1
            if terminado:
                break

        # Fim do Episódio
        historico_recompensas_j1.append(recompensa_acumulada_j1)
        vitoria_j1 = 1 if jogo.vencedor == "J1" else 0
        historico_vitorias_j1.append(vitoria_j1)

        log_str = f"Episódio: {episodio}/{NUM_EPISODIOS}, J1 Recomp: {recompensa_acumulada_j1:.2f}, J1 Epsilon: {agente_dqn_j1.epsilon:.4f}, Movs: {num_movimentos_episodio}"
        if jogo.vencedor:
            log_str += f", Vencedor: {jogo.vencedor}"
        else:
            log_str += ", Jogo Incompleto (Max Movs)"

        if MODO_TREINAMENTO == "self_play":
            historico_recompensas_j2.append(recompensa_acumulada_j2)
            vitoria_j2 = 1 if jogo.vencedor == "J2" else 0
            historico_vitorias_j2.append(vitoria_j2)
            log_str += f", J2 Recomp: {recompensa_acumulada_j2:.2f}, J2 Epsilon: {agente_dqn_j2.epsilon:.4f}"

        print(log_str)

        # Salvar modelo periodicamente
        if (episodio + 1) % SALVAR_MODELO_A_CADA_N_EPISODIOS == 0:
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            print(
                f"[DEBUG] Episódio {episodio} - Antes de salvar modelo J1", flush=True
            )
            caminho_salvar_j1 = (
                f"{PASTA_MODELOS}/{NOME_BASE_MODELO}_j1_ep{episodio}_{timestamp}.h5"
            )
            agente_dqn_j1.salvar_modelo(caminho_salvar_j1)
            print(f"Modelo J1 salvo em: {caminho_salvar_j1}")
            if MODO_TREINAMENTO == "self_play":
                print(
                    f"[DEBUG] Episódio {episodio} - Antes de salvar modelo J2 (self_play)",
                    flush=True,
                )
                caminho_salvar_j2 = (
                    f"{PASTA_MODELOS}/{NOME_BASE_MODELO}_j2_ep{episodio}_{timestamp}.h5"
                )
                agente_dqn_j2.salvar_modelo(caminho_salvar_j2)
                print(f"Modelo J2 salvo em: {caminho_salvar_j2}")

    # Salvar modelo final
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    caminho_final_j1 = (
        f"{PASTA_MODELOS}/{NOME_BASE_MODELO}_j1_final_ep{NUM_EPISODIOS}_{timestamp}.h5"
    )
    agente_dqn_j1.salvar_modelo(caminho_final_j1)
    print(f"Modelo final J1 salvo em: {caminho_final_j1}")
    if MODO_TREINAMENTO == "self_play":
        caminho_final_j2 = f"{PASTA_MODELOS}/{NOME_BASE_MODELO}_j2_final_ep{NUM_EPISODIOS}_{timestamp}.h5"
        agente_dqn_j2.salvar_modelo(caminho_final_j2)
        print(f"Modelo final J2 salvo em: {caminho_final_j2}")

    print("[DEBUG] Fim da função treinar()", flush=True)
    print(f"Treinamento {MODO_TREINAMENTO} concluído.")

if __name__ == "__main__":
    print("[DEBUG] Iniciando execução do script treinar_dqn.py", flush=True)
    print("MAIN_BLOCK_REACHED", flush=True)
    treinar()

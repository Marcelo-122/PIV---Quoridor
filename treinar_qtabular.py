import datetime
import os
import random
import sys
import time

from src.ai.q_learning_agent import AgenteQLearningTabular
from src.core.game import JogoQuoridor
import numpy as np
import sys

sys.path.append("src/core")
from debug_utils import visualizar_tabuleiro

# Garante que o diretório raiz do projeto esteja no sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Configurações e Hiperparâmetros ---
NUM_EPISODIOS = 1000  # Aumentado para 1000 episódios
TAMANHO_TABULEIRO = 5  # Tabuleiro 5x5
PAREDES_POR_JOGADOR = 3  # 3 paredes por jogador
MAX_MOVIMENTOS_POR_EPISODIO = 200  # Aumentado para 200 para permitir jogos mais longos


# Parâmetros para AgenteQLearningTabular
LEARNING_RATE = 0.1  # Taxa de aprendizado (alpha)
GAMMA = 0.95  # Fator de desconto
EPSILON_INICIAL = 1.0  # Exploração inicial 100%
MIN_EPSILON = 0.1  # Mínimo de exploração 10%
EPSILON_DECAY = 0.995  # Taxa de decaimento aumentada

# Salvamento do modelo Q-tabela
PASTA_MODELOS = "saved_models_q_tabular"
NOME_BASE_MODELO = "quoridor_q_tabular"
SALVAR_MODELO_A_CADA_N_EPISODIOS = 500
CARREGAR_MODELO = False
CAMINHO_MODELO_CARREGAR = f"{PASTA_MODELOS}/quoridor_q_tabular_episodio_XXXX.pkl"

# Recompensas
RECOMPENSA_VITORIA = 1000.0
RECOMPENSA_DERROTA = -100.0
PENALIDADE_MOVIMENTO = -0.1  # Pequena penalidade para incentivar movimentos eficientes
BONUS_APROXIMACAO = 10.0  # Aumentado para incentivar mais a aproximação do objetivo
PENALIDADE_MOVIMENTO_INVALIDO = -100.0  # Penalidade específica para movimentos inválidos


def calcular_recompensa(jogo, turno_idx, estado_anterior, estado_atual):
    """
    Calcula a recompensa para o agente com base na transição de estado.

    Args:
        jogo: Instância do jogo Quoridor
        turno_idx: Índice do jogador atual (0 para J1, 1 para J2)
        estado_anterior: Estado do jogo antes da ação
        estado_atual: Estado do jogo após a ação

    Returns:
        float: Valor da recompensa
    """
    # Verifica se o jogo terminou
    if jogo.jogo_terminado:
        if jogo.vencedor == ("J1" if turno_idx == 0 else "J2"):
            return RECOMPENSA_VITORIA
        else:
            return RECOMPENSA_DERROTA

    # Extrai informações dos estados para calcular a progressão
    pos_anterior = estado_anterior[turno_idx] if turno_idx <= 1 else estado_anterior[0]
    pos_atual = estado_atual[turno_idx] if turno_idx <= 1 else estado_atual[0]

    # A linha objetivo depende de qual jogador está jogando
    linha_objetivo = jogo.linhas - 1 if turno_idx == 0 else 0

    # Distância até o objetivo (em termos de linhas apenas, para simplificar)
    distancia_anterior = abs(pos_anterior[0] - linha_objetivo)
    distancia_atual = abs(pos_atual[0] - linha_objetivo)

    # Recompensa progressiva por aproximação ao objetivo
    if distancia_atual < distancia_anterior:
        # Recompensa proporcional à aproximação
        melhoria = distancia_anterior - distancia_atual
        return BONUS_APROXIMACAO * melhoria

    # Calcular proximidade ao objetivo como porcentagem do caminho total
    distancia_total = jogo.linhas - 1  # Máxima distância possível
    proximidade = 1 - (distancia_atual / distancia_total)  # 0 = longe, 1 = no objetivo

    # Pequeno bônus baseado na proximidade atual ao objetivo
    bonus_proximidade = proximidade * 0.5

    # Penalidade para movimento que não aproxima (incentiva ser eficiente)
    return PENALIDADE_MOVIMENTO + bonus_proximidade


def treinar():
    print(
        "Iniciando treinamento Q-Learning Tabular para Quoridor simplificado.",
        flush=True,
    )
    print(
        f"Tabuleiro: {TAMANHO_TABULEIRO}x{TAMANHO_TABULEIRO}, Paredes por jogador: {PAREDES_POR_JOGADOR}"
    )
    print(f"Número de Episódios: {NUM_EPISODIOS}")

    # Cria a pasta para salvar modelos, se não existir
    os.makedirs(PASTA_MODELOS, exist_ok=True)

    # Inicializa o jogo simplificado (5x5, 3 paredes)
    jogo = JogoQuoridor(
        linhas=TAMANHO_TABULEIRO,
        colunas=TAMANHO_TABULEIRO,
        total_paredes_jogador=PAREDES_POR_JOGADOR,
    )

    # Inicializa agente Q-Learning tabular
    agente = AgenteQLearningTabular(
        taxa_aprendizado=LEARNING_RATE,
        fator_desconto=GAMMA,
        epsilon=EPSILON_INICIAL,
        min_epsilon=MIN_EPSILON,
        epsilon_decay=EPSILON_DECAY,
    )

    if CARREGAR_MODELO and CAMINHO_MODELO_CARREGAR:
        try:
            agente.carregar_q_tabela(CAMINHO_MODELO_CARREGAR)
            print(f"Q-tabela carregada de {CAMINHO_MODELO_CARREGAR}")
        except Exception as e:
            print(f"Erro ao carregar Q-tabela: {e}")
            print("Continuando com Q-tabela nova.")

    # Estatísticas de treinamento
    vitorias_j1 = 0
    vitorias_j2 = 0
    movimentos_por_episodio = []
    timestamp_inicio = datetime.datetime.now()

    # Loop principal de treinamento
    for episodio in range(1, NUM_EPISODIOS + 1):
        jogo.resetar_jogo()
        total_movimentos = 0
        estado_atual_j1 = jogo.get_estado_tupla(0)  # Estado inicial J1
        estado_atual_j2 = jogo.get_estado_tupla(1)  # Estado inicial J2

        # Contador de movimentos inválidos para evitar loops infinitos
        movimentos_invalidos_consecutivos = 0
        MAX_MOVIMENTOS_INVALIDOS = 10  # Limite de movimentos inválidos consecutivos

        # Loop de jogo até terminar ou atingir limite de movimentos
        while (
            not jogo.jogo_terminado and total_movimentos < MAX_MOVIMENTOS_POR_EPISODIO
        ):
            # Jogador 1 (turno 0)
            acoes_validas_j1 = jogo.get_acoes_validas(0)

            # Se não houver ações válidas, terminar o episódio
            if not acoes_validas_j1:
                break

            acao_j1 = agente.escolher_acao(estado_atual_j1, acoes_validas_j1)

            # Aplica o movimento do J1
            sucesso = jogo.aplicar_movimento(acao_j1, 0)
            if not sucesso:
                # Penalidade para movimento inválido, mas não termina o jogo
                recompensa_j1 = PENALIDADE_MOVIMENTO_INVALIDO

                # Incrementa contador de movimentos inválidos
                movimentos_invalidos_consecutivos += 1

                # Se muitos movimentos inválidos consecutivos, terminar episódio
                if movimentos_invalidos_consecutivos >= MAX_MOVIMENTOS_INVALIDOS:
                    print(
                        f"[DEBUG] Muitos movimentos inválidos consecutivos, terminando episódio."
                    )
                    jogo.jogo_terminado = True
                    break

                # Tentar outro movimento válido aleatório em vez de terminar o jogo
                if acoes_validas_j1:
                    acao_j1 = random.choice(acoes_validas_j1)
                    sucesso = jogo.aplicar_movimento(acao_j1, 0)
                    if not sucesso:
                        continue  # Tenta novamente na próxima iteração

                print(f"[DEBUG] Tabuleiro atual:")
                print(visualizar_tabuleiro(jogo))
                print(f"[DEBUG] Posição J1: {jogo.jogadores['J1']}")
                print(f"[DEBUG] Ações válidas: {acoes_validas_j1[:3]}...")
                print(f"[DEBUG] Movimento inválido para J1: {acao_j1}")
                continue

            # Resetar contador de movimentos inválidos se o movimento foi bem-sucedido
            movimentos_invalidos_consecutivos = 0

            # Obtém o novo estado e calcula recompensa
            novo_estado_j1 = jogo.get_estado_tupla(0)
            recompensa_j1 = calcular_recompensa(
                jogo, 0, estado_atual_j1, novo_estado_j1
            )

            # Verificar se J1 venceu
            if jogo.verificar_vitoria_jogador("J1"):
                recompensa_j1 = RECOMPENSA_VITORIA
                jogo.jogo_terminado = True
                jogo.vencedor = "J1"
                vitorias_j1 += 1
                print(
                    f"[VITÓRIA] J1 venceu no episódio {episodio} após {total_movimentos} movimentos!"
                )

            # Atualiza Q-valores para J1
            proximo_acoes_j1 = (
                jogo.get_acoes_validas(0) if not jogo.jogo_terminado else []
            )
            agente.aprender(
                estado_atual_j1,
                acao_j1,
                recompensa_j1,
                novo_estado_j1,
                proximo_acoes_j1,
                jogo.jogo_terminado,
            )
            estado_atual_j1 = novo_estado_j1
            total_movimentos += 1

            # Verifica se o jogo terminou após o movimento de J1
            if jogo.jogo_terminado:
                break

                # Jogador 2 (turno 1)
            acoes_validas_j2 = jogo.get_acoes_validas(1)

            # Se não houver ações válidas, terminar o episódio
            if not acoes_validas_j2:
                break

            acao_j2 = agente.escolher_acao(estado_atual_j2, acoes_validas_j2)

            # Aplica o movimento do J2
            sucesso = jogo.aplicar_movimento(acao_j2, 1)
            if not sucesso:
                # Penalidade para movimento inválido, mas não termina o jogo
                recompensa_j2 = PENALIDADE_MOVIMENTO_INVALIDO

                # Incrementa contador de movimentos inválidos
                movimentos_invalidos_consecutivos += 1

                # Se muitos movimentos inválidos consecutivos, terminar episódio
                if movimentos_invalidos_consecutivos >= MAX_MOVIMENTOS_INVALIDOS:
                    print(
                        f"[DEBUG] Muitos movimentos inválidos consecutivos, terminando episódio."
                    )
                    jogo.jogo_terminado = True
                    break

                # Tentar outro movimento válido aleatório em vez de terminar o jogo
                if acoes_validas_j2:
                    acao_j2 = random.choice(acoes_validas_j2)
                    sucesso = jogo.aplicar_movimento(acao_j2, 1)
                    if not sucesso:
                        continue  # Tenta novamente na próxima iteração

                print(f"[DEBUG] Tabuleiro atual:")
                print(visualizar_tabuleiro(jogo))
                print(f"[DEBUG] Posição J2: {jogo.jogadores['J2']}")
                print(f"[DEBUG] Ações válidas: {acoes_validas_j2[:3]}...")
                print(f"[DEBUG] Movimento inválido para J2: {acao_j2}")
                continue

            # Resetar contador de movimentos inválidos se o movimento foi bem-sucedido
            movimentos_invalidos_consecutivos = 0

            # Obtém o novo estado e calcula recompensa
            novo_estado_j2 = jogo.get_estado_tupla(1)
            recompensa_j2 = calcular_recompensa(
                jogo, 1, estado_atual_j2, novo_estado_j2
            )

            # Verificar se J2 venceu
            if jogo.verificar_vitoria_jogador("J2"):
                recompensa_j2 = RECOMPENSA_VITORIA
                jogo.jogo_terminado = True
                jogo.vencedor = "J2"
                vitorias_j2 += 1
                print(
                    f"[VITÓRIA] J2 venceu no episódio {episodio} após {total_movimentos} movimentos!"
                )

            # Atualiza Q-valores para J2
            proximo_acoes_j2 = (
                jogo.get_acoes_validas(1) if not jogo.jogo_terminado else []
            )
            agente.aprender(
                estado_atual_j2,
                acao_j2,
                recompensa_j2,
                novo_estado_j2,
                proximo_acoes_j2,
                jogo.jogo_terminado,
            )
            estado_atual_j2 = novo_estado_j2
            total_movimentos += 1

            # Verifica se o jogo terminou após o movimento de J2
            if jogo.jogo_terminado:
                break

        # Registra estatísticas do episódio
        movimentos_por_episodio.append(total_movimentos)

        # Atualiza parâmetros do agente (epsilon)
        agente.atualizar_epsilon()

        # Salva o modelo a cada N episódios
        if episodio % SALVAR_MODELO_A_CADA_N_EPISODIOS == 0:
            caminho_modelo = (
                f"{PASTA_MODELOS}/{NOME_BASE_MODELO}_episodio_{episodio}.pkl"
            )
            agente.salvar_q_tabela(caminho_modelo)
            print(f"Q-tabela salva em {caminho_modelo}")

        # Imprime progresso a cada 10 episódios ou quando há uma vitória
        if episodio % 10 == 0 or vitorias_j1 > 0 or vitorias_j2 > 0:
            tempo_decorrido = datetime.datetime.now() - timestamp_inicio
            media_movimentos = (
                np.mean(movimentos_por_episodio[-100:])
                if episodio > 100
                else np.mean(movimentos_por_episodio)
            )

            print(
                f"Episódio {episodio}/{NUM_EPISODIOS} | "
                + f"Epsilon: {agente.epsilon:.4f} | "
                + f"Movimentos médios: {media_movimentos:.2f} | "
                + f"Tempo decorrido: {tempo_decorrido} | "
                + f"Vitórias J1/J2: {vitorias_j1}/{vitorias_j2} | "
                + f"Tamanho Q-tabela: {len(agente.q_tabela)}"
            )

    # Estatísticas finais
    tempo_total = datetime.datetime.now() - timestamp_inicio
    print("\n=== Estatísticas finais de treinamento ===")
    print(f"Tempo total de treinamento: {tempo_total}")
    print(f"Tamanho final da Q-tabela: {len(agente.q_tabela)} estados")
    print(f"Vitórias J1: {vitorias_j1}, Vitórias J2: {vitorias_j2}")
    print(f"Movimentos médios por episódio: {np.mean(movimentos_por_episodio):.2f}")

    # Salvar modelo final
    caminho_final = f"{PASTA_MODELOS}/{NOME_BASE_MODELO}_final.pkl"
    agente.salvar_q_tabela(caminho_final)
    print(f"Q-tabela final salva em {caminho_final}")

    return agente


if __name__ == "__main__":
    print("[DEBUG] Iniciando execução do script treinar_qtabular.py", flush=True)
    treinar()

import numpy as np
import random
from collections import deque  # Para o Buffer de Replay

# Precisaremos de uma biblioteca de aprendizado profundo, como TensorFlow/Keras ou PyTorch
# Vamos assumir TensorFlow/Keras por enquanto para o exemplo
from tensorflow.keras.models import Sequential, clone_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

from .dqn_config_acoes import (
    TOTAL_ACOES,
    indice_para_movimento,
    movimento_para_indice,
)  # Nossas configs de ação


class AgenteDQN:
    def __init__(
        self,
        tamanho_estado,
        tamanho_acao,
        taxa_aprendizado=0.001,
        gama=0.99,
        epsilon=1.0,
        epsilon_min=0.01,
        epsilon_decay=0.995,
        capacidade_buffer=10000,
        tamanho_lote=64,
        freq_atualizacao_alvo=100,
    ):
        self.tamanho_estado = tamanho_estado  # Ex: 135
        self.tamanho_acao = tamanho_acao  # Ex: 132

        self.gama = gama  # Fator de desconto
        self.epsilon = epsilon  # Exploração inicial
        self.epsilon_min = epsilon_min  # Exploração mínima
        self.epsilon_decay = epsilon_decay  # Decaimento da exploração
        self.taxa_aprendizado = taxa_aprendizado

        self.buffer_replay = deque(maxlen=capacidade_buffer)
        self.tamanho_lote = tamanho_lote
        self.freq_atualizacao_alvo = (
            freq_atualizacao_alvo  # Com que frequência atualizar a rede alvo
        )
        self.contador_atualizacao_alvo = 0

        # Rede Q Principal e Rede Q Alvo
        self.model = self._construir_modelo()
        self.target_model = self._construir_modelo()
        self.atualizar_rede_alvo()  # Inicializa target_model com os pesos de model

    def _construir_modelo(self):
        # Arquitetura da Rede Neural
        modelo = Sequential()
        modelo.add(
            Dense(128, input_dim=self.tamanho_estado, activation="relu")
        )  # Camada de entrada
        modelo.add(Dense(128, activation="relu"))  # Camada oculta
        modelo.add(
            Dense(self.tamanho_acao, activation="linear")
        )  # Camada de saída (Q-valores)
        modelo.compile(loss="mse", optimizer=Adam(learning_rate=self.taxa_aprendizado))
        return modelo

    def atualizar_rede_alvo(self):
        """Copia os pesos da rede principal para a rede alvo."""
        self.target_model.set_weights(self.model.get_weights())
        print("Rede alvo atualizada.")

    def armazenar_experiencia(
        self, estado, acao_indice, recompensa, proximo_estado, terminado
    ):
        """Adiciona uma experiência ao buffer de replay."""
        # O estado e proximo_estado já devem ser os vetores da DQN
        # acao_indice é o índice numérico da ação (0-131)
        self.buffer_replay.append(
            (estado, acao_indice, recompensa, proximo_estado, terminado)
        )

    def escolher_acao(self, estado_vetor, jogo, turno_jogador_atual):
        """
        Escolhe uma ação usando a política epsilon-greedy.
        Retorna o índice da ação (0-131) e o movimento do jogo ('move', 'd') ou ('wall', 'e5h').
        """
        # estado_vetor é o resultado de jogo.get_dqn_state_vector()
        # Precisamos obter as ações válidas para mascaramento ou seleção
        movimentos_validos_jogo = jogo.gerar_movimentos_possiveis(turno_jogador_atual)
        indices_acoes_validas = [
            movimento_para_indice(m[0], m[1])
            for m in movimentos_validos_jogo
            if m is not None
        ]

        if not indices_acoes_validas:  # Se não houver movimentos válidos (raro, mas possível em estados finais forçados)
            return None, None  # Ou alguma ação padrão/aleatória se necessário

        if np.random.rand() <= self.epsilon:
            # Ação aleatória (exploração) dentre as válidas
            indice_acao_escolhida = random.choice(indices_acoes_validas)
        else:
            # Ação baseada nos Q-valores (explotação)
            q_valores = self.model.predict(
                np.reshape(estado_vetor, [1, self.tamanho_estado])
            )[0]

            # Considerar apenas Q-valores de ações válidas
            q_valores_validos = {i: q_valores[i] for i in indices_acoes_validas}
            indice_acao_escolhida = max(q_valores_validos, key=q_valores_validos.get)

        movimento_escolhido_jogo = indice_para_movimento(indice_acao_escolhida)
        return indice_acao_escolhida, movimento_escolhido_jogo

    def aprender(self):
        """
        Treina a rede Q principal usando um lote de experiências do buffer de replay.
        Este é o "Q-Learning update rule" para DQN.
        """
        if len(self.buffer_replay) < self.tamanho_lote:
            return  # Não aprender até que o buffer tenha amostras suficientes

        lote_amostras = random.sample(self.buffer_replay, self.tamanho_lote)

        estados_lote = []
        q_alvos_lote = []

        for estado, acao_indice, recompensa, proximo_estado, terminado in lote_amostras:
            estado_np = np.reshape(estado, [1, self.tamanho_estado])
            proximo_estado_np = np.reshape(proximo_estado, [1, self.tamanho_estado])

            q_alvo_para_estado_atual = self.model.predict(estado_np)[
                0
            ]  # Q-valores atuais para todas as ações

            if terminado:
                q_alvo_acao = recompensa
            else:
                # Bellman equation: R + gamma * max_a' Q_target(s', a')
                q_futuro_max = np.amax(self.target_model.predict(proximo_estado_np)[0])
                q_alvo_acao = recompensa + self.gama * q_futuro_max

            q_alvo_para_estado_atual[acao_indice] = (
                q_alvo_acao  # Atualiza o Q-valor apenas para a ação tomada
            )

            estados_lote.append(estado)  # Adiciona o estado original
            q_alvos_lote.append(
                q_alvo_para_estado_atual
            )  # Adiciona os Q-valores alvo (com a ação tomada atualizada)

        # Treinar o modelo principal
        # Keras espera que as entradas (estados) e saídas (Q-alvos) sejam arrays numpy
        self.model.fit(
            np.array(estados_lote), np.array(q_alvos_lote), epochs=1, verbose=0
        )

        # Decaimento do Epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        # Atualizar a rede alvo periodicamente
        self.contador_atualizacao_alvo += 1
        if self.contador_atualizacao_alvo % self.freq_atualizacao_alvo == 0:
            self.atualizar_rede_alvo()

    # Poderíamos adicionar métodos para salvar/carregar o modelo
    # def salvar_modelo(self, nome_arquivo):
    #     self.model.save_weights(nome_arquivo)
    # def carregar_modelo(self, nome_arquivo):
    #     self.model.load_weights(nome_arquivo)
    #     self.atualizar_rede_alvo()

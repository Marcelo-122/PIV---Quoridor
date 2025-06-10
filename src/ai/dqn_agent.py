import numpy as np
import random
from collections import deque

# Imports do TensorFlow/Keras
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam

# Imports do projeto
from .dqn_config_acoes import (
    indice_para_movimento,
    movimento_para_indice,
)


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
        self.tamanho_estado = tamanho_estado
        self.tamanho_acao = tamanho_acao
        self.gama = gama
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.taxa_aprendizado = taxa_aprendizado
        self.buffer_replay = deque(maxlen=capacidade_buffer)
        self.tamanho_lote = tamanho_lote
        self.freq_atualizacao_alvo = freq_atualizacao_alvo
        self.contador_atualizacao_alvo = 0

        self.model = self._construir_modelo()
        self.target_model = self._construir_modelo()
        self.atualizar_rede_alvo()

    def _construir_modelo(self):
        modelo = Sequential()
        modelo.add(Input(shape=(self.tamanho_estado,)))
        modelo.add(Dense(128, activation="relu"))
        modelo.add(Dense(128, activation="relu"))
        modelo.add(Dense(self.tamanho_acao, activation="linear"))
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
        self.buffer_replay.append(
            (estado, acao_indice, recompensa, proximo_estado, terminado)
        )

    def escolher_acao(self, estado_vetor, jogo, turno_jogador_atual):
        """Escolhe uma ação usando a política epsilon-greedy."""
        movimentos_validos_jogo = jogo.gerar_movimentos_possiveis(turno_jogador_atual)
        indices_acoes_validas = [
            movimento_para_indice(m[0], m[1])
            for m in movimentos_validos_jogo
            if m is not None
        ]

        if not indices_acoes_validas:
            return None, None

        if np.random.rand() <= self.epsilon:
            indice_acao_escolhida = random.choice(indices_acoes_validas)
        else:
            q_valores = self.model.predict(
                np.reshape(estado_vetor, [1, self.tamanho_estado])
            )[0]
            q_valores_validos = {i: q_valores[i] for i in indices_acoes_validas}
            indice_acao_escolhida = max(q_valores_validos, key=q_valores_validos.get)

        movimento_escolhido_jogo = indice_para_movimento(indice_acao_escolhida)
        return indice_acao_escolhida, movimento_escolhido_jogo

    def aprender(self):
        """Treina a rede Q principal usando um lote de experiências."""
        if len(self.buffer_replay) < self.tamanho_lote:
            return

        lote_amostras = random.sample(self.buffer_replay, self.tamanho_lote)

        estados = np.array([amostra[0] for amostra in lote_amostras])
        proximos_estados = np.array([amostra[3] for amostra in lote_amostras])

        q_valores_atuais = self.model.predict(estados)
        q_valores_proximos_alvo = self.target_model.predict(proximos_estados)

        for i, (
            estado,
            acao_indice,
            recompensa,
            proximo_estado,
            terminado,
        ) in enumerate(lote_amostras):
            if terminado:
                q_alvo = recompensa
            else:
                q_alvo = recompensa + self.gama * np.amax(q_valores_proximos_alvo[i])

            q_valores_atuais[i][acao_indice] = q_alvo

        self.model.fit(estados, q_valores_atuais, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        self.contador_atualizacao_alvo += 1
        if self.contador_atualizacao_alvo % self.freq_atualizacao_alvo == 0:
            self.atualizar_rede_alvo()

    def salvar_modelo(self, caminho_arquivo):
        """Salva o modelo Q principal (arquitetura + pesos)."""
        print(f"Salvando modelo em: {caminho_arquivo}")
        self.model.save(caminho_arquivo)

    def carregar_modelo(self, caminho_arquivo):
        """Carrega um modelo Q principal de um arquivo."""
        print(f"Carregando modelo de: {caminho_arquivo}")
        self.model = load_model(caminho_arquivo)
        self.atualizar_rede_alvo()

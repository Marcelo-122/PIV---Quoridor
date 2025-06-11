# src/ai/q_learning_agent.py
import numpy as np
import random
import pickle
from collections import defaultdict

class AgenteQLearningTabular:
    def __init__(self, taxa_aprendizado=0.1, fator_desconto=0.99,
                 epsilon=1.0, min_epsilon=0.01, epsilon_decay=0.9995, nome_arquivo_q_tabela=None):
        """
        Agente que aprende usando Q-Learning tabular.

        Args:
            taxa_aprendizado (float): Alpha, o quanto o agente aprende com novas informações.
            fator_desconto (float): Gamma, importância das recompensas futuras.
            epsilon (float): Probabilidade inicial de tomar uma ação aleatória (exploração).
            min_epsilon (float): Valor mínimo de epsilon.
            epsilon_decay (float): Fator pelo qual epsilon é multiplicado a cada passo de aprendizado.
            nome_arquivo_q_tabela (str, optional): Nome do arquivo para carregar/salvar a Q-tabela.
        """
        self.alpha = taxa_aprendizado
        self.gamma = fator_desconto
        self.epsilon = epsilon
        self.min_epsilon = min_epsilon
        self.epsilon_decay = epsilon_decay

        self.q_tabela = defaultdict(lambda: defaultdict(float))
        
        self.nome_arquivo_q_tabela = nome_arquivo_q_tabela
        if self.nome_arquivo_q_tabela:
            self.carregar_q_tabela(self.nome_arquivo_q_tabela)

    def obter_q_valor(self, estado, acao):
        """Retorna o Q-valor para um par estado-ação."""
        return self.q_tabela[estado][acao]

    def escolher_acao(self, estado, acoes_disponiveis):
        if not acoes_disponiveis:
            print(f"[WARN] Sem ações válidas disponíveis no estado {estado}")
            return None
            
        if np.random.random() < self.epsilon:
            # Exploração: escolhe uma ação aleatória
            return random.choice(acoes_disponiveis)
        else:
            # Exploração: escolhe a melhor ação conhecida
            q_values = [self.q_tabela.get((estado, acao), 0.0) for acao in acoes_disponiveis]
            max_q = max(q_values)
            
            # Se há múltiplas ações com mesmo Q-value, escolhe aleatoriamente entre elas
            melhores_acoes = [acao for acao in acoes_disponiveis if self.q_tabela.get((estado, acao), 0.0) == max_q]
            return random.choice(melhores_acoes)

    def aprender(self, estado, acao, recompensa, proximo_estado, proximo_acoes_disponiveis, done):
        """
        Atualiza o Q-valor para o par estado-ação usando a regra de Bellman.
        Q(s,a) = Q(s,a) + alpha * (recompensa + gamma * max_a'(Q(s',a')) - Q(s,a))
        Se done (fim do episódio), o valor futuro (gamma * max_a'(Q(s',a'))) é 0.
        """
        q_atual = self.q_tabela[estado][acao]
        
        valor_q_max_proximo_estado = 0.0
        if not done and proximo_acoes_disponiveis:
            q_valores_proximo_estado = self.q_tabela[proximo_estado]
            if q_valores_proximo_estado: # Se o próximo estado já foi visitado e tem ações exploradas
                valor_q_max_proximo_estado = max(q_valores_proximo_estado[acao] for acao in proximo_acoes_disponiveis)
            # Se proximo_estado não está na q_tabela ou não tem ações em proximo_acoes_disponiveis
            # com entradas, max retornaria erro em lista vazia ou usaria 0.0 de defaultdict.
            # O defaultdict garante que q_valores_proximo_estado[acao] seja 0.0 para ações não vistas.
            # Se proximo_acoes_disponiveis for vazio, este bloco é pulado e valor_q_max_proximo_estado é 0.

        td_target = recompensa + self.gamma * valor_q_max_proximo_estado
        td_error = td_target - q_atual
        self.q_tabela[estado][acao] = q_atual + self.alpha * td_error

    def atualizar_epsilon(self):
        """Atualiza o valor de epsilon de acordo com a taxa de decaimento."""
        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.epsilon_decay
            self.epsilon = max(self.min_epsilon, self.epsilon)  # Garante que não caia abaixo do mínimo
    
    def salvar_q_tabela(self, nome_arquivo=None):
        """Salva a Q-tabela em um arquivo usando pickle."""
        if nome_arquivo is None:
            nome_arquivo = self.nome_arquivo_q_tabela
        if nome_arquivo is None:
            print("Erro: Nome do arquivo para salvar a Q-tabela não especificado.")
            return

        q_tabela_serializavel = {k: dict(v) for k, v in self.q_tabela.items()}
        try:
            with open(nome_arquivo, 'wb') as f:
                pickle.dump(q_tabela_serializavel, f)
            print(f"Q-tabela salva em {nome_arquivo}")
        except Exception as e:
            print(f"Erro ao salvar Q-tabela: {e}")

    def carregar_q_tabela(self, nome_arquivo=None):
        """Carrega a Q-tabela de um arquivo usando pickle."""
        if nome_arquivo is None:
            nome_arquivo = self.nome_arquivo_q_tabela
        if nome_arquivo is None:
            print("Erro: Nome do arquivo para carregar a Q-tabela não especificado.")
            return
        try:
            with open(nome_arquivo, 'rb') as f:
                q_tabela_carregada = pickle.load(f)
                self.q_tabela = defaultdict(lambda: defaultdict(float))
                for estado, acoes_q_valores in q_tabela_carregada.items():
                    # As chaves do estado (tuplas) e ações (tuplas) devem ser preservadas pelo pickle
                    for acao, q_valor in acoes_q_valores.items():
                        self.q_tabela[estado][acao] = q_valor
            print(f"Q-tabela carregada de {nome_arquivo}")
        except FileNotFoundError:
            print(f"Arquivo da Q-tabela '{nome_arquivo}' não encontrado. Iniciando com Q-tabela vazia.")
        except Exception as e:
            print(f"Erro ao carregar Q-tabela: {e}. Iniciando com Q-tabela vazia.")
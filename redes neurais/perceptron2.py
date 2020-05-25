import random
import numpy as np
import pandas as pd
import math 

dataframe = pd.read_csv('/home/alvaro/Documentos/mestrado/computação bio/redes neurais/datasets/iris2.csv', header = 0)

previsores = dataframe.iloc[:, 0:4] 
classe = dataframe['class']

def z_score_normalization(value):
    media = previsores[value.name].mean()
    desvio_padrao = previsores[value.name].std()

    return (value - media) / desvio_padrao

previsores = previsores.apply(lambda row: z_score_normalization(row))

def get_dicionario_classes(classe):
    dict_classes = {}
    count = 0
    
    for i in classe.unique():
        dict_classes[i] = count
        count += 1
        
    return dict_classes

dict_classes = get_dicionario_classes(classe)

def transformar_categorico_em_numerico(valor, dict_classes):
    return dict_classes[valor]
    
classe = classe.apply(lambda row: transformar_categorico_em_numerico(row, dict_classes))

def codificar_classe():
    classe_codificada = {}
    
    array_classe = np.array([[1]  + ([0] * (len(classe.unique()) - 1)) ])
    
    count = 1
    
    classe_codificada[0] = array_classe.copy()
    
    for i in range(len(classe.unique()) - 1):

        array_classe[0][count - 1] = 0
        array_classe[0][count] = 1  
        classe_codificada[count] = array_classe.copy()
        count += 1
    
    return classe_codificada
        
classe_codificada = codificar_classe()

classe_nova = []

for i in classe:
    classe_nova.append(classe_codificada[i])
    
classe_nova = np.array(classe_nova).reshape(150,3)

def substituir_classe_codificada(valor, classe_codificada):
    return classe_codificada[valor]

classe = classe.apply(lambda row: substituir_classe_codificada(row, classe_codificada))

def dividir_dataframe(previsores, classe, p_treinamento, p_teste, p_validacao):
    x_treinamento = previsores.sample(frac = p_treinamento)
    y_treinamento = classe[x_treinamento.index]
    
    x_teste_sem_previsores = previsores.drop(x_treinamento.index)
    nova_p_teste = p_teste / (1 - p_treinamento)
    
    x_teste = x_teste_sem_previsores.sample(frac = nova_p_teste)
    y_teste = classe[x_teste.index]
    
    x_validacao = x_teste_sem_previsores.drop(x_teste.index)
    y_validacao = classe[x_validacao.index]
    
    return x_treinamento.reset_index(drop=True), y_treinamento, \
    x_teste.reset_index(drop=True), y_teste, x_validacao.reset_index(drop=True), y_validacao


def inicializar_pesos(dominio):
    pesos_final = []
    
    for i in range(len(previsores.columns)):
        pesos = [] 
        for j in range(len(dict_classes)):
            pesos.append(random.uniform(dominio[0], dominio[1]))
        pesos_final.append(pesos)
    return pesos_final

def somatoria(entradas, pesos):
    return np.dot(entradas, pesos)    

def funcao_ativacao_sigmoid(soma):
    resultado = 1 / (1 + math.e ** -soma)
    index_excitacao = np.argmax(resultado, 1) 
    
    count = 0
    for i in index_excitacao:
        resultado[count] = 0
        resultado[count][i] = 1
        count += 1
        
    return resultado
    
def funcao_custo(valor_correto, valor_previsto):
    erro = list(abs(np.array(valor_correto) - np.array(valor_previsto)))
    acerto = 0
    
    for i in erro:
        if sum(i) == 0:
            acerto += 1
    
    return sum(sum(erro)), acerto # valor escalar

def atualizar_peso(entrada, peso, erro, tx_aprendizado = 0.01):
    novo_peso = peso + sum((tx_aprendizado * entrada * erro))
    return novo_peso

def treinar(epocas, funcao_ativacao, funcao_custo, pesos, x_treinamento, y_treinamento,
                                     x_teste, y_teste):
    execucoes = 0
    precisoes_treinamento = []
    while execucoes < epocas:

        np.random.shuffle(x_treinamento.values) # embaralhar os valores dos previsores, por que sem isso, podemos ter sempre uma ordem fixa de ajuste de pesos, prejudicando a rede

        entradas = x_treinamento.values   
        soma = somatoria(entradas, pesos)
    
        ativacao = funcao_ativacao_sigmoid(soma)
    
        erro, acertos = funcao_custo(y_treinamento, ativacao) # baseado no meu resultado previsto, dado na última função de ativação.
    
        count = 0
        precisoes_treinamento.append(acertos / len(x_treinamento))    

        for i in range(entradas.shape[1]): # o for tem que atualizar cada peso da camada
            novo_peso = atualizar_peso(entradas[:, i], pesos[i], erro)
            pesos[count] = novo_peso
            count += 1
        
        execucoes += 1
    
    return precisoes_treinamento

previsores['bias'] = 1


def executar_perceptron(funcao_ativacao, funcao_custo, epocas, dominio_pesos = [0, 1]):
    precisao_treinamento = []
    # precisao_teste = []

    for i in range(30):
        pesos = inicializar_pesos(dominio_pesos) # Alterando os pesos em cada inicialização
        x_treinamento, y_treinamento, x_teste, y_teste, x_validacao, y_validacao = dividir_dataframe(previsores, classe_nova, 0.7, 0.15, 0.15)

        treinamento = treinar(epocas, funcao_ativacao, funcao_custo, pesos, x_treinamento, y_treinamento,
                                     x_teste, y_teste)
                                     
        precisao_treinamento.append(max(treinamento))
        # precisao_teste.append(max(treinamento[1]))


    print('Melhor precisão de treinamento', max(precisao_treinamento))
    print('Média de treinamento', np.mean(treinamento))
    print('Desvio de treinamento', np.std(treinamento))

    # print('Melhor precisão de teste', max(precisao_teste))

executar_perceptron(funcao_ativacao_sigmoid, funcao_custo, 200, [-0.5, 0.5])


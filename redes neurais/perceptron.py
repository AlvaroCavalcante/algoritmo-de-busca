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
previsores['bias'] = 1

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
    
    array_classe = [1] + [0] * (len(classe.unique()) - 1)
    
    count = 1
    
    classe_codificada[0] = array_classe.copy()
    
    for i in range(len(classe.unique()) - 1):

        array_classe[count - 1] = 0
        array_classe[count] = 1     
        classe_codificada[count] = array_classe.copy()
        count += 1
    
    return classe_codificada       

classe_codificada = codificar_classe()

def substituir_classe_codificada(valor, classe_codificada):
    return classe_codificada[valor]

classe = classe.apply(lambda row: substituir_classe_codificada(row, classe_codificada))

def inicializar_pesos():
    pesos_final = []
    
    for i in range(len(previsores.columns)):
        pesos = [] 
        for j in range(len(dict_classes)):
            pesos.append(random.random())
        pesos_final.append(pesos)
    return pesos_final

def somatoria(entradas, pesos):
    return np.dot(entradas, pesos)    

def funcao_ativacao_step(soma):
    ativacao = []
    for i in soma:
        if i > 0:
            ativacao.append(1)
        else:
            ativacao.append(0)

    return ativacao

def funcao_ativacao_sigmoid(soma):
    resultado = list(1 / (1 + math.e ** -soma))
    index_excitacao = resultado.index(max(resultado)) 
    resultado = [0] * len(soma)
    resultado[index_excitacao] = 1
    
    return resultado

def funcao_custo(valor_correto, valor_previsto):
    erro = list(abs(np.array(valor_correto) - np.array(valor_previsto)))
    return sum(erro) # valor escalar

def atualizar_peso(entrada, peso, erro, tx_aprendizado = 0.001):
    novo_peso = peso + (tx_aprendizado * entrada * erro)
    return novo_peso

def treinar(epocas, f_ativacao):
    execucoes = 0
    precisoes = [0]
    while execucoes < epocas:
        precisao = 0
        iteracao = 0

        np.random.shuffle(previsores.values) # embaralhar os valores dos previsores, por que sem isso, podemos ter sempre uma ordem fixa de ajuste de pesos, prejudicando a rede

        for i in previsores.values:
            entradas = i   
            soma = somatoria(entradas, pesos)
        
            ativacao = f_ativacao(soma)
        
            erro = funcao_custo(classe[iteracao], ativacao) # baseado no meu resultado previsto, dado na última função de ativação.
        
            if erro > 0:
                count = 0
                    
                for i in entradas:
                    novo_peso = atualizar_peso(i, pesos[count], erro)
                    pesos[count] = novo_peso
                    count += 1
            else:
                precisao += 100 / len(previsores)
                precisoes.append(precisao)

            iteracao += 1
        
        execucoes += 1
    return max(precisoes)

precisao_rede = []

for i in range(10):
    pesos = inicializar_pesos()
    precisao_rede.append(treinar(100, funcao_ativacao_sigmoid))

print('Melhor precisão da rede', max(precisao_rede))
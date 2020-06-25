import math
import random
import numpy as np
import pandas as pd
import itertools

dataframe = pd.read_csv('/home/alvaro/Documentos/mestrado/computação bio/algoritmos-otimizacao/dataset/berlin.csv')
dataframe['index'] = list(map(lambda x: x, dataframe.index))

def get_distancia_entre_pontos(cidade1, cidade2): # distância euclidiana 
    diferenca_coord = (cidade1[0] - cidade2[0])**2 + (cidade1[1] - cidade2[1])**2
    distancia = math.sqrt(diferenca_coord)
    return distancia

def get_dicionario_cidades(combinacao_cidades):
    cidades = {}
    for i in combinacao_cidades:
        cidades[i] = [1] 

    return cidades

def iniciar_colonia(n_formigas, n_cidades):
    colonia = []

    for i in range(n_formigas):
        colonia.append([(random.randint(0, n_cidades),)])

    return colonia

def get_distancia_cidades_vizinhas(formigas, dataframe):
    distancias = []

    for i in formigas:
        coordenadas_formiga = dataframe[dataframe['index'] == i[-1][-1]]
        coordenadas_formiga = coordenadas_formiga.iloc[:, 1:3].values
        
        removed_cities = list(map(lambda x: x[-1], i))

        df_cidades = dataframe[~dataframe['index'].isin(removed_cities)]
        df_cidades = df_cidades.values 

        distancia_formiga = {}      
        
        for vizinho in df_cidades:                
            distancia_formiga[(i[-1][-1], int(vizinho[0]))] = get_distancia_entre_pontos([coordenadas_formiga[0][0], \
                                coordenadas_formiga[0][1]], [vizinho[1], vizinho[2]])

        distancias.append(distancia_formiga)

    return distancias

def get_proximo_movimento(distancia_cidades_vizinhas, arestas_cidades, alfa = 1, beta = 5):
    proximos_movimentos = []
    distancias_percorridas = []
    
    for distancia in distancia_cidades_vizinhas:
        proba_cidade = [0, 0]
        count = 0
        for cidade in distancia:
            inverso_distancia = 1 / distancia[cidade]
            
            p = (arestas_cidades[cidade][0]**alfa) * (inverso_distancia**beta) / 1
            
            proba_cidade = [p, count] if p > proba_cidade[0] else proba_cidade
            count += 1
        
        cidade_mais_proxima = list(distancia.keys())[proba_cidade[1]]
        
        distancias_percorridas.append(distancia[cidade_mais_proxima])
        
        proximos_movimentos.append(cidade_mais_proxima)
        
    return proximos_movimentos, distancias_percorridas

def movimentar_formigas(formigas, cidades, movimento_formigas, distancia_percorrida, Q = 100):
    for i in range(len(formigas)):
        formigas[i].append(movimento_formigas[i])
        feromonios_depositados = Q / distancia_percorrida[i]
        cidades[movimento_formigas[i]] = [feromonios_depositados + cidades[movimento_formigas[i]][0]]

    return formigas

combinacao_cidades = list(itertools.permutations(dataframe['index'].values, 2))

arestas_cidades = get_dicionario_cidades(combinacao_cidades)

formigas = iniciar_colonia(20, len(dataframe) - 1)

execucoes = 0

while execucoes < 10:    
    distancia_cidades_vizinhas = get_distancia_cidades_vizinhas(formigas, dataframe)
    
    movimento_formigas, distancia_percorrida = get_proximo_movimento(distancia_cidades_vizinhas, arestas_cidades) # TODO: estou pegando a distância, mas falta os feromônios
    
    formigas = movimentar_formigas(formigas, arestas_cidades, movimento_formigas, distancia_percorrida)
      
    execucoes += 1

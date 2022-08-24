#Importando a biblioteca PuLP                          
#pip install pulp
import pulp as p
import pandas as pd
import numpy as np
from collections import OrderedDict

class Simplex(object):
    def __init__(self):
        pass
        
    def set_temp_tot_estud_municip(self, tempo):
        """
        Insira o tempo médio nacional de estudos semnanal dos estudantes
        """
        self.__temp_tot_estud_municip = tempo
        
    
    def set_notas_municipio(self, *notas):
        """
        Preencher na ordem:
        1 notas_arquivo_CN 
        2 notas_arquivo_CH 
        3 notas_arquivo_LC 
        4 notas_arquivo_MT 
        5 notas_arquivo_Red  
        """
        self.__notas_arquivo_CN = notas[0]
        self.__notas_arquivo_CH = notas[1]
        self.__notas_arquivo_LC = notas[2]
        self.__notas_arquivo_MT = notas[3]
        self.__notas_arquivo_Red = notas[4]
    
    def set_notas_desejada_User(self, *notas):
        """
        Preencher na ordem:
        1 notas_desejada_User_CN
        2 notas_desejada_User_CH
        3 notas_desejada_User_LC
        4 notas_desejada_User_MT
        5 notas_desejada_User_Red
        """
        self.__notas_desejada_User_CN = notas[0]
        self.__notas_desejada_User_CH = notas[1]
        self.__notas_desejada_User_LC = notas[2]
        self.__notas_desejada_User_MT = notas[3]
        self.__notas_desejada_User_Red = notas[4]
    
    # preparando os dados
    def somaNotas(self, *notas):
        soma = 0
        for i in notas: # soma todas as notas
            soma += i  
        return [i/soma for i in notas] # Retorna a lista com as porcentagens que representa cada nota

    def temp_med_p_area_conhecimento(self, **tempoKey):
        tempo = tempoKey.get("tempo") # Recuperando o tempo do usuario
        percents = tempoKey.get("percents") # percentual de notas
        return [i*tempo for i in percents] # Retorna a lista com o tempo de estudo em cada area do conhecimento
    
    def get_horas_prev_user(self):
        """
        Esse método retorna uma lista com todas as horas previstas para o usuário nas áreas do conhecimento
        na seguinte ordem: 
        1 HORAS_CN 
        2 HORAS_CH 
        3 HORAS_LC 
        4 HORAS_MT 
        5 HORAS_RED
        
        :return: List notas
        
        """
        self.__temp_med_municip_CN *= self.__percent_otimo_simplex[0]
        self.__temp_med_municip_CH *= self.__percent_otimo_simplex[1]
        self.__temp_med_municip_LC *= self.__percent_otimo_simplex[2]
        self.__temp_med_municip_MT *= self.__percent_otimo_simplex[3]
        self.__temp_med_municip_Red *= self.__percent_otimo_simplex[4]
        
        tempos = [self.__temp_med_municip_CN, self.__temp_med_municip_CH, self.__temp_med_municip_LC, self.__temp_med_municip_MT, self.__temp_med_municip_Red]
        
        soma = 0
        for i in tempos:
            soma += i
        
        tempos.append(soma)
        
        return tempos
    
    def get_notas_prev_user(self):
        """
        Esse método retorna uma lista com todas as notas previstas para o usuário nas áreas do conhecimento
        na seguinte ordem: 
        1 NOTA_CN 
        2 NOTA_CH 
        3 NOTA_LC 
        4 NOTA_MT 
        5 NOTA_RED
        
        :return: List notas
        
        """
        self.__notas_arquivo_CN *= self.__percent_otimo_simplex[0]
        self.__notas_arquivo_CH *= self.__percent_otimo_simplex[1]
        self.__notas_arquivo_LC *= self.__percent_otimo_simplex[2]
        self.__notas_arquivo_MT *= self.__percent_otimo_simplex[3]
        self.__notas_arquivo_Red *= self.__percent_otimo_simplex[4]
        
        return [self.__notas_desejada_User_CN, self.__notas_desejada_User_CH, self.__notas_desejada_User_LC, self.__notas_desejada_User_MT, self.__notas_desejada_User_Red]

    def resolver(self):
        # proporção das notas em % dos estudantes do municípo   
        list_percent_notas = self.somaNotas(self.__notas_arquivo_CN, self.__notas_arquivo_CH, self.__notas_arquivo_LC, self.__notas_arquivo_MT, self.__notas_arquivo_Red)

        # Tempo médio de estudos dos estudantes do municípo em cada área do conhecimento
        __list_temp_med_municip = self.temp_med_p_area_conhecimento(percents=list_percent_notas, tempo=self.__temp_tot_estud_municip)
        self.__temp_med_municip_CN = __list_temp_med_municip[0]
        self.__temp_med_municip_CH = __list_temp_med_municip[1]
        self.__temp_med_municip_LC = __list_temp_med_municip[2]
        self.__temp_med_municip_MT = __list_temp_med_municip[3]
        self.__temp_med_municip_Red = __list_temp_med_municip[4]

        # simplex
        # Definindo problema de maximização
        prob = p.LpProblem("Notas", p.LpMaximize)

        # Definindo variáveis de decisão >= 0
        x1 = p.LpVariable("x1", lowBound=0)
        x2 = p.LpVariable("x2", lowBound=0)
        x3 = p.LpVariable("x3", lowBound=0)
        x4 = p.LpVariable("x4", lowBound=0)
        x5 = p.LpVariable("x5", lowBound=0)

        coeficente = [self.__temp_med_municip_CN, self.__temp_med_municip_CH, 
                      self.__temp_med_municip_LC, self.__temp_med_municip_MT, 
                      self.__temp_med_municip_Red]
        
        # Função objetivo
        prob += (coeficente[0]*x1) + (coeficente[1]*x2) + (coeficente[2]*x3) + (coeficente[3]*x4) + (coeficente[4]*x5)

        # Restrições
        prob += (self.__notas_arquivo_CN*x1)  <= self.__notas_desejada_User_CN
        prob += (self.__notas_arquivo_CH*x2)  <= self.__notas_desejada_User_CH
        prob += (self.__notas_arquivo_LC*x3)  <= self.__notas_desejada_User_LC
        prob += (self.__notas_arquivo_MT*x4)  <= self.__notas_desejada_User_MT
        prob += (self.__notas_arquivo_Red*x5) <= self.__notas_desejada_User_Red

        # Resolvendo o modelo
        prob.solve()
        
        # Resultado da função objetivo contendo o número de horas ótimo de estudos do user
        self.__resultado_otimo_simplex = prob.objective.value()
        
        # Obtendo a lista de percentual ótimo por varável x
        self.__percent_otimo_simplex = [varX.value() for varX in prob.variables()]


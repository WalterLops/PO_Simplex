import sys
from interface import *
from PyQt6 import QtCore, QtGui, QtWidgets 
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QApplication, QStatusBar
from PyQt6.QtGui import QPixmap
class Otimizador(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        
        self.btnArquivo.clicked.connect(self.abrirArquivo)
        
        self.btnSair.clicked.connect(self.sair)
        
        self.btnAvaliar.clicked.connect(self.avaliar)
        
        self.validEstado.clicked.connect(self.prencheMunicipio)
        
        self.verInfoEstudantes.clicked.connect(self.preencherInfoEstudantes)
        
        self.municipio = list()
        
        self.btnReiniciar.clicked.connect(self.reiniciar)
        
        self.setLogo()
        
        self.show()
             
    def setLogo(self):
        """
        Insere a logo do Enem na tela
        """
        import os
        img = QPixmap(QPixmap(os.path.join(os.getcwd(), "img", "enem-logo.jpg")))
        newImg = img.scaledToWidth(400)
        self.imagem.clear()
        self.imagem.setPixmap(newImg)
        
    def abrirArquivo(self):
        import pandas as pd
        import numpy as np
        
        try:
            self.statusbar.showMessage("Lendo arquivo...")
            
            # janela de diálogo para escolher base de dados
            arquivo, _ =  QFileDialog.getOpenFileName(
                self,
                
                'Abir arquivo',
                #options=QFileDialog.DontUseNativeDialog
            )
            self.localArquivo.setText(arquivo)
            
            col = ["NO_MUNICIPIO_PROVA", "SG_UF_PROVA", "NU_NOTA_CN", "NU_NOTA_CH", 
            "NU_NOTA_LC", "NU_NOTA_MT", "NU_NOTA_REDACAO"]
            
            self.MICRODADOS_ENEM_2020 = pd.read_csv(arquivo, encoding='ISO-8859-1', sep = ';', usecols=col, memory_map=True) #lendo arquivo
            self.MICRODADOS_ENEM_2020.dropna(axis=0, inplace=True) #limpando dados nulos
            
            #obter os estados e municípios 
            estados = self.MICRODADOS_ENEM_2020.sort_values(by=['SG_UF_PROVA'], ascending=True)
            estados = estados['SG_UF_PROVA'].unique()

            estados = [i for i in estados]
            estados
            
            self.btnEstado.addItems(estados)
            
            self.statusbar.clearMessage()
        
        except Exception:
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Ocorreu um erro. Tente novamente")
     
    def obterNotasMunicipio(self):
        """
        Se a base de dados não estiver sido submetida o retorno será -1
        :return:  lista com a mediana das notas do município
        """
        try:
            # Obtendo minicipio 
            coluna, cidade = 'NO_MUNICIPIO_PROVA', self.btnMunicipio.currentText()
            
            # Filtrando os dados do minicipio na coluna NO_MUNICIPIO_PROVA
            dadosMunicipio = self.MICRODADOS_ENEM_2020.query(f"{coluna} == '{cidade}'")
            
            # Ordenando os dados em forma crescente com base na coluna NU_NOTA_REDACAO
            dadosMunicipio.sort_values(by=['NU_NOTA_REDACAO'], ascending=False)

            # Obtendo dados estatísticos dos dados selecionados
            dadosEstatisticos = dadosMunicipio.describe()
            
            # Obtendo a mediana
            dadosEstatisticos.query("index == '50%'", inplace=True)
            
            # Extraindo os dados
            medianaNotas = [j for i in dadosEstatisticos.values for j in i]
        
            return medianaNotas
        
        except AttributeError:
            self.statusbar.clearMessage() 
            self.statusbar.showMessage("Por favor escolha a base de dados primeiro")
            return -1
        
    def avaliar(self):
        """
        Resolve o modelo Simplex com base em:
            mediana das notas do município;
            notas que o usuário deseja obter;
            tempo médio de estudos dos estudante do municípo para as provas do Enem
        """
        from Simplex import Simplex
        
        # obtendo a mediana das notas do minicipio
        notas_arquivo = self.obterNotasMunicipio()
        if notas_arquivo == -1:
            return 0
        
        nota_cn, nota_ch, nota_lc, nota_mat, nota_red = notas_arquivo
       
        try:
            # obtendo as notas desejadas
            while True:
                self.notasUser = [self.cxCN.text(), self.cxCH.text(), self.cxLC.text(), self.cxMat.text(), self.cxRed.text()]
                self.notasUser = [int(i) for i in self.notasUser]
                
                cont_valores_m_1000 = 0
                for i in self.notasUser:
                    if i > 1000:
                        cont_valores_m_1000 += 1
                
                if cont_valores_m_1000 > 0:
                    self.statusbar.clearMessage()
                    self.statusbar.showMessage("Ocorreu um erro. Digite apenas notas <= 1000")
                    return -1
                else:
                    break
            
            # obtendo o tempo de estudos dos estudantes da região
            self.tempo = (int(self.cxTempoHoras.text())*3600) + int(self.cxTempoMinutos.text())*60
            
            if self.tempo <= 0:
                self.statusbar.clearMessage()
                self.statusbar.showMessage("Ocorreu um erro. Digite o valor de tempo maior que 0")
                return -1
            
        except ValueError as e:
            self.statusbar.clearMessage()
            self.statusbar.showMessage("Ocorreu um erro. Digite apenas números")
            return -1
        
        simplex = Simplex()
        
        simplex.set_temp_tot_estud_municip(self.tempo)
        
        # preenchendo dos atributos relacionados as notas do município selecionado
        simplex.set_notas_municipio(nota_cn, nota_ch, nota_lc, nota_mat, nota_red)
        
        # preenchendo dos atributos relacionados as notas do notas desejadas do usuário
        simplex.set_notas_desejada_User(self.notasUser[0], self.notasUser[1], self.notasUser[2], self.notasUser[3], self.notasUser[4])
        
        # resulvendo o modelo
        simplex.resolver()

        # formatando o tempo em segundos pra HH:MM:SS
        horarios = [self.formataHorio(i) for i in simplex.get_horas_prev_user()]

        # preenchendo os horários de estudos recomendado
        self.preencheHorarios(horarios)
    
    def preencherInfoEstudantes(self):
        """
        Gera o gráfico e a tabela com as legendas 
        """
        self.adcionarGrafico()
        self.tabGrafico()
        
    def formataHorio(self, segundos):
        """
        Converte um valor de tempo em segundos para formato hora completa
        """
        valores = list(range(3))
        valores[0] = int(segundos / 3600) #hora
        valores[1] = int((segundos / 60) % 60) #minutos
        valores[2] = int((segundos % 60)) #segundos
        
        # adcionando 0 em valores menores que 10
        for j, i in enumerate(valores):
            if i < 10:
                valores[j] = f'0{i}'
        
        # retorno formatado
        return f'{valores[0]}:{valores[1]}:{valores[2]}'
           
    def prencheMunicipio(self):
        """
        Preenche o comboBox com as informações dos municípios
        """
        self.btnMunicipio.setDuplicatesEnabled(True)
        self.btnMunicipio.clear()
        
        busca = self.btnEstado.currentText()
        cidadesEscolhidas = self.MICRODADOS_ENEM_2020.query(f"SG_UF_PROVA == '{busca}'")
        cidadesEscolhidas = cidadesEscolhidas.sort_values(by=['NO_MUNICIPIO_PROVA'], ascending=True)
        cidadesEscolhidas = cidadesEscolhidas['NO_MUNICIPIO_PROVA'].unique()
        cidadesEscolhidas = [ i for i in cidadesEscolhidas]
        self.btnMunicipio.addItems(cidadesEscolhidas)
    
    def preencheHorarios(self, lista_horarios):
        """
        Preenche os horários de estudos recomendado gerado pelo Simplex
        :param lista_horarios: recebe lista de horarios formatados em formato str
        """
        
        # preenche a tabela com descrição dos dados gerados pelo Simplex
        self.preencherTabela()
        self.tempo1.setText(lista_horarios[0])
        self.tempo2.setText(lista_horarios[1])
        self.tempo3.setText(lista_horarios[2])
        self.tempo4.setText(lista_horarios[3])
        self.tempo5.setText(lista_horarios[4])
        self.tempo_total.setText(lista_horarios[5])
        
    def preencherTabela(self):
        """
        Preenche a descrição dos dados da tabela do Simplex
        """
        self.tituloTabelaResult.setText("Resultado")
        self.subtituloTabelaResult.setText("Horas de estudo recomendas")
        self.result1.setText("Ciências Humanas e suas Tecnologias")
        self.result2.setText("Ciências da Natureza e suas Tecnologias")
        self.result3.setText("Linguagens, Códigos e suas Tecnologias")
        self.result4.setText("Matemática e suas Tecnologias")
        self.result5.setText("Redação")
        self.result_total.setText("Tempo total")
    
    def limparTabela(self):
        """
        Faz a limpeza de todos os elementos variáveis da tela
        """
        self.subtituloTabelaResult.clear()
        self.result1.clear()
        self.result2.clear()
        self.result3.clear()
        self.result4.clear()
        self.result5.clear()
        self.tempo1.clear()
        self.tempo2.clear()
        self.tempo3.clear()
        self.tempo4.clear()
        self.tempo5.clear()
        self.result_total.clear()
        self.tempo_total.clear()
        
        self.tituloTabelaResult.clear()
        self.cxTempoHoras.setText("00")
        self.cxTempoMinutos.setText("00")
        
        self.cxCN.clear()
        self.cxCH.clear()
        self.cxLC.clear()
        self.cxMat.clear()
        self.cxRed.clear()
        
        self.bar1.clear()
        self.bar2.clear()
        self.bar3.clear()
        self.bar4.clear()
        self.bar5.clear()
              
    def adcionarGrafico(self):
        import numpy as np
        import matplotlib.pyplot as plt
        import os
        
        
        # obtendo a mediana das notas do minicipio
        notas_arquivo = self.obterNotasMunicipio()
        if notas_arquivo == -1:
            return 0
        
        yValores = notas_arquivo
        
        colunasGrafico = ["NOTA_CN", "NOTA_CH", "NOTA_LC", "NOTA_MT", "NOTA_REDACAO"]
        #xValores = list(dadosEstatisticos.columns.values)
        xValores = colunasGrafico
        
        # definindo indices e larguras das colunas do gráfico
        index = np.arange(len(xValores)) + 0.3
        bar_width = 0.4

        # plotando as barras do gráfico
        plt.bar(index, yValores, bar_width)

        # título do eixo y
        plt.ylabel("Notas")
        
        # título do gráfico
        plt.xlabel("Áreas do conhecimento")
        
        # valores do eixo x
        plt.xticks(np.arange(len(xValores)), xValores)
        
        # título do gráfico
        plt.title('Mediana das notas dos alunos')
        
        # criando a pasta onde seram armazenadas as imagens do gráfico geradas 
        self.diretorio = os.path.join(os.getcwd(), "arquivosOtimizador")
        if not os.path.exists(self.diretorio):
            os.makedirs(self.diretorio)
        
        # gerando a imagem do gráfico na pasta definida acima
        plt.savefig(os.path.join(self.diretorio, "grafico.png"), format='png')
                
        # definindo o título do gráfico         
        self.idGrafico.setText("Gráfico com o desempenho dos alunos na região")
        
        # carregando a imagem da pasta criada
        img = QPixmap(QPixmap(os.path.join(self.diretorio, "grafico.png")))
        
        # definindo a imagem com a escala de 400px de largura
        newImg = img.scaledToWidth(400)
        self.imagem.clear()
        
        # enviando o gráfico para a tela
        self.imagem.setPixmap(newImg)
        
    def tabGrafico(self):
        """
        Preenche a tabela com a descrição dos valores do gráfico de barras
        """
        notas_arquivo = self.obterNotasMunicipio()
        if notas_arquivo == -1:
            return 0
        
        a0, a1, a2, a3, a4 = notas_arquivo
            
        self.bar1.setText(f"{'Barra 1: Nota da prova de Ciências da Natureza':.<50} {a0:2.2f}")
        self.bar2.setText(f"{'Barra 2: Nota da prova de Ciências Humanas':.<50} {a1:2.2f}")
        self.bar3.setText(f"{'Barra 3: Nota da prova de Linguagens e Códigos':.<50} {a2:2.2f}")
        self.bar4.setText(f"{'Barra 4: Nota da prova de Matemática':.<50} {a3:2.2f}")
        self.bar5.setText(f"{'Barra 5: Nota da prova de Redação':.<50} {a4:2.2f}") 
    
    def reiniciar(self):
        """
        Faz a limpeza dos elementos:
            self.btnMunicipio
            self.imagem
            self.idGrafico
            self.limparTabela()
            self.statusbar
        e insere novamente o logo do app na tela
        """
        self.btnMunicipio.clear()
        self.imagem.clear()
        self.idGrafico.clear()
        self.limparTabela()
        self.statusbar.clearMessage()
        self.setLogo()
        
    def sair (self):
        """
        Faz logoff e remove a pasta onde foram geradas as imagens do gráfico
        """
        import shutil
        try:
            # removendo o diretório onde é gerado a imagem do gráfico
            shutil.rmtree(self.diretorio)
        except AttributeError as e:
            pass
        except OSError:
            pass
        finally:
            self.close()
     
        
if __name__ == '__main__':
    qt = QApplication(sys.argv)
    otimizador = Otimizador()
    sys.exit(qt.exec())
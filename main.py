import sys
from interface import *
from PyQt6 import QtCore, QtGui, QtWidgets 
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QApplication
from PyQt6.QtGui import QPixmap

class Novo(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        
        self.btnArquivo.clicked.connect(self.abrirArquivo)
        
        self.btnSair.clicked.connect(self.sair)
        
        self.btnAvaliar.clicked.connect(self.avaliar)
        
        #self.estados = ["Espírito Santo", "Minas Gerais", "Rio de Janeiro"]
        
        self.validEstado.clicked.connect(self.prencheMunicipio)
        
        self.municipio = list()
        
        self.btnReiniciar.clicked.connect(self.reiniciar)
        
        self.show()
    def sair (self):
        import shutil

        try:
            shutil.rmtree(self.diretorio)
        except OSError as e:
            pass
        self.close()
        
    def abrirArquivo(self):
        try:
            self.infoArquivo.setText("Lendo arquivo...")
            
            
            arquivo, _ =  QFileDialog.getOpenFileName(
                self,
                
                'Abir arquivo',
                
                #options=QFileDialog.DontUseNativeDialog
            )
            self.localArquivo.setText(arquivo)
            #self.btnEstado.addItems(self.estados)
            
            import pandas as pd
            import numpy as np
            
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
            
            self.infoArquivo.clear()
        
        except Exception:
            self.infoArquivo.setText("Ocorreu um erro. Tente novamente")
        
        
    def avaliar(self):
        text = f'0{self.btnTempo.time().hour()}:0{self.btnTempo.time().minute()}'
       
        self.preencheHorarios(text,text,text,text,text)
        
        self.adcionarGrafico()
        
        self.tabGrafico()
        
        
    def prencheMunicipio(self):
        self.btnMunicipio.setDuplicatesEnabled(True)
        self.btnMunicipio.clear()
        
        '''
        if self.estados[0] == self.btnEstado.currentText():
            self.municipio = ["VILA VELHA", "CARIACICA"]
        if self.estados[1] == self.btnEstado.currentText():
            self.municipio = ["Diamantina", "Belo Horizonte"]
        if self.estados[2] == self.btnEstado.currentText():
            self.municipio = ["SÃO GONÇALO", "DUQUE DE CAXIAS"]
        self.btnMunicipio.addItems(self.municipio)'''
        
        busca = self.btnEstado.currentText()
        cidadesEscolhidas = self.MICRODADOS_ENEM_2020.query(f"SG_UF_PROVA == '{busca}'")
        cidadesEscolhidas = cidadesEscolhidas.sort_values(by=['NO_MUNICIPIO_PROVA'], ascending=True)
        cidadesEscolhidas = cidadesEscolhidas['NO_MUNICIPIO_PROVA'].unique()
        cidadesEscolhidas = [ i for i in cidadesEscolhidas]
        self.btnMunicipio.addItems(cidadesEscolhidas)
    
    def preencheHorarios(self, *args):
        self.preencherTabela()
        self.tempo1.setText(args[0])
        self.tempo2.setText(args[1])
        self.tempo3.setText(args[2])
        self.tempo4.setText(args[3])
        self.tempo5.setText(args[4])
        
    def preencherTabela(self):
        self.result0.setText("Horas de estudo recomendas")
        self.result1.setText("Ciências Humanas e suas Tecnologias")
        self.result2.setText("Ciências da Natureza e suas Tecnologias")
        self.result3.setText("Linguagens, Códigos e suas Tecnologias")
        self.result4.setText("Matemática e suas Tecnologias")
        self.result5.setText("Redação")
    
    def limparTabela(self):
        self.result0.clear()
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
        
        self.bar1.clear()
        self.bar2.clear()
        self.bar3.clear()
        self.bar4.clear()
        self.bar5.clear()

        
    def adcionarGrafico(self):
        import numpy as np
        import matplotlib.pyplot as plt
        import os
        
        co, val = 'NO_MUNICIPIO_PROVA', self.btnMunicipio.currentText()
        a = self.MICRODADOS_ENEM_2020.query(f"{co} == '{val}'")
        a.sort_values(by=['NU_NOTA_REDACAO'], ascending=False)

        d = a.describe()
        d.query("index == '50%'", inplace=True)
        
        colunasGrafico = ["NOTA_CN", "NOTA_CH", "NOTA_LC", "NOTA_MT", "NOTA_REDACAO"]
        
        yValores = [(j) for i in d.values for j in i]
        xValores = list(d.columns.values)
        
        # Info Label
        '''legenda = [f"NOTA_CN = Nota da prova de Ciências da Natureza"
        +f"\nNOTA_CH = Nota da prova de Ciências Humanas"
        +f"\nNOTA_LC = Nota da prova de Linguagens e Códigos"
        +f"\nNOTA_MT = Nota da prova de Matemática"
        +f"\nNOTA_REDACAO = Nota da prova de redação"]'''
        

        xValores = colunasGrafico
        
        index = np.arange(len(xValores)) + 0.3
        bar_width = 0.4

        plt.bar(index, yValores, bar_width)

        plt.ylabel("Notas")
        plt.xlabel("Áreas do conhecimento")
        plt.xticks(np.arange(len(xValores)), xValores)
        plt.title('Mediana das notas dos alunos')
        
        self.diretorio = os.path.join(os.getcwd(), "arquivosOtimizador")
        if not os.path.exists(self.diretorio):
            os.makedirs(self.diretorio)

        plt.savefig(os.path.join(self.diretorio, "grafico.png"), format='png')
                
        self.idGrafico.setText("Gráfico com com o desempenho dos alunos na região")
        img = QPixmap(QPixmap(os.path.join(self.diretorio, "grafico.png")))
        newImg = img.scaledToWidth(400)
        self.imagem.clear()
        self.imagem.setPixmap(newImg)
        
    def tabGrafico(self):
        co, val = 'NO_MUNICIPIO_PROVA', self.btnMunicipio.currentText()
        a = self.MICRODADOS_ENEM_2020.query(f"{co} == '{val}'")
        a.sort_values(by=['NU_NOTA_REDACAO'], ascending=False)

        d = a.describe()
        d.query("index == '50%'", inplace=True)
        
        yValores = [j for i in d.values for j in i]
        
        a0, a1, a2, a3, a4 = yValores
            
        self.bar1.setText(f"{'Barra 1: Nota da prova de Ciências da Natureza':.<49} {a0:>2.2f}")
        self.bar2.setText(f"{'Barra 2: Nota da prova de Ciências Humanas':.<49} {a1:>2.2f}")
        self.bar3.setText(f"{'Barra 3: Nota da prova de Linguagens e Códigos':.<49} {a2:>2.2f}")
        self.bar4.setText(f"{'Barra 4: Nota da prova de Matemática':.<49} {a3:>2.2f}")
        self.bar5.setText(f"{'Barra 5: Nota da prova de redação':.<49} {a4:>2.2f}") 
        pass
    
    def popupGrafico(self, xValores, yValores):
        import numpy as np
        import matplotlib.pyplot as pltp
        
        index = np.arange(len(xValores)) + 0.3
        bar_width = 0.4

        pltp.bar(index, yValores, bar_width)

        pltp.ylabel("Notas")
        pltp.xlabel("Áreas do conhecimento")
        pltp.xticks(np.arange(len(xValores)), xValores)
        pltp.title('Mediana das notas dos alunos')
        pltp.show()
    
    def reiniciar(self):
        self.btnEstado.clear()
        self.btnMunicipio.clear()
        self.localArquivo.clear()
        self.imagem.clear()
        self.idGrafico.clear()
        self.limparTabela()
        pass
        
if __name__ == '__main__':
    qt = QApplication(sys.argv)
    novo = Novo()
    sys.exit(qt.exec())